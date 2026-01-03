#!/bin/bash

# Monitor script to check if the fix has been applied

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 MONITORING FIX STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Time: $(date -u '+%Y-%m-%d %H:%M:%S') UTC"
echo ""

# Check 1: Has fix-external-ids workflow been run?
echo "━━━ CHECK 1: Fix Workflow Status ━━━"
echo ""

fix_workflow=$(curl -s "https://api.github.com/repos/Amaradona-max/pronostici-serie-a/actions/workflows/fix-external-ids.yml/runs?per_page=5")
fix_runs=$(echo "$fix_workflow" | python3 -c "
import sys, json
data = json.load(sys.stdin)
runs = data.get('workflow_runs', [])
if runs:
    latest = runs[0]
    print(f\"✅ Fix workflow HAS been run!\")
    print(f\"   Run #: {latest.get('run_number')}\")
    print(f\"   Status: {latest.get('status')} / {latest.get('conclusion')}\")
    print(f\"   Time: {latest.get('created_at')}\")
else:
    print('⚠️  Fix workflow NOT YET run')
    print('   Action needed: Run manually on GitHub Actions')
")
echo "$fix_runs"
echo ""

# Check 2: Are the API data updated?
echo "━━━ CHECK 2: API Data Status ━━━"
echo ""

api_data=$(curl -s "https://seriea-predictions-api.onrender.com/api/v1/fixtures/serie-a/2025-2026?limit=10" | python3 -c "
import sys, json
data = json.load(sys.stdin)
fixtures = data.get('fixtures', [])

cagliari_milan_updated = False
como_udinese_updated = False

for f in fixtures:
    home = f.get('home_team', {}).get('name', '')
    away = f.get('away_team', {}).get('name', '')
    home_score = f.get('home_score')
    away_score = f.get('away_score')
    status = f.get('status')

    if 'Cagliari' in home and 'Milan' in away:
        if home_score == 0 and away_score == 1 and status == 'finished':
            print('✅ Cagliari 0-1 AC Milan: UPDATED! (finished)')
            cagliari_milan_updated = True
        else:
            print(f'❌ Cagliari vs AC Milan: NOT updated (status: {status}, score: {home_score}-{away_score})')

    elif 'Como' in home and 'Udinese' in away:
        if home_score == 1 and away_score == 1 and status == 'finished':
            print('✅ Como 1-1 Udinese: UPDATED! (finished)')
            como_udinese_updated = True
        else:
            print(f'❌ Como vs Udinese: NOT updated (status: {status}, score: {home_score}-{away_score})')

if cagliari_milan_updated and como_udinese_updated:
    print('')
    print('🎉 SUCCESS! All data updated correctly!')
else:
    print('')
    print('⏳ Data not yet updated - fix needs to be applied')
")
echo "$api_data"
echo ""

# Check 3: Recent sync workflow runs
echo "━━━ CHECK 3: Recent Sync Workflows ━━━"
echo ""

sync_workflow=$(curl -s "https://api.github.com/repos/Amaradona-max/pronostici-serie-a/actions/workflows/sync-live-data.yml/runs?per_page=3" | python3 -c "
import sys, json
data = json.load(sys.stdin)
runs = data.get('workflow_runs', [])

for i, run in enumerate(runs, 1):
    number = run.get('run_number')
    sha = run.get('head_sha', '')[:7]
    status = run.get('status')
    conclusion = run.get('conclusion')
    time = run.get('created_at', '')
    icon = '✅' if conclusion == 'success' else '❌' if conclusion == 'failure' else '⏳'
    print(f'{icon} Run #{number} ({sha}) - {status}/{conclusion} - {time}')
")
echo "$sync_workflow"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "NEXT STEPS:"
echo ""
echo "If fix NOT applied:"
echo "  → Go to: https://github.com/Amaradona-max/pronostici-serie-a/actions/workflows/fix-external-ids.yml"
echo "  → Click 'Run workflow' and wait"
echo ""
echo "If fix applied but data NOT updated:"
echo "  → Check DATABASE_URL in GitHub Secrets"
echo "  → See FIX_INSTRUCTIONS.md for details"
echo ""
echo "To run this monitor again:"
echo "  bash monitor_fix_status.sh"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
