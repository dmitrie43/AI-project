# 90-дневный календарь: Дмитрий Ефимов → AI / GenAI Engineer

Персональный план на **13 недель (~90 дней)**, **15–18 ч/нед**. Базовая дорожная карта (не дублировать целиком): `[/cursor/stores/bc-bd190d03-7a61-4259-967e-d5fd8ff9a97a/docs/ai-engineer-roadmap.md](/cursor/stores/bc-bd190d03-7a61-4259-967e-d5fd8ff9a97a/docs/ai-engineer-roadmap.md)`.

**Профиль:** PHP/Laravel, MySQL/PostgreSQL, Redis, Docker, Elasticsearch · Python ≈ 0 · ML/LLM = 0  
**Цели:** (1) предложить и собрать внутренний GenAI-пилот на работе; (2) подготовка к собеседованиям AI/GenAI Engineer.

**Трек:** Python+данные (жёстко, н. 1–3) → классический ML легко → LLM/RAG/агенты как основной трек, с мостом Laravel → FastAPI.

---



## Пилот для работы (pitch + MVP)

**Название:** Internal Docs & Ticket Assistant (поддержка / онбординг / поиск по внутренним докам)

**Проблема:** сотрудники и поддержка тратят время на поиск по Confluence/Notion/вики, тикетам и runbook’ам; ответы разрознены, нет citations.

**Предложение (1 слайд / ½ страницы менеджеру):**

- Laravel — UI, auth (SSO/RBAC), audit log, gateway API
- Python FastAPI — ingest, embeddings, retrieval, LLM-ответы
- PostgreSQL + **pgvector** — чанки/эмбеддинги; опционально **Elasticsearch** — BM25 / hybrid
- Redis — очередь ingest/инференса, кэш эмбеддингов и ответов
- Docker Compose — локальный стенд; секреты через env

**MVP (4–6 недель после фундамента, укладывается в н. 7–12):**

1. Ingest 50–200 внутренних (или синтетических/open) документов → chunk → index
2. `POST /ask` с ответом + citations (файл/якорь)
3. Laravel-страница чата за существующей auth
4. Golden set ≥ 30 вопросов; hit-rate retrieval + ручная оценка ответов
5. Метрики: latency p95, tokens/$, cache hit; Redis job для async ingest
6. Design note: риски (PII, prompt injection), cost ceiling, fallback «не знаю»

**Метрики успеха пилота:** ≥70% полезных ответов на golden set; p95 < 5–8 с на CPU/API; понятный cost/запрос; 5–10 внутренних пользователей попробовали.

---



## Неделя 1 — Python с нуля под ML-стиль (~16 ч)

**Темы:** Python 3.11+, venv/uv, типы, dataclasses, pathlib, CLI (`argparse`/`typer`), пакетная структура, pytest минимум.

**Практика:**

- [x] Настроить uv/venv + ruff/pytest
- [x] CLI: читает CSV → считает агрегаты → пишет JSON-отчёт
- [x] 10–15 маленьких упражнений на типы/dataclass/ошибки I/O

**Deliverable:** репо `py-fundamentals` — CLI + README «как запустить».

**Interview slice:** «Почему Python в AI-стеке при сильном Laravel?» — экосистема ML/LLM + ваш backend как gateway/продукт.

---



## Неделя 2 — Данные: NumPy, pandas, SQL (~17 ч)

**Темы:** NumPy массивы/broadcast; pandas: load/clean/groupby/merge; train/val intuition; SQL-выгрузки → parquet; matplotlib — 2–3 графика.

**Практика:**

- [x] Выгрузка из Postgres (или CSV-прокси) → очистка → parquet
- [x] Отчёт: пропуски, распределения, простые метрики
- [x] Ручной cosine similarity на NumPy (векторы → похожесть)

**Deliverable:** ноутбук/скрипт `data-pipeline` + 1-страничный отчёт по датасету.

**Interview slice:** leakage, train/test split, «что такое baseline без ML».

---



## Неделя 3 — FastAPI + Docker + мост из Laravel (~18 ч)

**Темы:** FastAPI (роуты, Pydantic, upload), uvicorn, Docker multi-service; Laravel HTTP-клиент → Python; Redis как очередь/кэш (простой job).

**Практика:**

