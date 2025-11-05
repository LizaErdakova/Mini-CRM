# Mini-CRM для онлайн-курсов

Бэкенд-сервис для управления пользователями и курсами, разработанный на FastAPI.

## Технологии

- **FastAPI** - современный и быстрый веб-фреймворк
- **SQLAlchemy** - ORM для работы с базой данных
- **Pydantic** - валидация данных и сериализация
- **SQLite** - легкая база данных (можно заменить на MySQL/PostgreSQL)
- **Cookie-сессии** - для аутентификации пользователей
- **Apache Kafka** - брокер сообщений для event-driven архитектуры

## Установка и запуск

### Предварительные требования

- **Python 3.8+**
- **Docker Desktop** (для Kafka и Zookeeper)
  - [Скачать Docker Desktop для Windows](https://www.docker.com/products/docker-desktop)
  - Требуется WSL 2 (устанавливается автоматически с Docker Desktop)

### Пошаговая инструкция

#### 1. Клонировать репозиторий
```bash
git clone https://github.com/ваш-аккаунт/mini-crm.git
cd mini-crm
```

#### 2. Создать виртуальное окружение
```bash
# Windows
python -m venv .venv
.venv\Scripts\Activate.ps1

# Linux/Mac
python -m venv .venv
source .venv/bin/activate
```

#### 3. Установить зависимости
```bash
pip install -r requirements.txt
```

#### 4. Настроить переменные окружения (опционально)

Создайте файл `.env` в корне проекта (если нужны кастомные настройки):
```env
DB_URL=sqlite:///./test.db
SECRET_KEY=your-secret-key
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

> **Примечание:** Файл `.env` уже в `.gitignore` и не будет загружен в репозиторий.

#### 5. Запустить Docker-сервисы (Kafka, Zookeeper, Kafka UI)

```bash
docker compose up -d
```

Это запустит:
- **Zookeeper** (порт 2181) - координатор для Kafka
- **Kafka** (порт 9092) - брокер сообщений
- **Kafka UI** (порт 8080) - веб-интерфейс для просмотра топиков и событий

Проверить статус:
```bash
docker compose ps
```

#### 6. Запустить FastAPI сервер

```bash
uvicorn app.main:app --reload
```

#### 7. Открыть в браузере

- **API документация (Swagger UI)**: http://127.0.0.1:8000/docs
- **Kafka UI** (просмотр топиков и событий): http://localhost:8080
- **Health-check**: http://127.0.0.1:8000/ping

### Тестирование

#### 1. Создать администратора
```bash
POST http://127.0.0.1:8000/users
Content-Type: application/json

{
  "email": "admin@example.com",
  "name": "Администратор",
  "age": 25,
  "password": "admin123",
  "is_admin": true
}
```

#### 2. Войти в систему
```bash
POST http://127.0.0.1:8000/auth/login
Content-Type: application/json

{
  "email": "admin@example.com",
  "password": "admin123"
}
```

#### 3. Создать курс (требуется авторизация)
```bash
POST http://127.0.0.1:8000/courses
Content-Type: application/json
Cookie: session_token=ваш_токен

{
  "title": "Python для начинающих",
  "description": "Изучите Python с нуля",
  "price": 5000.00
}
```

#### 4. Проверить события в Kafka UI

1. Откройте http://localhost:8080
2. В левом меню выберите **Topics**
3. Кликните на топик `user-events` или `course-events`
4. Перейдите на вкладку **Messages** - вы увидите все события

### Остановка

Остановить FastAPI:
- Нажмите `Ctrl+C` в терминале, где запущен uvicorn

Остановить Docker-сервисы:
```bash
docker compose down
```

Остановить и удалить данные:
```bash
docker compose down -v
```

> **Примечание:** Если Docker не установлен, приложение будет работать, но события не будут обрабатываться через Kafka. База данных SQLite будет работать нормально.

## API Эндпоинты

### Пользователи
- `POST /users` - создание пользователя
- `GET /users/{id}` - получение пользователя по ID
- `GET /users` - список всех пользователей

### Авторизация
- `POST /login` - вход в систему
- `GET /me` - информация о текущем пользователе
- `POST /logout` - выход из системы

### Курсы
- `POST /courses` - создание курса (только админ)
- `GET /courses/{id}` - получение курса по ID
- `GET /courses` - список всех курсов

## Структура проекта

```
app/
├── main.py              # Точка входа FastAPI + запуск Kafka consumers
├── core/                # Ядро приложения
│   ├── config.py        # Настройки из .env (включая Kafka)
│   ├── database.py      # Подключение к БД
│   ├── kafka_producer.py # Producer для отправки событий в Kafka
│   └── kafka_consumer.py # Consumer для обработки событий из Kafka
├── models/              # SQLAlchemy модели
│   ├── user.py          # Модель пользователя
│   └── course.py        # Модель курса
├── schemas/             # Pydantic схемы
│   ├── user.py          # Схемы пользователя
│   ├── course.py        # Схемы курса
│   └── events.py        # Схемы событий для Kafka
├── routers/             # API маршруты
│   ├── users.py         # Эндпоинты пользователей (+ отправка событий)
│   ├── auth.py          # Эндпоинты авторизации (+ отправка событий)
│   └── courses.py       # Эндпоинты курсов (+ отправка событий)
├── auth.py              # Функции авторизации
└── dependencies.py      # Общие зависимости
```

## Примеры запросов

### Создание пользователя
```bash
curl -X POST "http://127.0.0.1:8000/users" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "name": "Тестовый пользователь",
    "age": 30,
    "password": "password123",
    "is_admin": false
  }'
