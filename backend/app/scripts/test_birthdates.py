
import sys
import os
from datetime import date

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.data.player_birthdates import get_birthdate

def test_birthdates():
    test_cases = [
        ("Reijnders", "T. Reijnders"),
        ("Acerbi", "F. Acerbi"),
        ("Bremer", "G. Bremer"),
        ("Balotelli", "M. Balotelli"),
        ("Jankto", "J. Jankto"),
        ("Douglas Luiz", "Douglas Luiz"),
        ("M. Thuram", "M. Thuram"),
        ("K. Thuram", "K. Thuram"),
        ("Sommer", "Y. Sommer"),
        ("Maignan", "M. Maignan"),
        ("T. Hernandez", "T. Hernández"), # This might fail if accent is issue? "T. Hernández" in dict.
        ("Hernandez", "T. Hernández"), # Should work via fuzzy? No, "T. Hernández" ends with "Hernández" (accent). "Hernandez" (no accent) won't match endswith.
        ("Fofana", "Y. Fofana"),
    ]

    print("Testing birthdate lookups...")
    failed = []
    for query, expected_key in test_cases:
        bd = get_birthdate(query)
        if bd:
            print(f"[OK] {query} -> Found: {bd}")
        else:
            print(f"[FAIL] {query} -> Not found")
            failed.append(query)
    
    # Test specific accent case manually
    print("\nChecking accent handling:")
    print(f"Query 'Hernandez': {get_birthdate('Hernandez')}")
    print(f"Query 'T. Hernandez': {get_birthdate('T. Hernandez')}")
    
    if failed:
        print(f"\nFailed queries: {failed}")
        sys.exit(1)
    else:
        print("\nAll tests passed!")

if __name__ == "__main__":
    test_birthdates()
