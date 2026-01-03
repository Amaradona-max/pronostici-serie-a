#!/bin/bash

echo "🤖 MONITORING AUTOMATICO ATTIVO"
echo "Controllo ogni 15 secondi fino al successo..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

success=false
iteration=0

while [ "$success" = false ]; do
    iteration=$((iteration + 1))
    echo "⏰ Check #$iteration - $(date '+%H:%M:%S')"
    
    # Check 1: Fix workflow eseguito?
    fix_status=$(curl -s "https://api.github.com/repos/Amaradona-max/pronostici-serie-a/actions/workflows/fix-external-ids.yml/runs?per_page=1" | python3 -c "
import sys, json
data = json.load(sys.stdin)
runs = data.get('workflow_runs', [])
if runs and runs[0].get('conclusion') == 'success':
    print('fix_success')
elif runs:
    print('fix_running')
else:
    print('fix_none')
" 2>/dev/null)
    
    # Check 2: API aggiornata?
    api_status=$(curl -s "https://seriea-predictions-api.onrender.com/api/v1/fixtures/serie-a/2025-2026?limit=5" | python3 -c "
import sys, json
data = json.load(sys.stdin)
fixtures = data.get('fixtures', [])
for f in fixtures:
    home = f.get('home_team', {}).get('name', '')
    away = f.get('away_team', {}).get('name', '')
    if 'Cagliari' in home and 'Milan' in away:
        if f.get('home_score') == 0 and f.get('away_score') == 1:
            print('api_updated')
            exit()
print('api_not_updated')
" 2>/dev/null)
    
    if [ "$fix_status" = "fix_success" ]; then
        echo "   ✅ Fix workflow completato!"
    elif [ "$fix_status" = "fix_running" ]; then
        echo "   🔄 Fix workflow in esecuzione..."
    else
        echo "   ⏳ In attesa esecuzione fix workflow..."
    fi
    
    if [ "$api_status" = "api_updated" ]; then
        echo "   ✅ API aggiornata!"
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "🎉 SUCCESSO! L'APP È AGGIORNATA!"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "Verifica completa:"
        bash monitor_fix_status.sh
        success=true
    else
        echo "   ⏳ API non ancora aggiornata"
    fi
    
    if [ "$success" = false ]; then
        echo ""
        sleep 15
    fi
done

echo ""
echo "✅ L'app è pronta su: https://pronostici-serie-a.vercel.app"
echo "✅ Apri il link per vedere i dati aggiornati!"
