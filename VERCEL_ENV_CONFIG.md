# Vercel Environment Variables Configuration

## Required Environment Variables

### Frontend (Vercel)

Vai su: https://vercel.com/dashboard → Pronostici Serie A → Settings → Environment Variables

Aggiungi questa variabile:

```
Name: NEXT_PUBLIC_API_URL
Value: https://seriea-predictions-api.onrender.com
```

**IMPORTANTE:** NON includere `/api/v1` alla fine - viene aggiunto automaticamente dal codice!

### Verifica Configurazione

Dopo aver aggiunto la variabile:
1. Vai su Deployments
2. Clicca sui 3 puntini del deployment più recente
3. Clicca "Redeploy"
4. Seleziona "Use existing Build Cache" → Redeploy

## Troubleshooting

Se vedi "Errore nel caricamento delle partite":
1. Apri la console del browser (F12)
2. Controlla se l'URL chiamato è corretto: `https://seriea-predictions-api.onrender.com/api/v1/fixtures/...`
3. Se vedi `/api/fixtures/...` (senza il dominio), la variabile non è configurata
