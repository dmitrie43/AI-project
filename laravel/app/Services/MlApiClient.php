<?php

namespace App\Services;

use Illuminate\Http\Client\ConnectionException;
use Illuminate\Http\Client\RequestException;
use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;
use RuntimeException;
use Throwable;

/**
 * HTTP client to the ml-api microservice (FastAPI).
 */
class MlApiClient
{
    public function __construct(
        private readonly string $baseUrl,
        private readonly int $timeoutSeconds,
        private readonly int $retryTimes,
    ) {}

    public static function fromConfig(): self
    {
        return new self(
            baseUrl: rtrim((string) config('services.ml_api.url'), '/'),
            timeoutSeconds: (int) config('services.ml_api.timeout', 10),
            retryTimes: (int) config('services.ml_api.retry', 2),
        );
    }

    /**
     * @return array<string, mixed>
     */
    public function health(): array
    {
        $started = microtime(true);

        Log::debug('ml_api.health.request', [
            'base_url' => $this->baseUrl,
        ]);

        try {
            $response = Http::baseUrl($this->baseUrl)
                ->timeout($this->timeoutSeconds)
                ->retry($this->retryTimes, 200)
                ->acceptJson()
                ->get('/health');

            $response->throw();
        } catch (Throwable $e) {
            Log::warning('ml_api.health.failed', [
                'base_url' => $this->baseUrl,
                'duration_ms' => (int) ((microtime(true) - $started) * 1000),
                'error' => $e->getMessage(),
            ]);

            throw $e;
        }

        /** @var array<string, mixed> $json */
        $json = $response->json();

        Log::debug('ml_api.health.response', [
            'base_url' => $this->baseUrl,
            'duration_ms' => (int) ((microtime(true) - $started) * 1000),
            'body' => $json,
        ]);

        return $json;
    }

    /**
     * POST /analyze with a CSV upload.
     *
     * @return array<string, mixed>
     */
    public function analyze(UploadedFile $file): array
    {
        $path = $file->getRealPath();
        if ($path === false) {
            throw new RuntimeException('Uploaded file path is not readable');
        }

        $binary = file_get_contents($path);
        if ($binary === false) {
            throw new RuntimeException('Cannot read uploaded file');
        }

        $filename = $file->getClientOriginalName() ?: 'upload.csv';
        $started = microtime(true);

        Log::info('ml_api.analyze.request', [
            'base_url' => $this->baseUrl,
            'filename' => $filename,
            'size_bytes' => strlen($binary),
            'timeout' => $this->timeoutSeconds,
            'retry' => $this->retryTimes,
        ]);

        try {
            $response = Http::baseUrl($this->baseUrl)
                ->timeout($this->timeoutSeconds)
                ->retry($this->retryTimes, 200)
                ->attach(
                    'file',
                    $binary,
                    $filename,
                )
                ->post('/analyze');
        } catch (ConnectionException $e) {
            Log::error('ml_api.analyze.connection_error', [
                'base_url' => $this->baseUrl,
                'filename' => $filename,
                'duration_ms' => (int) ((microtime(true) - $started) * 1000),
                'error' => $e->getMessage(),
            ]);

            throw new RuntimeException(
                'ml-api unreachable at '.$this->baseUrl,
                previous: $e,
            );
        }

        $durationMs = (int) ((microtime(true) - $started) * 1000);

        try {
            $response->throw();
        } catch (RequestException $e) {
            $detail = $response->json('detail') ?? $response->body();

            Log::error('ml_api.analyze.http_error', [
                'base_url' => $this->baseUrl,
                'filename' => $filename,
                'status' => $response->status(),
                'duration_ms' => $durationMs,
                'detail' => $detail,
            ]);

            throw new RuntimeException(
                'ml-api error: '.(is_string($detail) ? $detail : json_encode($detail)),
                previous: $e,
            );
        }

        /** @var array<string, mixed> $json */
        $json = $response->json();

        Log::info('ml_api.analyze.response', [
            'base_url' => $this->baseUrl,
            'filename' => $filename,
            'status' => $response->status(),
            'duration_ms' => $durationMs,
            'rows' => $json['rows'] ?? null,
        ]);

        return $json;
    }

    /**
     * POST /predict with ticket features JSON.
     *
     * @param  array{category: string, priority: float|null, satisfaction: float|null, tag_count: float}  $features
     * @return array<string, mixed>
     */
    public function predict(array $features): array
    {
        $started = microtime(true);

        Log::info('ml_api.predict.request', [
            'base_url' => $this->baseUrl,
            'features' => $features,
        ]);

        try {
            $response = Http::baseUrl($this->baseUrl)
                ->timeout($this->timeoutSeconds)
                ->retry($this->retryTimes, 200)
                ->acceptJson()
                ->asJson()
                ->post('/predict', $features);
        } catch (ConnectionException $e) {
            Log::error('ml_api.predict.connection_error', [
                'base_url' => $this->baseUrl,
                'duration_ms' => (int) ((microtime(true) - $started) * 1000),
                'error' => $e->getMessage(),
            ]);

            throw new RuntimeException(
                'ml-api unreachable at '.$this->baseUrl,
                previous: $e,
            );
        }

        $durationMs = (int) ((microtime(true) - $started) * 1000);

        try {
            $response->throw();
        } catch (RequestException $e) {
            $detail = $response->json('detail') ?? $response->body();

            Log::error('ml_api.predict.http_error', [
                'base_url' => $this->baseUrl,
                'status' => $response->status(),
                'duration_ms' => $durationMs,
                'detail' => $detail,
            ]);

            throw new RuntimeException(
                'ml-api error: '.(is_string($detail) ? $detail : json_encode($detail)),
                previous: $e,
            );
        }

        /** @var array<string, mixed> $json */
        $json = $response->json();

        Log::info('ml_api.predict.response', [
            'base_url' => $this->baseUrl,
            'status' => $response->status(),
            'duration_ms' => $durationMs,
            'prediction' => $json['prediction'] ?? null,
        ]);

        return $json;
    }

    /**
     * @return array<string, mixed>
     */
    public function metrics(): array
    {
        $response = Http::baseUrl($this->baseUrl)
            ->timeout($this->timeoutSeconds)
            ->retry($this->retryTimes, 200)
            ->acceptJson()
            ->get('/metrics');

        $response->throw();

        /** @var array<string, mixed> $json */
        $json = $response->json();

        return $json;
    }
}

