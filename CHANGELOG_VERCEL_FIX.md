# Changelog - Fix Vercel Deployment Issues

**Data**: 2025-12-28
**Obiettivo**: Risolvere problemi di build e deployment su Vercel

## Problemi Risolti

### 1. Path Alias Non Riconosciuti su Vercel ❌→✅

**Problema**:
```
Error: Module not found: Can't resolve '@/components/...'
```

**Causa**: Il `tsconfig.json` non aveva configurato `baseUrl` e `paths` per i path alias `@/`

**Fix applicato**:
```json
// frontend/tsconfig.json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./*"]
    }
  }
}
```

### 2. Build Error - Invalid Rewrite Destination ❌→✅

**Problema**:
```
`destination` does not start with `/`, `http://`, or `https://` for route
Error: Invalid rewrite found
```

**Causa**: `process.env.NEXT_PUBLIC_API_URL` era `undefined` durante il build

**Fix applicato**:
```javascript
// frontend/next.config.js
async rewrites() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL

  // Only add rewrites if API URL is defined
  if (!apiUrl) {
    return []
  }

  return [
    {
      source: '/api/:path*',
      destination: apiUrl + '/:path*',
    },
  ]
}
```

### 3. Type Error - Stadium Property ❌→✅

**Problema**:
```
Type error: Property 'stadium' does not exist on type 'Fixture'
```

**Causa**: Il tipo `Fixture` non ha una proprietà `stadium` diretta

**Fix applicato**:
```tsx
// frontend/components/fixtures/FixtureCard.tsx
// Prima: fixture.stadium?.name
// Dopo:  fixture.home_team.stadium_name
{fixture.home_team.stadium_name && `🏟️ ${fixture.home_team.stadium_name} • `}
```

### 4. Import Error - API Client ❌→✅

**Problema**:
```
Attempted import error: 'api' is not exported from '@/lib/api'
```

**Causa**: Il file esporta `apiClient` ma i componenti importavano `api`

**Fix applicato**:
```tsx
// frontend/components/fixtures/FixturesList.tsx
// Prima: import { api } from '@/lib/api'
// Dopo:  import { apiClient } from '@/lib/api'
```

### 5. Array Response Format ❌→✅

**Problema**: La query API si aspettava `data.fixtures` ma l'API ritorna un array diretto

**Fix applicato**:
```tsx
// frontend/components/fixtures/FixturesList.tsx
// Prima: if (!data || data.fixtures.length === 0)
//        data.fixtures.map(...)
// Dopo:  if (!data || data.length === 0)
//        data.map(...)
```

### 6. Celery Schedule File nel Git ❌→✅

**Problema**: File temporaneo `celerybeat-schedule` non ignorato da Git

**Fix applicato**:
```gitignore
# .gitignore
# Celery
celerybeat-schedule
celerybeat.pid
```

## File Modificati

```
M  .gitignore
M  frontend/tsconfig.json
M  frontend/next.config.js
M  frontend/components/fixtures/FixtureCard.tsx
M  frontend/components/fixtures/FixturesList.tsx
A  VERCEL_DEPLOY.md
A  CHANGELOG_VERCEL_FIX.md
```

## Risultati

### Build Test - Prima ❌
```
Failed to compile.
Type error: Property 'stadium' does not exist on type 'Fixture'
Error: Invalid rewrite found
```

### Build Test - Dopo ✅
```
✓ Compiled successfully in 625ms
✓ Generating static pages (4/4)
Route (app)                                 Size  First Load JS
┌ ○ /                                     5.3 kB         122 kB
└ ○ /_not-found                            994 B         103 kB
```

## Prossimi Step per Deploy

1. **Push changes su GitHub**:
   ```bash
   git add .
   git commit -m "Fix: Resolve Vercel build issues - path aliases, rewrites, types"
   git push origin main
   ```

2. **Deploy su Vercel**:
   ```bash
   cd frontend
   vercel --prod
   ```

3. **Configurare Environment Variables su Vercel**:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.onrender.com/api/v1
   ```

4. **Configurare CORS nel Backend**:
   ```python
   CORS_ORIGINS=["https://your-app.vercel.app"]
   ```

## Compatibilità

- ✅ **Next.js 15**: Compatibile
- ✅ **Vercel**: Build funzionante
- ✅ **TypeScript**: Strict mode OK
- ✅ **Local Development**: Funzionante
- ✅ **Production Build**: Funzionante

## Testing

```bash
# Local build test
cd frontend
npm run build    # ✅ Success

# Local dev test
npm run dev      # ✅ Success

# Type check
npx tsc --noEmit # ✅ No errors
```

## Note

- Il warning sui lockfile multipli è normale e non blocca il build
- L'app può fare build anche senza `NEXT_PUBLIC_API_URL` (mostrerà "Nessuna partita trovata")
- Tutti i path alias `@/` ora funzionano correttamente sia in dev che in prod

## Documentazione Aggiunta

- `VERCEL_DEPLOY.md`: Guida completa per deployment su Vercel
- `CHANGELOG_VERCEL_FIX.md`: Questo file

---

**Status**: ✅ PRONTO PER DEPLOY SU VERCEL
