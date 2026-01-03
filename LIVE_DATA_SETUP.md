# 🔴 LIVE DATA SETUP - Guida Completa

## Setup Dati in Tempo Reale con Football-Data.org (GRATUITO!)

Questa guida ti permette di avere **dati automatici e aggiornati** ogni 2-5 minuti, completamente GRATIS.

---

## 📋 PANORAMICA SOLUZIONE

### ✅ Cosa Ottieni:

- **Aggiornamenti automatici** ogni 2-5 minuti
- **Partite live** con punteggi in tempo reale
- **Classifica aggiornata** automaticamente dopo ogni giornata
- **Zero manutenzione manuale** richiesta
- **100% GRATUITO** (14,400 richieste/giorno)
- **Affidabile e professionale**

### 🏗️ Architettura:

```
Football-Data.org API (Gratis)
         ↓
Backend (Render) - Script Automatico
         ↓
Database PostgreSQL
         ↓
Frontend (Vercel) - Aggiornamento Automatico
```

---

## 🚀 STEP 1: Registrazione su Football-Data.org (5 minuti)

### 1.1 Crea Account

1. Vai su: **https://www.football-data.org/client/register**
2. Compila il form:
   - Nome
   - Email
   - Password
   - Accetta i termini
3. Clicca **"Register"**

### 1.2 Ottieni API Key

1. Dopo la registrazione, **controlla la tua email**
2. Troverai un messaggio con la tua **API Key**
3. Formato: `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` (32 caratteri)
4. **COPIA questa chiave** - ti servirà dopo!

### 1.3 Verifica Limite

- **Free Tier**: 10 richieste/minuto = 14,400/giorno
- **Serie A**: Inclusa GRATIS forever
- **No carta di credito richiesta**

✅ **Hai completato lo Step 1!**

---

## 🔧 STEP 2: Configurazione Backend (10 minuti)

### 2.1 File .env Locale (per test)

Crea/modifica il file `.env` nella cartella `backend/`:

```bash
# Football-Data.org API (OBBLIGATORIO)
FOOTBALL_DATA_KEY=la_tua_chiave_api_qui

# Abilita aggiornamenti live
ENABLE_LIVE_UPDATES=true

# Altre variabili (opzionali)
ENVIRONMENT=production
DATABASE_URL=your_postgres_url_here
```

### 2.2 Configurazione Render.com (PRODUZIONE)

#### A. Vai su Render Dashboard

1. Apri: **https://dashboard.render.com**
2. Seleziona il tuo servizio backend
3. Vai in **"Environment"** nel menu laterale

#### B. Aggiungi Variabili d'Ambiente

Clicca **"Add Environment Variable"** e aggiungi:

| Key | Value |
|-----|-------|
| `FOOTBALL_DATA_KEY` | `la_tua_chiave_api_qui` |
| `ENABLE_LIVE_UPDATES` | `true` |

Clicca **"Save Changes"**

⚠️ **IMPORTANTE**: Render farà automaticamente il re-deploy dopo aver salvato le variabili.

### 2.3 Verifica Configurazione

Dopo il deploy, verifica che funzioni:

```bash
curl https://seriea-predictions-api.onrender.com/api/v1/health
```

Dovresti vedere:
```json
{
  "status": "healthy",
  "service": "seriea-predictions-api",
  "version": "1.0.0"
}
```

✅ **Hai completato lo Step 2!**

---

## ⏰ STEP 3: Configurazione Aggiornamenti Automatici (15 minuti)

### 3.1 Render Cron Jobs (Raccomandato - Gratis)

Render offre **Cron Jobs gratuiti** perfetti per aggiornamenti automatici!

#### A. Crea Nuovo Cron Job

1. Vai su **https://dashboard.render.com**
2. Clicca **"New +"** → **"Cron Job"**
3. Connetti il repository GitHub

#### B. Configura il Cron Job

**Nome**: `seriea-live-sync`

**Comando**:
```bash
python -m app.scripts.sync_live_data
```

