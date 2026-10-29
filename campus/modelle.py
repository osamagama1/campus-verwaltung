"""Datenklassen (OOP) für die Campus-Verwaltung."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Person:
    vorname: str
    nachname: str

    @property
    def name(self) -> str:
        return f"{self.vorname} {self.nachname}"


@dataclass
class Studierende(Person):
    matrikelnummer: int
    studiengang: str
    id: Optional[int] = None


@dataclass
class Modul:
    kuerzel: str
    titel: str
    ects: int
    id: Optional[int] = None

    def __post_init__(self):
        if not 1 <= self.ects <= 30:
            raise ValueError("ECTS müssen zwischen 1 und 30 liegen")
