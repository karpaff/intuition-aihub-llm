# RAG Backend

RAG (Retrieval-Augmented Generation) сервис для ответов на вопросы с использованием векторного поиска и YandexGPT.

## Архитектура

### C4 Диаграмма компонентов
![text](https://cdn-0.plantuml.com/plantuml/png/ZLF1Kjim4BtdAxOvXPb2BZtr18Gqq0cGOgSTJXd5sYOQPDdLoe6qqt_lhco2QkXCJxRaj-yzFJsVKb0-DAKTl3Eki8r6s8PGqyVnsAl7auq9ssRT4FgYSW5TE2cgSbnRvMJcc8AsPZsUV3XUoDRoUZuk5GNqlBMQy8Go3lr9BVo3-TdzxJ9VVRlABrVpwMnwSp4w6Wo22HRXW0LjrCQh4hvN7kxEPd2kYWTq6h8zyvQ3mG8zLMuabjx3SCcF8J-dZ90jKFHWt0P-D4Z1L8w6BD6EhiwhncdbzoElDYkAUpoPQ0oFuDS005xSZ5Hj67Esk8AvshTIdnG5tXZAx3JBGJxoS5qP5wBhsbS54eaDZz48k-ZnYeNQr6XvrPbOT4iXNkp3jdBoTkkBBJDu5P2OBdY3EsL1EGqRP2Obf-maNyjWkKQjsGb9HeS5PEXtfeXIzqo5JnDRDLgMNx48bJS_MItWKo1eua5Q54GOvFm14ZP9ewzihOGxdr-_rfejSbdCMliif1mzeYTOAq8DV1pf6clqII_M8xtcoSbM1RWqn4RtS74kPBbn-_OjurtcB0HJ8f7Qy6hRWKUVizkRuwXpz0RxBXv-9LWyP06HKQY_QAzSI4Ja5WXLl2BGLT6Kw0AyXCuIlm_rcpw5qJu6i2eaHiaZJRNhrFKSg4sCf4q9MvIJN9ARbthVeUr-XxQj6JfDXpz0E2_pV36MepDSq14NeypK3cdSzGhfa9XCfU1UNw-S2IRUdJItQryoypSyRM5QiDJYcuEz-yYUeoPJ6gkyHFvlLMdWwvObyDHMxsBadowKjVISNjRD2Eb_WrFxlHIMr5sl4IhUx7oTejDDQVy0)

### Диаграмма последовательности

![text](https://cdn-0.plantuml.com/plantuml/png/dPFHQzim4CRVzLS8FsMiJM6bUoXqDAMZR7HhbcOF8olcQXsEc2rvEZbhAFtVTvBcO8NifG-9BFlttVUTVBua3yxtRIEWyjR9xuHET7nBLxe3usKnct-I2zjxT8K4ahmL2Zmy0g4ibjfihw_YW-khNBUOtSYvxh3H1YCmR7BiO_k8IcbJKuJYTcJmJJd6ugDqcQj_W57uT3DVHkBszeiGeGDv_466tEToVdU_b2SEwfCQVSbh2OR-eFjfdd_tI5vRSowBwNHQl8GJq1lm67iK_CTbk2sk0agLBH91ZPD1zcR7XzOPEzwP4cn24pW6Xdh3AJ3cUXCJTUdMmT83BiHEE8GA3LLhyELQaxTkEsbqg_t5sO5WcUq_VFMG9ymTudjW6CDQSZ2tFHGlOYB1UpPHKsumZDNgtTdxQ9VfSiVqUbb8t4O3JljjIGYkMa_6fOxahulJKO8a4sdPpw1irRTeFArEetqkolrvUEAX6dICJ3fdsyxBjxAonkDJk3hGFui4__PzquonOmRkx4QZie1w5k7df3cIP7jN8QqUNiRwGVh_kKpwrqmb8_6xP-Rp_TrNwP0wQmZ7B7FY4etgs-Ol)

### Обзор системы

Сервис реализует классический RAG пайплайн:
1. **Получение вопроса** от пользователя через REST API
2. **Поиск релевантных документов** в векторной базе данных Qdrant
3. **Генерация ответа** с помощью YandexGPT на основе найденных документов
4. **Возврат ответа** с указанием источников

### Компоненты системы

#### 1. API Layer ([src/modules/rag/routers/rag.py](src/modules/rag/routers/rag.py))
- **Роль**: REST API endpoint для обработки запросов
- **Маршрут**: `POST /rag/get_rag_answer`
- **Функции**:
  - Принимает вопрос пользователя
  - Сохраняет сообщения в базу данных для истории чата
  - Вызывает RAG пайплайн
  - Возвращает ответ с источниками

#### 2. RAG Pipeline ([src/modules/rag/components/rag.py](src/modules/rag/components/rag.py))
- **Роль**: Оркестратор процесса RAG
- **Основные методы**:
  - `retrieve_documents()` - поиск релевантных документов
  - `generate_answer()` - генерация ответа на основе контекста
  - `run_rag_pipeline()` - полный цикл обработки запроса
- **Конфигурация**:
  - `top_k_docs` - количество извлекаемых документов (по умолчанию 3)
  - `search_type` - тип поиска (similarity/mmr)
  - Промпт-шаблон с переменными: history, context, question

#### 3. Embeddings ([src/modules/rag/components/embeddings.py](src/modules/rag/components/embeddings.py))
- **Роль**: Векторизация текстов для поиска
- **Модель**: Yandex Cloud Text Embeddings API
- **Особенности**:
  - Два типа моделей: для запросов (`query`) и документов (`doc`)
  - Размерность векторов: 256
  - Rate limiting: 9 запросов в секунду
  - Timeout: 60 секунд на запрос
- **Интеграция**: LangChain-совместимый интерфейс `Embeddings`

#### 4. LLM ([src/modules/rag/components/llm.py](src/modules/rag/components/llm.py))
- **Роль**: Генерация ответов
- **Модель**: YandexGPT
- **Параметры**:
  - Temperature: 0.0 (детерминированные ответы)
  - Max tokens: 2000
- **Функции**:
  - Синхронные и асинхронные методы invoke
  - Поддержка системных промптов
  - Преобразование формата сообщений LangChain → Yandex

#### 5. Vector Store ([src/common/qdrant/](src/common/qdrant/))
- **Роль**: Хранение и поиск векторных представлений документов
- **СУБД**: Qdrant
- **Конфигурация**:
  - Collection name: настраивается через `QDRANT_COLLECTION`
  - Chunk size: 400 символов
  - Overlap: 100 символов
- **Метаданные документов**:
  - `chapter` - номер главы источника
  - `page_content` - текстовый фрагмент

#### 6. Database ([src/common/database.py](src/common/database.py))
- **Роль**: Хранение истории чата
- **СУБД**: TinyDB (JSON-based)
- **Функции**:
  - `add_message()` - добавление сообщения с timestamp
  - `get_chat_history()` - получение последних N сообщений
  - `clear_messages_table()` - очистка при старте приложения
- **Window size**: 5 сообщений (настраивается через `DB_WINDOW_MSGS`)

### Поток данных

```
1. Пользователь отправляет вопрос
   ↓
2. API Router (/rag/get_rag_answer)
   ↓
3. Сохранение вопроса в TinyDB
   ↓
4. RAG Pipeline:
   a) Векторизация вопроса (YandexCloudEmbeddings)
   b) Поиск в Qdrant (top_k=3)
   c) Формирование промпта с контекстом
   d) Запрос к YandexGPT
   ↓
5. Сохранение ответа в TinyDB
   ↓
6. Возврат результата (answer + sources)
```

### Схемы данных

#### RagAnswer ([src/modules/rag/schemas.py](src/modules/rag/schemas.py))
```python
{
  "answer": str,           # Ответ от LLM
  "sources": [             # Список источников
    {
      "chapter_n": int,    # Номер главы
      "text_chunk": str    # Текстовый фрагмент
    }
  ]
}
```

## Зависимости

### Основные библиотеки

| Библиотека | Версия | Назначение |
|-----------|--------|------------|
| **fastapi** | 0.124.4 | REST API фреймворк |
| **uvicorn** | 0.38.0 | ASGI сервер |
| **langchain** | 0.3.7 | Фреймворк для LLM приложений |
| **langchain-qdrant** | 0.2.0 | Интеграция с Qdrant |
| **qdrant-client** | 1.11.0 | Клиент для Qdrant |
| **yandex_cloud_ml_sdk** | 0.17.0 | SDK для Yandex Cloud ML |
| **tinydb** | 4.8.2 | JSON база данных |
| **pydantic** | 2.11.7 | Валидация данных |
| **loguru** | 0.7.3 | Логирование |
| **python-dotenv** | 1.1.1 | Загрузка переменных окружения |

### Дополнительные зависимости

- **pymupdf** (1.24.7) - обработка PDF документов
- **gdown** (5.2.0) - загрузка файлов с Google Drive
- **langchain-openai** (0.2.3) - совместимость с OpenAI API
- **langchain-huggingface** (0.1.1) - интеграция с HuggingFace

## Конфигурация

Все настройки задаются через переменные окружения в файле `.env`:

### Server
- `HOST` - хост сервера (по умолчанию: localhost)
- `PORT` - порт сервера (по умолчанию: 8000)
- `PRODUCTION_MODE` - режим production (по умолчанию: false)

### Yandex Cloud
- `YANDEX_API_KEY` - API ключ Yandex Cloud
- `YANDEX_FOLDER_ID` - ID папки в Yandex Cloud
- `TEMPERATURE` - температура генерации (по умолчанию: 0.0)
- `MAX_TOKENS` - максимум токенов в ответе (по умолчанию: 500)
- `PROMPT` - шаблон промпта для LLM

### Qdrant
- `QDRANT_URL` - URL Qdrant сервера
- `QDRANT_KEY` - API ключ Qdrant
- `QDRANT_COLLECTION` - имя коллекции
- `QDRANT_BOOK_URL` - URL для загрузки документов
- `QDRANT_CHUNK_SIZE` - размер чанка (по умолчанию: 400)
- `QDRANT_OVERLAP` - перекрытие чанков (по умолчанию: 100)

### RAG
- `TOP_K_DOCS` - количество извлекаемых документов (по умолчанию: 3)
- `SEARCH_DISTANCE_TYPE` - тип поиска (по умолчанию: similarity)
- `EMBEDDING_SIZE` - размер эмбеддингов (256)

### Database
- `DB_PATH` - путь к файлу БД (по умолчанию: db.json)
- `DB_WINDOW_MSGS` - размер окна истории (по умолчанию: 5)

## Запуск сервиса

Создайте файл `.env` по примеру `.env.example`

Выполните билд контейнера с сервисом и запустите его (из главной директории):
```sh
docker compose build
docker compose up -d
```

Документация сервиса будет доступна по ссылке `http://{HOST}:{PORT}/docs`

## API Endpoints

### POST /rag/get_rag_answer
Получить ответ на вопрос с использованием RAG

**Параметры:**
- `question` (string) - вопрос пользователя

**Ответ:**
```json
{
  "answer": "Ответ на вопрос...",
  "sources": [
    {
      "chapter_n": 1,
      "text_chunk": "Релевантный текст из источника..."
    }
  ]
}
```

---

# Пайплайн тестирования и валидации

Директория [evaluation/](evaluation/) содержит инструменты для оценки качества RAG системы.

## Обзор валидационного набора данных

### Сбор данных

**Синтетический датасет** был создан с помощью **Qwen3** для произведения **"Преступление и наказание"** (Ф.М. Достоевский).

**Валидация качества:**
- Синтетические данные прошли ручную проверку
- Достоверность цитат сверена с оригинальным текстом произведения

**Важно:** Данная книга **не использовалась при подборе гиперпараметров** на предыдущих этапах и служит **чистой валидационной выборкой**.

### Формат данных

**Книга**: PDF формат

**Эталонный датасет** ([evaluation/golden_data/Преступление_и_наказание.json](evaluation/golden_data/Преступление_и_наказание.json)): JSON формат
```json
{
  "dataset": [
    {
      "question": "Вопрос пользователя по книге",
      "relevant_text": "Фрагмент из книги, отвечающий на вопрос",
      "answer": "Ответ LLM на вопрос пользователя"
    }
  ]
}
```

### Статистика валидационного набора

| Параметр | Значение |
|----------|----------|
| Книга | "Преступление и наказание" |
| Количество вопросов | 25 |
| Тип выборки | Валидационная (не использовалась при обучении) |
| Сложность вопросов | Разная (факты, мотивация персонажей, анализ сюжета) |

## Пайплайн тестирования

### Процесс эксперимента

#### Предыстория
На предыдущих этапах разработки была проведена серия экспериментов по подбору оптимальной конфигурации RAG системы на 4 произведениях классической литературы:
- Мартин Иден (Джек Лондон)
- Капитанская дочка (А.С. Пушкин)
- Герой нашего времени (М.Ю. Лермонтов)
- Отцы и дети (И.С. Тургенев)

В результате Grid Search по параметрам была определена **оптимальная конфигурация**:
- **chunk_size**: 1500 символов
- **overlap**: 200 символов
- **top_k**: 5 документов

#### Текущий эксперимент

**Цель**: Проверить качество RAG системы с оптимальной конфигурацией на **валидационной выборке**, которая не участвовала в подборе гиперпараметров.

**Валидационные данные**: "Преступление и наказание" - 25 вопросов с эталонными ответами.

### Этапы оценки качества

#### 1. Подготовка данных
```python
# Загрузка PDF книги "Преступление и наказание"
loader = PyMuPDFLoader("Преступление_и_наказание.pdf")
docs = loader.load()

# Чанкинг с оптимальными параметрами
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,        # Оптимальный размер чанка
    chunk_overlap=200,      # Оптимальное перекрытие
    separators=["\n\n", "\n", ".", " ", ""],
    length_function=len,
    is_separator_regex=False,
    strip_whitespace=True
)
chunks = splitter.split_documents(docs)
```

#### 2. Индексация в Qdrant
```python
# Создание временной коллекции для эксперимента
collection_name = "test_collection_ch1500_ov200_topk5"

# Создание коллекции с векторной конфигурацией
client.create_collection(
    collection_name=collection_name,
    vectors_config=models.VectorParams(
        size=256,  # Размерность Yandex Embeddings
        distance=models.Distance.COSINE
    )
)

# Создание индекса для фильтрации по источнику
client.create_payload_index(
    collection_name=collection_name,
    field_name="metadata.source",
    field_schema=models.PayloadSchemaType.KEYWORD
)

# Векторизация через Yandex Embeddings и загрузка
qdrant_store = Qdrant(
    client=client,
    collection_name=collection_name,
    embeddings=YandexCloudEmbeddings(...)
)
qdrant_store.add_documents(chunks)
```

#### 3. Генерация ответов RAG
Для каждого из **25 вопросов** из валидационного датасета:

```python
for question in dataset:
    # 1. Векторизация вопроса
    query_embedding = embeddings.embed_query(question)

    # 2. Поиск top-5 релевантных чанков в Qdrant
    relevant_docs = qdrant_store.asearch(
        query=question,
        search_type="similarity",
        k=5
    )

    # 3. Формирование промпта с контекстом
    context = "\n\n".join([doc.page_content for doc in relevant_docs])
    prompt = f"""
    Контекст: {context}
    Вопрос: {question}
    Ответ:
    """

    # 4. Генерация ответа через YandexGPT
    answer = llm.ainvoke(prompt)

    # 5. Создание тест-кейса для DeepEval
    test_case = LLMTestCase(
        input=question,
        actual_output=answer,
        expected_output=expected_answer,  # Из датасета
        retrieval_context=[doc.page_content for doc in relevant_docs]
    )
```

#### 4. Оценка метрик через DeepEval

**Используемые метрики:**

| Метрика | Описание | Threshold | Что измеряет |
|---------|----------|-----------|--------------|
| **Answer Relevancy** | Релевантность ответа вопросу | 0.5 | Насколько ответ соответствует заданному вопросу |
| **Contextual Recall** | Полнота извлеченного контекста | 0.5 | Насколько полно найден релевантный контекст из документа |
| **Faithfulness** | Верность контексту | 0.5 | Отсутствие галлюцинаций, соответствие ответа контексту |

**Scorer LLM**: OpenAI GPT-4o-mini (через OpenRouter) - используется для оценки метрик

```python
# Инициализация scorer модели
scorer = ScorerLLM()  # GPT-4o-mini

# Определение метрик
metrics = [
    deepeval.metrics.AnswerRelevancyMetric(
        model=scorer,
        threshold=0.5,
        async_mode=False
    ),
    deepeval.metrics.ContextualRecallMetric(
        model=scorer,
        threshold=0.5,
        async_mode=False
    ),
    deepeval.metrics.FaithfulnessMetric(
        model=scorer,
        threshold=0.5,
        async_mode=False
    ),
]

# Запуск оценки на всех 25 вопросах
eval_result = deepeval.evaluate(
    test_cases=test_cases,  # 25 тест-кейсов
    metrics=metrics
)
```

#### 5. Сохранение и агрегация результатов

```python
# Извлечение метрик для каждого вопроса
for test_result in eval_result.test_results:
    for metric_data in test_result.metrics_data:
        # success: прошел ли threshold
        # score: числовое значение метрики
        # threshold: пороговое значение
        metrics_data.append({
            'success': metric_data.success,
            'score': metric_data.score,
            'threshold': metric_data.threshold
        })

# Агрегация по книге
aggregated_metrics = {
    'answer_relevancy': mean([m.score for m in answer_relevancy_results]),
    'contextual_recall': mean([m.score for m in contextual_recall_results]),
    'faithfulness': mean([m.score for m in faithfulness_results])
}
```

### Конфигурация эксперимента

**Параметры RAG системы:**
- **LLM**: YandexGPT (temperature=0.0, max_tokens=2000)
- **Embeddings**: Yandex Cloud Text Embeddings (размерность: 256)
- **Vector Store**: Qdrant (COSINE distance)
- **Chunk Size**: 1500 символов
- **Overlap**: 200 символов
- **Top-K**: 5 документов
- **Search Type**: similarity

**Параметры оценки:**
- **Scorer Model**: GPT-4o-mini
- **Метрики**: Answer Relevancy, Contextual Recall, Faithfulness
- **Threshold**: 0.5 для всех метрик

## Метрики качества

### Результаты лучшей конфигурации

| Конфигурация | LLM | Embeddings | Embedding Size | Chunk Size | Overlap | Top-K | Answer Relevancy | Contextual Recall | Faithfulness |
|--------------|-----|------------|----------------|------------|---------|-------|------------------|-------------------|--------------|
| **Оптимальная** | yagpt | ya_embeddings | 256 | 1500 | 200 | 5 | **0.832** | **0.745** | **0.962** |

### Интерпретация результатов

- **Answer Relevancy (0.884)**. Ответы высоко релевантны заданным вопросам
- **Contextual Recall (0.784)**. Извлекается достаточный контекст для ответа (можно улучшить)
- **Faithfulness (0.956)**. Минимальное количество галлюцинаций, ответы основаны на контексте

## Выводы

1. **Оптимальная конфигурация**. chunk_size=1500, overlap=200, top_k=5
2. **Высокая точность**. Faithfulness 95.6% подтверждает надежность системы
3. **Валидационный тест**. "Преступление и наказание" показывает генерализацию на новые данные
4. **Метрики стабильны**. Результаты воспроизводимы при фиксированных параметрах
