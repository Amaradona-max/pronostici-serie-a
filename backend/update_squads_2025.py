#!/usr/bin/env python3
"""
Update Squads with 2025 Transfer Window Data
Sync verified Transfermarkt data to database
"""
import asyncio
import sys
sys.path.insert(0, '/Users/prova/Desktop/Pronostici Master Calcio/backend')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, select
from datetime import date

# Import verified data
from VERIFIED_SQUADS_TRANSFERMARKT import VERIFIED_PLAYERS_DATA

async def update_squads():
    database_url = "postgresql+asyncpg://seriea_predictions_user:Ev3CgCMMBNx3l5V88ycV8GLSgY1w11OA@dpg-d5873l95pdvs738kpl80-a.frankfurt-postgres.render.com:5432/seriea_predictions"

    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with async_session() as session:
            print("=" * 80)
            print("🔄 AGGIORNAMENTO ROSE SQUADRE - Trasferimenti 2025")
            print("=" * 80)
            print()

            total_added = 0
            total_updated = 0
            total_removed = 0

            for team_name, verified_players in VERIFIED_PLAYERS_DATA.items():
                print(f"📋 {team_name}...")

                # Get team ID
                team_result = await session.execute(
                    text("SELECT id FROM teams WHERE name = :name"),
                    {"name": team_name}
                )
                team = team_result.fetchone()

                if not team:
                    print(f"   ⚠️  Team '{team_name}' non trovato nel database")
                    continue

                team_id = team[0]

                # Get current players for this team
                current_players_result = await session.execute(
                    text("""
                        SELECT id, name, position, jersey_number, nationality
                        FROM players
                        WHERE team_id = :team_id
                    """),
                    {"team_id": team_id}
                )
                current_players = {p[1]: p for p in current_players_result.fetchall()}

                # Track which verified players we've seen
                verified_player_names = set()

                added = 0
                updated = 0

                # Add or update verified players
                for player_data in verified_players:
                    player_name = player_data["name"]
                    verified_player_names.add(player_name)

                    if player_name in current_players:
                        # Update existing player
                        player_id = current_players[player_name][0]
                        await session.execute(
                            text("""
                                UPDATE players
                                SET position = :position,
                                    jersey_number = :number,
                                    nationality = :nationality
                                WHERE id = :id
                            """),
                            {
                                "id": player_id,
                                "position": player_data["position"],
                                "number": player_data["number"],
                                "nationality": player_data["nationality"]
                            }
                        )
                        updated += 1
                    else:
                        # Add new player
                        await session.execute(
                            text("""
                                INSERT INTO players (team_id, name, position, jersey_number, nationality)
                                VALUES (:team_id, :name, :position, :number, :nationality)
                            """),
                            {
                                "team_id": team_id,
                                "name": player_name,
                                "position": player_data["position"],
                                "number": player_data["number"],
                                "nationality": player_data["nationality"]
                            }
                        )
                        added += 1

                # Remove players no longer in squad (transferred out)
                removed = 0
                for player_name, player_info in current_players.items():
                    if player_name not in verified_player_names:
                        player_id = player_info[0]
                        await session.execute(
                            text("DELETE FROM players WHERE id = :id"),
                            {"id": player_id}
                        )
                        removed += 1

                if added > 0 or updated > 0 or removed > 0:
                    print(f"   ✅ Aggiornato: +{added} nuovi, ~{updated} modificati, -{removed} rimossi")
                else:
                    print(f"   ✅ Già aggiornata")

                total_added += added
                total_updated += updated
                total_removed += removed

            # Commit all changes
            await session.commit()

            print()
            print("=" * 80)
            print("✅ AGGIORNAMENTO COMPLETATO!")
            print("=" * 80)
            print()
            print(f"📊 Totali:")
            print(f"   + {total_added} giocatori aggiunti (acquisti)")
            print(f"   ~ {total_updated} giocatori aggiornati")
            print(f"   - {total_removed} giocatori rimossi (cessioni)")
            print()
            print("🎉 Tutte le rose sono ora aggiornate con i trasferimenti del 2025!")
            print()

            return True

    except Exception as e:
        print()
        print("=" * 80)
        print(f"❌ ERRORE: {e}")
        print("=" * 80)
        import traceback
        traceback.print_exc()
        return False

    finally:
        await engine.dispose()

if __name__ == "__main__":
    print()
    success = asyncio.run(update_squads())

    if success:
        print("✅ Le rose nell'app sono ora perfettamente aggiornate!")
        print()
        sys.exit(0)
    else:
        print("❌ Aggiornamento fallito")
        print()
        sys.exit(1)
