import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from campus.datenbank import CampusDB
from campus.modelle import Modul, Studierende


@pytest.fixture
def db():
    d = CampusDB(":memory:")
    yield d
    d.schliessen()


def test_anlegen_und_suchen(db):
    db.studierende_anlegen(Studierende("Lena", "Hansen", 1, "MB"))
    assert [s.name for s in db.studierende_suchen("Han")] == ["Lena Hansen"]


def test_matrikelnummer_eindeutig(db):
    db.studierende_anlegen(Studierende("A", "B", 1, "MB"))
    with pytest.raises(sqlite3.IntegrityError):
        db.studierende_anlegen(Studierende("C", "D", 1, "MB"))


def test_ects_und_gewichteter_schnitt(db):
    s = db.studierende_anlegen(Studierende("A", "B", 1, "MB"))
    m1 = db.modul_anlegen(Modul("M1", "Eins", 5))
    m2 = db.modul_anlegen(Modul("M2", "Zwei", 10))
    m3 = db.modul_anlegen(Modul("M3", "Drei", 5))
    for m, note in [(m1, 1.0), (m2, 2.5), (m3, 5.0)]:  # M3 nicht bestanden
        db.einschreiben(s.id, m.id)
        db.note_eintragen(s.id, m.id, note)
    assert db.ects_bestanden(s.id) == 15
    assert db.notenschnitt(s.id) == 2.0  # (1,0*5 + 2,5*10) / 15


def test_ungueltige_ects():
    with pytest.raises(ValueError):
        Modul("X", "Zu groß", 40)


def test_loeschen_entfernt_einschreibungen(db):
    s = db.studierende_anlegen(Studierende("A", "B", 1, "MB"))
    m = db.modul_anlegen(Modul("M1", "Eins", 5))
    db.einschreiben(s.id, m.id)
    db.studierende_loeschen(s.id)
    assert db.modulstatistik() == [("M1", 0, None)]
