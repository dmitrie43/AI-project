# Лекция: Dense Retrieval, Embeddings и RAG (по открытым источникам)

**Аудитория:** GenAI Engineer path, после cosine/top-k (math A) и шага 1 mini-retriever.  
**Стиль:** учебная лекция с опорой на статьи/доки; в конце — как это ложится на `ml-api`.  
**Не цель:** пересказать все papers целиком — дать рабочую картину мира.

---

## 1. Постановка задачи: зачем retrieval

Большие языковые модели хранят знания **в параметрах** (parametric memory). На knowledge-intensive задачах этого мало: факты устаревают, нет provenance («откуда взяли»), сложно обновить знания без дорогого переобучения.

Классическая идея **Retrieval-Augmented Generation (RAG)** (Lewis et al., 2020, Meta AI / FAIR):

> Соединить **генератор** (seq2seq / LLM) с **внешней памятью** — индексом документов, из которого достают релевантные фрагменты и подмешивают в генерацию.

В оригинальной работе:

- non-parametric memory = dense-индекс Wikipedia;
- retriever = DPR (dense passage retriever);
- generator = BART;
- статьи Wikipedia резали на куски ~**100 слов**, получили ~21M passages;
- для быстрого поиска по миллионам векторов — FAISS / HNSW (приближённый nearest neighbor).

