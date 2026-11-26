<?php

namespace App\Http\Controllers;

use App\Http\Requests\PredictTicketRequest;
use App\Services\MlApiClient;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Log;
use Illuminate\View\View;
use RuntimeException;
use Throwable;

/**
 * Gateway for ml-api POST /predict.
 */
class PredictController extends Controller
{
    public function form(): View
    {
        return view('predict');
    }

    public function predict(PredictTicketRequest $request): JsonResponse
    {
        $features = $request->features();

        Log::info('predict.request', $features);

        try {
            $result = MlApiClient::fromConfig()->predict($features);
        } catch (RuntimeException $e) {
            Log::warning('predict.ml_api_failed', [
                'features' => $features,
                'error' => $e->getMessage(),
            ]);

            return response()->json(['error' => $e->getMessage()], 502);
        } catch (Throwable $e) {
            Log::error('predict.unexpected_error', [
                'features' => $features,
                'error' => $e->getMessage(),
                'exception' => $e::class,
            ]);

            return response()->json(['error' => $e->getMessage()], 500);
        }

        Log::info('predict.success', [
            'features' => $features,
            'prediction' => $result['prediction'] ?? null,
            'label' => $result['label'] ?? null,
        ]);

        return response()->json(['data' => $result]);
    }
}
