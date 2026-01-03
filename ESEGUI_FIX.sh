#!/bin/bash

# SCRIPT FIX DEFINITIVO - Esecuzione Automatica
# Risolve il problema degli external_id definitivamente

clear

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                    🔧 FIX DEFINITIVO - EXTERNAL IDs                        ║"
echo "║                                                                            ║"
echo "║  Questo script risolverà DEFINITIVAMENTE il problema dei dati non         ║"
echo "║  aggiornati nell'app.                                                      ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "⏱️  Tempo stimato: 2 minuti"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 PASSO 1: Ottieni DATABASE_URL da Render"
echo ""
echo "   1. Apri nel browser:"
echo "      https://dashboard.render.com/web/srv-ctfqnvaj1k6c738j63cg"
echo ""
echo "   2. Clicca su 'Environment' nel menu laterale"
echo ""
echo "   3. Trova la variabile 'DATABASE_URL'"
echo ""
echo "   4. Clicca sull'icona 'occhio' per vedere il valore"
echo ""
echo "   5. Clicca 'Copy' per copiarlo"
echo ""
echo "   ⚠️  IMPORTANTE: L'URL deve contenere '@' e finire con il nome del database"
echo "      Esempio: postgresql+asyncpg://user:pass@host.render.com:5432/dbname"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Open Render dashboard automatically
echo "🌐 Apertura Render Dashboard..."
open "https://dashboard.render.com/web/srv-ctfqnvaj1k6c738j63cg" 2>/dev/null || echo "   (Apri manualmente il link sopra)"
echo ""

read -p "Premi INVIO quando hai copiato DATABASE_URL... "

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 PASSO 2: Esegui il fix"
echo ""

# Execute the fix script
cd "/Users/prova/Desktop/Pronostici Master Calcio"
python3 FIX_DEFINITIVO.py

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
