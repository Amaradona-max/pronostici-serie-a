# ⚽ Serie A Predictions 2025/2026

Applicazione completa per pronostici calcistici Serie A con intelligenza artificiale.

## 🌐 Link Applicazione

- **Frontend:** https://pronostici-serie-a.vercel.app
- **Backend API:** https://seriea-predictions-api.onrender.com
- **API Docs:** https://seriea-predictions-api.onrender.com/docs

## ✨ Funzionalità

- 📊 **Classifica Serie A** aggiornata in tempo reale
- ⚽ **Capocannonieri** con statistiche complete
- 🟨 **Situazione Cartellini** e giocatori a rischio squalifica
- 📅 **Calendario Partite** con date e orari
- 🤖 **Pronostici AI** basati su algoritmi statistici
- 🔍 **Filtro Squadre** per vedere solo le partite di interesse
- 📱 **Design Responsive** per tutti i dispositivi

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

## 📊 Stato Attuale

- ✅ Backend deployato su Render con auto-deploy
- ✅ Frontend deployato su Vercel con auto-deploy
- ✅ Database PostgreSQL popolato con dati reali Serie A 2025/2026
- ✅ Classifica, Marcatori, Cartellini aggiornati (Giornata 17)
- ✅ Pronostici AI implementati e funzionanti
- ✅ Filtro squadre operativo
- ✅ **Pagina Statistiche completa** (NUOVO)
- ✅ **Analisi dettagliata partite** (NUOVO)
- ✅ **Pagina Partite con tabs** (NUOVO)
- ✅ Design moderno completato
- ✅ **Responsive mobile/tablet verificato** (NUOVO)
- ✅ **Dati accurati 100%** (no squadre fittizie)

## 📝 Ultimo Checkpoint

**Data:** 29 Dicembre 2025 - 23:41:39

Vedi file `CHECKPOINT_2025-12-29_23-41-39.md` per dettagli completi su:
- Tutte le funzionalità implementate (6 pagine complete)
- Come riprendere il lavoro
- Aggiornamenti futuri
- Troubleshooting
- Verifica compatibilità mobile

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
