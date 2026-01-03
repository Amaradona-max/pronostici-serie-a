#!/usr/bin/env python3
"""
SCRIPT FIX DEFINITIVO - External IDs
Esegue il fix degli external_id direttamente sul database Render.
"""
import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# IDs corretti da Football-Data.org (API-Football format)
CORRECT_EXTERNAL_IDS = {
    "Inter": 505,
    "AC Milan": 489,
    "Juventus": 496,
    "Napoli": 492,
    "AS Roma": 497,
    "Lazio": 487,
    "Atalanta": 499,
    "Fiorentina": 502,
    "Bologna": 500,
    "Torino": 503,
    "Udinese": 494,
    "Lecce": 867,
    "Cagliari": 490,
    "Hellas Verona": 504,
    "Genoa": 495,
    "Parma": 130,
    "Como": 1047,
    "Sassuolo": 488,
    "Pisa": 506,
    "Cremonese": 520
}


async def fix_external_ids(database_url: str):
    """
    Fix external_ids for all Serie A teams.
    """
    print("=" * 80)
    print("🔧 FIX DEFINITIVO EXTERNAL IDs")
    print("=" * 80)
    print()

    # Create async engine
    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with async_session() as session:
            # Get all teams
            print("📊 Recupero teams dal database...")
            result = await session.execute(text("SELECT id, name, external_id FROM teams ORDER BY name"))
            teams = result.fetchall()

            if not teams:
                print("❌ Nessun team trovato nel database!")
                return False

            print(f"✅ Trovati {len(teams)} teams\n")
            print("-" * 80)
            print(f"{'Team':<25} {'Current ID':<15} {'Correct ID':<15} {'Action':<15}")
            print("-" * 80)

            fixed_count = 0
            updates = []

            for team_id, team_name, current_external_id in teams:
                correct_id = CORRECT_EXTERNAL_IDS.get(team_name)

                if correct_id is None:
                    action = "⚠️  Skipped"
                    print(f"{team_name:<25} {current_external_id:<15} {'N/A':<15} {action:<15}")
                    continue

                if current_external_id != correct_id:
                    action = "🔄 UPDATE"
                    updates.append((team_id, team_name, correct_id))
                    fixed_count += 1
                else:
                    action = "✅ OK"

                print(f"{team_name:<25} {current_external_id or 'NULL':<15} {correct_id:<15} {action:<15}")

            print("-" * 80)
            print()

            if fixed_count == 0:
                print("✅ Tutti gli external_id sono già corretti!")
                print("   Non è necessario fare nulla.")
                return True

            # Ask for confirmation
            print(f"⚠️  Verranno aggiornati {fixed_count} teams.")
            print()
            confirm = input("Procedi con l'aggiornamento? (yes/no): ").strip().lower()

            if confirm not in ['yes', 'y', 'si', 'sì']:
                print("❌ Operazione annullata.")
                return False

            print()
            print("🔄 Esecuzione updates...")

            # Execute updates
            for team_id, team_name, correct_id in updates:
                await session.execute(
                    text("UPDATE teams SET external_id = :new_id WHERE id = :team_id"),
                    {"new_id": correct_id, "team_id": team_id}
                )
                print(f"   ✅ {team_name}: external_id → {correct_id}")

            # Commit changes
            await session.commit()

            print()
            print("=" * 80)
            print(f"🎉 FIX COMPLETATO CON SUCCESSO!")
            print(f"   {fixed_count} teams aggiornati")
            print("=" * 80)
            print()
            print("✅ Il prossimo sync automatico (entro 5 minuti) aggiornerà i dati!")
            print()

            return True

    except Exception as e:
        print()
        print("=" * 80)
        print(f"❌ ERRORE: {e}")
        print("=" * 80)
        print()
        print("Possibili cause:")
        print("1. DATABASE_URL non corretto")
        print("2. Database non raggiungibile")
        print("3. Permessi insufficienti")
        return False

    finally:
        await engine.dispose()


async def main():
    print()
    print("=" * 80)
    print("🚀 SCRIPT FIX DEFINITIVO - EXTERNAL IDs")
    print("=" * 80)
    print()
    print("Questo script aggiorna gli external_id dei teams nel database Render.")
    print()
    print("REQUISITI:")
    print("1. DATABASE_URL completo da Render")
    print("2. Connessione internet")
    print()
    print("=" * 80)
    print()

    # Get DATABASE_URL
    database_url = input("Incolla DATABASE_URL da Render: ").strip()

    if not database_url:
        print("❌ DATABASE_URL vuoto. Uscita.")
        return

    if not database_url.startswith("postgresql"):
        print("⚠️  WARNING: DATABASE_URL non inizia con 'postgresql'")
        print(f"   URL fornito: {database_url[:50]}...")
        confirm = input("Continua comunque? (yes/no): ").strip().lower()
        if confirm not in ['yes', 'y']:
            return

    print()
    print("🔗 Connessione al database...")
    print()

    success = await fix_external_ids(database_url)

    if success:
        print()
        print("✅ OPERAZIONE COMPLETATA!")
        print()
        print("PROSSIMI PASSI:")
        print("1. Aspetta 5 minuti (prossimo sync automatico)")
        print("2. Apri: https://pronostici-serie-a.vercel.app")
        print("3. Ricarica la pagina")
        print("4. Dovresti vedere i punteggi aggiornati!")
        print()
        sys.exit(0)
    else:
        print()
        print("❌ OPERAZIONE FALLITA")
        print()
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n❌ Operazione interrotta dall'utente")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Errore inaspettato: {e}")
        sys.exit(1)
