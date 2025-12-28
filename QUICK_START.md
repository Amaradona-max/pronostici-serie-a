# Quick Start Guide

Guida rapida per avviare il progetto Serie A Predictions in 5 minuti.

## Setup Rapido

### 1. Prerequisiti

```bash
# Verifica Docker installato
docker --version
docker-compose --version

# Se mancano, installa da: https://docs.docker.com/get-docker/
```

### 2. Clone e Configurazione

```bash
# Clone repository
cd ~/Desktop
git clone <repository-url> "Pronostici Msterr Calcio"
cd "Pronostici Msterr Calcio"

# Crea file .env
cp .env.example .env
```

### 3. Configura API Key

1. Registrati su [RapidAPI](https://rapidapi.com/api-sports/api/api-football)
2. Sottoscrivi piano gratuito di API-Football
3. Copia API key
4. Apri `.env` e incolla:

```bash
API_FOOTBALL_KEY=your_key_here
SECRET_KEY=$(openssl rand -hex 32)
```

### 4. Avvia Progetto

```bash
# Avvia tutti i servizi
docker-compose up -d

# Attendi ~30 secondi per il primo avvio
```

### 5. Inizializza Database

```bash
# Esegui migrations
docker-compose exec backend alembic upgrade head

# Popola squadre Serie A
docker-compose exec backend python -m app.scripts.seed_teams

# Sincronizza fixtures (OPZIONALE - richiede API key valida)
# docker-compose exec backend python -m app.tasks.sync_tasks sync_season_fixtures 2025-2026
```

### 6. Verifica Installazione

```bash
# Backend API
curl http://localhost:8000/api/v1/health
# Risposta attesa: {"status":"healthy"}

# Frontend
open http://localhost:3000

# API Docs (Swagger)
open http://localhost:8000/docs
```

## Comandi Utili

```bash
# Visualizza logs
make logs

# Stop servizi
make down

# Restart completo
docker-compose down && docker-compose up -d

# Shell backend (per debug)
make shell

# Accedi a PostgreSQL
make shell-db
```

## Struttura Progetto

```
Pronostici Msterr Calcio/
├── backend/          # FastAPI + Python
│   ├── app/
│   │   ├── api/      # Endpoints REST
│   │   ├── db/       # Models e migrations
│   │   ├── ml/       # Dixon-Coles model
│   │   └── tasks/    # Celery tasks
├── frontend/         # Next.js + React
│   ├── app/          # Pages
│   ├── components/   # UI components
│   └── lib/          # Utilities
└── docker-compose.yml
```

## Prossimi Passi

1. **Esplora API**: http://localhost:8000/docs
2. **Vedi Frontend**: http://localhost:3000
3. **Consulta README**: `README.md` per dettagli completi
4. **Deployment**: `DEPLOYMENT.md` per messa in produzione

## Troubleshooting

### Porta 8000 già in uso

```bash
# Cambia porta in docker-compose.yml
ports:
  - "8001:8000"  # Usa 8001 invece di 8000
```

### Database connection error

```bash
# Restart PostgreSQL
docker-compose restart postgres

# Verifica container running
docker-compose ps
```

### Frontend non carica

```bash
# Rebuil frontend
docker-compose build frontend
docker-compose up -d frontend

# Check logs
docker-compose logs frontend
```

## Support

- **Documentazione completa**: `README.md`
- **Guide deployment**: `DEPLOYMENT.md`
- **Issues**: Crea issue su GitHub se problemi

---

**Tempo totale setup**: ~5 minuti ⚡
