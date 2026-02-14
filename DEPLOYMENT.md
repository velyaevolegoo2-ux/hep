# Hep - Инструкции по деплою на Render

## 📋 Подготовка

### 1. GitHub репозиторий

Создайте новый репозиторий и загрузите код:

```bash
git init
git add .
git commit -m "Initial commit: Hep v1.0"
git remote add origin https://github.com/YOUR_USERNAME/hep.git
git push -u origin main
```

---

## 🗄️ ШАГ 1: PostgreSQL Database

1. Зайдите на https://dashboard.render.com
2. Нажмите **New +** → **PostgreSQL**
3. Настройки:
   - **Name:** `hep-database`
   - **Database:** `hep`
   - **User:** (автоматически)
   - **Region:** `Oregon (US West)`
   - **Plan:** `Free` или `Starter ($7/month)`
4. Нажмите **Create Database**
5. **ВАЖНО:** Скопируйте **Internal Database URL** (понадобится для backend)

---

## 🔧 ШАГ 2: Backend Web Service

1. Нажмите **New +** → **Web Service**
2. **Connect repository:** выберите ваш GitHub репозиторий `hep`
3. Настройки:
   - **Name:** `hep-backend`
   - **Root Directory:** `backend`
   - **Environment:** `Python 3`
   - **Region:** `Oregon (US West)` (тот же что БД!)
   - **Branch:** `main`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** `Free` или `Starter ($7/month)`

4. **Environment Variables** - добавьте все:

```
DATABASE_URL=<Internal Database URL из шага 1>
ANTHROPIC_API_KEY=sk-ant-...
NOTION_API_KEY=secret_...
NOTION_DATABASE_ID=0090e9235da045c8b4f08c55d41dff57
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_PROBLEMS=...
TELEGRAM_CHAT_PRICING=...
TELEGRAM_MASTER_K23=-850392862
TELEGRAM_MASTER_P5=-890475499
TELEGRAM_MASTER_KR11=-4101389388
TELEGRAM_MASTER_K17=-4927540786
TELEGRAM_MASTER_K48=-4039825511
FRONTEND_URL=https://hep.onrender.com
```

5. Нажмите **Create Web Service**

6. **Дождитесь деплоя** (~2-3 минуты)

7. **Проверьте:** Откройте URL (например, `https://hep-backend.onrender.com`)
   - Должны увидеть: `{"app":"Hep","version":"1.0.0","status":"running"}`

---

## 🎨 ШАГ 3: Frontend Static Site

1. Нажмите **New +** → **Static Site**
2. **Connect repository:** выберите ваш GitHub репозиторий `hep`
3. Настройки:
   - **Name:** `hep`
   - **Root Directory:** `frontend`
   - **Branch:** `main`
   - **Build Command:** (оставить пустым)
   - **Publish Directory:** `.` (точка)

4. Нажмите **Create Static Site**

5. **После деплоя:** Откройте `index.html` в редакторе

6. **Замените API_URL:**
   ```javascript
   // Было:
   const API_URL = 'http://localhost:8000';
   
   // Стало:
   const API_URL = 'https://hep-backend.onrender.com';
   ```

7. **Commit и push изменения:**
   ```bash
   git add frontend/index.html
   git commit -m "Update API URL for production"
   git push
   ```

8. **Render автоматически задеплоит** обновление (~1 минута)

---

## 🔐 ШАГ 4: CORS настройки (важно!)

1. Откройте `backend/main.py`
2. Обновите CORS origins:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=[
           "https://hep.onrender.com",  # Ваш frontend URL
           "http://localhost:3000",
       ],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

3. Commit и push:
   ```bash
   git add backend/main.py
   git commit -m "Update CORS for production"
   git push
   ```

---

## ✅ ШАГ 5: Проверка работы

### 5.1 Проверьте Backend

Откройте `https://hep-backend.onrender.com/health`

Должны увидеть:
```json
{"status":"healthy"}
```

### 5.2 Синхронизация с Notion

```bash
curl -X POST https://hep-backend.onrender.com/api/orders/sync-notion
```

Должны увидеть:
```json
{"success":true,"synced_count":150}
```

### 5.3 Проверьте Frontend

1. Откройте `https://hep.onrender.com`
2. Нажмите кнопку **Sync**
3. Должны загрузиться заказы в левой колонке

---

## 🎯 ШАГ 6: Первое использование

1. Выберите заказ из списка (например, `а511`)
2. Введите английский текст: `Hello! When will my order be ready?`
3. Подождите 1 секунду → появится русский перевод
4. Нажмите **➤ К23** (или другой мастер)
5. Проверьте Telegram чат мастера → должно прийти сообщение

---

## 🔧 Troubleshooting

### Проблема: "Failed to load orders"

**Решение:**
1. Проверьте Backend Logs в Render Dashboard
2. Убедитесь что `DATABASE_URL` правильный
3. Проверьте что `NOTION_API_KEY` работает

### Проблема: "CORS error"

**Решение:**
1. Проверьте `backend/main.py` → CORS origins
2. Убедитесь что frontend URL точно совпадает
3. Redeploy backend после изменений

### Проблема: "Translation не работает"

**Решение:**
1. Проверьте `ANTHROPIC_API_KEY` в Environment Variables
2. Проверьте Backend Logs на ошибки
3. Убедитесь что API key активен и имеет credits

### Проблема: "Telegram не отправляет"

**Решение:**
1. Проверьте `TELEGRAM_BOT_TOKEN`
2. Проверьте chat IDs мастеров (должны быть отрицательные числа)
3. Убедитесь что бот добавлен в чаты

---

## 📊 Мониторинг

### Logs

Render показывает логи в реальном времени:
- Backend: Dashboard → hep-backend → Logs
- Frontend: Dashboard → hep → Logs (обычно пустые для static site)

### Alerts

Настройте email alerts при падении сервисов:
- Dashboard → Service → Settings → Health Checks

---

## 💰 Стоимость

**Free tier (для тестирования):**
- PostgreSQL Free: 90 дней, потом $7/месяц
- Web Service Free: спит через 15 мин неактивности
- Static Site: бесплатно навсегда

**Starter tier (для production):**
- PostgreSQL Starter: $7/месяц
- Web Service Starter: $7/месяц  
- Static Site: бесплатно
- **Итого: $14/месяц**

---

## 🔄 Обновления

При изменении кода:

```bash
git add .
git commit -m "Your changes"
git push
```

Render автоматически задеплоит:
- Backend: ~1-2 минуты
- Frontend: ~30 секунд

---

## 📝 Checklist

- [ ] PostgreSQL создана
- [ ] Backend задеплоен
- [ ] Environment variables настроены
- [ ] Frontend задеплоен
- [ ] API_URL обновлён в frontend
- [ ] CORS настроен
- [ ] Notion синхронизация работает
- [ ] Перевод работает
- [ ] Telegram отправка работает
- [ ] Все тесты пройдены

---

**Готово! 🎉**

Ваше приложение Hep работает на Render!

URL: https://hep.onrender.com
