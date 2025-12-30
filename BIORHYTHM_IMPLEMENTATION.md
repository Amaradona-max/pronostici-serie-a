# Sistema Bioritmi Calciatori - Documentazione Implementazione

## Panoramica

Implementazione completa del sistema di bioritmi per l'analisi delle performance dei calciatori basato sulla teoria dei cicli biologici. Il sistema calcola tre tipi di bioritmi per ogni giocatore e fornisce analisi aggregate per squadra.

## Teoria dei Bioritmi

I bioritmi seguono tre cicli sinusoidali dalla nascita:

1. **Bioritmo Fisico** (23 giorni)
   - Influenza: forza, resistenza, coordinazione, velocità
   - Peso nel calcolo: 50%

2. **Bioritmo Emotivo** (28 giorni)
   - Influenza: umore, creatività, stabilità mentale
   - Peso nel calcolo: 30%

3. **Bioritmo Intellettuale** (33 giorni)
   - Influenza: concentrazione, memoria, tattica, decisioni
   - Peso nel calcolo: 20%

### Formula di Calcolo

```
Bioritmo = sin(2π × giorni_dalla_nascita / periodo) × 100
Overall = (Fisico × 0.5) + (Emotivo × 0.3) + (Intellettuale × 0.2)
```

### Interpretazione Valori

- **> 50**: Eccellente (fase ascendente alta)
- **0 a 50**: Buono (fase ascendente)
- **-50 a 0**: Basso (fase discendente)
- **< -50**: Critico (fase discendente bassa)

## Implementazione Backend

### File Creati

1. **`app/utils/biorhythm.py`**
   - Funzioni di calcolo bioritmi
   - Algoritmi per confronto squadre
   - Identificazione giorni critici
   - Previsioni multi-giorno

2. **`app/data/player_birthdates.py`**
   - Database di 356 calciatori Serie A
   - Date di nascita realistiche
   - Funzioni di lookup per nome giocatore
   - Helper per estrazione date per squadra

3. **`app/api/schemas.py`** (esteso)
   - `PlayerBiorhythm`: bioritmi singolo giocatore
   - `TeamBiorhythm`: statistiche aggregate squadra
   - `FixtureBiorhythmsResponse`: risposta completa per partita

4. **`app/api/endpoints/predictions.py`** (esteso)
   - Endpoint `GET /api/v1/predictions/{fixture_id}/biorhythms`
   - Calcolo bioritmi per entrambe le squadre
   - Top 3 performers per squadra
   - Determinazione vantaggio biorhythm

### Endpoint API

**GET** `/api/v1/predictions/{fixture_id}/biorhythms`

**Risposta:**
```json
{
  "fixture_id": 123,
  "match_date": "2025-12-30T20:00:00Z",
  "home_team_biorhythm": {
    "team_name": "Inter",
    "avg_physical": 15.3,
    "avg_emotional": -5.2,
    "avg_intellectual": 22.1,
    "avg_overall": 12.4,
    "players_excellent": 3,
    "players_good": 5,
    "players_low": 2,
    "players_critical": 1,
    "total_players": 11,
    "top_performers": [
      {
        "player_name": "L. Martinez",
        "position": "FW",
        "physical": 94.2,
        "emotional": -62.1,
        "intellectual": -81.3,
        "overall": 12.1,
        "status": "good"
      }
    ]
  },
  "away_team_biorhythm": { ... },
  "biorhythm_advantage": "home"  // o "away" o "neutral"
}
```

## Implementazione Frontend

### Componente React

**`components/predictions/TeamBiorhythms.tsx`**

Caratteristiche:
- Visualizzazione bioritmi medi per squadra
- Griglia con 4 valori (Fisico, Emotivo, Intellettuale, Overall)
- Color coding basato sul valore:
  - Verde: > 50 (eccellente)
  - Blu: 0-50 (buono)
  - Arancione: -50-0 (basso)
  - Rosso: < -50 (critico)
- Distribuzione giocatori per status
- Top 3 performers con dettaglio bioritmi
- Indicatore vantaggio squadra
- Banner informativo sulla teoria

### Integrazione

Il componente è integrato in `FixtureCard.tsx` insieme a:
- Expected Goals
- Scorer Probabilities
- Probable Lineups

## Database Calciatori

### Copertura

- **356 calciatori** della Serie A 2024-25
- **20 squadre** complete
- Date di nascita da fonti open-source:
  - Transfermarkt
  - Wikipedia
  - Database pubblici

### Squadre Coperte

Inter, AC Milan, Napoli, Juventus, AS Roma, Bologna, Atalanta, Lazio, Como, Fiorentina, Parma, Torino, Udinese, Lecce, Sassuolo, Genoa, Cagliari, Hellas Verona, Cremonese, Pisa

## Test e Validazione

### Test Suite

File: `test_biorhythm.py`

Test implementati:
1. **Calcolo Base**: verifica formula matematica
2. **Giocatori Reali**: test con 5 top players
3. **Confronto Squadre**: simulazione Inter vs Milan
4. **Copertura Database**: verifica 356 giocatori

### Risultati Test

```
============================================================
TUTTI I TEST SUPERATI! ✓
============================================================
```

Esempio output:
```
L. Martinez    | Overall: +12.1  | Status: good    | F:+94 E:-62 I:-81
M. Thuram      | Overall: +24.0  | Status: good    | F:-0  E:+22 I:+87
C. Pulisic     | Overall: +27.4  | Status: good    | F:+100 E:-62 I:-19
```

## Fonti e References

### Teoria Biorhythm

- [Biorhythm Calculator](https://www.biorhythm-calculator.net/)
- [Biorhythm (Pseudoscience) - Wikipedia](https://en.wikipedia.org/wiki/Biorhythm_(pseudoscience))
- [Biorhythm Theory - HMRRC](https://www.hmrrc.com/members/pacesetter/2021/november/biorhythm-theory)

### Note Scientifiche

⚠️ **Disclaimer**: La teoria dei bioritmi è considerata pseudoscienza dalla comunità scientifica. Questa implementazione è fornita come strumento di analisi aggiuntivo e non dovrebbe essere l'unico fattore nelle decisioni di predizione.

## Utilizzo

### Per sviluppatori

```python
from app.utils.biorhythm import calculate_player_biorhythm
from app.data.player_birthdates import get_birthdate
from datetime import date

# Calcola bioritmo di un giocatore
birthdate = get_birthdate("L. Martinez")
match_date = date(2025, 12, 30)
bio = calculate_player_biorhythm(birthdate, match_date)

print(f"Overall: {bio.overall:.1f}")
print(f"Status: {bio.status}")
```

### Per frontend

```tsx
import { TeamBiorhythms } from '@/components/predictions/TeamBiorhythms'

<TeamBiorhythms
  fixtureId={123}
  homeTeamName="Inter"
  awayTeamName="Milan"
/>
```

## Prossimi Sviluppi Possibili

1. **Giorni Critici**: evidenziare quando un giocatore attraversa lo zero
2. **Trend Chart**: grafico andamento bioritmi ultimi 7 giorni
3. **Correlazione Predizioni**: integrare bioritmi nel modello xG
4. **Alert System**: notifiche quando tutta la squadra è in fase critica
5. **Historical Analysis**: correlazione risultati passati con bioritmi

## Maintenance

- Aggiornare `player_birthdates.py` ad ogni mercato
- Verificare date di nascita da fonti ufficiali
- Testare con nuove squadre se cambiano in Serie A

---

**Implementato il**: 30 Dicembre 2025
**Versione**: 1.0.0
**Status**: ✅ Production Ready