```

### Вход в систему
```bash
curl -X POST "http://127.0.0.1:8000/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

### Создание курса (требуется авторизация админа)
```bash
curl -X POST "http://127.0.0.1:8000/courses" \
  -H "Content-Type: application/json" \
  -H "Cookie: session_token=ваш_токен" \
  -d '{
    "title": "Python для начинающих",
    "description": "Базовый курс по Python",
    "price": 5000
  }'
```

---

## Event-Driven архитектура с Kafka

Проект использует **Apache Kafka** для асинхронной обработки событий и реализации event-driven архитектуры.

### Как это работает

```
┌─────────────────┐
│   FastAPI App    │
│  (POST /users)   │
└────────┬─────────┘
         │
         │ 1. Сохранить в БД
         ▼
    ┌─────────┐
    │ SQLite  │
    └─────────┘
         │
         │ 2. Отправить событие
         ▼
┌─────────────────┐
│ Kafka Producer  │ ───┐
└─────────────────┘    │
                        │ Событие "user.created"
                        ▼
                  ┌──────────┐
                  │  Kafka   │  ← Хранилище событий
                  │ (Topic)   │
                  └────┬─────┘
                       │
                       │ 3. Читать событие
                       ▼
              ┌─────────────────┐
              │ Kafka Consumer  │
              │ (логирование)    │
              └─────────────────┘
```

### События в системе

#### События пользователей (`user-events`)

**`user.created`** - создание нового пользователя
```json
{
  "event_type": "user.created",
  "user_id": 1,
  "email": "user@example.com",
  "name": "Иван Иванов",
  "age": 25,
  "is_admin": false,
  "timestamp": "2025-01-28T12:00:00"
}
```

**`user.logged_in`** - вход пользователя в систему
```json
{
  "event_type": "user.logged_in",
  "user_id": 1,
  "email": "user@example.com",
  "timestamp": "2025-01-28T12:05:00"
}
```

#### События курсов (`course-events`)

**`course.created`** - создание нового курса
```json
{
  "event_type": "course.created",
  "course_id": 1,
  "title": "Python для начинающих",
  "price": 5000.0,
  "created_by": 1,
  "timestamp": "2025-01-28T12:10:00"
}
```

### Преимущества

- **Асинхронная обработка** - API не блокируется на долгие операции
- **Масштабируемость** - легко добавлять новые обработчики событий
- **Аудит действий** - все события сохраняются для анализа
- **Разделение ответственности** - компоненты системы независимы друг от друга
- **Event-driven архитектура** - демонстрация современных практик разработки

### Где используются события

События автоматически обрабатываются **Kafka Consumer**, который:
- Запускается при старте приложения (в `app/main.py`)
- Работает в отдельных потоках для каждого топика
- Логирует все события в консоль
- Может быть расширен для:
  - Отправки email уведомлений
  - Интеграции с аналитическими системами
  - Обновления метаданных
  - Других бизнес-процессов

### Kafka UI - Веб-интерфейс для просмотра событий

После запуска `docker compose up -d`, откройте **http://localhost:8080** для доступа к Kafka UI.

**Что можно делать:**
- Просматривать все топики (`user-events`, `course-events`)
- Видеть партиции и их состояние
- Читать сообщения (события) в реальном времени
- Создавать новые топики
- Мониторить производительность Kafka

**Как использовать:**
1. Откройте http://localhost:8080
2. В левом меню выберите **Topics**
3. Кликните на топик (например, `user-events`)
4. Перейдите на вкладку **Messages** - увидите все события с данными в JSON формате

---

## Структура проекта

```
ПроектFastApi/
├── app/
│   ├── main.py              # Точка входа FastAPI + запуск Kafka consumers
│   ├── auth.py              # Функции авторизации
│   ├── dependencies.py      # Общие зависимости (get_db)
│   ├── core/
│   │   ├── config.py        # Настройки из .env (включая Kafka)
│   │   ├── database.py      # Подключение к БД (SQLite)
│   │   ├── kafka_producer.py # Producer для отправки событий в Kafka
│   │   └── kafka_consumer.py # Consumer для обработки событий из Kafka
│   ├── models/              # SQLAlchemy модели
│   │   ├── user.py          # Модель пользователя
│   │   └── course.py        # Модель курса
│   ├── schemas/             # Pydantic схемы
│   │   ├── user.py          # Схемы пользователя (UserCreate, UserOut, UserLogin)
│   │   ├── course.py        # Схемы курса (CourseCreate, CourseOut)
│   │   └── events.py        # Схемы событий для Kafka
│   └── routers/             # API маршруты
│       ├── users.py         # Эндпоинты пользователей (+ отправка событий)
│       ├── auth.py          # Эндпоинты авторизации (+ отправка событий)
│       └── courses.py       # Эндпоинты курсов (+ отправка событий)
├── docker-compose.yml       # Конфигурация Docker (Kafka, Zookeeper, Kafka UI)
├── requirements.txt         # Зависимости Python
├── .gitignore              # Игнорируемые файлы
└── README.md               # Документация
```

---

## Для стажировки / портфолио

Этот проект демонстрирует:
- RESTful API на FastAPI
- Работу с базой данных через SQLAlchemy ORM
- Аутентификацию через cookie-сессии
- Валидацию данных через Pydantic
- **Event-Driven архитектуру с Apache Kafka**
- Producer и Consumer паттерны
- Docker и Docker Compose
- Асинхронную обработку событий
- Структурированный код с разделением ответственности

---

## Лицензия

MIT License 