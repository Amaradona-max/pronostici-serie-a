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
- ✅ **Rose squadre VERIFICATE al 100% da Transfermarkt** (3 Gen 2026)
- ✅ **SISTEMA LIVE DATA IMPLEMENTATO** 🔴 **[NUOVO - 3 Gen 2026]**
  - Aggiornamenti automatici ogni 2-5 minuti
  - Football-Data.org integration (gratis, 14,400 req/giorno)
  - Sync automatico partite live, risultati e classifica
  - Guida completa setup: **[LIVE_DATA_SETUP.md](./LIVE_DATA_SETUP.md)**
- ✅ Giornata 18 in corso (2-4 Gennaio 2026)
- ✅ Classifica aggiornata (Milan 38 pts - in testa dopo Cagliari 0-1)
- ✅ Pronostici AI implementati e funzionanti
- ✅ Filtro squadre operativo
- ✅ **Pagina Statistiche completa**
- ✅ **Analisi dettagliata partite**
- ✅ **Pagina Partite con tabs**
- ✅ Design moderno completato
- ✅ **Responsive mobile/tablet verificato**
- ✅ **Dati accurati 100%** - Tutte le 20 squadre verificate da fonti ufficiali

## 📝 Ultimo Aggiornamento

**Data:** 3 Gennaio 2026

### ⚠️ Aggiornamento Critico Rose - 3 Gen 2026
- ✅ Verificate TUTTE le 20 rose di Serie A da Transfermarkt
- ✅ Rimossi trasferimenti fittizi/speculativi
- ✅ Aggiunti nuovi acquisti confermati (es. Fullkrug al Milan)
- ✅ Corretti numeri di maglia e nazionalità
- ✅ Dati pronti per uso professionale

**Checkpoint precedente:** 29 Dicembre 2025 - 23:41:39

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

# Copia e configura variabili d'ambiente
cp .env.example .env
# Modifica .env con le tue API keys

uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 🔴 Setup Dati Live (Opzionale ma Raccomandato)

Per abilitare aggiornamenti automatici di partite, risultati e classifica:

**📖 Leggi la guida completa**: [LIVE_DATA_SETUP.md](./LIVE_DATA_SETUP.md)

**Quick Start**:
1. Registrati gratis su https://www.football-data.org/client/register
2. Ottieni la tua API key via email
3. Aggiungi `FOOTBALL_DATA_KEY` nelle variabili d'ambiente
4. Configura Render Cron Job (5 minuti una tantum)

**Risultato**: Dati aggiornati automaticamente ogni 2-5 minuti, gratis forever! 🎉

## 📚 Documentazione

- [Deploy Backend su Render](./DEPLOY_BACKEND_RENDER.md)
- [Deploy Frontend su Vercel](./VERCEL_DEPLOY.md)
- [Changelog Fix Vercel](./CHANGELOG_VERCEL_FIX.md)
- [Checkpoint Ultimo](./CHECKPOINT_2025-12-28_23-57-36.md)
