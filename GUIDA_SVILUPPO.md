# 📘 Guida Sviluppo - Serie A Predictions

Guida semplice e completa per avviare e modificare l'applicazione dal tuo Mac.

---

## 🌐 Link Applicazione Online

**Condividi questi link con i tuoi amici:**

- **App Principale**: https://pronostici-serie-a.vercel.app
- **Classifica**: https://pronostici-serie-a.vercel.app/classifica
- **Marcatori**: https://pronostici-serie-a.vercel.app/marcatori
- **Cartellini**: https://pronostici-serie-a.vercel.app/cartellini

L'app è già online e funzionante! I tuoi amici possono accedere direttamente senza installare nulla.

---

## 🚀 Come Avviare l'App sul Tuo Mac

### Prerequisiti

Prima di iniziare, assicurati di avere installato:

1. **Homebrew** (se non ce l'hai):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Python 3.11+**:
   ```bash
   brew install python@3.11
   ```

3. **Node.js 18+**:
   ```bash
   brew install node
   ```

4. **Git** (dovrebbe essere già installato):
   ```bash
   git --version
   ```

---

## 📂 Passo 1: Aprire il Progetto

1. Apri **Terminal** (puoi trovarlo in Applicazioni > Utility > Terminal)

2. Vai nella cartella del progetto:
   ```bash
   cd "/Users/prova/Desktop/Pronostici Master Calcio"
   ```

3. Verifica di essere nella cartella giusta:
   ```bash
   pwd
   # Dovrebbe mostrare: /Users/prova/Desktop/Pronostici Master Calcio

   ls
   # Dovrebbe mostrare: backend  frontend  README.md  ...
   ```

---

## 🔧 Passo 2: Avviare il Backend (Server API)

Il backend gestisce i dati, le previsioni e le statistiche.

### Prima Volta - Installazione

1. Vai nella cartella backend:
   ```bash
   cd backend
   ```

2. Crea l'ambiente virtuale Python:
   ```bash
   python3 -m venv venv
   ```

3. Attiva l'ambiente virtuale:
   ```bash
   source venv/bin/activate
   ```

   Vedrai `(venv)` prima del prompt del terminale.

4. Installa le dipendenze:
   ```bash
   pip install -r requirements.txt
   ```

### Ogni Volta - Avvio Backend

1. Assicurati di essere nella cartella backend:
   ```bash
   cd "/Users/prova/Desktop/Pronostici Master Calcio/backend"
   ```

2. Attiva l'ambiente virtuale:
   ```bash
   source venv/bin/activate
   ```

3. Avvia il server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. Il backend è pronto quando vedi:
   ```
   INFO:     Uvicorn running on http://0.0.0.0:8000
   INFO:     Application startup complete
   ```

5. **NON CHIUDERE QUESTA FINESTRA DEL TERMINAL!** Lasciala aperta.

6. Testa che funzioni aprendo nel browser:
   - http://localhost:8000 (dovrebbe mostrare info API)
   - http://localhost:8000/docs (documentazione interattiva)

### Fermare il Backend

- Premi `CTRL + C` nel terminale dove sta girando

---

## 🎨 Passo 3: Avviare il Frontend (Interfaccia Web)

Il frontend è ciò che gli utenti vedono nel browser.

### Prima Volta - Installazione

1. **Apri una NUOVA finestra del Terminal** (lascia l'altra con il backend aperta!)

2. Vai nella cartella frontend:
   ```bash
   cd "/Users/prova/Desktop/Pronostici Master Calcio/frontend"
   ```

3. Installa le dipendenze:
   ```bash
   npm install
   ```

### Ogni Volta - Avvio Frontend

1. Assicurati di essere nella cartella frontend:
   ```bash
   cd "/Users/prova/Desktop/Pronostici Master Calcio/frontend"
   ```

2. Avvia il server di sviluppo:
   ```bash
   npm run dev
   ```

3. Il frontend è pronto quando vedi:
   ```
   ▲ Next.js 15.x.x
   - Local:        http://localhost:3000
   ✓ Ready in Xs
   ```

4. Apri il browser e vai su: **http://localhost:3000**

5. **NON CHIUDERE QUESTA FINESTRA DEL TERMINAL!** Lasciala aperta.

### Fermare il Frontend

- Premi `CTRL + C` nel terminale dove sta girando

---

## ✏️ Come Fare Modifiche

### Modificare il Frontend (Layout, Colori, Testo)

1. **Apri il progetto in un editor di codice** (consigliato: Visual Studio Code)
   ```bash
   cd "/Users/prova/Desktop/Pronostici Master Calcio"
   code .
   ```

2. I file principali da modificare:
   - `frontend/app/page.tsx` - Home page
   - `frontend/app/classifica/page.tsx` - Pagina classifica
   - `frontend/app/marcatori/page.tsx` - Pagina marcatori
   - `frontend/app/cartellini/page.tsx` - Pagina cartellini
   - `frontend/components/layout/Header.tsx` - Menu di navigazione
   - `frontend/components/fixtures/FixtureCard.tsx` - Card delle partite

3. **Salva il file** dopo le modifiche

4. **Il browser si aggiorna automaticamente!** Non serve riavviare nulla.

### Modificare i Dati (Classifica, Marcatori, ecc.)

1. Apri il file:
   ```
   backend/app/api/endpoints/standings.py
   ```

2. Cerca la sezione con i dati reali:
   - Linea 83: `real_standings_data` - Classifica
   - Linea 146: `real_scorers_data` - Marcatori
   - Linea 205: `real_cards_by_team` - Cartellini

3. Modifica i dati (punti, gol, cartellini, ecc.)

4. Salva il file

5. **Il backend si riavvia automaticamente** (se hai usato `--reload`)

### Modificare il Calendario Partite

1. Apri il file:
   ```
   backend/app/api/endpoints/admin.py
   ```

2. Cerca la sezione `giornata_18_fixtures` (linea 125)

3. Modifica date e orari delle partite

4. Salva il file

5. Reset del database per applicare le modifiche:
   ```bash
   curl -X POST http://localhost:8000/api/v1/admin/reset-database
   ```

---

## 🚢 Come Pubblicare le Modifiche Online

Dopo aver fatto e testato le modifiche in locale, puoi pubblicarle online.

### Passo 1: Commit delle Modifiche

1. Apri il Terminal nella cartella del progetto:
   ```bash
   cd "/Users/prova/Desktop/Pronostici Master Calcio"
   ```

2. Verifica cosa hai modificato:
   ```bash
   git status
   ```

3. Aggiungi i file modificati:
   ```bash
   git add .
   ```

4. Crea un commit con messaggio descrittivo:
   ```bash
   git commit -m "Descrizione delle modifiche fatte"
   ```

   Esempio:
   ```bash
   git commit -m "Aggiornamento classifica dopo Giornata 19"
   ```

### Passo 2: Push su GitHub

```bash
git push origin main
```

### Passo 3: Deploy Automatico

**Non devi fare nient'altro!** 🎉

- **Vercel** (frontend) si aggiorna automaticamente in 2-3 minuti
- **Render** (backend) si aggiorna automaticamente in 3-5 minuti

### Passo 4: Verifica Online

Dopo 5 minuti, visita:
- https://pronostici-serie-a.vercel.app

Le tue modifiche sono online!

---

## 🔄 Reset Database in Produzione

Se hai modificato i dati e vuoi aggiornarli sul server online:

```bash
curl -X POST https://seriea-predictions-api.onrender.com/api/v1/admin/reset-database
```

Questo comando:
- Cancella tutti i dati vecchi
- Inserisce i nuovi dati che hai messo nel codice
- Ricrea le partite e le statistiche

---

## 📋 Comandi Utili Riassunti

### Ogni Sessione di Sviluppo

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

### Pubblicare Online

```bash
cd "/Users/prova/Desktop/Pronostici Master Calcio"
git add .
git commit -m "Descrizione modifiche"
git push origin main
```

### Reset Database Online

```bash
curl -X POST https://seriea-predictions-api.onrender.com/api/v1/admin/reset-database
```

---

## ❓ Problemi Comuni e Soluzioni

### "command not found: python3"
**Soluzione:**
```bash
brew install python@3.11
```

### "command not found: npm"
**Soluzione:**
```bash
brew install node
```

### Backend non si avvia
**Soluzione:**
1. Verifica di aver attivato l'ambiente virtuale:
   ```bash
   source venv/bin/activate
   ```
2. Reinstalla le dipendenze:
   ```bash
   pip install -r requirements.txt
   ```

### Frontend mostra errori
**Soluzione:**
1. Cancella i moduli e reinstalla:
   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

### Le modifiche non si vedono online
**Soluzione:**
1. Verifica che il push sia andato a buon fine:
   ```bash
   git status
   # Dovrebbe dire "nothing to commit, working tree clean"
   ```
2. Aspetta 5 minuti per il deploy automatico
3. Svuota la cache del browser: `CTRL + SHIFT + R` (o `CMD + SHIFT + R` su Mac)

### Database non si aggiorna
**Soluzione:**
```bash
# Reset database locale
curl -X POST http://localhost:8000/api/v1/admin/reset-database

# Reset database online
curl -X POST https://seriea-predictions-api.onrender.com/api/v1/admin/reset-database
```

---

## 📱 Condividere l'App

### Link Principale da Condividere

Invia questo link ai tuoi amici:

```
https://pronostici-serie-a.vercel.app
```

### Link Diretti alle Sezioni

- **Home**: https://pronostici-serie-a.vercel.app/
- **Classifica Serie A**: https://pronostici-serie-a.vercel.app/classifica
- **Capocannonieri**: https://pronostici-serie-a.vercel.app/marcatori
- **Situazione Cartellini**: https://pronostici-serie-a.vercel.app/cartellini
- **Partite**: https://pronostici-serie-a.vercel.app/partite

### Compatibilità

L'app funziona perfettamente su:
- ✅ Computer (Windows, Mac, Linux)
- ✅ iPhone e iPad (Safari, Chrome)
- ✅ Smartphone Android (Chrome, Firefox)
- ✅ Tablet

---

## 🎯 Workflow Tipico

Ecco un esempio di come lavorerai normalmente:

1. **Lunedì mattina**: Partite finite, vuoi aggiornare la classifica

2. **Avvia l'app in locale**:
   - Terminal 1: Backend
   - Terminal 2: Frontend
   - Browser: http://localhost:3000

3. **Modifica i dati**:
   - Apri `backend/app/api/endpoints/standings.py`
   - Aggiorna punti, gol, vittorie, ecc.
   - Salva

4. **Testa**:
   - Vai su http://localhost:3000/classifica
   - Verifica che i dati siano corretti

5. **Reset database locale**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/admin/reset-database
   ```

6. **Pubblica online**:
   ```bash
   git add .
   git commit -m "Aggiornamento classifica dopo Giornata 19"
   git push origin main
   ```

7. **Dopo 5 minuti**, reset database online:
   ```bash
   curl -X POST https://seriea-predictions-api.onrender.com/api/v1/admin/reset-database
   ```

8. **Verifica** su https://pronostici-serie-a.vercel.app/classifica

9. **Condividi** con i tuoi amici! 🎉

---

## 📞 Supporto

Se hai problemi:

1. Controlla questa guida
2. Guarda la sezione "Problemi Comuni"
3. Verifica i log nel Terminal (messaggi di errore)
4. Controlla i checkpoint salvati nella cartella del progetto

---

**Buon lavoro! ⚽🚀**