**Schedule**: Scegli uno di questi:

| Frequenza | Cron Expression | Descrizione |
|-----------|-----------------|-------------|
| Ogni 2 minuti | `*/2 * * * *` | Massima reattività |
| Ogni 5 minuti | `*/5 * * * *` | Bilanciato (raccomandato) |
| Ogni 10 minuti | `*/10 * * * *` | Conservativo |

**Environment Variables**:
- Eredita automaticamente dal servizio backend
- Oppure aggiungi `FOOTBALL_DATA_KEY` manualmente

#### C. Crea e Attiva

Clicca **"Create Cron Job"** - Render inizierà a eseguirlo automaticamente!

### 3.2 Alternativa: Script Shell Manuale

Se preferisci controllo manuale, puoi usare questo script:

```bash
#!/bin/bash
# sync-data.sh

cd /path/to/backend
source venv/bin/activate
python -m app.scripts.sync_live_data
```

Esegui manualmente:
```bash
bash sync-data.sh
```

✅ **Hai completato lo Step 3!**

---

## 🧪 STEP 4: Test Sistema Live (5 minuti)

### 4.1 Test Manuale Sync Script

Esegui localmente per testare:

```bash
cd backend
python -m app.scripts.sync_live_data
```

Output atteso:
```
============================================================
Starting live data synchronization
Time: 2026-01-03 15:30:00
============================================================
📡 Syncing live matches...
Found 2 live matches
✅ Updated 2 live matches
📅 Syncing today's fixtures...
Found 8 recent fixtures
✅ Updated 8 fixtures
📊 Checking if standings update needed...
✅ Standings updated
✅ Live data synchronization completed successfully!
```

### 4.2 Verifica API Endpoints

**Test 1: Partite Recenti**
```bash
curl "https://seriea-predictions-api.onrender.com/api/v1/fixtures/serie-a/2025-2026?limit=5"
```

**Test 2: Classifica**
```bash
curl "https://seriea-predictions-api.onrender.com/api/v1/standings/serie-a/2025-2026"
```

### 4.3 Verifica Frontend

1. Apri: **https://pronostici-serie-a.vercel.app**
2. Controlla che vedi partite aggiornate
3. Verifica punteggi live (se ci sono partite in corso)

✅ **Hai completato lo Step 4!**

---

## 📊 STEP 5: Monitoraggio e Manutenzione

### 5.1 Dashboard Render

Monitora i Cron Jobs su:
**https://dashboard.render.com** → Cron Jobs → `seriea-live-sync`

Vedrai:
- ✅ Execuzioni riuscite
- ❌ Eventuali errori
- 📊 Log completi

### 5.2 Log del Sistema

Per vedere i log in tempo reale:

```bash
# Su Render
render logs --tail --service your-backend-service
```

### 5.3 Rate Limiting

Football-Data.org free tier:
- **10 richieste/minuto**
- **14,400 richieste/giorno**

Con sync ogni 5 minuti:
- **~12 richieste/ora** = **288 richieste/giorno**
- **Uso: ~2% del limite**

✅ Hai margine enorme!

### 5.4 Monitoraggio Header

Ogni risposta include:
```
X-Requests-Available-Minute: 8
```

Se vedi `0`, stai eccedendo il rate limit.

---

## ⚙️ CONFIGURAZIONI AVANZATE (Opzionale)

### Personalizzare Frequenza Sync

Modifica `backend/app/scripts/sync_live_data.py`:

```python
# Sync solo durante orari partite
if 12 <= datetime.now().hour <= 23:
    await synchronizer.sync_live_matches()
```

### Aggiungere Notifiche

Invia notifica quando finiscono partite:

```python
# In sync_live_data.py
if fixture.status == FixtureStatus.FINISHED:
    await send_notification(f"{home_team} {home_score}-{away_score} {away_team}")
```

### Cache Redis (Opzionale)

Per ridurre chiamate API, aggiungi cache:

