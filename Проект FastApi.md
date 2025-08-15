### 📚 Общая картина проекта

**Mini-CRM** — это небольшой, но «живой» backend-сервис для онлайн-курсов:

- **FastAPI** + **SQLAlchemy** + **MySQL**
    
- Авторизация по cookie-сессии
    
- Валидация данных (Pydantic + кастомные валидаторы)
    
- Swagger UI автоматически «из коробки»
    
- Автотесты (pytest + TestClient)
    
- Полная контейнеризация (app + MySQL)
    
- GitHub Actions → линтеры + тесты
    

> 💡 **Философия**: после `git clone && docker-compose up` у рекрутёра сразу открывается `http://localhost:8000/docs`, там рабочие эндпоинты — без дополнительной настройки.

---

## 🗂️ Итоговая структура репозитория

```
.
├── app/
│   ├── main.py          # create_app() + FastAPI instance
│   ├── core/
│   │   ├── config.py    # load_dotenv() + pydantic.BaseSettings
│   │   └── database.py  # create_engine() + SessionLocal + Base
│   ├── models/          # SQLAlchemy ORM
│   ├── schemas/         # Pydantic DTO
│   ├── routers/         # APIRouters
│   ├── auth.py          # логин, генерация cookie, get_current_user
│   └── dependencies.py  # общие Depends
├── tests/
├── alembic/             # миграции
├── Dockerfile
├── docker-compose.yml
├── .env                 # DEV-секреты: DB_URL, SECRET_KEY...
├── requirements.txt
└── README.md
```



## Концепция и компоненты

|Компонент|Роль в системе|На что обратить внимание|
|---|---|---|
|**FastAPI**|HTTP-фреймворк, автоматически генерирует Swagger-UI.|Декораторы `@app.post`, dependency-инжекторы, фоновые задачи.|
|**SQLAlchemy**|ORM + декларативные модели.|Работа с сессиями, ленивые отношения, миграции через Alembic.|
|**MySQL**|Основное хранилище.|Docker-контейнер, кодировка `utf8mb4`, движок InnoDB.|
|**Pydantic**|Валидация входных / выходных схем.|e-mail валидатор, кастомные методы `@validator`.|
|**Cookie-сессии**|Авторизация: сервер выдаёт `session_token` (HttpOnly).|Хранить токен в БД или Redis? Для MVP подходит in-memory dict.|
|**Docker Compose**|«Кнопка» для локального запуска.|Два сервиса: `app` и `db`; сеть, переменные окружения.|
|**Pytest**|Автотесты: happy-path + edge-cases.|Использовать `TestClient`, фикстуры базы (rollback).|
|**GitHub Actions**|Проверка PR.|Линтеры + pytest, кеширование pip.|

---

## 2. Дерево проекта (без файлов кода)

bash

КопироватьРедактировать

`app/ │ ├── main.py              # Создаёт FastAPI, подключает роутеры ├── core/ │   └── database.py      # engine + SessionLocal + Base ├── models/              # SQLAlchemy таблицы ├── schemas/             # Pydantic-схемы (Create / Out / DB) ├── routers/             # Эндпоинты (users, courses, …) ├── auth.py              # /login, cookie-утилиты ├── dependencies.py      # get_current_user, common deps └── config.py            # .env → settings (pydantic.BaseSettings) tests/                   # Pytest-тесты alembic/                 # Версия миграций .env                     # Секреты/DSN Dockerfile docker-compose.yml README.md`

---

## 3. Пошаговый план (расширенный)

### Шаг 0 — «Скелет»

- **Цель:** «чистый» репозиторий, который уже ставится и запускается `uvicorn --reload`.
    
- **Действия:**
    
    1. `python -m venv venv && source venv/bin/activate`
        
    2. `pip install fastapi uvicorn sqlalchemy[asyncio] aiomysql alembic pydantic[email] pytest python-dotenv`
        
    3. `requirements.txt` → `pip freeze > requirements.txt`
        
    4. Пустой файл `app/main.py` с `FastAPI()` и `@app.get("/")`.
        
- **Проверка:** `uvicorn app.main:app`. Swagger открывается.
    

### Шаг 1 — «База + первая модель»

- **Что делаем:**
    
    1. `core/database.py`: создаём `engine = create_async_engine("mysql+aiomysql://user:pass@db:3306/crm")`, `SessionLocal = async_sessionmaker(...)`, `Base = declarative_base()`.
        
    2. `models/user.py` с полями `id`, `email`, `name`, `age`, `is_admin`.
        
    3. `alembic init alembic` → настроить `env.py` (асинхронный MySQL URL).
        
    4. `alembic revision --autogenerate -m "create users"` → `upgrade head`.
        
