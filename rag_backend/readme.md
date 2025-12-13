# rag_backend

## Запуск сервиса

Создайте файл `.env` по примеру `.env.example.`

Выполните билд контейнера с сервисом и запустите его
```sh
docker compose build
docker compose up -d
```

Документация сервиса будет доступна по ссылке `http://{HOST}:{PORT}⁠/docs`