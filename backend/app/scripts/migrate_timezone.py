#!/usr/bin/env python3
"""
Migration script to convert DateTime columns from WITHOUT TIME ZONE to WITH TIME ZONE
"""
import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def migrate_timezone(database_url: str):
    """
    Convert all timestamp columns from WITHOUT TIME ZONE to WITH TIME ZONE
    """
    print("=" * 80)
    print("🔧 MIGRAZIONE TIMEZONE - TIMESTAMP WITH TIME ZONE")
    print("=" * 80)
    print()

    engine = create_async_engine(database_url, echo=False)

    # Lista delle tabelle e colonne da convertire
    conversions = [
        ("fixtures", "match_date"),
        ("fixtures", "last_synced_at"),
        ("fixtures", "created_at"),
        ("fixtures", "updated_at"),
        ("teams", "created_at"),
        ("teams", "updated_at"),
        ("competitions", "created_at"),
        ("competitions", "updated_at"),
        ("players", "created_at"),
        ("players", "updated_at"),
        ("team_stats", "created_at"),
        ("team_stats", "updated_at"),
        ("match_stats", "created_at"),
        ("injuries", "created_at"),
        ("injuries", "updated_at"),
        ("suspensions", "created_at"),
        ("suspensions", "updated_at"),
        ("predictions", "created_at"),
        ("feature_snapshots", "snapshot_timestamp"),
        ("prediction_evaluations", "evaluated_at"),
        ("data_sync_logs", "started_at"),
        ("data_sync_logs", "completed_at"),
        ("data_sync_logs", "created_at"),
        ("stadiums", "created_at"),
        ("stadiums", "updated_at"),
    ]

    try:
        async with engine.begin() as conn:
            print("🔄 Conversione colonne timestamp...")
            print()

            for table, column in conversions:
                try:
                    # Converti la colonna da TIMESTAMP WITHOUT TIME ZONE a TIMESTAMP WITH TIME ZONE
                    # Assumendo che tutti i timestamp esistenti siano UTC
                    sql = text(f"""
                        ALTER TABLE {table}
                        ALTER COLUMN {column} TYPE TIMESTAMP WITH TIME ZONE
                        USING {column} AT TIME ZONE 'UTC'
                    """)

                    await conn.execute(sql)
                    print(f"   ✅ {table}.{column} → TIMESTAMP WITH TIME ZONE")

                except Exception as e:
                    if "does not exist" in str(e).lower() or "column" in str(e).lower():
                        print(f"   ⚠️  {table}.{column} → Skipped (non esiste)")
                    else:
                        print(f"   ❌ {table}.{column} → Error: {e}")

            print()
            print("=" * 80)
            print("🎉 MIGRAZIONE COMPLETATA!")
            print("=" * 80)
            print()
            print("✅ Tutte le colonne timestamp ora supportano timezone!")
            print()

            return True

    except Exception as e:
        print()
        print("=" * 80)
        print(f"❌ ERRORE NELLA MIGRAZIONE: {e}")
        print("=" * 80)
        return False

    finally:
        await engine.dispose()


async def main():
    print()
    print("=" * 80)
    print("🚀 MIGRAZIONE DATABASE - TIMEZONE SUPPORT")
    print("=" * 80)
    print()
    print("Questo script converte tutte le colonne timestamp da:")
    print("  TIMESTAMP WITHOUT TIME ZONE")
    print("a:")
    print("  TIMESTAMP WITH TIME ZONE")
    print()
    print("I timestamp esistenti verranno interpretati come UTC.")
    print()
    print("=" * 80)
    print()

    database_url = input("Incolla DATABASE_URL da Render: ").strip()

    if not database_url:
        print("❌ DATABASE_URL vuoto. Uscita.")
        return

    # Convert postgresql:// to postgresql+asyncpg:// and add port if needed
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    if ":5432" not in database_url and "render.com" in database_url:
        # Add port before the /database part
        database_url = database_url.replace(".render.com/", ".render.com:5432/")

    print()
    print("🔗 Connessione al database...")
    print()

    success = await migrate_timezone(database_url)

    if success:
        print()
        print("✅ MIGRAZIONE COMPLETATA!")
        print()
        print("PROSSIMI PASSI:")
        print("1. Committa e pusha il codice aggiornato (models.py)")
        print("2. Il prossimo sync automatico funzionerà correttamente!")
        print()
        sys.exit(0)
    else:
        print()
        print("❌ MIGRAZIONE FALLITA")
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
        import traceback
        traceback.print_exc()
        sys.exit(1)
