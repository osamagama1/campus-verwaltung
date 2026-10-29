"""Grafische Oberfläche (Tkinter) für die Campus-Verwaltung."""
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

from .datenbank import CampusDB
from .modelle import Studierende


class CampusApp(tk.Tk):
    def __init__(self, db: CampusDB):
        super().__init__()
        self.db = db
        self.title("Campus-Verwaltung")
        self.geometry("820x420")
        self._formular_bauen()
        self._tabelle_bauen()
        self.aktualisieren()

    def _formular_bauen(self):
        rahmen = ttk.LabelFrame(self, text="Neue Studierende")
        rahmen.pack(fill="x", padx=10, pady=8)
        self.felder = {}
        for spalte, name in enumerate(["Vorname", "Nachname", "Matrikelnr.", "Studiengang"]):
            ttk.Label(rahmen, text=name).grid(row=0, column=spalte, padx=4, sticky="w")
            eingabe = ttk.Entry(rahmen, width=18)
            eingabe.grid(row=1, column=spalte, padx=4, pady=4)
            self.felder[name] = eingabe
        ttk.Button(rahmen, text="Hinzufügen", command=self.hinzufuegen).grid(row=1, column=4, padx=6)

        suche = ttk.Frame(self)
        suche.pack(fill="x", padx=10)
        ttk.Label(suche, text="Suche:").pack(side="left")
        self.suchtext = tk.StringVar()
        self.suchtext.trace_add("write", lambda *_: self.aktualisieren())
        ttk.Entry(suche, textvariable=self.suchtext, width=30).pack(side="left", padx=6)
        ttk.Button(suche, text="Löschen", command=self.loeschen).pack(side="right")

    def _tabelle_bauen(self):
        spalten = ("name", "matrikel", "studiengang", "ects", "schnitt")
        self.tabelle = ttk.Treeview(self, columns=spalten, show="headings")
        breiten = [220, 110, 200, 80, 80]
        for spalte, titel, breite in zip(spalten, ["Name", "Matrikelnr.", "Studiengang", "ECTS", "Ø Note"], breiten):
            self.tabelle.heading(spalte, text=titel)
            self.tabelle.column(spalte, width=breite, anchor="w" if breite > 100 else "center")
        self.tabelle.pack(fill="both", expand=True, padx=10, pady=8)

    def aktualisieren(self):
        self.tabelle.delete(*self.tabelle.get_children())
        for s in self.db.studierende_suchen(self.suchtext.get()):
            schnitt = self.db.notenschnitt(s.id)
            self.tabelle.insert("", "end", iid=str(s.id), values=(
                s.name, s.matrikelnummer, s.studiengang, self.db.ects_bestanden(s.id),
                f"{schnitt:.2f}" if schnitt else "–"))

    def hinzufuegen(self):
        werte = {k: e.get().strip() for k, e in self.felder.items()}
        if not all(werte.values()) or not werte["Matrikelnr."].isdigit():
            messagebox.showwarning("Eingabe prüfen", "Bitte alle Felder ausfüllen (Matrikelnr. nur Ziffern).")
            return
        try:
            self.db.studierende_anlegen(Studierende(werte["Vorname"], werte["Nachname"],
                                                    int(werte["Matrikelnr."]), werte["Studiengang"]))
        except sqlite3.IntegrityError:
            messagebox.showerror("Fehler", "Diese Matrikelnummer existiert bereits.")
            return
        for e in self.felder.values():
            e.delete(0, "end")
        self.aktualisieren()

    def loeschen(self):
        auswahl = self.tabelle.selection()
        if auswahl and messagebox.askyesno("Löschen", "Ausgewählte Person wirklich löschen?"):
            self.db.studierende_loeschen(int(auswahl[0]))
            self.aktualisieren()
