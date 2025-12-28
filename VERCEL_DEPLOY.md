# Deployment su Vercel - Guida Rapida

## Problemi Risolti ✅

1. **Path Alias**: Aggiunto `baseUrl` e `paths` al `tsconfig.json`
2. **Rewrite API**: Reso condizionale per evitare errori quando `NEXT_PUBLIC_API_URL` non è definito
3. **Import corretto**: Cambiato `api` in `apiClient` in tutti i componenti
4. **Type errors**: Corretti tipi Fixture e riferimenti corretti alle proprietà

## Deploy su Vercel

### 1. Preparazione Repository

Assicurati che il codice sia pushato su GitHub:

```bash
git add .
git commit -m "Fix: Resolve Vercel build issues"
git push origin main
```

### 2. Deploy su Vercel

#### Opzione A: Vercel CLI (Consigliata)

```bash
# Installa Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy (dalla root del progetto)
cd "/Users/prova/Desktop/Pronostici Master Calcio/frontend"
vercel --prod
```

Durante il setup, Vercel chiederà:
- **Project name**: `seriea-predictions` (o quello che preferisci)
- **Framework Preset**: Next.js (auto-detected)
- **Build Command**: `npm run build` (default)
- **Output Directory**: `.next` (default)
- **Root Directory**: `frontend` (o usa il deploy dalla cartella frontend)

#### Opzione B: Vercel Dashboard

1. Vai su [vercel.com](https://vercel.com)
2. Clicca **"Add New..." → "Project"**
3. Importa il repository GitHub
4. Configura:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Next.js (auto-detected)
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

### 3. Environment Variables su Vercel

Aggiungi la seguente variabile d'ambiente:

**Nel Dashboard Vercel**: Settings → Environment Variables

```
NEXT_PUBLIC_API_URL=https://your-backend-api.onrender.com/api/v1
```

**Nota**: Sostituisci `your-backend-api.onrender.com` con l'URL effettivo del tuo backend.

Se non hai ancora il backend deployato:
- Lascia vuoto per ora (l'app farà build ma mostrerà "Nessuna partita trovata")
- Aggiungi dopo quando il backend è pronto

### 4. Verifica Build

Dopo il deploy, Vercel mostrerà:
- ✅ **Build Output**: Verificare che non ci siano errori
- ✅ **Preview URL**: URL temporaneo per testare
- ✅ **Production URL**: URL finale dell'app

### 5. Test Deploy

Visita l'URL fornito da Vercel e verifica:
- ✅ Homepage carica correttamente
- ✅ Dark mode funziona
- ✅ Non ci sono errori JavaScript nella console

## Risoluzione Problemi

### Build Fails - "Module not found: Can't resolve '@/...'"

**Causa**: Path alias non configurati correttamente
**Soluzione**: Già risolto! Il `tsconfig.json` ora ha `baseUrl` e `paths` configurati

### Build Fails - "destination does not start with..."

**Causa**: `NEXT_PUBLIC_API_URL` non definito
**Soluzione**: Già risolto! Il `next.config.js` ora gestisce il caso undefined

### Runtime Error - "Cannot read property 'stadium'"

**Causa**: Tipo Fixture non corrispondente
**Soluzione**: Già risolto! Ora usa `fixture.home_team.stadium_name`

### API Calls Fail

**Causa**: Backend non configurato o URL errato
**Soluzione**:
1. Verifica che il backend sia deployato e accessibile
2. Controlla che `NEXT_PUBLIC_API_URL` sia corretto nelle Environment Variables di Vercel
3. Aggiungi l'URL del frontend Vercel al `CORS_ORIGINS` del backend

## Deploy Backend su Render

Se non hai ancora deployato il backend, segui `DEPLOYMENT.md` sezione "Render".

Quick steps:
1. Deploy PostgreSQL database su Render
2. Deploy Redis su Render
3. Deploy backend API su Render
4. Copia l'URL del backend (es: `https://seriea-api.onrender.com`)
5. Aggiungi `/api/v1` all'URL e usalo come `NEXT_PUBLIC_API_URL` su Vercel

## CORS Configuration

Nel backend, aggiungi l'URL Vercel al `CORS_ORIGINS`:

```python
# backend/.env
CORS_ORIGINS=["https://your-app.vercel.app"]
```

## Custom Domain (Opzionale)

Su Vercel:
1. Settings → Domains
2. Aggiungi il tuo dominio custom
3. Configura DNS come indicato da Vercel
4. Aggiorna `CORS_ORIGINS` nel backend con il nuovo dominio

## Monitoring

Vercel fornisce:
- **Analytics**: Traffic e performance
- **Logs**: Runtime e build logs
- **Speed Insights**: Core Web Vitals

Accedi da: Dashboard → Il tuo progetto → Analytics/Logs

## Costi

- **Hobby Plan (Free)**:
  - ✅ Unlimited deployments
  - ✅ 100 GB bandwidth/month
  - ✅ Serverless Functions
  - ❌ No team features

- **Pro Plan ($20/mese)**:
  - Più bandwidth
  - Password protection
  - Team collaboration

Per MVP, il piano gratuito è più che sufficiente.

## Auto-Deploy

Vercel auto-deploya quando fai push su GitHub:
- **main branch** → Production
- **altre branches** → Preview deployments

Puoi disabilitare auto-deploy in: Settings → Git

## Comandi Utili

```bash
# Deploy production
vercel --prod

# Deploy preview
vercel

# View logs
vercel logs

# Link progetto locale
vercel link

# Pull environment variables
vercel env pull
```

## Checklist Finale

- [x] Build locale funziona (`npm run build`)
- [x] Path alias configurati in `tsconfig.json`
- [x] `next.config.js` gestisce env vars undefined
- [x] Types corretti in tutti i componenti
- [x] `.env.example` documentato
- [ ] Backend deployato e URL disponibile
- [ ] `NEXT_PUBLIC_API_URL` configurato su Vercel
- [ ] CORS configurato nel backend
- [ ] Deploy su Vercel completato
- [ ] Test dell'applicazione live

## Supporto

- **Documentazione Vercel**: [vercel.com/docs](https://vercel.com/docs)
- **Next.js su Vercel**: [nextjs.org/docs/deployment](https://nextjs.org/docs/deployment)
- **Troubleshooting**: [vercel.com/guides/troubleshooting](https://vercel.com/guides/troubleshooting)

---

Buon deploy! 🚀