- **Почему важно:** Понимаешь связку SQLAlchemy ⇄ Alembic ⇄ MySQL; проверяешь, как создаётся настоящая таблица в контейнере.
    
- **Хитрость:** В `docker-compose.yml` укажи `command: --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci`, иначе эмодзи/русский могут сломаться.
    

### Шаг 2 — «CRUD /users»

- **Что добавляем:**
    
    - Pydantic-схемы: `UserCreate` (email, name, age), `UserOut` (id, email, name).
        
    - `routers/users.py`:
        
        - `@router.post("/users", response_model=UserOut)` — создаёт запись.
            
        - `@router.get("/users/{user_id}", response_model=UserOut)` — читает.
            
- **Проверяем:** Через Swagger отправляем POST, получаем 200 и JSON.
    
- **Что учишь:** Разница между схемой «ввод» и «вывод», работа с асинхронной сессией.
    

### Шаг 3 — «Авторизация cookie»

- **Механика:**
    
    1. `/login` принимает `BasicAuth` (email+password*), сравнивает с БД.
        
    2. Генерирует `uuid4()` → кладёт в куку `session_token`, `httponly=True, samesite="lax"`.
        
    3. В памяти (или отдельной таблице) хранишь `token → user_id`.
        
    4. Депенд `get_current_user` достаёт куку, ищет пользователя.
        
    5. `/me` использует этот депенд и просто возвращает `UserOut`.
        
- **Навык:** Как устроены cookie-заголовки, где их прятать, чем отличаются от JWT.  
    *Пароли в MVP можно хранить в plain-text, но лучше сразу bcrypt.
    

### Шаг 4 — «Курсы»

- **Действия:**
    
    1. `models/course.py` + миграция.
        
    2. Схемы: `CourseCreate`, `CourseOut`.
        
    3. CRUD-роутер `/courses` (GET-list, POST, GET by id).
        
- **Уловки:** У курса цена decimal → в MySQL лучше `DECIMAL(10,2)`.
    

### Шаг 5 — «Заявки (Enrolment)»

- **Что важно:**
    
    - В модели `enrolment` поставить `UniqueConstraint("user_id", "course_id")`.
        
    - POST `/enrolments` должен брать `current_user` и `course_id` из body.
        
    - Если пара уже есть — `HTTP_400_BAD_REQUEST`.
        
    - GET `/enrolments` отдаёт список курсов текущего пользователя.
        
- **Навык:** Работа с FK + уникальными ограничениями.
    

### Шаг 6 — «Отзывы»

- **Фишка:** Кастомный валидатор на «плохие слова».
    
    - В `schemas/feedback.py`:
        
        python
        
        КопироватьРедактировать
        
        `class FeedbackCreate(BaseModel):     text: str      @validator("text")     def no_bad_words(cls, v):         blacklist = {"дурень", "badword"}         if any(w in v.lower() for w in blacklist):             raise ValueError("Недопустимые слова")         return v`
        
    - POST `/feedback` (авторизован).
        
    - GET `/feedback` публичный, пагинация optional.
        

### Шаг 7 — «Headers демо»

- Цель — показать работу с `Header` и проверками.
    
    - `/headers`: читает `User-Agent`, `Accept-Language`; если нет — `HTTP_400`.
        
    - Возвращает эти значения в JSON.
        

### Шаг 8 — «Тесты»

- **Треугольник: arrange-act-assert**.
    
    - Фикстура `async_client` (TestClient с `app`).
        
    - Тест: создать пользователя → логин → `/me` OK.
        
    - Проверка валидации e-mail, возраста `< 16` → 422.
        
    - Двойная заявка → 400.
        

### Шаг 9 — «Docker Compose»

- **docker-compose.yml**:
    

yaml

КопироватьРедактировать

`services:   db:     image: mysql:8.4     restart: always     environment:       MYSQL_ROOT_PASSWORD: root       MYSQL_DATABASE: crm       MYSQL_USER: crm       MYSQL_PASSWORD: crm     ports: ["3306:3306"]    app:     build: .     depends_on: [db]     environment:       DATABASE_URL: mysql+aiomysql://crm:crm@db:3306/crm     ports: ["8000:8000"]`

- `Dockerfile` — копируешь проект, `pip install`, запускаешь `uvicorn`.
    

### Шаг 10 — «CI + линтеры»

- `.github/workflows/ci.yml`:
    
    - `actions/checkout`, `setup-python`, `pip install -r`.
        
    - `pytest` + `black --check` + `flake8`.
        
    - Можно кэшировать pip (`actions/cache@v4`).
        

