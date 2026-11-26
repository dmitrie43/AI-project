<?php

namespace App\Http\Requests;

use Illuminate\Contracts\Validation\Validator;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Http\Exceptions\HttpResponseException;

class PredictTicketRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    /**
     * @return array<string, list<string>>
     */
    public function rules(): array
    {
        return [
            'category' => ['required', 'string', 'max:64'],
            'priority' => ['nullable', 'numeric', 'min:1', 'max:5'],
            'satisfaction' => ['nullable', 'numeric', 'min:1', 'max:5'],
            'tag_count' => ['nullable', 'numeric', 'min:0', 'max:50'],
        ];
    }

    /**
     * @return array{category: string, priority: float|null, satisfaction: float|null, tag_count: float}
     */
    public function features(): array
    {
        return [
            'category' => (string) $this->input('category'),
            'priority' => $this->filled('priority') ? (float) $this->input('priority') : null,
            'satisfaction' => $this->filled('satisfaction') ? (float) $this->input('satisfaction') : null,
            'tag_count' => $this->filled('tag_count') ? (float) $this->input('tag_count') : 0.0,
        ];
    }

    protected function failedValidation(Validator $validator): void
    {
        throw new HttpResponseException(response()->json([
            'message' => 'The given data was invalid.',
            'errors' => $validator->errors(),
        ], 422));
    }
}
