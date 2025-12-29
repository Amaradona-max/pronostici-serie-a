# ⚡ Quick Start - Sviluppo Locale

Guida rapida per avviare l'app sul tuo Mac in 5 minuti.

---

## 🚀 Comandi Rapidi

### Avvio Completo (2 Terminal)

**Terminal 1 - Backend:**
```bash
cd "/Users/prova/Desktop/Pronostici Master Calcio/backend"
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd "/Users/prova/Desktop/Pronostici Master Calcio/frontend"
npm run dev
```

**Browser:**
- Apri http://localhost:3000

---

## 📝 Modificare e Pubblicare

### 1. Modifica i File
- Frontend: `frontend/app/*/page.tsx`
- Dati: `backend/app/api/endpoints/standings.py`
- Calendario: `backend/app/api/endpoints/admin.py`

### 2. Testa in Locale
- Frontend: http://localhost:3000
- Backend: http://localhost:8000/docs

### 3. Reset Database Locale (se hai modificato i dati)
```bash
curl -X POST http://localhost:8000/api/v1/admin/reset-database
```

### 4. Pubblica Online
```bash
git add .
git commit -m "Descrizione modifiche"
git push origin main
```

### 5. Reset Database Online (dopo 5 minuti dal push)
```bash
curl -X POST https://seriea-predictions-api.onrender.com/api/v1/admin/reset-database
```

---

## 🔗 Link Utili

### Per Te (Sviluppo)
- **Locale Frontend**: http://localhost:3000
- **Locale Backend**: http://localhost:8000
- **Locale API Docs**: http://localhost:8000/docs

### Per Condividere
- **App Online**: https://pronostici-serie-a.vercel.app
- **Classifica**: https://pronostici-serie-a.vercel.app/classifica
- **Marcatori**: https://pronostici-serie-a.vercel.app/marcatori
- **Cartellini**: https://pronostici-serie-a.vercel.app/cartellini

---

## 📂 File Principali da Modificare

### Dati (Backend)
```
backend/app/api/endpoints/standings.py
  Linea 83:  real_standings_data    → Classifica
  Linea 146: real_scorers_data      → Marcatori
  Linea 205: real_cards_by_team     → Cartellini

backend/app/api/endpoints/admin.py
  Linea 125: giornata_18_fixtures   → Calendario partite
```

### Layout (Frontend)
```
frontend/app/page.tsx                → Home page
frontend/app/classifica/page.tsx     → Classifica
frontend/app/marcatori/page.tsx      → Marcatori
frontend/app/cartellini/page.tsx     → Cartellini
frontend/components/layout/Header.tsx → Menu navigazione
```

---

## 🛠️ Prima Installazione

Se è la prima volta che avvii l'app:

### Backend (solo una volta)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend (solo una volta)
```bash
cd frontend
npm install
```

---

## ⚠️ Problemi Comuni

### Backend non parte
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend mostra errori
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Modifiche non online
```bash
# Verifica commit
git status

# Se ci sono file non committati
git add .
git commit -m "Aggiornamento"
git push origin main

# Aspetta 5 minuti, poi reset database
curl -X POST https://seriea-predictions-api.onrender.com/api/v1/admin/reset-database
```

---

## 📱 Fermare i Server

In entrambi i Terminal, premi: **CTRL + C**

---

**Per la guida completa, vedi:** `GUIDA_SVILUPPO.md`
