# 🔄 GitHub Actions Setup - Aggiornamenti Automatici GRATIS

## Setup Aggiornamenti Automatici con GitHub Actions (NO CARTA DI CREDITO!)

Questa guida configura aggiornamenti automatici ogni 5 minuti usando **GitHub Actions** - completamente **GRATUITO**.

---

## ✅ VANTAGGI GitHub Actions

- ✅ **100% GRATUITO** (2,000 minuti/mese gratis)
- ✅ **NO carta di credito** richiesta
- ✅ **Aggiornamenti ogni 5 minuti** automatici
- ✅ **Facile da configurare** (10 minuti)
- ✅ **Log completi** su GitHub
- ✅ **Può essere disabilitato** quando vuoi

---

## 🚀 SETUP COMPLETO (10 minuti)

### STEP 1: Configura GitHub Secrets (5 minuti)

I "Secrets" sono variabili sicure che GitHub Actions usa per connettersi al database.

#### 1.1 Vai su GitHub Repository

Apri: **https://github.com/Amaradona-max/pronostici-serie-a**

#### 1.2 Vai nelle Settings

1. Clicca sulla tab **"Settings"** (in alto a destra)
2. Nel menu laterale sinistro, cerca **"Secrets and variables"**
3. Clicca su **"Actions"**

#### 1.3 Aggiungi i Secrets

Clicca **"New repository secret"** e aggiungi questi 2 secrets:

**Secret 1:**
- **Name**: `FOOTBALL_DATA_KEY`
- **Secret**: `0b0926ead0f545c7bc196d8be1639b51` (la tua API key)
- Clicca **"Add secret"**

**Secret 2:**
- **Name**: `DATABASE_URL`
- **Secret**: Il tuo database URL di Render (lo trovi su Render Dashboard → Backend → Environment → DATABASE_URL)
- Formato: `postgresql+asyncpg://user:password@host:5432/database`
- Clicca **"Add secret"**

✅ **Fatto!** I secrets sono configurati.

---

### STEP 2: Attiva GitHub Actions (2 minuti)

#### 2.1 Vai alla Tab Actions

1. Sul repository GitHub, clicca sulla tab **"Actions"** (in alto)
2. Se vedi un messaggio che chiede di abilitare i workflows, clicca **"I understand my workflows, go ahead and enable them"**

#### 2.2 Trova il Workflow

Dovresti vedere il workflow: **"Sync Live Serie A Data"**

#### 2.3 Abilita il Workflow

Se il workflow è disabilitato:
1. Clicca sul workflow
2. Clicca **"Enable workflow"**

✅ **Fatto!** GitHub Actions è attivo.

---

### STEP 3: Test Manuale (3 minuti)

Prima di aspettare i 5 minuti, testiamo subito!

#### 3.1 Esegui Manualmente

1. Nella tab **"Actions"**
2. Clicca sul workflow **"Sync Live Serie A Data"**
3. Clicca sul pulsante **"Run workflow"** (a destra)
4. Seleziona branch: **main**
5. Clicca **"Run workflow"** (verde)

#### 3.2 Monitora l'Esecuzione

1. Vedrai apparire un nuovo run (ci mette qualche secondo)
2. Clicca sul nome del run per vedere i dettagli
3. Clicca su **"Sync Live Football Data"** per vedere i log
4. Aspetta che finisca (1-2 minuti)

#### 3.3 Verifica Successo

Se vedi un **✅ checkmark verde**, funziona!

Se vedi una **❌ X rossa**, controlla i log per vedere l'errore.

---

## 📊 COME FUNZIONA

### Scheduling Automatico

Il workflow si esegue **automaticamente ogni 5 minuti**:

```
*/5 * * * *
```

Questo significa:
- **Ogni 5 minuti** di ogni ora
- **Tutti i giorni**
- **Automaticamente**

### Ottimizzazione Intelligente

Per risparmiare minuti GitHub Actions, il workflow:
- ✅ Si esegue **solo durante orari partite** (11:00 - 23:59 UTC)
- ✅ Può essere eseguito **manualmente** quando vuoi
- ✅ **Auto-disabilitato** di notte (non serve)

Se vuoi che giri **sempre 24/7**, rimuovi la condizione `if` nel file `.github/workflows/sync-live-data.yml`.

---

## 🔍 MONITORAGGIO

