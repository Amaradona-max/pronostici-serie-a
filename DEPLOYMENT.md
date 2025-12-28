# Deployment Guide

Guida completa per il deploy del progetto Serie A Predictions.

## Prerequisiti

- Docker & Docker Compose
- Account API-Football (RapidAPI)
- Account GitHub (per CI/CD)
- VPS o cloud provider (Railway, Render, AWS, etc.)

## Setup Locale

### 1. Clone e Configurazione

```bash
git clone <repository-url>
cd seriea-predictions

# Crea .env da template
cp .env.example .env

# Modifica .env con le tue credenziali
nano .env
```

### 2. Genera Secret Key

```bash
openssl rand -hex 32
# Copia l'output in .env come SECRET_KEY
```

### 3. Avvia Stack

```bash
# Build e avvio
docker-compose up -d

# Verifica logs
docker-compose logs -f
```

### 4. Inizializza Database

```bash
# Esegui migrations
docker-compose exec backend alembic upgrade head

# Seed teams Serie A
docker-compose exec backend python -m app.scripts.seed_teams

# Sync fixtures iniziale
docker-compose exec backend celery -A app.tasks.celery_app call app.tasks.sync_tasks.sync_season_fixtures --args='["2025-2026"]'
```

### 5. Verifica

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Frontend
open http://localhost:3000
```

## Deploy Produzione

### Opzione A: Render (Consigliato per Semplicità)

Render offre un ottimo piano gratuito e setup semplice per MVP.

#### Step 1: Crea Account e Progetto

1. Vai su [render.com](https://render.com) e crea un account
2. Collegati con GitHub
3. Fai push del tuo codice su un repository GitHub

#### Step 2: Deploy PostgreSQL Database

1. Nel dashboard Render, clicca **"New +"** → **"PostgreSQL"**
2. Configura:
   - **Name**: `seriea-predictions-db`
   - **Database**: `seriea_predictions`
   - **User**: `seriea`
   - **Region**: Frankfurt (più vicino all'Italia)
   - **Plan**: Free (per MVP) o Starter ($7/mese)
3. Clicca **"Create Database"**
4. Copia l'**Internal Database URL** (formato: `postgresql://user:pass@host/db`)

#### Step 3: Deploy Redis

1. Clicca **"New +"** → **"Redis"**
2. Configura:
   - **Name**: `seriea-predictions-redis`
   - **Region**: Frankfurt
   - **Plan**: Free (per testing) o Starter ($10/mese)
   - **Maxmemory Policy**: `allkeys-lru`
3. Clicca **"Create Redis"**
4. Copia l'**Internal Redis URL** (formato: `redis://host:port`)

#### Step 4: Deploy Backend API

1. Clicca **"New +"** → **"Web Service"**
2. Connetti il tuo repository GitHub
3. Configura:
   - **Name**: `seriea-predictions-api`
   - **Region**: Frankfurt
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Docker`
   - **Docker Command**: (lascia vuoto, usa il Dockerfile)
   - **Plan**: Free (con limitazioni) o Starter ($7/mese)

4. **Environment Variables** - Aggiungi le seguenti:
   ```
   DATABASE_URL=<Internal Database URL da Step 2>
   REDIS_URL=<Internal Redis URL da Step 3>
   CELERY_BROKER_URL=<Internal Redis URL da Step 3>
   CELERY_RESULT_BACKEND=<Internal Redis URL da Step 3>

   API_FOOTBALL_KEY=<La tua API key di RapidAPI>
   SECRET_KEY=<Genera con: openssl rand -hex 32>

   ENVIRONMENT=production
   CORS_ORIGINS=["https://your-frontend.onrender.com"]
   LOG_LEVEL=INFO
   ```

5. Clicca **"Create Web Service"**

#### Step 5: Deploy Celery Worker

1. Clicca **"New +"** → **"Background Worker"**
2. Connetti lo stesso repository
3. Configura:
   - **Name**: `seriea-predictions-worker`
   - **Region**: Frankfurt
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Docker`
   - **Docker Command**:
     ```bash
     celery -A app.tasks.celery_app worker --loglevel=info
     ```
   - **Plan**: Free o Starter ($7/mese)

4. **Environment Variables** - Copia le stesse del Backend (Step 4)

5. Clicca **"Create Background Worker"**

#### Step 6: Deploy Celery Beat (Scheduler)

