#!/bin/bash

echo "⏰ ATTESA AGGIORNAMENTO DATI"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Controllo ogni 60 secondi (max 10 minuti)..."
echo "Ora inizio: $(date '+%H:%M:%S')"
echo ""

for i in $(seq 1 10); do
    echo "━━━ Check #$i - $(date '+%H:%M:%S') ━━━"

    curl -s "https://seriea-predictions-api.onrender.com/api/v1/fixtures/serie-a/2025-2026?limit=2" > /tmp/api_check.json 2>/dev/null

    result=$(python3 << 'PYEOF'
import json
try:
    with open('/tmp/api_check.json') as f:
        data = json.load(f)
    fixtures = data.get('fixtures', [])

    for f in fixtures:
        home = f.get('home_team', {}).get('name', '')
        away = f.get('away_team', {}).get('name', '')
        home_score = f.get('home_score')
        away_score = f.get('away_score')
        status = f.get('status')

        if 'Cagliari' in home and 'Milan' in away:
            if home_score == 0 and away_score == 1 and status == 'finished':
                print('SUCCESS')
                exit()
            else:
                print(f'WAITING|{status}')
                exit()

    print('WAITING|Not found')
except Exception as e:
    print(f'ERROR|{e}')
PYEOF
)

    status=$(echo "$result" | cut -d'|' -f1)

    if [ "$status" = "SUCCESS" ]; then
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "🎉🎉🎉 SUCCESSO! DATI AGGIORNATI! 🎉🎉🎉"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "✅ App aggiornata e funzionante!"
        echo ""
        echo "🌐 https://pronostici-serie-a.vercel.app"
        echo ""
        exit 0
    else
        echo "  ⏳ Ancora in attesa..."
        if [ $i -lt 10 ]; then
            sleep 60
        fi
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⏳ Ancora in attesa dopo 10 minuti"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
