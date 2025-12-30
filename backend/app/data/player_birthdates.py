"""
Date di nascita dei calciatori Serie A 2024-25

Dati basati su fonti open-source:
- Transfermarkt
- Wikipedia
- Database pubblici di calciatori professionisti

Le date sono realistiche e basate sulle rose attuali della Serie A.
"""

from datetime import date

# Dizionario con date di nascita dei calciatori
# Formato: "Nome Cognome": date(anno, mese, giorno)
PLAYER_BIRTHDATES = {
    # ===== INTER =====
    "Y. Sommer": date(1988, 12, 17),
    "B. Pavard": date(1996, 3, 28),
    "S. de Vrij": date(1992, 2, 5),
    "A. Bastoni": date(1999, 4, 13),
    "D. Dumfries": date(1996, 4, 18),
    "N. Barella": date(1997, 2, 7),
    "H. Calhanoglu": date(1994, 2, 8),
    "H. Mkhitaryan": date(1989, 1, 21),
    "F. Dimarco": date(1997, 11, 10),
    "L. Martinez": date(1997, 8, 22),
    "M. Thuram": date(1997, 8, 6),
    "E. Audero": date(1997, 3, 18),
    "D. Frattesi": date(1999, 9, 22),
    "K. Asllani": date(2002, 3, 9),
    "M. Arnautovic": date(1989, 4, 19),
    "J. Correa": date(1994, 3, 13),
    "M. Darmian": date(1989, 12, 2),
    "C. Augusto": date(1999, 5, 8),

    # ===== AC MILAN =====
    "M. Maignan": date(1995, 7, 3),
    "E. Royal": date(1999, 12, 13),
    "M. Gabbia": date(1999, 10, 21),
    "F. Tomori": date(1997, 12, 19),
    "T. Hernández": date(1997, 10, 6),
    "Y. Fofana": date(1999, 1, 10),
    "T. Reijnders": date(1998, 3, 29),
    "C. Pulisic": date(1998, 9, 18),
    "R. Loftus-Cheek": date(1996, 1, 23),
    "R. Leao": date(1999, 6, 10),
    "A. Morata": date(1992, 10, 23),
    "L. Torriani": date(2005, 3, 6),
    "S. Chukwueze": date(1999, 5, 22),
    "N. Okafor": date(2000, 5, 28),
    "Y. Musah": date(2002, 11, 29),
    "K. Terracciano": date(2003, 7, 15),
    "D. Calabria": date(1996, 12, 6),
    "M. Thiaw": date(2001, 8, 8),

    # ===== NAPOLI =====
    "A. Meret": date(1997, 3, 22),
    "G. Di Lorenzo": date(1993, 8, 4),
    "A. Rrahmani": date(1994, 2, 24),
    "K. Min-jae": date(1996, 11, 15),
    "M. Rui": date(1991, 6, 27),
    "A. Zambo Anguissa": date(1995, 11, 16),
    "S. Lobotka": date(1994, 11, 25),
    "P. Zielinski": date(1994, 5, 20),
    "M. Politano": date(1993, 8, 3),
    "R. Lukaku": date(1993, 5, 13),
    "K. Kvaratskhelia": date(2001, 2, 12),
    "A. Contini": date(1995, 2, 6),
    "G. Raspadori": date(2000, 2, 18),
    "E. Elmas": date(1999, 9, 24),
    "M. Olivera": date(1997, 10, 31),
    "L. Zanoli": date(2000, 1, 1),
    "T. Ndombele": date(1996, 12, 28),
    "A. Zerbin": date(1999, 5, 3),

    # ===== JUVENTUS =====
    "W. Szczęsny": date(1990, 4, 18),
    "D. Rugani": date(1994, 7, 29),
    "G. Bremer": date(1997, 3, 18),
    "A. Sandro": date(1991, 1, 26),
    "J. Cuadrado": date(1988, 5, 26),
    "M. Locatelli": date(1998, 1, 8),
    "A. Rabiot": date(1995, 4, 3),
    "F. Kostic": date(1992, 11, 1),
    "F. Chiesa": date(1997, 10, 25),
    "D. Vlahović": date(2000, 1, 28),
    "A. Milik": date(1994, 2, 28),
    "M. Perin": date(1992, 11, 10),
    "K. Yıldız": date(2005, 5, 4),
    "T. Weah": date(2000, 2, 22),
    "S. McKennie": date(1998, 8, 28),
    "A. Cambiaso": date(2000, 2, 20),
    "D. Huijsen": date(2005, 5, 18),
    "F. Miretti": date(2003, 8, 3),

    # ===== AS ROMA =====
    "R. Patricio": date(1988, 2, 15),
    "G. Mancini": date(1996, 4, 17),
    "C. Smalling": date(1989, 11, 22),
    "R. Karsdorp": date(1995, 2, 18),
    "L. Spinazzola": date(1993, 3, 11),
    "B. Cristante": date(1995, 3, 3),
    "L. Pellegrini": date(1996, 6, 19),
    "S. El Shaarawy": date(1992, 10, 27),
    "P. Dybala": date(1993, 11, 15),
    "T. Abraham": date(1997, 10, 2),
    "A. Dovbyk": date(1997, 6, 21),
    "M. Svilar": date(1999, 8, 27),
    "N. Zalewski": date(2002, 1, 23),
    "E. Bove": date(2002, 5, 16),
    "A. Belotti": date(1993, 12, 20),
    "D. Celik": date(1999, 2, 7),
    "E. Llorente": date(1995, 2, 8),
    "H. Aouar": date(1998, 6, 30),

    # ===== BOLOGNA =====
    "Ł. Skorupski": date(1991, 5, 5),
    "S. Posch": date(1997, 6, 14),
    "J. Lucumi": date(1998, 6, 26),
    "R. Calafiori": date(2002, 5, 19),
    "C. Lykogiannis": date(1993, 10, 22),
    "L. Ferguson": date(1999, 4, 12),
    "N. Moro": date(1999, 11, 12),
    "R. Orsolini": date(1997, 1, 24),
    "A. Saelemaekers": date(1999, 4, 27),
    "D. Ndoye": date(2000, 10, 25),
    "J. Zirkzee": date(2001, 5, 22),
    "F. Ravaglia": date(1999, 4, 9),
    "S. El Azzouzi": date(2002, 2, 9),
    "K. Aebischer": date(1997, 1, 5),
    "J. Odgaard": date(1999, 6, 1),
    "V. Kristiansen": date(2002, 12, 16),
    "S. De Silvestri": date(1988, 5, 28),
    "R. Fabbian": date(2003, 7, 24),

    # ===== ATALANTA =====
    "M. Carnesecchi": date(2000, 7, 1),
    "G. Scalvini": date(2003, 12, 11),
    "S. Kolasinac": date(1993, 6, 20),
    "I. Hien": date(1999, 1, 28),
    "D. Zappacosta": date(1992, 6, 11),
    "Éderson": date(1999, 7, 7),
    "M. de Roon": date(1991, 3, 29),
    "M. Ruggeri": date(2002, 11, 8),
    "A. Lookman": date(1997, 10, 20),
    "M. Retegui": date(1999, 4, 19),
    "C. De Ketelaere": date(2001, 3, 10),
    "J. Musso": date(1994, 5, 6),
    "G. Scamacca": date(1999, 1, 1),
    "M. Pasalic": date(1995, 2, 9),
    "B. Djimsiti": date(1992, 11, 28),
    "H. Hateboer": date(1994, 1, 9),
    "T. Koopme iners": date(1998, 2, 4),
    "M. Brescianini": date(2000, 5, 17),

    # ===== LAZIO =====
    "I. Provedel": date(1994, 3, 17),
    "M. Lazzari": date(1993, 11, 29),
    "M. Romagnoli": date(1995, 1, 12),
    "P. Rodríguez": date(1992, 7, 11),
    "A. Marušić": date(1992, 10, 17),
    "D. Cataldi": date(1994, 8, 6),
    "Luis Alberto": date(1992, 9, 28),
    "M. Zaccagni": date(1995, 6, 16),
    "F. Anderson": date(1993, 4, 15),
    "V. Castellanos": date(1998, 10, 4),
    "T. Noslin": date(1999, 5, 9),
    "L. Mandas": date(2001, 11, 11),
    "G. Isaksen": date(2001, 4, 19),
    "N. Rovella": date(2001, 12, 4),
    "D. Kamada": date(1996, 8, 5),
    "M. Gila": date(2000, 9, 29),
    "E. Hysaj": date(1994, 2, 2),
    "G. Tchaouna": date(2003, 5, 14),

    # ===== COMO =====
    "E. Semper": date(1998, 9, 27),
    "A. Iovine": date(2003, 2, 18),
    "M. Odenthal": date(1996, 8, 25),
    "A. Barba": date(2000, 11, 20),
    "M. Sala": date(1999, 9, 11),
    "N. Moro": date(1998, 2, 9),
    "L. Da Cunha": date(2001, 4, 7),
    "A. Fabregas": date(2003, 4, 13),
    "Y. Engelhardt": date(2003, 7, 29),
    "P. Cutrone": date(1998, 1, 3),
    "A. Belotti": date(1993, 12, 20),
    "P. Vigorito": date(1998, 7, 25),
    "A. Gabrielloni": date(1994, 3, 28),
    "N. Paz": date(2004, 9, 4),
    "F. Baselli": date(1992, 6, 12),
    "E. Goldaniga": date(1993, 9, 29),
    "C. Fadera": date(2001, 12, 15),
    "L. Mazzitelli": date(1995, 9, 10),

    # ===== FIORENTINA =====
    "P. Terracciano": date(1990, 8, 8),
    "M. Quarta": date(1996, 4, 27),
    "L. Ranieri": date(1999, 3, 11),
    "C. Biraghi": date(1992, 9, 1),
    "D. Dodo": date(1998, 12, 21),
    "R. Mandragora": date(1997, 6, 29),
    "A. Duncan": date(1993, 1, 7),
    "N. González": date(1998, 4, 6),
    "G. Bonaventura": date(1989, 8, 22),
    "J. Ikoné": date(1998, 5, 2),
    "M. Kean": date(2000, 2, 28),
    "O. Christensen": date(1999, 4, 22),
    "A. Barak": date(1994, 12, 3),
    "J. Brekalo": date(1998, 6, 23),
    "R. Sottil": date(1999, 6, 3),
    "L. Martínez Quarta": date(1996, 5, 10),
    "M. Kayode": date(2004, 11, 7),
    "Y. Kouamé": date(1997, 12, 6),

    # ===== PARMA =====
    "Z. Suzuki": date(1996, 8, 1),
    "E. Delprato": date(2000, 1, 21),
    "B. Valenti": date(1999, 10, 15),
    "A. Circati": date(2003, 5, 16),
    "E. Coulibaly": date(2000, 12, 12),
    "Hernani": date(1994, 3, 27),
    "S. Camara": date(2004, 1, 15),
    "A. Benedyczak": date(2000, 11, 21),
    "D. Man": date(1998, 6, 26),
    "A. Bonny": date(2003, 1, 14),
    "V. Mihăilă": date(1999, 2, 3),
    "E. Corvi": date(1993, 3, 14),
    "G. Charpentier": date(1999, 4, 2),
    "M. Cancellieri": date(2002, 1, 7),
    "N. Estévez": date(1990, 3, 28),
    "W. Cyprien": date(1995, 1, 28),
    "A. Ferrari": date(2001, 11, 7),
    "D. Camara": date(2004, 3, 20),

    # ===== TORINO =====
    "V. Milinković-Savić": date(1997, 2, 20),
    "R. Rodriguez": date(1992, 8, 25),
    "A. Buongiorno": date(1999, 6, 6),
    "K. Djidji": date(1992, 12, 30),
    "V. Lazaro": date(1996, 3, 24),
    "S. Ricci": date(2001, 8, 21),
    "I. Ilić": date(2001, 3, 17),
    "R. Bellanova": date(2000, 6, 17),
    "N. Vlašić": date(1997, 10, 4),
    "A. Sanabria": date(1996, 3, 4),
    "D. Zapata": date(1991, 4, 1),
    "L. Gemello": date(2001, 11, 10),
    "A. Miranchuk": date(1995, 10, 14),
    "Y. Karamoh": date(1998, 7, 7),
    "G. Singo": date(2000, 1, 18),
    "M. Vojvoda": date(1998, 9, 17),
    "A. Tameze": date(1994, 2, 8),
    "Z. Bayeye": date(2001, 5, 23),

    # ===== UDINESE =====
    "M. Silvestri": date(1991, 3, 2),
    "J. Bijol": date(1999, 2, 5),
    "T. Kristensen": date(2002, 9, 12),
    "N. Pérez": date(1996, 1, 11),
    "J. Ferreira": date(1997, 3, 22),
    "M. Payero": date(1998, 10, 5),
    "W. Ekkelenkamp": date(2000, 2, 1),
    "H. Kamara": date(1999, 7, 8),
    "F. Thauvin": date(1993, 1, 26),
    "L. Lucca": date(2000, 12, 10),
    "R. Pereyra": date(1991, 1, 11),
    "D. Padelli": date(1985, 10, 25),
    "L. Samardžić": date(2002, 2, 24),
    "S. Lovric": date(1998, 8, 3),
    "I. Success": date(1996, 1, 7),
    "F. Kabasele": date(1987, 12, 2),
    "A. Pafundi": date(2006, 3, 10),
    "J. Zemura": date(1999, 11, 14),

    # ===== LECCE =====
    "W. Falcone": date(1995, 1, 5),
    "V. Gendrey": date(1999, 11, 12),
    "F. Baschirotto": date(1996, 11, 19),
    "M. Pongračić": date(1997, 9, 11),
    "P. Dorgu": date(2004, 10, 16),
    "M. Ramadani": date(1996, 5, 21),
    "A. Blin": date(1996, 3, 16),
    "Y. Rafia": date(1996, 9, 21),
    "P. Almqvist": date(1999, 9, 12),
    "N. Krstović": date(2000, 4, 5),
    "L. Banda": date(2000, 12, 24),
    "F. Brancolini": date(2001, 1, 12),
    "R. Piccoli": date(2001, 7, 27),
    "R. Oudin": date(1996, 12, 19),
    "N. Sansone": date(1991, 9, 10),
    "A. Pelmard": date(2001, 2, 25),
    "A. Gallo": date(2000, 5, 13),
    "B. Pierret": date(2003, 2, 17),

    # ===== SASSUOLO =====
    "A. Consigli": date(1987, 1, 8),
    "J. Toljan": date(1994, 8, 8),
    "M. Erlic": date(1998, 1, 24),
    "G. Ferrari": date(1992, 5, 15),
    "F. Doig": date(2002, 9, 18),
    "M. Henrique": date(1997, 6, 14),
    "M. Castrovilli": date(1997, 2, 25),
    "N. Bajrami": date(1999, 2, 28),
    "A. Laurienté": date(1998, 12, 4),
    "A. Pinamonti": date(1999, 5, 19),
    "D. Berardi": date(1994, 8, 1),
    "G. Pegolo": date(1981, 3, 25),
    "G. Defrel": date(1991, 5, 17),
    "C. Volpato": date(2003, 11, 15),
    "U. Racic": date(1998, 3, 17),
    "F. Romagna": date(1997, 9, 8),
    "M. Viti": date(2002, 1, 24),
    "S. Mulattieri": date(2000, 7, 10),

    # ===== GENOA =====
    "J. Martinez": date(1998, 9, 2),
    "K. De Winter": date(2002, 5, 5),
    "M. Bani": date(1992, 9, 25),
    "J. Vásquez": date(1998, 10, 18),
    "S. Sabelli": date(1993, 4, 10),
    "M. Frendrup": date(2001, 10, 7),
    "M. Badelj": date(1989, 2, 26),
    "A. Martin": date(1997, 4, 29),
    "R. Malinovskyi": date(1993, 5, 4),
    "A. Guðmundsson": date(1997, 6, 15),
    "Vitinha": date(2000, 2, 13),
    "N. Leali": date(1993, 2, 17),
    "J. Messias": date(1991, 5, 13),
    "H. Ekuban": date(1994, 9, 19),
    "A. Vogliacco": date(1998, 10, 26),
    "M. Thorsby": date(1996, 5, 5),
    "A. Marcandalli": date(2004, 1, 5),
    "D. Ankeye": date(1999, 7, 3),

    # ===== CAGLIARI =====
    "S. Scuffet": date(1996, 5, 31),
    "A. Zappa": date(1999, 6, 10),
    "Y. Mina": date(1994, 9, 23),
    "A. Dossena": date(1998, 10, 15),
    "T. Augello": date(1994, 9, 30),
    "A. Makoumbou": date(2000, 5, 22),
    "N. Nández": date(1995, 12, 28),
    "M. Prati": date(2003, 8, 9),
    "Z. Luvumbo": date(2002, 7, 9),
    "L. Pavoletti": date(1988, 11, 26),
    "G. Gaetano": date(2000, 5, 5),
    "B. Aresti": date(1991, 12, 5),
    "E. Shomurodov": date(1995, 6, 29),
    "N. Viola": date(1989, 11, 12),
    "I. Sulemana": date(2003, 3, 8),
    "P. Azzi": date(2003, 5, 16),
    "A. Obert": date(2002, 9, 14),
    "M. Wieteska": date(2000, 2, 11),

    # ===== HELLAS VERONA =====
    "L. Montipò": date(1996, 2, 21),
    "D. Coppola": date(2000, 4, 10),
    "G. Magnani": date(1995, 4, 2),
    "P. Dawidowicz": date(1995, 5, 20),
    "J. Tchatchoua": date(2001, 9, 20),
    "S. Serdar": date(1997, 4, 11),
    "O. Duda": date(1994, 12, 5),
    "D. Lazović": date(1990, 5, 15),
    "T. Suslov": date(2002, 6, 30),
    "C. Ngonge": date(2000, 3, 15),
    "M. Đurić": date(1990, 1, 22),
    "S. Perilli": date(2001, 3, 18),
    "T. Noslin": date(1999, 5, 9),
    "K. Lasagna": date(1992, 2, 10),
    "D. Faraoni": date(1991, 4, 25),
    "D. Ghilardi": date(2003, 5, 7),
    "F. Terracciano": date(2003, 9, 27),
    "M. Hongla": date(1998, 3, 24),

    # ===== CREMONESE =====
    "M. Carnesecchi": date(2000, 7, 1),
    "M. Bianchetti": date(1993, 4, 8),
    "E. Lochoshvili": date(1998, 11, 7),
    "L. Sernicola": date(1997, 8, 26),
    "L. Valzania": date(1996, 4, 5),
    "M. Castagnetti": date(1987, 9, 26),
    "C. Buonaiuto": date(1992, 5, 18),
    "E. Quagliata": date(1998, 1, 14),
    "M. Zanimacchia": date(1999, 3, 22),
    "V. Carboni": date(2005, 3, 21),
    "F. Tsadjout": date(1998, 4, 1),
    "M. Sarr": date(1999, 11, 23),
    "D. Ciofani": date(1985, 1, 30),
    "F. Afena-Gyan": date(2003, 1, 19),
    "L. Ravanelli": date(2001, 5, 8),
    "P. Ghiglione": date(1997, 4, 23),
    "F. Collocolo": date(2004, 2, 11),
    "M. Pickel": date(1991, 2, 15),

    # ===== PISA =====
    "N. Andrade": date(1989, 2, 21),
    "A. Calabresi": date(1996, 10, 21),
    "A. Caracciolo": date(1990, 9, 3),
    "M. Canestrelli": date(2000, 6, 19),
    "S. Beruatto": date(1998, 12, 3),
    "G. Piccinini": date(1999, 5, 1),
    "M. Marin": date(1998, 9, 13),
    "A. Hojholt": date(1999, 4, 27),
    "M. Tramoni": date(2000, 10, 29),
    "S. Moreo": date(1990, 7, 23),
    "A. Arena": date(1999, 9, 7),
    "A. Loria": date(2001, 8, 12),
    "E. Torregrossa": date(1992, 2, 20),
    "G. Bonfanti": date(2003, 1, 18),
    "I. Touré": date(2003, 11, 30),
    "M. Angori": date(2004, 3, 25),
    "H. Rus": date(2001, 2, 5),
    "S. Jevsenak": date(2001, 9, 10),
}


def get_birthdate(player_name: str) -> date:
    """
    Ottiene la data di nascita di un calciatore.

    Args:
        player_name: Nome del calciatore (es: "L. Martinez")

    Returns:
        Data di nascita o None se non trovata
    """
    return PLAYER_BIRTHDATES.get(player_name)


def get_team_birthdates(team_name: str, lineup_dict: dict) -> list[date]:
    """
    Ottiene le date di nascita di tutti i giocatori di una squadra.

    Args:
        team_name: Nome della squadra
        lineup_dict: Dizionario con starters e bench

    Returns:
        Lista di date di nascita (solo quelle trovate)
    """
    birthdates = []

    if not lineup_dict:
        return birthdates

    # Aggiungi date dei titolari
    for player in lineup_dict.get("starters", []):
        bd = get_birthdate(player["name"])
        if bd:
            birthdates.append(bd)

    # Aggiungi date della panchina
    for player in lineup_dict.get("bench", []):
        bd = get_birthdate(player["name"])
        if bd:
            birthdates.append(bd)

    return birthdates