- [x] FastAPI: `POST /analyze` (upload CSV → агрегаты JSON) — `internal-assistant-project/ml-api`
- [x] Docker Compose: отдельные compose для `laravel` и `ml-api` (+ redis/postgres в laravel) на сети `internal-assistant-net`
- [x] Laravel controller вызывает FastAPI; Redis кэширует повторный запрос
- [x] Healthchecks, timeout, retry

**Deliverable:** [`internal-assistant-project`](./internal-assistant-project/) — Laravel gateway + ml-api.

**Interview slice:** sync API vs async worker; где держать секреты API-ключей; контракт версий API.

---



## Неделя 4 — Классический ML легко + `/predict` (~16 ч)

**Темы:** sklearn pipeline; train/val/test; Precision/Recall/F1/ROC-AUC; один бустинг или logistic; сериализация (`joblib`); overfitting на пальцах.

**Практика:**

- [x] Табличный датасет end-to-end (baseline → модель) — `internal-assistant-project/ml-api` + [`docs/ML.md`](./internal-assistant-project/ml-api/docs/ML.md)
- [x] FastAPI `POST /predict` + `GET /metrics`
- [x] Laravel вызывает `/predict` (Form Request + UI)

**Deliverable:** tabular ML в [`internal-assistant-project/ml-api`](./internal-assistant-project/ml-api/) (вместо отдельного `tabular-ml-api`).

**Interview slice:** выбор метрики под бизнес; failure modes; почему бустинг часто бьёт линейную модель на таблицах.

---



## Неделя 5 — Эмбеддинги и retrieval (по шагам, ~16 ч)

Код mini-retriever уже есть (`ml-api` + [`docs/RETRIEVAL.md`](./internal-assistant-project/ml-api/docs/RETRIEVAL.md)). Неделя разбита на **маленькие блоки**: один блок = одна идея. Не читать deep-lecture целиком; лекции — справка по запросу.

### 5A — Что такое embedding *(сейчас)*
- Одна идея: модель превращает текст в вектор чисел; похожий смысл → похожее направление.
- Практика: encode 2–3 фразы MiniLM, посмотреть `shape` (длина вектора), сравнить cosine «VPN reset» vs «пароль» vs «принтер».
- Не трогать: BM25, RAG, LLM, fine-tune.
- Готово, когда своими словами: «embedding ≠ класс тикета / ≠ predict_proba».

### 5B — Зачем offline index
- Одна идея: документы кодируем один раз; на вопрос кодируем только query.
- Мини-лекция + практика: [`docs/week5-5b-offline-index.md`](./internal-assistant-project/ml-api/docs/week5-5b-offline-index.md) · `scripts/practice_5b_offline_index.py`
- Готово, когда объясните аналогию с DB index (ускорение, не тот же механизм).

### 5C — Top-k и одна модель A/A
- Одна идея: сортировка по cosine, берём k лучших документов; query и docs — одна embedding-модель.
- Мини-лекция + практика: [`docs/week5-5c-topk-same-model.md`](./internal-assistant-project/ml-api/docs/week5-5c-topk-same-model.md) · `scripts/practice_5c_topk.py`
- Готово, когда: search возвращает **документ**, не класс.

### 5D — BM25 (keyword)
- Одна идея: ранжирование по словам (TF-IDF-семейство), без «смысла» модели.
- Мини-лекция + практика: [`docs/week5-5d-bm25.md`](./internal-assistant-project/ml-api/docs/week5-5d-bm25.md) · `scripts/practice_5d_bm25_vs_vector.py`
- Готово, когда видите кейс, где BM25 лучше (точный код/ID) и где vector лучше (перефраз).

### 5E — Hybrid + зачем retrieval до LLM
- Одна идея: keyword + vector дополняют друг друга; retrieval даёт факты LLM, чтобы меньше выдумывать.
- Мини-лекция + практика: [`docs/week5-5e-hybrid-rag.md`](./internal-assistant-project/ml-api/docs/week5-5e-hybrid-rag.md) · `scripts/practice_5e_hybrid.py`
- Заметка (deliverable): [`docs/hybrid-note.md`](./internal-assistant-project/ml-api/docs/hybrid-note.md)
- Interview later: chunk size, «зачем rerank» — после 5E, не раньше.

**Чеклист:**

