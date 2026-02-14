# Hep - Translation & Messaging Tool

**Упрощённая версия Hepler без интеграции с Etsy**

Веб-приложение для автоматического перевода сообщений клиентов и отправки их мастерам в Telegram.

---

## 🎯 Возможности

- ✅ Перевод EN ↔ RU через Claude AI
- ✅ Отправка сообщений мастерам в Telegram
- ✅ Синхронизация заказов из Notion
- ✅ Компактный интерфейс (левая колонка 8 символов)
- ✅ Поиск по номеру заказа и ссылке Etsy
- ✅ Quick Replies (шаблоны ответов)
- ✅ История отправок в Telegram

---

## 🏗️ Архитектура

**Основано на проверенной архитектуре Hepler:**

```
hep/
├── backend/          # FastAPI + PostgreSQL
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   ├── services/     # Claude, Telegram, Notion
│   └── routes/       # API endpoints
└── frontend/         # Простой HTML + JS
    └── index.html
```

---

## 🚀 Deployment на Render

### Backend (Web Service)

1. Создайте новый Web Service
2. Подключите GitHub репозиторий
3. Настройки:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory:** `backend`
   - **Python Version:** 3.13

4. Environment Variables (см. `.env.example`)

### Frontend (Static Site)

1. Создайте новый Static Site
2. Подключите GitHub репозиторий
3. Настройки:
   - **Publish Directory:** `frontend`
   - **Build Command:** (оставить пустым)

### Database (PostgreSQL)

1. Создайте Managed PostgreSQL
2. Скопируйте Internal URL
3. Добавьте в Backend Environment Variables как `DATABASE_URL`

---

## 🔧 Локальная разработка

### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Заполните .env файл
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
python -m http.server 3000
# Или любой другой статический сервер
```

Откройте http://localhost:3000

---

## 📊 База данных

**3 таблицы (упрощённая версия без чатов):**

1. **order_cache** - кеш заказов из Notion
2. **quick_replies** - шаблоны ответов
3. **telegram_sends** - история отправок в Telegram

---

## 🔑 Критические принципы (из Hepler)

### ⚠️ Принцип №1: "Что видишь - то отправится"

Пользователь ВСЕГДА должен видеть ФИНАЛЬНЫЙ текст ДО отправки.

```python
# ✅ ПРАВИЛЬНО
async def send_to_telegram(message: str):
    # Отправляем КАК ЕСТЬ
    await bot.send_message(text=message)

# ❌ НЕПРАВИЛЬНО
async def send_to_telegram(message: str):
    # НЕ добавляем ничего!
    message = f"📬 {message}"  # ❌ Пользователь этого не видел!
```

### ⚠️ Принцип №2: Номер заказа добавляется ОДИН РАЗ

**Где:** В функции перевода (`claude_service.py`)

```python
if order_number and not translation.startswith(order_number):
    translation = f"{order_number}\n{translation}"
```

Пользователь видит это в поле → это и отправляется.

### ⚠️ Принцип №3: Русская буква "а" в номерах

- ✅ Правильно: `а511`, `а455`
- ❌ Неправильно: `a511`, `a455`

### ⚠️ Принцип №4: Чистые сообщения в Telegram

**БЕЗ:**
- ❌ Эмодзи (📬, ❓, 💵)
- ❌ Заголовков ("Новое сообщение")
- ❌ Ссылок
- ❌ Таймеров отмены
- ❌ Слова "Заказ:" перед номером

---

## 🎨 UI Спецификация

### Левая колонка (80px = ~8 символов)

```
┌────────┐
│Заказы  │
├────────┤
│[     ] │ ← Поиск
├────────┤
│а511    │
│а498    │
│ChIJx   │
└────────┘
```

### Правая колонка (адаптивная)

```
а511
К23 Ольга    Нужен к: 20.02    $2,460
Дата мастера: 18.02    wings, costume

┌─────────────────────────────┐
│ АНГЛИЙСКИЙ (ОРИГИНАЛ)       │
└─────────────────────────────┘

┌─────────────────────────────┐
│ РУССКИЙ (ДЛЯ МАСТЕРА)       │
│ а511                        │
│ Привет! Когда готово?       │
└─────────────────────────────┘

[❌][?][💰][➤ К23]
```

---

## 🔗 API Endpoints

### Заказы

```
GET  /api/orders/             # Список заказов
GET  /api/orders/{number}     # Детали заказа
POST /api/orders/sync-notion  # Синхронизация с Notion
```

### Переводы

```
POST /api/translate/
{
  "text": "Hello!",
  "direction": "to_russian",
  "order_number": "а511"
}
```

### Telegram

```
POST /api/telegram/send
{
  "order_number": "а511",
  "destination": "K23",
  "message": "а511\nПривет!"
}
```

---

## 💰 Стоимость (~$14-15/месяц)

- Render Web Service: $7
- PostgreSQL: $6
- Claude API: ~$1-2

---

## 📝 История изменений

**v1.0.0** - Первая версия
- Упрощённая архитектура без Etsy
- Компактный UI (8 символов левая колонка)
- Все проверенные принципы из Hepler
- Google OAuth (планируется)

---

## 🔒 Безопасность

**Планируется:**
- Google OAuth для входа
- Ограничение по email'ам
- Логирование всех действий

---

## 📚 Документация

Основано на опыте разработки **Hepler**:
- Итеративная разработка
- Тестирование на каждом шаге
- Простота важнее сложности
- Прозрачность для пользователя

---

## 🤝 Support

При проблемах проверьте:
1. Render Logs (Backend)
2. Browser Console (Frontend)
3. Telegram сообщения (что реально отправилось)

---

*Создано: февраль 2026*  
*На основе архитектуры Hepler*