1. Clicca **"New +"** → **"Background Worker"**
2. Connetti lo stesso repository
3. Configura:
   - **Name**: `seriea-predictions-beat`
   - **Region**: Frankfurt
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Docker`
   - **Docker Command**:
     ```bash
     celery -A app.tasks.celery_app beat --loglevel=info
     ```
   - **Plan**: Free o Starter ($7/mese)

4. **Environment Variables** - Copia le stesse del Backend

5. Clicca **"Create Background Worker"**

#### Step 7: Inizializza Database

Una volta che il backend è deployed e running:

1. Vai al servizio **`seriea-predictions-api`**
2. Apri la **Shell** (tab "Shell" nel menu)
3. Esegui le migrations:
   ```bash
   alembic upgrade head
   ```

4. Seed dei team Serie A:
   ```bash
   python -m app.scripts.seed_teams
   ```

5. Prima sincronizzazione fixtures (opzionale):
   ```bash
   python -c "from app.tasks.sync_tasks import sync_season_fixtures; sync_season_fixtures('2025-2026')"
   ```

#### Step 8: Deploy Frontend (Render Static Site)

**Opzione 1: Deploy su Render**

1. Clicca **"New +"** → **"Static Site"**
2. Connetti repository
3. Configura:
   - **Name**: `seriea-predictions-frontend`
   - **Branch**: `main`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `.next`

4. **Environment Variables**:
   ```
   NEXT_PUBLIC_API_URL=https://seriea-predictions-api.onrender.com/api/v1
   ```

5. Clicca **"Create Static Site"**

**Opzione 2: Deploy su Vercel (Raccomandato per Next.js)**

```bash
cd frontend
npm install -g vercel
vercel login
vercel --prod
```

Durante il setup, configura:
- **NEXT_PUBLIC_API_URL**: `https://seriea-predictions-api.onrender.com/api/v1`

#### Step 9: Verifica Deployment

1. **Health Check API**:
   ```bash
   curl https://seriea-predictions-api.onrender.com/api/v1/health
   ```

2. **API Docs**:
   ```
   https://seriea-predictions-api.onrender.com/docs
   ```

3. **Frontend**:
   ```
   https://seriea-predictions-frontend.onrender.com
   # oppure
   https://your-project.vercel.app
   ```

#### Step 10: Monitoring su Render

1. Nel dashboard di ogni servizio, monitora:
   - **Metrics**: CPU, RAM usage
   - **Logs**: Controlla errori
   - **Events**: Deploy history

2. Setup **Health Check Path** (opzionale):
   - Path: `/api/v1/health`
   - Expected Status: 200

#### Costi Render (Free Tier)

- ✅ PostgreSQL Free: 1GB storage
- ✅ Redis Free: 25MB
- ✅ Web Services Free: Con sleep dopo 15 minuti di inattività
- ✅ Background Workers Free: 1 worker gratis

**Limitazioni Free Tier**:
- I servizi free "dormono" dopo 15 minuti di inattività
- Prima richiesta dopo sleep: ~30 secondi di cold start
- 750 ore/mese di runtime (sufficiente per 1 servizio 24/7)

**Upgrade a Paid ($25/mese totale)**:
- PostgreSQL Starter: $7/mese
- Redis Starter: $10/mese
- Web Service: $7/mese (no sleep)
- Background Workers: Inclusi

#### Troubleshooting Render

**1. Build Fallisce**

```bash
# Verifica il Dockerfile locale
cd backend
docker build -t test .
docker run -p 8000:8000 test
```

**2. Database Connection Error**

- Verifica che `DATABASE_URL` sia l'**Internal** URL (non External)
- Formato corretto: `postgresql://user:pass@host.internal/db`

**3. Celery Non Esegue Task**

```bash
# Controlla logs del worker
# Nel dashboard Render → seriea-predictions-worker → Logs

# Verifica connessione Redis
# Assicurati che CELERY_BROKER_URL sia l'Internal Redis URL
```

**4. CORS Error dal Frontend**

- Aggiorna `CORS_ORIGINS` nel backend:
  ```
  CORS_ORIGINS=["https://your-frontend.onrender.com", "https://your-app.vercel.app"]
  ```

### Opzione B: Railway (Consigliato per MVP)

#### Backend

1. Crea nuovo progetto su Railway.app
2. Aggiungi PostgreSQL addon
3. Aggiungi Redis addon
4. Deploy backend:

```bash
# railway.toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "backend/Dockerfile"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
```

5. Configura environment variables:
   - `DATABASE_URL` (auto da PostgreSQL addon)
   - `REDIS_URL` (auto da Redis addon)
   - `API_FOOTBALL_KEY`
   - `SECRET_KEY`
   - `ENVIRONMENT=production`

6. Deploy Celery worker (servizio separato):

```bash
# worker railway.toml
[deploy]
startCommand = "celery -A app.tasks.celery_app worker --loglevel=info"
```

7. Deploy Celery beat:

```bash
# beat railway.toml
[deploy]
startCommand = "celery -A app.tasks.celery_app beat --loglevel=info"
```

#### Frontend

1. Deploy su Vercel:

```bash
cd frontend
vercel --prod
```

2. Configura environment variable:
   - `NEXT_PUBLIC_API_URL=https://your-backend.railway.app/api/v1`

### Opzione B: VPS (DigitalOcean, Hetzner)

