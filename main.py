"""Startet die Campus-Verwaltung.

  python main.py            -> grafische Oberfläche
  python main.py --bericht  -> Auswertung in der Konsole
"""
import sys

from campus.beispieldaten import befuellen
from campus.datenbank import CampusDB


def bericht(db: CampusDB) -> None:
    print(f"{'Name':<18}{'ECTS':>6}{'Ø Note':>8}")
    for s in db.studierende_suchen():
        schnitt = db.notenschnitt(s.id)
        print(f"{s.name:<18}{db.ects_bestanden(s.id):>6}{(f'{schnitt:.2f}' if schnitt else '–'):>8}")
    print("\nModul   Teilnehmende  Ø Note")
    for kuerzel, anzahl, schnitt in db.modulstatistik():
        print(f"{kuerzel:<8}{anzahl:>12}  {schnitt if schnitt is not None else '–'}")


if __name__ == "__main__":
    datenbank = CampusDB("campus.db")
    befuellen(datenbank)
    if "--bericht" in sys.argv:
        bericht(datenbank)
    else:
        from campus.gui import CampusApp
        CampusApp(datenbank).mainloop()
    datenbank.schliessen()
