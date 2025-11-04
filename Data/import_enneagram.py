#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Імпорт психологічного тесту Енеаграми з Excel у pairs.json.

Підтримка:
- Аркуш із двома рядками на кожну пару (однаковий № пари в першій колонці).
- Текст твердження у другій колонці.
- Стовпці A..I позначають шкалу твердження (значення '1' або символи 'x','X','х','Х','×','✗','✘').
- На виході: pairs.json (масив з 144 елементів, кожен елемент — пара з left/right і відповідною шкалою).

Виклик:
    python import_enneagram.py --excel "Тест_старт.xlsx" --sheet "Основа" --out "pairs.json"
"""

import pandas as pd
import json
import os
import sys

# === ТУТ МОЖНА ЗМІНИТИ СВОЇ НАЗВИ ФАЙЛІВ ==========================
EXCEL_FILE = "Test.xlsx"     # твій Excel-файл з питаннями
SHEET_NAME = "Основа"        # назва аркуша в Excel
OUT_FILE = "pairs.json"      # куди зберегти результат
# ===================================================================

ACCEPTED_MARKS = {"1", "1.0", "x", "X", "х", "Х", "×", "✗", "✘"}
SCALES = list("ABCDEFGHI")

def normalize_mark(v):
    if pd.isna(v): return 0
    s = str(v).strip()
    return 1 if s in ACCEPTED_MARKS else 0

def detect_columns(df):
    id_col = df.columns[0]
    text_col = df.columns[1]
    scale_cols = [c for c in df.columns if isinstance(c, str) and c in SCALES]
    if not scale_cols:
        raise ValueError("Не знайдено колонок A..I зі шкалами")
    return id_col, text_col, scale_cols

def row_scale(row, scale_cols):
    marks = [c for c in scale_cols if normalize_mark(row.get(c)) == 1]
    return marks[0] if len(marks) == 1 else None

def build_pairs(df):
    id_col, text_col, scale_cols = detect_columns(df)
    groups = df.groupby(id_col, dropna=True, sort=True)
    pairs = []
    for key, g in groups:
        g = g.reset_index(drop=True)
        if len(g) != 2:
            continue
        left_row, right_row = g.iloc[0], g.iloc[1]
        left_text = str(left_row.get(text_col, "")).strip()
        right_text = str(right_row.get(text_col, "")).strip()
        left_scale = row_scale(left_row, scale_cols)
        right_scale = row_scale(right_row, scale_cols)
        if left_text and right_text and left_scale and right_scale:
            pairs.append({
                "pair": int(key) if pd.notna(key) else None,
                "left": {"text": left_text, "scale": left_scale},
                "right": {"text": right_text, "scale": right_scale}
            })
    return pairs

def main():
    if not os.path.exists(EXCEL_FILE):
        print(f"❌ Не знайдено файл {EXCEL_FILE}")
        sys.exit(1)

    print(f"📘 Імпорт із '{EXCEL_FILE}', аркуш '{SHEET_NAME}'...")
    df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)
    pairs = build_pairs(df)

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(pairs, f, ensure_ascii=False, indent=2)

    print(f"✅ Збережено {len(pairs)} пар у '{OUT_FILE}'")

if __name__ == "__main__":
    main()