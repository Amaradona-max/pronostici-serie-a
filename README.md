# Serie A Predictions 2025/2026

Applicazione per pronostici calcistici Serie A basata su modello statistico Dixon-Coles.

## 🌐 Link Applicazione

- **Frontend:** https://pronostici-serie-a.vercel.app
- **Backend API:** https://seriea-predictions-api.onrender.com
- **API Docs:** https://seriea-predictions-api.onrender.com/docs

## 🛠️ Stack Tecnologico

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **Database:** PostgreSQL
- **Cache:** Redis
- **Task Queue:** Celery
- **ML Model:** Dixon-Coles per predizioni calcistiche
- **Hosting:** Render.com

### Frontend
- **Framework:** Next.js 15 (App Router)
- **UI:** React 18 + TypeScript
- **Styling:** Tailwind CSS + shadcn/ui
- **State Management:** TanStack Query (React Query)
- **Hosting:** Vercel

## 📊 Stato Deploy

- ✅ Backend deployato su Render
- ✅ Frontend deployato su Vercel
- ✅ Database PostgreSQL configurato
- ✅ Redis configurato
- ✅ CORS configurato
- ⏳ Database da popolare con fixtures Serie A

## 📝 Ultimo Checkpoint

**Data:** 28 Dicembre 2025 - 23:57:36

Vedi file `CHECKPOINT_2025-12-28_23-57-36.md` per dettagli completi su:
- Stato attuale del progetto
- Problemi risolti
- Prossimi passi
- Configurazione ambiente

## 🚀 Sviluppo Locale

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 📚 Documentazione

- [Deploy Backend su Render](./DEPLOY_BACKEND_RENDER.md)
- [Deploy Frontend su Vercel](./VERCEL_DEPLOY.md)
- [Changelog Fix Vercel](./CHANGELOG_VERCEL_FIX.md)
- [Checkpoint Ultimo](./CHECKPOINT_2025-12-28_23-57-36.md)
