# Hep - Quick Start

## 🚀 За 5 минут до первого запуска

### Локальная разработка

```bash
# 1. Клонируйте проект
cd hep

# 2. Backend
cd backend
pip install -r requirements.txt
cp .env.example .env
# Заполните .env файл вашими ключами
uvicorn main:app --reload

# 3. Frontend (в другом терминале)
cd ../frontend
python -m http.server 3000
```

Откройте http://localhost:3000

---

## 🎯 Минимальный набор переменных для теста

```env
DATABASE_URL=postgresql://user:pass@localhost:5432/hep
ANTHROPIC_API_KEY=sk-ant-your-key
NOTION_API_KEY=secret_your-key
NOTION_DATABASE_ID=your-database-id
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_MASTER_K23=your-chat-id
```

---

## 📦 Production Deploy (Render)

**3 простых шага:**

1. **PostgreSQL:** New → PostgreSQL → Create
2. **Backend:** New → Web Service → Connect GitHub → Deploy
3. **Frontend:** New → Static Site → Connect GitHub → Deploy

Детальные инструкции: `DEPLOYMENT.md`

---

## ✅ Первая проверка работы

1. Откройте frontend
2. Нажмите **Sync** → должны загрузиться заказы
3. Выберите заказ
4. Введите текст на английском
5. Подождите → появится перевод на русском
6. Нажмите **➤ Отправить** → проверьте Telegram

---

## 🔧 Если что-то не работает

**Переводы не работают?**
→ Проверьте `ANTHROPIC_API_KEY`

**Notion не синхронизируется?**
→ Проверьте `NOTION_API_KEY` и `NOTION_DATABASE_ID`

**Telegram не отправляет?**
→ Проверьте `TELEGRAM_BOT_TOKEN` и chat IDs

**CORS errors?**
→ Обновите `allow_origins` в `backend/main.py`

---

## 📚 Документация

- `README.md` - полное описание
- `DEPLOYMENT.md` - деплой на Render
- `Hepler-Project-Context.md` - принципы из исходного проекта

---

Удачи! 🎉