- [x] Каркас: эмбеддинги → cosine top-k в `ml-api`
- [ ] 5A — intuition embedding (hands-on)
- [x] 5B — offline index
- [x] 5C — top-k + same model
- [x] 5D — BM25 vs vector
- [x] 5E — hybrid note + RAG vs fine-tune (кратко)

**Deliverable:** тот же mini-retriever + сравнение BM25 + короткая заметка hybrid.

---



## Неделя 6 — LLM API: промпты, структура, стоимость (~16 ч)

**Темы:** tokens, context window, temperature; structured output / JSON schema; tool calling intro; кэш промптов; оценка $/запрос; OpenAI-compatible API + опционально Ollama локально.

**Практика:**

- [ ] Сервис `POST /complete` с жёстким JSON-ответом
- [ ] 10 кейсов промпт-тестов (регрессия поведения)
- [ ] Таблица cost/latency: маленькая vs большая модель
- [ ] Laravel: форма → FastAPI → показ ответа (без RAG пока)

**Deliverable:** `llm-gateway` + cost notes + набор промпт-тестов.

**Interview slice:** temperature vs determinism; prompt as spec + tests; model routing.

---



## Неделя 7 — RAG v1: chunk → pgvector → ответ (~18 ч)

**Темы:** chunking стратегии; ingest pipeline; **pgvector**; citations; hybrid: Elasticsearch BM25 + vector merge (простой RRF или weighted).

**Практика:**

- [ ] Ingest корпуса (внутренние доки-заглушки / open docs)
- [ ] Index в Postgres+pgvector; опционально дубль keyword в ES
- [ ] `POST /ask` → retrieve → LLM → ответ + citations
- [ ] Laravel UI: чат за auth (или mock auth)

**Deliverable:** рабочий RAG MVP в Compose (Laravel + FastAPI + Postgres + Redis [+ ES]).

**Interview slice:** chunk overlap; metadata filters; hybrid retrieval tradeoffs.

---



## Неделя 8 — RAG v2: качество retrieval + Redis jobs (~17 ч)

**Темы:** hit-rate@k; query rewriting (лёгкий); Redis queue для ingest/reindex; идемпотентность ingest; кэш эмбеддингов запросов.

**Практика:**

- [ ] Golden set 20–30 вопросов с ожидаемыми doc-id
- [ ] Метрика retrieval hit-rate@5; починить chunking/top-k по результатам
- [ ] Async ingest через Redis (Laravel job или Python worker)
- [ ] Логи: query_id, latency, model, tokens

**Deliverable:** отчёт retrieval metrics + очередь ingest в README.

**Interview slice:** online vs offline eval intro; идемпотентный reindex; cache invalidation для эмбеддингов.

---



## Неделя 9 — Eval, faithfulness, продуктовые метрики (~16 ч)

**Темы:** faithfulness / answer relevance; LLM-as-judge осторожно; human review rubric; error taxonomy (hallucination, miss, refuse); Ragas или свой скрипт.

**Практика:**

- [ ] Расширить golden set до ≥30–50
- [ ] Eval suite: retrieval + answer scores → JSON/Markdown отчёт
- [ ] 10 «adversarial» вопросов (вне корпуса, jailbreak-лёгкий)
- [ ] Правило: «не знаю» + пустые citations лучше выдумки

**Deliverable:** `eval/` с прогоном одной командой + цифры в README.

**Interview slice:** почему без eval нет AI-продукта; риски LLM-as-judge; как презентовать метрики менеджеру.

---



## Неделя 10 — Cost, latency, безопасность, observability (~17 ч)

**Темы:** streaming; model routing; batching embeddings; rate limits; prompt injection / PII; OpenTelemetry или Langfuse-like трейсинг; Prometheus-метрики минимум.

**Практика:**

- [ ] Streaming ответа в API (+ Laravel consume если успеете)
- [ ] Бюджет: hard limit tokens/$ на пользователя/день
- [ ] Базовые guardrails: strip system leak, отказ при injection-паттернах
- [ ] Трейс цепочки: retrieve → generate; дашборд или хотя бы structured logs

**Deliverable:** design notes «latency/cost/security» (1–2 стр.) + включённый трейсинг.

**Interview slice:** system design: multi-tenant RAG, circuit breaker, fallback model, p95 vs cost.

