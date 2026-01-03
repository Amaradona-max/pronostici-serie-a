#!/bin/bash
echo "⏰ ASPETTANDO COMPLETAMENTO WORKFLOW..."
echo ""

while true; do
    status=$(curl -s "https://api.github.com/repos/Amaradona-max/pronostici-serie-a/actions/workflows/fix-external-ids.yml/runs?per_page=1" | python3 -c "
import sys, json
data = json.load(sys.stdin)
runs = data.get('workflow_runs', [])
if runs:
    r = runs[0]
    print(f\"{r.get('status')}|{r.get('conclusion')}\")
" 2>/dev/null)
    
    run_status=$(echo "$status" | cut -d'|' -f1)
    conclusion=$(echo "$status" | cut -d'|' -f2)
    
    if [ "$run_status" = "completed" ]; then
        if [ "$conclusion" = "success" ]; then
            echo "🎉 WORKFLOW COMPLETATO CON SUCCESSO!"
            echo ""
            echo "Aspetto 10 secondi che i dati si propaghino..."
            sleep 10
            echo ""
            echo "Verifico l'API..."
            bash monitor_fix_status.sh
            exit 0
        else
            echo "❌ Workflow completato con errore: $conclusion"
            echo "Controlla i log su GitHub"
            exit 1
        fi
    fi
    
    echo -n "."
    sleep 3
done