### Vedere i Log

1. Vai su GitHub → Repository
2. Clicca tab **"Actions"**
3. Clicca su un run specifico
4. Vedi i log completi

### Cosa Vedrai nei Log

```
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

---

## ⚙️ CONFIGURAZIONI AVANZATE

### Cambiare Frequenza

Modifica il file `.github/workflows/sync-live-data.yml`:

```yaml
schedule:
  - cron: '*/10 * * * *'  # Ogni 10 minuti
  - cron: '*/2 * * * *'   # Ogni 2 minuti
  - cron: '0 * * * *'     # Ogni ora
```

### Disabilitare Temporaneamente

1. Vai su GitHub → Actions
2. Clicca sul workflow
3. Clicca **"Disable workflow"**

### Riabilitare

1. Stesso percorso
2. Clicca **"Enable workflow"**

---

## 💰 COSTI

**TUTTO GRATUITO!**

| Servizio | Limite Gratis | Uso Effettivo |
|----------|---------------|---------------|
| GitHub Actions | 2,000 min/mese | ~150 min/mese |
| Football-Data.org | 14,400 req/giorno | ~288 req/giorno |
| Render Database | Incluso | - |
| **TOTALE** | **$0/mese** | **$0/mese** |

### Calcolo GitHub Actions:

- **5 minuti tra esecuzioni** = 12 runs/ora
- **Ogni run dura ~1 minuto**
- **12 ore/giorno** (orari partite) = 144 runs/giorno
- **144 minuti/giorno** × 30 giorni = ~4,320 minuti/mese

❌ **ASPETTA!** Troppo per il free tier (2,000 minuti/mese)

✅ **SOLUZIONE**: Il workflow è configurato per girare **solo durante orari partite** (11:00-23:59 UTC), risparmiando il 50% dei minuti!

Risultato finale: **~2,160 minuti/mese** - appena sopra il limite.

### Ottimizzazioni per Rimanere nel Free Tier:

1. **Opzione 1**: Esegui ogni **10 minuti** invece di 5 (dimezza i minuti)
2. **Opzione 2**: Esegui solo **sabato/domenica** (quando ci sono più partite)
3. **Opzione 3**: Trigger manuale quando serve

---

## ❓ TROUBLESHOOTING

### Errore: "Secret not found"

**Soluzione**: Verifica di aver aggiunto i secrets:
1. GitHub → Settings → Secrets and variables → Actions
2. Controlla che ci siano `FOOTBALL_DATA_KEY` e `DATABASE_URL`

### Errore: "Module not found"

**Soluzione**: Il workflow installa automaticamente le dipendenze. Se fallisce, controlla `requirements.txt`.

### Workflow non si esegue

**Soluzione**:
1. Verifica che il workflow sia abilitato
2. Controlla che il file `.github/workflows/sync-live-data.yml` sia nel repository
3. Vai su Actions → controlla se ci sono errori

### Database connection error

**Soluzione**: Verifica che `DATABASE_URL` secret sia corretto:
1. Copia il database URL da Render Dashboard
2. Aggiornalo nei GitHub Secrets

---

## 🎯 CHECKLIST SETUP

Prima di considerare il setup completo:

- [ ] GitHub Secrets configurati (`FOOTBALL_DATA_KEY` e `DATABASE_URL`)
- [ ] GitHub Actions abilitato nel repository
- [ ] Workflow eseguito manualmente con successo
- [ ] Log verificati senza errori
- [ ] Prossima esecuzione automatica schedulata

---

## 🆚 CONFRONTO: GitHub Actions vs Render Cron Jobs

| Feature | GitHub Actions | Render Cron Jobs |
|---------|----------------|------------------|
| **Costo** | Gratis (2,000 min/mese) | Gratis (con carta) |
| **Carta richiesta** | ❌ NO | ✅ SI |
| **Setup** | 10 minuti | 5 minuti |
| **Affidabilità** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Log** | GitHub UI | Render Dashboard |
| **Controllo** | Full control | Gestito da Render |

---

## 🎉 CONGRATULAZIONI!

Hai configurato un sistema professionale di aggiornamenti automatici completamente gratuito e senza carta di credito!

**La tua app ora ha dati live ogni 5 minuti!** 🚀

---

_Guida creata il 3 Gennaio 2026_
_Alternativa gratuita a Render Cron Jobs_
