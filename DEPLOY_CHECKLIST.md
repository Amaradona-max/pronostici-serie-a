# ✅ Checklist Deploy Completo

## Status Attuale

### ✅ Completato

- [x] **Frontend deployato su Vercel**
  - URL: https://frontend-rho-wheat-24.vercel.app
  - Build: Funzionante ✅
  - Status: Live

- [x] **Codice pushato su GitHub**
  - Repository: https://github.com/Amaradona-max/pronostici-serie-a
  - Branch: main
  - Ultimo commit: 7580fae (Fix Vercel issues)

- [x] **SECRET_KEY generato**
  - Chiave sicura: `2ca93ca18f5135c4d4f936301d452cf89d982575949771ef2ea44c6964931137`

- [x] **Documentazione creata**
  - ✅ DEPLOY_BACKEND_RENDER.md (guida completa)
  - ✅ VERCEL_DEPLOY.md
  - ✅ CHANGELOG_VERCEL_FIX.md
  - ✅ PROJECT_SUMMARY.md

### ⏳ Da Completare (segui DEPLOY_BACKEND_RENDER.md)

- [ ] **Deploy PostgreSQL su Render**
  - Tempo: ~2 minuti
  - Piano: Free

- [ ] **Deploy Redis su Render**
  - Tempo: ~2 minuti
  - Piano: Free

- [ ] **Deploy Backend API su Render**
  - Tempo: ~3 minuti
  - Piano: Free (con sleep) o Starter $7/mese

- [ ] **Inizializza Database**
  - Migrations: `alembic upgrade head`
  - Seed teams: `python -m app.scripts.seed_teams`

- [ ] **Deploy Celery Worker**
  - Tempo: ~2 minuti
  - Piano: Free

- [ ] **Deploy Celery Beat**
  - Tempo: ~2 minuti
  - Piano: Free

- [ ] **Connetti Frontend al Backend**
  - Configurare `NEXT_PUBLIC_API_URL` su Vercel
  - Redeploy frontend

- [ ] **Test Completo**
  - Health check backend
  - API Docs accessibili
  - Frontend mostra dati

---

## 🚀 Quick Start - Deploy Backend (10 minuti)

Segui questa procedura in ordine:

### 1. Apri Render.com
→ https://render.com (fai login/registrati)

### 2. Crea PostgreSQL
**New +** → **PostgreSQL**
- Name: `seriea-predictions-db`
- Region: Frankfurt
- Plan: Free
- **Copia Internal Database URL** ← IMPORTANTE!

### 3. Crea Redis
**New +** → **Redis**
- Name: `seriea-predictions-redis`
- Region: Frankfurt
- Plan: Free
- **Copia Internal Redis URL** ← IMPORTANTE!

### 4. Deploy Backend API
**New +** → **Web Service**
- Repository: `Amaradona-max/pronostici-serie-a`
- Root Directory: `backend`
- Runtime: Docker

**Environment Variables** (clicca Advanced):
```
DATABASE_URL=<Internal Database URL da step 2>
REDIS_URL=<Internal Redis URL da step 3>
CELERY_BROKER_URL=<Stesso Redis URL>
CELERY_RESULT_BACKEND=<Stesso Redis URL>
API_FOOTBALL_KEY=<La tua API key>
SECRET_KEY=2ca93ca18f5135c4d4f936301d452cf89d982575949771ef2ea44c6964931137
ENVIRONMENT=production
CORS_ORIGINS=["https://frontend-rho-wheat-24.vercel.app"]
LOG_LEVEL=INFO
```

### 5. Inizializza Database
Backend → Shell → Esegui:
```bash
alembic upgrade head
python -m app.scripts.seed_teams
```

### 6. Deploy Workers
Ripeti per Worker e Beat:
- **Worker**: Docker Command = `celery -A app.tasks.celery_app worker --loglevel=info`
- **Beat**: Docker Command = `celery -A app.tasks.celery_app beat --loglevel=info`
- Stesse environment variables del backend

### 7. Connetti Frontend
Vercel → frontend → Settings → Environment Variables:
```
NEXT_PUBLIC_API_URL=<URL del backend da step 4>/api/v1
```
Redeploy frontend

### 8. Test
- Backend: `https://your-api.onrender.com/api/v1/health`
- Frontend: `https://frontend-rho-wheat-24.vercel.app`

---

## 📋 Informazioni Chiave

### Repository GitHub
```
https://github.com/Amaradona-max/pronostici-serie-a
```

### Frontend Vercel
```
https://frontend-rho-wheat-24.vercel.app
```

### SECRET_KEY (per Render)
```
2ca93ca18f5135c4d4f936301d452cf89d982575949771ef2ea44c6964931137
```

### API Football
Ottieni la key: https://rapidapi.com/api-sports/api/api-football
(Piano gratuito disponibile)

---

## 🆘 Help

Se incontri problemi:
1. Consulta **DEPLOY_BACKEND_RENDER.md** (guida dettagliata)
2. Controlla i logs su Render Dashboard
3. Verifica che tutti gli URL siano "Internal" non "External"

---

## 💰 Costi Totali

**Free Tier**: $0/mese
- PostgreSQL Free (1GB)
- Redis Free (25MB)
- Backend Free (con sleep)
- 2x Workers Free
- Frontend Vercel Free

**Limitazione**: I servizi free "dormono" dopo 15min inattività
→ Prima richiesta: ~30 secondi di cold start

**Upgrade opzionale**: ~$25/mese per servizi sempre attivi

---

## ✨ Prossimi Step Dopo Deploy

1. Sincronizza dati partite:
   ```bash
   python -c "from app.tasks.sync_tasks import sync_season_fixtures; sync_season_fixtures('2025')"
   ```

2. Monitora logs per errori

3. Testa tutte le funzionalità

4. Aggiungi dominio custom (opzionale)

---

**Tempo totale deploy**: ~10-15 minuti
**Difficoltà**: Facile (segui la guida passo-passo)

Buon deploy! 🚀
