# 🚀 Hep - Быстрый запуск (30-40 минут)

## ✅ Что у вас уже есть:
- Все API ключи готовы
- GitHub аккаунт есть
- Render аккаунт есть (используется для Hepler)

---

## 📦 ШАГ 1: Создание GitHub репозитория (5 минут)

### 1.1 Скачайте проект
Скачайте папку `hep` из outputs

### 1.2 Откройте терминал в папке проекта
```bash
cd /path/to/hep
```

### 1.3 Инициализируйте Git репозиторий
```bash
git init
git add .
git commit -m "Initial commit: Hep v1.0"
```

### 1.4 Создайте репозиторий на GitHub
1. Зайдите на https://github.com/new
2. Название: `hep`
3. Описание: `Translation and messaging tool`
4. Public или Private (на ваш выбор)
5. **НЕ** создавайте README, .gitignore, license
6. Нажмите "Create repository"

### 1.5 Подключите локальный репозиторий к GitHub
```bash
git remote add origin https://github.com/YOUR_USERNAME/hep.git
git branch -M main
git push -u origin main
```

✅ **Проверка:** Обновите страницу GitHub — код должен появиться

---

## 🗄️ ШАГ 2: PostgreSQL на Render (3 минуты)

### 2.1 Создайте базу данных
1. Зайдите на https://dashboard.render.com
2. Нажмите **New +** → **PostgreSQL**
3. Заполните:
   - **Name:** `hep-database`
   - **Database:** `hep`
   - **Region:** `Oregon (US West)` ⚠️ **Важно: тот же регион что backend!**
   - **Plan:** `Starter` ($7/мес) или `Free` (для теста на 90 дней)
4. Нажмите **Create Database**

### 2.2 Скопируйте Internal Database URL
1. Дождитесь создания (~1 минута)
2. Найдите **Internal Database URL** 
3. **Скопируйте его полностью** (начинается с `postgresql://`)
4. Сохраните в блокноте — понадобится для backend

✅ **Проверка:** URL должен выглядеть как `postgresql://user:password@...`

---

## 🔧 ШАГ 3: Backend на Render (10 минут)

### 3.1 Создайте Web Service
1. Нажмите **New +** → **Web Service**
2. **Connect repository:** выберите `hep`
3. Заполните:
   - **Name:** `hep-backend`
   - **Root Directory:** `backend`
   - **Environment:** `Python 3`
   - **Region:** `Oregon (US West)` ⚠️ **Тот же что БД!**
   - **Branch:** `main`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** `Starter` ($7/мес) или `Free`

### 3.2 Добавьте Environment Variables

⚠️ **Очень важный шаг!** Добавьте все переменные:

```
DATABASE_URL=<Internal Database URL из шага 2.2>
ANTHROPIC_API_KEY=<ваш Claude API key>
NOTION_API_KEY=<ваш Notion API key>
NOTION_DATABASE_ID=<ваш Notion Database ID>
TELEGRAM_BOT_TOKEN=<ваш Telegram bot token>
TELEGRAM_CHAT_PROBLEMS=<chat ID для проблем>
TELEGRAM_CHAT_PRICING=<chat ID для цен>
TELEGRAM_MASTER_K23=<chat ID мастера К23>
TELEGRAM_MASTER_P5=<chat ID мастера P5>
TELEGRAM_MASTER_KR11=<chat ID мастера KR11>
TELEGRAM_MASTER_K17=<chat ID мастера K17>
TELEGRAM_MASTER_K48=<chat ID мастера K48>
FRONTEND_URL=https://hep.onrender.com
```

### 3.3 Нажмите "Create Web Service"

### 3.4 Дождитесь деплоя (~2-3 минуты)

✅ **Проверка:** Откройте `https://hep-backend.onrender.com`
Должны увидеть: `{"app":"Hep","version":"1.0.0","status":"running"}`

---

## 🎨 ШАГ 4: Frontend на Render (5 минут)

