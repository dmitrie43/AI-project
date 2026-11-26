<?php

namespace App\Http\Controllers;

use App\Http\Requests\AnalyzeCsvRequest;
use App\Services\MlApiClient;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\Log;
use Illuminate\View\View;
use RuntimeException;
use Throwable;

/**
 * CSV analyze gateway: proxies to ml-api and caches results by content hash.
 */
class AnalyzeController extends Controller
{
    public function form(): View
    {
        return view('analyze');
    }

    public function analyze(AnalyzeCsvRequest $request): JsonResponse
    {
        $file = $request->uploadedFile();
        $filename = $file->getClientOriginalName() ?: 'upload.csv';
        $sizeBytes = $file->getSize() ?: 0;
        $contents = file_get_contents($file->getRealPath());
        $contentHash = hash('sha256', (string) $contents);
        $cacheKey = 'ml_analyze:'.$contentHash;

        Log::info('analyze.request', [
            'filename' => $filename,
            'size_bytes' => $sizeBytes,
            'content_hash' => $contentHash,
        ]);

        if (Cache::has($cacheKey)) {
            Log::info('analyze.cache_hit', [
                'content_hash' => $contentHash,
                'filename' => $filename,
            ]);

            return response()->json([
                'cached' => true,
                'data' => Cache::get($cacheKey),
            ]);
        }

        Log::info('analyze.cache_miss', [
            'content_hash' => $contentHash,
            'filename' => $filename,
        ]);

        try {
            $result = MlApiClient::fromConfig()->analyze($file);
        } catch (RuntimeException $e) {
            Log::warning('analyze.ml_api_failed', [
                'content_hash' => $contentHash,
                'filename' => $filename,
                'error' => $e->getMessage(),
            ]);

            return response()->json(['error' => $e->getMessage()], 502);
        } catch (Throwable $e) {
            Log::error('analyze.unexpected_error', [
                'content_hash' => $contentHash,
                'filename' => $filename,
                'error' => $e->getMessage(),
                'exception' => $e::class,
            ]);

            return response()->json(['error' => $e->getMessage()], 500);
        }

        Cache::put($cacheKey, $result, now()->addMinutes(30));

        Log::info('analyze.success', [
            'content_hash' => $contentHash,
            'filename' => $filename,
            'rows' => $result['rows'] ?? null,
            'cached' => false,
        ]);

        return response()->json([
            'cached' => false,
            'data' => $result,
        ]);
    }

    public function mlHealth(): JsonResponse
    {
        try {
            $health = MlApiClient::fromConfig()->health();

            Log::info('ml_health.ok', ['ml_api' => $health]);

            return response()->json([
                'laravel' => 'ok',
                'ml_api' => $health,
            ]);
        } catch (Throwable $e) {
            Log::warning('ml_health.unreachable', [
                'error' => $e->getMessage(),
            ]);

            return response()->json([
                'laravel' => 'ok',
                'ml_api' => 'unreachable',
                'error' => $e->getMessage(),
            ], 502);
        }
    }
}