---



## Неделя 11 — Агенты легко: tools + Laravel-домен (~16 ч)

**Темы:** tool-calling loop; human-in-the-loop; audit log; ограничения «автономных» агентов; tools: поиск по индексу, digests тикетов (mock), SQL read-only (осторожно).

**Практика:**

- [ ] Агент с 2–3 tools (search_docs, get_ticket_mock, link_policy)
- [ ] Laravel пишет audit: кто спросил, какие tools, ответ
- [ ] Guardrail: запрет tools без роли; max N шагов

**Deliverable:** demo «ticket/docs helper» с audit log + отказ при превышении лимита шагов.

**Interview slice:** agent vs RAG-only; когда tools обязательны; failure modes и контроль.

---



## Неделя 12 — Пилот: pitch, MVP-harden, портфолио (~18 ч)

**Темы:** упаковка пилота для работы; README как hiring artifact; архитектурная схема; позиционирование «backend → GenAI».

**Практика:**

- [ ] One-pager pitch + MVP plan (из блока выше) → адаптация под реалии команды
- [ ] Довести Compose до «clone → up → demo»
- [ ] Схема архитектуры (Laravel / FastAPI / pgvector / ES / Redis)
- [ ] Список рисков и mitigation для security/legal
- [ ] Черновик сообщения тимлиду / продукта

**Deliverable:** флагман-репо + one-pager pitch PDF/MD + готовое письмо-предложение.

**Interview slice:** behavioral STAR: «как предложил пилот / конфликт scope / tradeoff cost vs quality».

---



## Неделя 13 — Interview bootcamp + day-90 checkpoint (~16 ч)

**Темы:** system design AI 45 мин; RAG tradeoffs; eval; Python/SQL лёгкие; behavioral из пилота; резюме 3–5 bullet’ов с метриками.

**Практика:**

- [ ] 3 мок system design: (1) internal RAG, (2) support triage agent, (3) multi-tenant docs Q&A
- [ ] Шпаргалка: RAG vs fine-tune vs prompt+tools
- [ ] Обновить резюме/LinkedIn narrative под GenAI + Laravel strengths
- [ ] Прогнать полный eval suite; зафиксировать итоговые цифры
- [ ] Чеклист day 90 (ниже)

**Deliverable:** interview cheat-sheet (2–3 стр.) + резюме-черновик + записанный 5-мин walkthrough демо.

**Interview slice:** полный прогон рассказа о пилоте: проблема → архитектура → метрики → риски → next steps.

---



## Распределение нагрузки (ориентир)


| Недели | Фокус                                    | Часы  |
| ------ | ---------------------------------------- | ----- |
| 1–3    | Python, данные, FastAPI + Laravel bridge | 16–18 |
| 4–5    | ML легко + эмбеддинги                    | 16    |
| 6–11   | LLM → RAG → eval → cost → agents         | 16–18 |
| 12–13  | Пилот на работу + интервью               | 16–18 |


Итого: **~210–230 ч** за 90 дней при 15–18 ч/нед.

---



## Критерии успеха к дню 90

- [ ] Свободно пишете Python-сервисы (FastAPI) и стыкуете их с Laravel через HTTP/очереди Redis
- [ ] Есть табличный ML-сервис `/predict` (даже простой) — понимаете метрики и baseline
- [ ] Флагман: RAG/assistant с citations, Docker Compose, pgvector (± Elasticsearch hybrid), Redis ingest/cache
- [ ] Golden set ≥ 30 и повторно прогоняемый eval (цифры в README)
- [ ] Заметки по cost/latency/security; базовый трейсинг или structured logs
- [ ] One-pager пилота + черновик предложения на работу (Docs/Ticket Assistant)
- [ ] Можете 30–45 мин провести system design AI-фичи и объяснить RAG tradeoffs / eval / failure modes
- [ ] Резюме и устный нарратив: «backend engineer, доводящий GenAI до продакшена», а не «учу ML с нуля»
- [ ] Минимум один behavioral рассказ из пилота (STAR) с метриками или явными tradeoffs

**После дня 90:** углублять eval/агентов/MLOps по фазам 4–5 дорожной карты; запускать или итерировать внутренний пилот; первые отклики на AI/GenAI роли.