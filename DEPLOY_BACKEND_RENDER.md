# 🚀 Deploy Backend su Render - Guida Rapida (10 minuti)

Guida step-by-step per deployare il backend su Render.com

## ✅ Prerequisiti

- Account Render.com (gratis) → [render.com](https://render.com)
- API Key API-Football → [rapidapi.com/api-sports/api/api-football](https://rapidapi.com/api-sports/api/api-football)

---

## 📝 Step 1: Preparazione (2 min)

### 1.1 Crea Account Render

1. Vai su [render.com](https://render.com)
2. Clicca **"Get Started"**
3. Registrati con GitHub (consigliato) o Email

### 1.2 Informazioni che ti Servono

Tieni pronti questi valori (li useremo dopo):

```
SECRET_KEY: 2ca93ca18f5135c4d4f936301d452cf89d982575949771ef2ea44c6964931137
```

**API Football Key**: La tua chiave da RapidAPI
- Se non ce l'hai: [Registrati qui](https://rapidapi.com/api-sports/api/api-football) (piano gratuito disponibile)

---

## 🗄️ Step 2: Deploy PostgreSQL (2 min)

1. Nel dashboard Render, clicca **"New +"** → **"PostgreSQL"**

2. Configura:
   - **Name**: `seriea-predictions-db`
   - **Database**: `seriea_predictions`
   - **User**: `seriea`
   - **Region**: **Frankfurt** (più vicino all'Italia)
   - **PostgreSQL Version**: 16 (latest)
   - **Plan**: **Free** (per MVP)

3. Clicca **"Create Database"**

4. **IMPORTANTE**: Copia l'**Internal Database URL**
   - Vai alla tab "Info"
   - Cerca **"Internal Database URL"**
   - Clicca "Copy" e salvalo in un file di testo temporaneo
   - Formato: `postgresql://user:pass@dpg-xxx-a.frankfurt-postgres.render.com/dbname`

---

## 🔴 Step 3: Deploy Redis (2 min)

1. Clicca **"New +"** → **"Redis"**

2. Configura:
   - **Name**: `seriea-predictions-redis`
   - **Region**: **Frankfurt**
   - **Plan**: **Free** (25MB, sufficiente per MVP)
   - **Maxmemory Policy**: **allkeys-lru**

3. Clicca **"Create Redis"**

4. **IMPORTANTE**: Copia l'**Internal Redis URL**
   - Vai alla tab "Info"
   - Cerca **"Internal Redis URL"**
   - Clicca "Copy" e salvalo
   - Formato: `redis://red-xxx-a.frankfurt-redis.render.com:6379`

---

## 🚀 Step 4: Deploy Backend API (3 min)

1. Clicca **"New +"** → **"Web Service"**

2. **Connetti Repository GitHub**:
   - Se non hai ancora pushato su GitHub:
     ```bash
     # Nel tuo terminale locale
     cd "/Users/prova/Desktop/Pronostici Master Calcio"
     git remote add origin https://github.com/TUO-USERNAME/seriea-predictions.git
     git push -u origin main
     ```
   - Autorizza Render ad accedere ai tuoi repository
   - Seleziona il repository `seriea-predictions`

3. Configura il servizio:
   - **Name**: `seriea-predictions-api`
   - **Region**: **Frankfurt**
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: **Docker**
   - **Plan**: **Free** (con sleep dopo 15min inattività) o **Starter $7/mese** (no sleep)

4. **Environment Variables** - Clicca "Advanced" e aggiungi:

   ```
   DATABASE_URL=<INCOLLA Internal Database URL da Step 2>
   REDIS_URL=<INCOLLA Internal Redis URL da Step 3>

   CELERY_BROKER_URL=<INCOLLA STESSO Internal Redis URL>
   CELERY_RESULT_BACKEND=<INCOLLA STESSO Internal Redis URL>

   API_FOOTBALL_KEY=<LA TUA API KEY DA RAPIDAPI>
   SECRET_KEY=2ca93ca18f5135c4d4f936301d452cf89d982575949771ef2ea44c6964931137

   ENVIRONMENT=production
   CORS_ORIGINS=["https://frontend-rho-wheat-24.vercel.app"]
   LOG_LEVEL=INFO
   ```

5. Clicca **"Create Web Service"**

6. Attendi il deploy (~3-5 minuti)

7. **IMPORTANTE**: Una volta deployato, copia l'**URL del servizio**
   - Sarà tipo: `https://seriea-predictions-api.onrender.com`
   - Lo useremo dopo per connettere il frontend

---

## 🔧 Step 5: Inizializza Database (1 min)

Una volta che il backend è running (status "Live"):

1. Nel servizio `seriea-predictions-api`, clicca sulla tab **"Shell"**

2. Esegui questi comandi uno alla volta:

   ```bash
   # 1. Esegui migrations
   alembic upgrade head

   # 2. Seed team Serie A
   python -m app.scripts.seed_teams
   ```

3. Verifica che non ci siano errori (dovrebbe dire "Success" o completare senza errori)

---

## ⏰ Step 6: Deploy Celery Worker (2 min)

1. Clicca **"New +"** → **"Background Worker"**

2. Connetti lo **stesso repository** di prima

3. Configura:
   - **Name**: `seriea-predictions-worker`
   - **Region**: **Frankfurt**
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: **Docker**
   - **Docker Command**:
     ```bash
     celery -A app.tasks.celery_app worker --loglevel=info
     ```
   - **Plan**: **Free**

4. **Environment Variables**: Copia le **STESSE** variabili dello Step 4
   - Puoi copiarle da `seriea-predictions-api` → Settings → Environment Variables

5. Clicca **"Create Background Worker"**

---

## 📅 Step 7: Deploy Celery Beat (2 min)

1. Clicca **"New +"** → **"Background Worker"**

2. Connetti lo stesso repository

3. Configura:
   - **Name**: `seriea-predictions-beat`
   - **Region**: **Frankfurt**
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: **Docker**
   - **Docker Command**:
     ```bash
     celery -A app.tasks.celery_app beat --loglevel=info
     ```
   - **Plan**: **Free**

4. **Environment Variables**: Copia di nuovo le stesse variabili

5. Clicca **"Create Background Worker"**

---

## 🔗 Step 8: Connetti Frontend (2 min)

Ora che il backend è live, connetti il frontend Vercel:

1. Vai su [vercel.com](https://vercel.com)

2. Apri il progetto **frontend**

3. Vai su **Settings** → **Environment Variables**

4. Aggiungi una nuova variabile:
   - **Key**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://seriea-predictions-api.onrender.com/api/v1`
     (Sostituisci con l'URL effettivo del tuo backend da Step 4)
   - **Environment**: **Production**, **Preview**, **Development** (tutti e 3)

5. Clicca **"Save"**

6. Vai alla tab **"Deployments"**

7. Clicca sui **tre puntini** dell'ultimo deployment → **"Redeploy"**

---

## ✅ Step 9: Test Completo (1 min)

### 9.1 Test Backend

Apri nel browser:
```
https://seriea-predictions-api.onrender.com/api/v1/health
```

Dovresti vedere:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-28T...",
  "version": "1.0.0",
  "services": {
    "database": "connected",
    "redis": "connected"
  }
}
```

### 9.2 Test API Docs

```
https://seriea-predictions-api.onrender.com/docs
```

Dovresti vedere la documentazione Swagger interattiva.

### 9.3 Test Frontend

Apri:
```
https://frontend-rho-wheat-24.vercel.app
```

Se tutto funziona, dovresti vedere:
- ✅ Homepage carica
- ✅ Nessun errore nella console
- ⚠️ Potrebbe ancora dire "Nessuna partita trovata" (normale, devi sincronizzare i dati)

---

## 🔄 Step 10: Prima Sincronizzazione Dati (Opzionale)

Per popolare il database con partite reali:

1. Nel backend shell su Render:
   ```bash
   python -c "from app.tasks.sync_tasks import sync_season_fixtures; sync_season_fixtures('2025')"
   ```

2. Attendi qualche minuto

3. Ricarica il frontend - dovresti vedere le partite!

---

## 📊 Monitoring & Logs

### Backend Logs
Render Dashboard → `seriea-predictions-api` → **Logs**

### Celery Logs
Render Dashboard → `seriea-predictions-worker` → **Logs**

### Frontend Logs
Vercel Dashboard → `frontend` → **Logs**

---

## 💰 Costi Totali (Free Tier)

- ✅ PostgreSQL Free: 1GB storage
- ✅ Redis Free: 25MB
- ✅ Backend Free: Con sleep dopo 15min inattività
- ✅ 2x Workers Free: 1 worker gratis ciascuno
- ✅ Frontend Vercel: Gratis

**TOTALE: $0/mese**

**Limitazioni Free Tier**:
- Servizi "dormono" dopo 15 min di inattività
- Prima richiesta dopo sleep: ~30 secondi di cold start
- Sufficiente per MVP e testing

**Upgrade a Paid (~$25/mese)**:
- Backend Starter $7: No sleep, sempre attivo
- PostgreSQL Starter $7: 10GB storage
- Redis Starter $10: 100MB

---

## 🐛 Troubleshooting

### Backend non si avvia

**Controlla logs**: Render → `seriea-predictions-api` → Logs

**Errori comuni**:
- `DATABASE_URL` non corretto → Verifica Internal URL, non External
- `REDIS_URL` non corretto → Deve essere Internal URL
- Build fallita → Verifica che `backend/Dockerfile` esista

### CORS Error

Se vedi errori CORS nella console del frontend:

1. Backend → Settings → Environment Variables
2. Verifica `CORS_ORIGINS` include l'URL Vercel esatto:
   ```
   CORS_ORIGINS=["https://frontend-rho-wheat-24.vercel.app"]
   ```
3. Redeploy backend

### Database Connection Error

```bash
# Nel backend shell
python -c "from app.db.engine import engine; print(engine.url)"
```

Deve mostrare l'URL PostgreSQL corretto.

---

## 🎯 Checklist Finale

- [ ] PostgreSQL deployato e URL copiato
- [ ] Redis deployato e URL copiato
- [ ] Backend API deployato e running
- [ ] Migrations eseguite (`alembic upgrade head`)
- [ ] Team seedati (`python -m app.scripts.seed_teams`)
- [ ] Celery Worker running
- [ ] Celery Beat running
- [ ] `NEXT_PUBLIC_API_URL` configurato su Vercel
- [ ] `CORS_ORIGINS` configurato nel backend
- [ ] Frontend redeployato
- [ ] `/health` endpoint risponde 200
- [ ] `/docs` mostra Swagger UI
- [ ] Frontend mostra homepage senza errori

---

## 🚀 Deploy Completato!

Il tuo stack è ora completamente deployato:

- **Frontend**: https://frontend-rho-wheat-24.vercel.app
- **Backend API**: https://seriea-predictions-api.onrender.com
- **API Docs**: https://seriea-predictions-api.onrender.com/docs
- **Database**: PostgreSQL su Render
- **Cache**: Redis su Render
- **Workers**: Celery su Render

**Prossimi passi**:
1. Monitora i logs per errori
2. Sincronizza dati partite (Step 10)
3. Testa tutte le funzionalità
4. Aggiungi dominio custom (opzionale)

Congratulazioni! 🎉

