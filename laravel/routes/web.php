<?php

use App\Http\Controllers\AnalyzeController;
use App\Http\Controllers\PredictController;
use Illuminate\Support\Facades\Route;

Route::get('/', [AnalyzeController::class, 'form'])->name('analyze.form');
Route::post('/analyze', [AnalyzeController::class, 'analyze'])->name('analyze.run');
Route::get('/ml-health', [AnalyzeController::class, 'mlHealth'])->name('ml.health');

Route::get('/predict', [PredictController::class, 'form'])->name('predict.form');
Route::post('/predict', [PredictController::class, 'predict'])->name('predict.run');
