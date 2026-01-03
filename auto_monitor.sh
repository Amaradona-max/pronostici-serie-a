#!/bin/bash

# Automatic monitoring loop - checks every 30 seconds

echo "🤖 AUTO-MONITOR STARTED"
echo "Checking for fix workflow execution every 30 seconds..."
echo "Press Ctrl+C to stop"
echo ""

iteration=0

while true; do
    iteration=$((iteration + 1))
    echo "━━━ Check #$iteration - $(date -u '+%H:%M:%S UTC') ━━━"
    
    # Check if fix workflow has run
    fix_status=$(curl -s "https://api.github.com/repos/Amaradona-max/pronostici-serie-a/actions/workflows/fix-external-ids.yml/runs?per_page=1" | python3 -c "
import sys, json
data = json.load(sys.stdin)
runs = data.get('workflow_runs', [])
if runs:
    latest = runs[0]
    print(f'{latest.get(\"run_number\")}|{latest.get(\"conclusion\")}|{latest.get(\"created_at\")}')
else:
    print('none')
" 2>/dev/null)
    
    if [ "$fix_status" != "none" ]; then
        run_num=$(echo "$fix_status" | cut -d'|' -f1)
        conclusion=$(echo "$fix_status" | cut -d'|' -f2)
        time=$(echo "$fix_status" | cut -d'|' -f3)
        
        if [ "$conclusion" == "success" ]; then
            echo "✅ FIX WORKFLOW COMPLETED SUCCESSFULLY!"
            echo "   Run #$run_num at $time"
            echo ""
            echo "Waiting 30 seconds for data to sync..."
            sleep 30
            echo ""
            echo "Checking API data..."
            bash monitor_fix_status.sh
            echo ""
            echo "🎉 Auto-monitor detected fix execution!"
            echo "Review results above to verify success."
            break
        elif [ "$conclusion" == "failure" ]; then
            echo "❌ Fix workflow FAILED!"
            echo "   Check logs: https://github.com/Amaradona-max/pronostici-serie-a/actions"
            break
        else
            echo "⏳ Fix workflow running (status: $conclusion)"
        fi
    else
        echo "⏳ Fix workflow not yet executed"
    fi
    
    # Check API status briefly
    api_status=$(curl -s "https://seriea-predictions-api.onrender.com/api/v1/fixtures/serie-a/2025-2026?limit=5" | python3 -c "
import sys, json
data = json.load(sys.stdin)
fixtures = data.get('fixtures', [])
updated = False
for f in fixtures:
    if 'Cagliari' in f.get('home_team', {}).get('name', '') and 'Milan' in f.get('away_team', {}).get('name', ''):
        if f.get('home_score') == 0 and f.get('away_score') == 1:
            updated = True
            break
print('updated' if updated else 'not_updated')
" 2>/dev/null)
    
    if [ "$api_status" == "updated" ]; then
        echo "🎉 DATA ALREADY UPDATED IN API!"
        echo "Running full verification..."
        echo ""
        bash monitor_fix_status.sh
        break
    fi
    
    sleep 30
done