### 4.1 Создайте Static Site
1. Нажмите **New +** → **Static Site**
2. **Connect repository:** выберите `hep`
3. Заполните:
   - **Name:** `hep`
   - **Root Directory:** `frontend`
   - **Branch:** `main`
   - **Build Command:** (оставить пустым)
   - **Publish Directory:** `.` (точка)

### 4.2 Нажмите "Create Static Site"

### 4.3 Дождитесь деплоя (~30 секунд)

✅ **Проверка:** Откройте `https://hep.onrender.com`
Должны увидеть интерфейс Hep

---

## 🔗 ШАГ 5: Подключите Frontend к Backend (2 минуты)

### 5.1 Откройте `frontend/index.html` в редакторе

### 5.2 Найдите строку (примерно строка 313):
```javascript
const API_URL = 'http://localhost:8000';
```

### 5.3 Замените на:
```javascript
const API_URL = 'https://hep-backend.onrender.com';
```

### 5.4 Сохраните и закоммитьте:
```bash
git add frontend/index.html
git commit -m "Update API URL for production"
git push
```

### 5.5 Дождитесь автодеплоя (~30 секунд)

✅ **Проверка:** Обновите `https://hep.onrender.com` — должно работать!

---

## 🎯 ШАГ 6: Финальная проверка (10 минут)

### 6.1 Проверьте Backend Health
Откройте: `https://hep-backend.onrender.com/health`

Ожидаемый ответ:
```json
{"status":"healthy"}
```

### 6.2 Синхронизация с Notion
1. Откройте `https://hep.onrender.com`
2. Нажмите кнопку **Sync**
3. Проверьте логи Backend в Render Dashboard
4. Должны загрузиться заказы в левой колонке

### 6.3 Тест перевода
1. Выберите любой заказ из списка
2. Введите в поле "Английский": `Hello! When will it be ready?`
3. Подождите 1 секунду
4. В поле "Русский" должен появиться перевод с номером заказа

### 6.4 Тест отправки в Telegram
1. Убедитесь что русский текст есть
2. Нажмите кнопку **?** (проблемы)
3. Увидите таймер: 30, 29, 28...
4. Дождитесь 0 или отмените повторным нажатием
5. Проверьте Telegram чат "проблемы" — должно прийти сообщение

---

## ✅ ГОТОВО!

Ваш Hep запущен и работает!

- **Frontend:** https://hep.onrender.com
- **Backend:** https://hep-backend.onrender.com

---

## 🐛 Troubleshooting

### "Failed to load orders"
→ Проверьте Backend Logs в Render Dashboard
→ Убедитесь что `NOTION_API_KEY` и `NOTION_DATABASE_ID` правильные

### "Translation не работает"
→ Проверьте `ANTHROPIC_API_KEY` в Backend Environment Variables
→ Убедитесь что API key активен и имеет credits

### "Telegram не отправляет"
→ Проверьте `TELEGRAM_BOT_TOKEN` и chat IDs
→ Убедитесь что chat IDs отрицательные числа (начинаются с `-`)

### "CORS error"
→ Убедитесь что в `backend/main.py` в `allow_origins` есть `https://hep.onrender.com`
→ Redeploy backend после изменений

---

## 💰 Стоимость

**Starter tier (рекомендуется):**
- PostgreSQL Starter: $7/мес
- Web Service Starter: $7/мес
- Static Site: $0 (бесплатно)
- **Итого: $14/мес**

**Free tier (для теста):**
- PostgreSQL Free: 90 дней бесплатно, потом $7/мес
- Web Service Free: засыпает через 15 мин неактивности
- Static Site: $0 (бесплатно навсегда)

---

## 🎉 Поздравляем!

Теперь вы можете работать с Hep и дорабатывать UI по мере использования.

Для обновлений просто делайте:
```bash
git add .
git commit -m "Your changes"
git push
```

Render автоматически задеплоит изменения!