### Шаг 11 — «Документация»

- **README.md**:
    
    - Бейджики CI.
        
    - Команда запуска (`docker-compose up -d`).
        
    - Примеры `curl`: регистрация, логин, создание курса.
        
    - UML-картинка (PlantUML или mermaid) с компонентами.

## 🪜 Детальный план, шаг за шагом

### 🔹 Шаг 0. Подготовка окружения

1. **init repo & venv**
    
    ```bash
    git init mini-crm
    cd mini-crm
    python -m venv .venv && source .venv/bin/activate
    pip install --upgrade pip
    pip install fastapi uvicorn sqlalchemy alembic pydantic[email] python-dotenv pytest
    pip freeze > requirements.txt
    ```
    
2. Скелет каталогов `app/`, `tests/`.
    
3. Добавь минимальный `app/main.py`:
    
    ```python
    from fastapi import FastAPI
    
    app = FastAPI(title="Mini-CRM (online courses)")
    
    @app.get("/ping")
    def ping():
        return {"ok": True}
    ```
    
4. Запустись локально:  
    `uvicorn app.main:app --reload` → `http://127.0.0.1:8000/docs`.
    

---

### 🔹 Шаг 1. База + модели (User) — **уже на MySQL**

1. **docker-compose** сразу описываем MySQL 8:
    
    ```yaml
    services:
      db:
        image: mysql:8
        restart: unless-stopped
        environment:
          MYSQL_ROOT_PASSWORD: root
          MYSQL_DATABASE: crm
          MYSQL_USER: crm_user
          MYSQL_PASSWORD: crm_pass
        ports: ["3306:3306"]
        volumes:
          - dbdata:/var/lib/mysql
    volumes:
      dbdata:
    ```
    
2. **.env** (не коммить секреты в проде!):
    
    ```
    DB_URL=mysql+mysqldb://crm_user:crm_pass@db:3306/crm
    SECRET_KEY=super-secret
    ```
    
3. **`app/core/database.py`**
    
    ```python
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, declarative_base
    from app.core.config import settings             # pydantic BaseSettings
    
    engine = create_engine(settings.DB_URL, pool_pre_ping=True, future=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    Base = declarative_base()
    ```
    
4. **Модель User (app/models/user.py)**
    
    ```python
    from sqlalchemy import Column, Integer, String, Boolean
    from app.core.database import Base
    
    class User(Base):
        __tablename__ = "users"
    
        id        = Column(Integer, primary_key=True, index=True)
        email     = Column(String(320), unique=True, nullable=False, index=True)
        name      = Column(String(100), nullable=False)
        age       = Column(Integer, nullable=False)
        is_admin  = Column(Boolean, default=False)
    ```
    
5. **Alembic**
    
    ```bash
    alembic init alembic
    # в alembic.ini поменять sqlalchemy.url=${DB_URL}
    alembic revision -m "create users" --autogenerate
    alembic upgrade head
    ```
    

---

### 🔹 Шаг 2. CRUD `/users`

1. **schemas/user.py**
    
    ```python
    from pydantic import BaseModel, EmailStr, conint
    
    class UserCreate(BaseModel):
        email: EmailStr
        name: str
        age: conint(ge=10, le=120)
    
    class UserOut(BaseModel):
        id: int
        email: EmailStr
        name: str
        age: int
        is_admin: bool
    
        class Config:
            orm_mode = True
    ```
    
2. **routers/users.py**
    
    ```python
    from fastapi import APIRouter, Depends, HTTPException, status
    from sqlalchemy.orm import Session
    from app.schemas.user import UserCreate, UserOut
    from app.models.user import User
    from app.dependencies import get_db
    
    router = APIRouter(prefix="/users", tags=["users"])
    
    @router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
    def create_user(payload: UserCreate, db: Session = Depends(get_db)):
        if db.query(User).filter_by(email=payload.email).first():
            raise HTTPException(400, "Email already registered")
        user = User(**payload.dict())
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @router.get("/{user_id}", response_model=UserOut)
    def get_user(user_id: int, db: Session = Depends(get_db)):
        user = db.get(User, user_id)
        if not user:
            raise HTTPException(404, "User not found")
        return user
    ```
    
3. **Подключаем роутер** в `app/main.py`.
    

---

### 🔹 Шаг 3. Авторизация (cookie session)

- **/login** принимает `HTTPBasic`, сверяет email + «пароль» (для MVP можно просто email == password).
    
- В ответ ставим `Set-Cookie: session=jwt-token; HttpOnly; Secure`.
    
