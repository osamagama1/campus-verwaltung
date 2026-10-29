"""Füllt die Datenbank mit frei erfundenen Beispieldaten."""
from .datenbank import CampusDB
from .modelle import Modul, Studierende


def befuellen(db: CampusDB) -> None:
    if db.studierende_suchen():
        return
    module = [db.modul_anlegen(Modul(*m)) for m in [
        ("SWE", "Softwareentwicklung", 5), ("MDS", "Modellierung dynamischer Systeme", 5),
        ("NBTS", "Numerische Berechnung technischer Systeme", 5), ("PE", "Produktentwicklung", 6)]]
    personen = [db.studierende_anlegen(Studierende(*p)) for p in [
        ("Lena", "Hansen", 700101, "Maschinenbau"), ("Jonas", "Petersen", 700102, "Verfahrenstechnik"),
        ("Mia", "Schulz", 700103, "Energietechnik")]]
    noten = [[1.7, 2.3, None, 1.3], [2.0, 4.3, 2.7, None], [1.0, 1.7, 2.0, 2.3]]
    for person, zeile in zip(personen, noten):
        for modul, note in zip(module, zeile):
            db.einschreiben(person.id, modul.id)
            if note is not None:
                db.note_eintragen(person.id, modul.id, note)