#### Setup Server

```bash
# Connessione SSH
ssh root@your-server-ip

# Installa Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Installa Docker Compose
apt install docker-compose

# Clone repository
git clone <repository-url>
cd seriea-predictions
```

#### Configurazione Nginx (Reverse Proxy)

```nginx
# /etc/nginx/sites-available/seriea-predictions

server {
    server_name api.tuodominio.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

server {
    server_name tuodominio.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
    }
}
```

```bash
# Abilita configurazione
ln -s /etc/nginx/sites-available/seriea-predictions /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx

# Setup SSL con Let's Encrypt
apt install certbot python3-certbot-nginx
certbot --nginx -d tuodominio.com -d api.tuodominio.com
```

#### Avvio Produzione

```bash
# Crea .env
cp .env.example .env
nano .env  # Configura

# Build e avvio
docker-compose -f docker-compose.prod.yml up -d

# Migrations
docker-compose exec backend alembic upgrade head

# Seed data
docker-compose exec backend python -m app.scripts.seed_teams
```

## Monitoring & Maintenance

### Logs

```bash
# Backend logs
docker-compose logs -f backend

# Celery logs
docker-compose logs -f celery_worker

# Database logs
docker-compose logs -f postgres
```

### Backup Database

```bash
# Backup manuale
docker-compose exec postgres pg_dump -U seriea seriea_predictions > backup_$(date +%Y%m%d).sql

# Restore
docker-compose exec -T postgres psql -U seriea seriea_predictions < backup_20260115.sql
```

### Aggiornamento Codice

```bash
# Pull ultime modifiche
git pull origin main

# Rebuild containers
docker-compose build

# Restart con zero downtime
docker-compose up -d --no-deps --build backend

# Run migrations
docker-compose exec backend alembic upgrade head
```

## Scaling

### Horizontal Scaling (Kubernetes)

```yaml
# k8s/deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  replicas: 3  # Scale to 3 instances
  selector:
    matchLabels:
      app: backend
  template:
    spec:
      containers:
      - name: backend
        image: your-registry/seriea-backend:latest
        ports:
        - containerPort: 8000
```

### Database Read Replicas

Per carichi elevati, configurare PostgreSQL read replicas:

```python
# app/db/engine.py (modificato)

# Write connection
write_engine = create_async_engine(settings.DATABASE_URL)

# Read connections (replicas)
read_engine = create_async_engine(settings.DATABASE_READ_URL)
```

## Troubleshooting

### Backend non risponde

```bash
# Verifica container status
docker-compose ps

# Restart backend
docker-compose restart backend

# Check logs
docker-compose logs --tail=100 backend
```

### Celery task non eseguiti

```bash
# Verifica Celery worker
docker-compose logs celery_worker

# Restart worker
docker-compose restart celery_worker

# Verifica connessione Redis
docker-compose exec redis redis-cli ping
```

### Database connection error

```bash
# Verifica PostgreSQL
docker-compose exec postgres pg_isready

# Restart database
docker-compose restart postgres

# Check migrations status
docker-compose exec backend alembic current
```

## Sicurezza

### Checklist Produzione

- [ ] `ENVIRONMENT=production` in .env
- [ ] SECRET_KEY generato con `openssl rand -hex 32`
- [ ] CORS origins configurato solo per domini autorizzati
- [ ] HTTPS abilitato (certificato SSL)
- [ ] Database password complessa
- [ ] API keys in secret manager (non in codice)
- [ ] Rate limiting abilitato
- [ ] Backup automatici configurati
- [ ] Monitoring e alerting attivi (Sentry)

## Performance Optimization

### 1. Database Indexes

Già implementati negli script di migration. Verifica con:

```sql
SELECT * FROM pg_indexes WHERE tablename = 'fixtures';
```

### 2. Redis Caching

Configurato automaticamente. Per svuotare cache:

```bash
docker-compose exec redis redis-cli FLUSHALL
```

### 3. CDN per Static Assets

Configurare CloudFlare o simili per caching di:
- Frontend assets (JS, CSS)
- Team logos
- Static images

## Costi Stimati

### MVP (< 1000 utenti/giorno)

- **Railway**: $20/mese (Postgres + Redis + 2 services)
- **Vercel**: Gratis (hobby plan)
- **API-Football**: $30/mese (tier Pro)
- **Dominio**: $12/anno
- **TOTALE**: ~$50/mese

### Production (10k+ utenti/giorno)

- **AWS/GCP**: $200-500/mese
- **Database managed**: $50/mese
- **CDN**: $20/mese
- **Monitoring**: $30/mese
- **TOTALE**: ~$300-600/mese

## Support

Per problemi o domande:
- GitHub Issues: <repository-url>/issues
- Logs: Sempre controllare `docker-compose logs`
- Documentazione API: https://your-domain.com/docs
