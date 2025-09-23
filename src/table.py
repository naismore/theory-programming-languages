import csv
from dataclasses import dataclass


@dataclass
class Line:
    number: int
    symbol: str
    first_set: list[str]
    shift: bool
    error: bool
    pointer: int | None
    stack: bool
    end: bool


def write_table(table_data: list[Line]) -> None:
    with open("table.csv", "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter=";")
        for entry in table_data:
            writer.writerow([entry.number, entry.symbol, " ".join(sorted(entry.first_set)), "+" if entry.shift else "-",
                             "+" if entry.error else "-", entry.pointer, "+" if entry.stack else "-",
                             "+" if entry.end else "-"])


def read_table() -> list[Line]:
    with open("table.csv", "r", encoding="utf-8", newline="") as file:
        reader = csv.reader(file, delimiter=";")
        table_entries = []
        for row in reader:
            pointer_str = row[5].strip()
            pointer_val = int(pointer_str) if pointer_str else None

            table_entries.append(
                Line(number=int(row[0]), symbol=row[1], first_set=row[2].split() if row[2] else [], shift=row[3] == "+",
                     error=row[4] == "+", pointer=pointer_val, stack=row[6] == "+", end=row[7] == "+"))
        return table_entries