```python
@cache(expire=120)  # 2 minuti
async def get_fixtures():
    ...
```

---

## ❓ TROUBLESHOOTING

### Problema 1: "No API keys configured"

**Soluzione:**
1. Verifica che `FOOTBALL_DATA_KEY` sia settata su Render
2. Ri-deploya il servizio
3. Controlla che la chiave sia corretta (32 caratteri)

### Problema 2: "Rate limit exceeded"

**Soluzione:**
1. Riduci frequenza Cron Job (es. da 2 min a 5 min)
2. Verifica di non avere script duplicati attivi
3. Controlla dashboard Football-Data.org

### Problema 3: "Failed to sync fixtures"

**Soluzione:**
1. Controlla log Render per errore specifico
2. Verifica connessione database
3. Testa manualmente lo script

### Problema 4: "Teams not found for external IDs"

**Soluzione:**
1. Esegui seed teams: `python -m app.scripts.seed_teams`
2. Verifica mapping team IDs in `football_data.py`
3. Aggiorna external_id nelle squadre

---

## 📈 RISULTATI ATTESI

Dopo il setup completo:

### ✅ Aggiornamenti Automatici

- **Ogni 2-5 minuti**: Partite live e risultati
- **Dopo ogni giornata**: Classifica aggiornata
- **Zero intervento manuale**: Tutto automatico!

### ✅ Dati Affidabili

- **Fonte ufficiale**: Football-Data.org
- **Serie A garantita gratis**: Forever
- **Delay minimo**: 2-3 minuti max

### ✅ Performance

- **14,400 richieste/giorno**: Ampio margine
- **< 2% limite usato**: Con sync ogni 5 min
- **Scalabile**: Fino a 10,000+ utenti/giorno

---

## 💰 COSTI

### Soluzione Gratuita (Questa Guida)

| Servizio | Costo | Note |
|----------|-------|------|
| Football-Data.org | **$0/mese** | Free tier forever |
| Render Backend | **$0/mese** | Free tier 750h/mese |
| Render Cron Jobs | **$0/mese** | Inclusi nel free tier |
| Vercel Frontend | **$0/mese** | Free tier |
| **TOTALE** | **$0/mese** | 100% Gratis! |

### Upgrade Opzionale (Futuro)

Se in futuro serve più potenza:

| Piano | Costo | Benefici |
|-------|-------|----------|
| Render Pro | $7/mese | Servizio sempre attivo |
| API-Football | $10/mese | Aggiornamenti ogni 15 sec |

---

## 🎯 CHECKLIST FINALE

Prima di considerare il setup completo, verifica:

- [ ] Account Football-Data.org creato
- [ ] API Key ricevuta via email
- [ ] `FOOTBALL_DATA_KEY` configurata su Render
- [ ] `ENABLE_LIVE_UPDATES=true` settato
- [ ] Render Cron Job creato e attivo
- [ ] Test sync script eseguito con successo
- [ ] API endpoints rispondono correttamente
- [ ] Frontend mostra dati aggiornati
- [ ] Monitoraggio Render configurato
- [ ] Log verificati senza errori

---

## 📞 SUPPORTO

### Documentazione Ufficiale

- **Football-Data.org Docs**: https://www.football-data.org/documentation/api
- **Render Cron Jobs**: https://render.com/docs/cronjobs
- **API Reference**: https://docs.football-data.org/

### In Caso di Problemi

1. Controlla i log su Render Dashboard
2. Verifica variabili d'ambiente
3. Testa lo script manualmente in locale
4. Controlla il rate limiting header

---

## 🎉 CONGRATULAZIONI!

Hai configurato un sistema professionale di dati live completamente automatico e gratuito!

**Prossimi Step:**
1. Monitora i log per i primi giorni
2. Verifica accuratezza dati
3. Considera upgrade futuro se necessario

**La tua app ora è LIVE e professionale!** 🚀

---

_Guida creata il 3 Gennaio 2026_
_Versione: 1.0_