- `get_current_user()` — зависимость, читает и проверяет JWT, достаёт id пользователя.
    
- Защищённый `/me` возвращает `UserOut`.
    

> 🔐 **JWT + cookie** проще связать с `python-jose` или `itsdangerous`; в cookie хранится только токен, в БД ничего лишнего.

---

### 🔹 Шаг 4. Курсы

- **Модель Course** (`id, title, description, price`) + миграция.
    
- Схемы `CourseCreate`, `CourseOut` (price — `conint(ge=0)`).
    
- CRUD-роутер `/courses` (анонимный GET список, POST — только админ).
    

---

### 🔹 Шаг 5. Заявки (Enrolment)

- Таблица: `id, user_id (FK), course_id (FK), created TIMESTAMP)`  
    `UniqueConstraint("user_id", "course_id")`.
    
- POST `/enrolments` (авторизован) — «записаться на курс». При повторе 400.
    
- GET `/enrolments` — список моих курсов (`joinedload(course)` для 1 SQL-запроса).
    

---

### 🔹 Шаг 6. Отзывы (Feedback)

- Таблица: `id, user_id (FK), text, created`.
    
- Схема `FeedbackCreate` с кастом-валидатором:
    
    ```python
    BAD_WORDS = {"spam", "shit"}
    
    @validator("text")
    def no_bad_words(cls, v):
        lowered = v.lower()
        if any(bw in lowered for bw in BAD_WORDS):
            raise ValueError("Нецензурная лексика запрещена")
        return v
    ```
    
- POST `/feedback` (авторизован), GET `/feedback` (публично, пагинация).
    

---

### 🔹 Шаг 7. Заголовки-демка

```python
@router.get("/headers")
def echo_headers(user_agent: str = Header(...), accept_language: str = Header(...)):
    if "curl" in user_agent.lower():
        raise HTTPException(400, "curl запрещён")
    return {"ua": user_agent, "lang": accept_language}
```

---

### 🔹 Шаг 8. Pytest-тесты

- **conftest.py** — фикстура `client` (TestClient) с `override_dependency(get_db)`.
    
- **test_users.py** — happy-path создание → login → /me.
    
- **test_validation.py** — email, age 10–120.
    
- **test_enrolment.py** — повторная заявка == 400.
    

В CI они должны укладываться < 10 с.

---

### 🔹 Шаг 9. Docker / Compose

**Dockerfile**:

```dockerfile
FROM python:3.12-slim
WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml** (добавляем app-сервис + depends_on db):

```yaml
services:
  app:
    build: .
    env_file: .env
    ports: ["8000:8000"]
    depends_on:
      - db
```

> При первом `docker-compose up --build` Alembic не запустится сам. Добавь в `app/main.py` авто-upgrade:

```python
import alembic.config
def run_migrations() -> None:
    alembic.config.main(argv=["upgrade", "head"])
```

и вызови до `create_app()`.

---

### 🔹 Шаг 10. GitHub Actions

`.github/workflows/ci.yml`

```yaml
name: CI
on: [push, pull_request]
jobs:
  test
```

## 🎉 **Шаг 3 завершён — Авторизация через cookie-сессии!**

Добавлены:
- ✅ **Поле `password` в модель `User`**
- ✅ **Схемы для авторизации**
- ✅ **Модуль `auth.py` с функциями для сессий**
- ✅ **Роутер `auth.py` с эндпоинтами `/login`, `/me`, `/logout`**

## ⚠️ **Важно: нужно пересоздать базу данных**

Так как мы добавили новое поле `password` в модель `User`, нужно пересоздать таблицы:

1. **Остановите сервер** (Ctrl+C)
2. **Удалите файл `test.db`**
3. **Перезапустите сервер:**
   ```powershell
   py -m uvicorn app.main:app --reload
   ```

## 🔍 **Как проверить авторизацию:**

1. **Создайте пользователя:**
   - POST `/users` с данными:
     ```json
     {
       "email": "user@example.com",
       "name": "Тестовый Пользователь",
       "age": 30,
       "password": "secret123"
     }
     ```

2. **Войдите в систему:**
   - POST `/login` с данными:
     ```json
     {
       "email": "user@example.com",
       "password": "secret123"
     }
     ```
   - Должен вернуться `{"message": "Вход выполнен успешно"}`
   - В браузере установится cookie `session_token`

3. **Проверьте текущего пользователя:**
   - GET `/me` → должен вернуть данные пользователя

4. **Выйдите из системы:**
   - POST `/logout` → удалит cookie

## 🚀 **Следующий шаг — Курсы**

Готовы перейти к шагу 4 — создание модели `Course` и API для курсов?