Источник: [Lewis et al., RAG (arXiv:2005.11401)](https://arxiv.org/abs/2005.11401), обзор Meta: [RAG blog](https://ai.meta.com/blog/retrieval-augmented-generation-streamlining-the-creation-of-intelligent-natural-language-processing-models/).

**Для вашего пилота:** пока делаем только **retriever** (найти чанки). Generator (LLM) — недели 6–7.

---

## 2. Два семейства поиска

### 2.1. Lexical / sparse (BM25 и родственники)

Ищут по **совпадению терминов**. BM25 — стандартный ranking-функция в классическом IR (Elasticsearch, Lucene).

Сильна на:

- кодах ошибок, SKU, именах API;
- точных цитатах и редких токенах.

Слаба, когда формулировка вопроса **не совпадает** со словами в документе  
(«не коннектится удалёнка» vs текст про «VPN tunnel timeout»).

### 2.2. Dense / semantic (эмбеддинги)

Идея **dense retrieval**: и query, и документы кодируются в **плотные векторы**; релевантность ≈ близость в пространстве (часто cosine или inner product).

Hugging Face LLM Course формулирует так: token embeddings модели можно «сжать» (pooling) в вектор предложения/абзаца и искать документы с наибольшим overlap / similarity — в отличие от чистого keyword matching.

Источник: [HF Course — Semantic search with FAISS](https://huggingface.co/learn/llm-course/chapter5/6).

Сильна на paraphrases и «смысловых» вопросах.  
Слаба на редких идентификаторах (эмбеддинг «сглаживает» уникальный код).

Практический вывод индустрии (Pinecone, Qdrant, обзоры hybrid RAG): **методы комплементарны** — hybrid часто лучше любого одного.

Источники: [Pinecone Hybrid search](https://docs.pinecone.io/guides/search/hybrid-search), [Qdrant Hybrid Search](https://qdrant.tech/documentation/search-tuning/hybrid-search/).

---

## 3. Эмбеддинги предложений: Sentence Transformers

**Sentence Transformers** (SBERT-экосистема) — стандартный способ получить embedding целого предложения/абзаца для semantic search.

Типичный пайплайн из их documentation / examples:

1. Загрузить модель, напр. `sentence-transformers/all-MiniLM-L6-v2`
2. `encode` корпус документов **один раз**
3. `encode` query
4. Cosine similarity → top-k

Документация прямо рекомендует `util.semantic_search` (cosine по умолчанию) для корпусов примерно до **~1M** записей при точном (не ANN) поиске; дальше обычно берут FAISS/HNSW.

Источник: [Sentence Transformers — Semantic Search](https://sbert.net/examples/sentence_transformer/applications/semantic-search/).

### Нормализация

Если векторы L2-нормализованы (`normalize_embeddings=True`), **dot product = cosine**. Так быстрее и проще в коде — у вас в `app/retrieval` именно так.

### Asymmetric search (query vs document)

Для сценария «короткий вопрос → длинный ответ» некоторые модели используют разные prompt’ы: `encode_query` / `encode_document`.  
Для `all-MiniLM-L6-v2` на практике часто ведут себя как обычный `encode` — это отмечают гайды по semantic search.

Источник: [Semantic Search Guide — Sentence Transformers](https://semanticsearchguide.com/build/semantic-search-with-python/).

---

## 4. Cosine similarity — роль в IR

Cosine измеряет **угол** между векторами, а не «абсолютную длину».  
Тексты разной длины с близким направлением смысла получают высокий score.

Интуиция dense retrieval tutorials:

```
query → embedding
corpus → embeddings (заранее)
score = cosine(query, doc_i)
top-k по score
```

Важно: высокий cosine ≠ «факт верный». Это только **кандидат на релевантность**. Дальше — LLM, правила, rerank, человек.

---

## 5. Индекс: зачем offline encode

Считать embeddings всех документов на **каждый** запрос дорого (особенно на CPU/GPU).

Стандарт:

| Фаза | Что кодируем |
|------|----------------|
| Build / ingest | все чанки корпуса → сохранить матрицу / vector DB |
| Query | только вопрос → сравнить с индексом |

При миллионах векторов полный перебор (`O(n)`) меняют на **ANN** (Approximate Nearest Neighbors): FAISS, HNSW в pgvector и т.д.  
В RAG-paper как раз FAISS+HNSW на 21M passages.

У вас корпус ~27 доков → полный cosine ок; архитектура уже «как в проде», только без ANN.

---

## 6. Chunking (нарезка документов)

Lewis et al. резали Wikipedia на **непересекающиеся ~100-word chunks**.

Практика RAG сегодня (обобщение гайдов):

- слишком большой чанк → в топ попадает «про тему», но нужный абзац тонет;
- слишком мелкий → теряется контекст;
- overlap между чанками иногда помогает на границах.

У вас на шаге 1: **один `.md` = один chunk** — нормально для коротких runbook’ов.  
Для PDF/Confluence позже появится явный chunker.

---

## 7. Hybrid search и fusion (задел шага 2+)

Dense и BM25 ошибаются **по-разному**:

| Тип запроса | Часто лучше |
|-------------|-------------|
| «SKU AZ-4471», «ERR_4021» | BM25 |
| «как вернуть сломанный товар» (другие слова) | Dense |
| обычный FAQ с совпадением терминов | оба |

**Hybrid:** запустить оба → получить два ranked list → **слить**.

Нельзя слепо усреднять raw BM25 и cosine: шкалы несовместимы (BM25 unbounded, cosine примерно [-1, 1]).

Стандартный приём — **Reciprocal Rank Fusion (RRF)** (Cormack et al., 2009): учитывать **ранг** в каждом списке, а не «сырой» score.

Источники: [Pinecone Hybrid](https://docs.pinecone.io/guides/search/hybrid-search), [Qdrant Hybrid / RRF](https://qdrant.tech/documentation/search-tuning/hybrid-search/).

Опционально после fusion — **cross-encoder rerank** (смотрит пару query+doc целиком, дороже, но точнее). Имеет смысл, только если бьёт baseline на ваших labeled queries ([Qdrant: When is a reranker worth it?](https://qdrant.tech/documentation/search-tuning/when-a-reranker-is-worth-it/)).

---

## 8. Оценка retrieval (связка с math B)

В литературе/доках часто:

- **Recall@k / Hit-rate@k** — эталон попал в top-k?
- **nDCG@k**, **MRR** — учитывают позицию (выше = лучше)

Для пилота Internal Assistant достаточно начать с **Hit-rate@k** на golden-вопросах (как в фазе B / B4).

Правило Qdrant: мерять dense / sparse / hybrid на **одних и тех же** labeled queries, не гадать.

---

## 9. Bi-encoder vs cross-encoder (на пальцах)

| | Bi-encoder (у вас) | Cross-encoder |
|--|--------------------|---------------|
| Как | query и doc кодируются **отдельно** → векторы сравниваются | модель видит **пару** (query, doc) сразу |
| Скорость | быстрый search по индексу | медленнее, обычно только top-N кандидатов |
| Роль | first-stage retrieval | rerank |

Sentence Transformers = классический bi-encoder стек для first stage.

---

## 10. Карта на ваш код `ml-api`


| Понятие из источников | Где у вас |
|----------------------|-----------|
| Corpus / passages | `data/corpus/*.md` |
| Sentence Transformer encode | `app/retrieval/index.py`, `search.py` |
| Offline index | `artifacts/retrieval/embeddings.npy` + `meta.json` |
| Cosine + top-k | `app/retrieval/search.py` (`_cosine_matrix`, `argsort`) |
| Normalize → dot = cosine | `normalize_embeddings=True` при build/search |
| RAG generator | ещё нет (н.6–7) |
| BM25 / hybrid / RRF | шаг 2 недели 5 |
| FAISS / pgvector HNSW | позже, при росте корпуса |


Операционка: [`RETRIEVAL.md`](RETRIEVAL.md).  
Короткая лекция терминов: [`retrieval-lecture.md`](retrieval-lecture.md).

---

## 11. Чеклист «понял тему»

1. Зачем RAG разделяет parametric и non-parametric memory?  
2. Почему dense и BM25 дополняют друг друга?  
3. Почему не смешивают сырые BM25-score и cosine без fusion?  
4. Зачем encode корпуса offline?  
5. Чем bi-encoder отличается от cross-encoder?  
6. Как Hit-rate@k связан с выбором k в RAG?

---

## 12. Источники (для чтения дальше)

1. Lewis et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. https://arxiv.org/abs/2005.11401  
2. Meta AI blog on RAG. https://ai.meta.com/blog/retrieval-augmented-generation-streamlining-the-creation-of-intelligent-natural-language-processing-models/  
3. Sentence Transformers — Semantic Search. https://sbert.net/examples/sentence_transformer/applications/semantic-search/  
4. Hugging Face LLM Course — Semantic search with FAISS. https://huggingface.co/learn/llm-course/chapter5/6  
5. Pinecone — Hybrid search overview. https://docs.pinecone.io/guides/search/hybrid-search  
6. Qdrant — Hybrid search & fusion. https://qdrant.tech/documentation/search-tuning/hybrid-search/  
7. Semantic Search Guide — ST in Python. https://semanticsearchguide.com/build/semantic-search-with-python/  
8. Stanford SLP draft — IR and RAG (Jurafsky et al.). https://web.stanford.edu/~jurafsky/slp3/11  

---

## 13. Практическое задание после лекции

На своих 3–5 запросах к `cli_search`:

1. Запишите top-3 id и score.  
2. Отметьте: нашёлся ли «ожидаемый» runbook (как golden в фазе B).  
3. Придумайте 1 запрос, где keyword был бы лучше (например точный код/`CorpWiFi`) — это аргумент для BM25 на шаге 2.
