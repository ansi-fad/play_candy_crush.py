# CandyCrush Automator (11x11)

## Cum rulezi
1. Creează venv: `python -m venv .venv` (PyCharm face asta automat).
2. Instalează deps: `pip install -r requirements.txt`
3. Rulează: 
python play_candycrush.py --games 100 --rows 11 --cols 11 --target 10000 --out results/summary.csv --seed 42
4. Fișier rezultat: `results/summary.csv`

## CLI
- --games: număr jocuri (implicit 100)
- --rows/--cols: dimensiunea tablei (implicit 11)
- --target: pragul (implicit 10000)
- --input_predefined: încarcă matrice initiale din `--input_file`
- --out: cale csv iesire
- --seed: seed pentru reproducibilitate

## Format CSV rezultat
game_id,points,swaps,total_cascades,reached_target,stopping_reason,moves_to_10000
