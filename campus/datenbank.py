"""Datenbankzugriff (SQLite) – Repository-Klasse mit SQL-Abfragen."""
import sqlite3
from typing import Optional

from .modelle import Modul, Studierende

SCHEMA = """
CREATE TABLE IF NOT EXISTS studierende (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vorname TEXT NOT NULL,
    nachname TEXT NOT NULL,
    matrikelnummer INTEGER NOT NULL UNIQUE,
    studiengang TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS module (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kuerzel TEXT NOT NULL UNIQUE,
    titel TEXT NOT NULL,
    ects INTEGER NOT NULL CHECK (ects BETWEEN 1 AND 30)
);
CREATE TABLE IF NOT EXISTS einschreibungen (
    studierende_id INTEGER NOT NULL REFERENCES studierende(id) ON DELETE CASCADE,
    modul_id INTEGER NOT NULL REFERENCES module(id) ON DELETE CASCADE,
    note REAL CHECK (note IS NULL OR note BETWEEN 1.0 AND 5.0),
    PRIMARY KEY (studierende_id, modul_id)
);
"""


class CampusDB:
    def __init__(self, pfad: str = "campus.db"):
        self.verbindung = sqlite3.connect(pfad)
        self.verbindung.execute("PRAGMA foreign_keys = ON")
        self.verbindung.executescript(SCHEMA)

    # --- Studierende ---------------------------------------------------
    def studierende_anlegen(self, s: Studierende) -> Studierende:
        cur = self.verbindung.execute(
            "INSERT INTO studierende (vorname, nachname, matrikelnummer, studiengang) VALUES (?, ?, ?, ?)",
            (s.vorname, s.nachname, s.matrikelnummer, s.studiengang),
        )
        self.verbindung.commit()
        s.id = cur.lastrowid
        return s

    def studierende_suchen(self, text: str = "") -> list[Studierende]:
        muster = f"%{text}%"
        zeilen = self.verbindung.execute(
            "SELECT vorname, nachname, matrikelnummer, studiengang, id FROM studierende "
            "WHERE vorname LIKE ? OR nachname LIKE ? OR CAST(matrikelnummer AS TEXT) LIKE ? "
            "ORDER BY nachname",
            (muster, muster, muster),
        ).fetchall()
        return [Studierende(*z) for z in zeilen]

    def studierende_loeschen(self, studierende_id: int) -> None:
        self.verbindung.execute("DELETE FROM studierende WHERE id = ?", (studierende_id,))
        self.verbindung.commit()

    # --- Module --------------------------------------------------------
    def modul_anlegen(self, m: Modul) -> Modul:
        cur = self.verbindung.execute(
            "INSERT INTO module (kuerzel, titel, ects) VALUES (?, ?, ?)", (m.kuerzel, m.titel, m.ects)
        )
        self.verbindung.commit()
        m.id = cur.lastrowid
        return m

    def module(self) -> list[Modul]:
        zeilen = self.verbindung.execute("SELECT kuerzel, titel, ects, id FROM module ORDER BY kuerzel").fetchall()
        return [Modul(*z) for z in zeilen]

    # --- Einschreibungen & Noten --------------------------------------
    def einschreiben(self, studierende_id: int, modul_id: int) -> None:
        self.verbindung.execute(
            "INSERT OR IGNORE INTO einschreibungen (studierende_id, modul_id) VALUES (?, ?)",
            (studierende_id, modul_id),
        )
        self.verbindung.commit()

    def note_eintragen(self, studierende_id: int, modul_id: int, note: float) -> None:
        self.verbindung.execute(
            "UPDATE einschreibungen SET note = ? WHERE studierende_id = ? AND modul_id = ?",
            (note, studierende_id, modul_id),
        )
        self.verbindung.commit()

    # --- Auswertungen --------------------------------------------------
    def ects_bestanden(self, studierende_id: int) -> int:
        """Summe der ECTS aller bestandenen Module (Note <= 4,0)."""
        (summe,) = self.verbindung.execute(
            "SELECT COALESCE(SUM(m.ects), 0) FROM einschreibungen e JOIN module m ON m.id = e.modul_id "
            "WHERE e.studierende_id = ? AND e.note <= 4.0",
            (studierende_id,),
        ).fetchone()
        return summe

    def notenschnitt(self, studierende_id: int) -> Optional[float]:
        """ECTS-gewichteter Notendurchschnitt der bestandenen Module."""
        (schnitt,) = self.verbindung.execute(
            "SELECT SUM(e.note * m.ects) / SUM(m.ects) FROM einschreibungen e "
            "JOIN module m ON m.id = e.modul_id WHERE e.studierende_id = ? AND e.note <= 4.0",
            (studierende_id,),
        ).fetchone()
        return round(schnitt, 2) if schnitt is not None else None

    def modulstatistik(self) -> list[tuple]:
        """Pro Modul: Kürzel, Anzahl Teilnehmende, Durchschnittsnote."""
        return self.verbindung.execute(
            "SELECT m.kuerzel, COUNT(e.studierende_id), ROUND(AVG(e.note), 2) FROM module m "
            "LEFT JOIN einschreibungen e ON e.modul_id = m.id GROUP BY m.id ORDER BY m.kuerzel"
        ).fetchall()

    def schliessen(self) -> None:
        self.verbindung.close()
