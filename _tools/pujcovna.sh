#!/bin/bash
# Znovu vygeneruje a zašifruje stránku půjčovny.
# Použití:  bash _tools/pujcovna.sh "NoveHeslo"
# (texty a ceny se upravují v _tools/build.py v seznamu RENTAL)
set -e
cd "$(dirname "$0")/.."
PW="${1:?Zadejte heslo: bash _tools/pujcovna.sh \"heslo\"}"
python3 _tools/build.py
npx --yes staticrypt@3 _tools/pujcovna-src.html -p "$PW" --short -d _tools/out --remember 30 \
  --config _tools/.staticrypt.json \
  --template-title "Půjčovna techniky" \
  --template-instructions "Ceník je jen pro naše klienty. Heslo vám rádi pošleme: 777 272 802." \
  --template-button "Zobrazit ceník" --template-placeholder "Heslo" \
  --template-remember "Zapamatovat si mě" --template-error "Špatné heslo." \
  --template-color-primary "#0F0F0E" --template-color-secondary "#1C1C1A"
mv _tools/out/pujcovna-src.html pujcovna.html
rm -rf _tools/out _tools/pujcovna-src.html
echo "Hotovo: pujcovna.html je zašifrovaná."
