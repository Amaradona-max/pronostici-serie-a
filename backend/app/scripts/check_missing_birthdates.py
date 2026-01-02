import sys
import os

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.api.endpoints.predictions import MOCK_LINEUPS
from app.data.player_birthdates import PLAYER_BIRTHDATES

def normalize_name(name):
    """Normalize name for comparison (remove accents, etc)"""
    # Simple normalization for now, can be improved
    return name

def check_missing():
    print("Checking for missing birthdates...")
    missing = []
    total_players = 0
    found_players = 0
    
    # Also check keys in PLAYER_BIRTHDATES for normalization issues
    birthdate_keys = set(PLAYER_BIRTHDATES.keys())
    
    for team, data in MOCK_LINEUPS.items():
        print(f"\nChecking {team}...")
        
        # Check starting XI
        for player_tuple in data.get("starting_xi", []):
            total_players += 1
            name = player_tuple[0]
            
            # Simulate get_birthdate logic
            found = False
            if name in PLAYER_BIRTHDATES:
                found = True
            else:
                for key in birthdate_keys:
                    if key.endswith(" " + name):
                        found = True
                        break
            
            if not found:
                missing.append(f"{team}: {name} (Starter)")

        # Check bench
        for name in data.get("bench", []):
            total_players += 1
            found = False
            if name in PLAYER_BIRTHDATES:
                found = True
            else:
                for key in birthdate_keys:
                    if key.endswith(" " + name):
                        found = True
                        break
            
            if not found:
                missing.append(f"{team}: {name} (Bench)")
            else:
                found_players += 1

    print(f"\nTotal players checked: {total_players}")
    print(f"Found birthdates: {found_players}")
    print(f"Missing birthdates: {len(missing)}")
    
    if missing:
        print("\nMissing Players:")
        for p in missing:
            print(p)
    else:
        print("\nAll players have birthdates!")

if __name__ == "__main__":
    check_missing()
