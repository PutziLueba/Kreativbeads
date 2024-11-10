import sqlite3
from tkinter import Tk, Label, Entry, Button, Listbox, END, messagebox, Toplevel
from tkinter import ttk
from datetime import datetime

# Verbindung zur Datenbank
conn = sqlite3.connect('plotter.db')
cursor = conn.cursor()

# Erstellen der Tabellen, falls sie noch nicht existieren
cursor.execute('''
    CREATE TABLE IF NOT EXISTS folien (
        materialnummer TEXT PRIMARY KEY,
        hersteller TEXT,
        farbe TEXT,
        breite REAL,
        laenge REAL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS projekte (
        projekt_id INTEGER PRIMARY KEY AUTOINCREMENT,
        projektname TEXT,
        materialnummer TEXT,
        projekt_datum TEXT,
        plot_breite REAL,
        plot_laenge REAL,
        verschnitt_zugabe REAL,
        FOREIGN KEY (materialnummer) REFERENCES folien (materialnummer)
    )
''')

conn.commit()

# Funktion, um die Position des Hauptfensters abzurufen
def get_main_window_position():
    x = main_window.winfo_x()
    y = main_window.winfo_y()
    return f"+{x}+{y}"

# Funktion zum Öffnen des Fensters für das Hinzufügen und Bearbeiten einer Folie
def open_folie_hinzufuegen():
    main_window.withdraw()
    folie_window = Toplevel()
    folie_window.title("Folie hinzufügen")
    folie_window.geometry("600x500")
    folie_window.geometry(get_main_window_position())

    Label(folie_window, text="Materialnummer").grid(row=0, column=0, padx=10, pady=10)
    entry_materialnummer = Entry(folie_window)
    entry_materialnummer.grid(row=0, column=1, padx=10, pady=10)

    Label(folie_window, text="Hersteller").grid(row=1, column=0, padx=10, pady=10)
    entry_hersteller = Entry(folie_window)
    entry_hersteller.grid(row=1, column=1, padx=10, pady=10)

    Label(folie_window, text="Farbe").grid(row=2, column=0, padx=10, pady=10)
    entry_farbe = Entry(folie_window)
    entry_farbe.grid(row=2, column=1, padx=10, pady=10)

    Label(folie_window, text="Breite (cm)").grid(row=3, column=0, padx=10, pady=10)
    entry_breite = Entry(folie_window)
    entry_breite.grid(row=3, column=1, padx=10, pady=10)

    Label(folie_window, text="Länge (cm)").grid(row=4, column=0, padx=10, pady=10)
    entry_laenge = Entry(folie_window)
    entry_laenge.grid(row=4, column=1, padx=10, pady=10)

    def bestand_anzeigen():
        listbox_bestand.delete(0, END)
        cursor.execute('SELECT materialnummer, hersteller, farbe, breite, laenge FROM folien')
        folien = cursor.fetchall()
        for folie in folien:
            listbox_bestand.insert(
                END, f"Materialnummer: {folie[0]}, Hersteller: {folie[1]}, Farbe: {folie[2]}, Breite: {folie[3]} cm, Länge: {folie[4]} cm"
            )

    def folie_hinzufuegen():
        materialnummer = entry_materialnummer.get()
        hersteller = entry_hersteller.get()
        farbe = entry_farbe.get()
        breite = float(entry_breite.get())
        laenge = float(entry_laenge.get())
        
        cursor.execute(
            'INSERT INTO folien (materialnummer, hersteller, farbe, breite, laenge) VALUES (?, ?, ?, ?, ?)',
            (materialnummer, hersteller, farbe, breite, laenge)
        )
        conn.commit()
        messagebox.showinfo("Erfolg", "Folie erfolgreich hinzugefügt")
        bestand_anzeigen()
        entry_materialnummer.delete(0, END)
        entry_hersteller.delete(0, END)
        entry_farbe.delete(0, END)
        entry_breite.delete(0, END)
        entry_laenge.delete(0, END)

    # Bearbeitungs- und Löschfenster
    def folie_bearbeiten(event):
        selected_item = listbox_bestand.get(listbox_bestand.curselection())
        materialnummer = selected_item.split(",")[0].split(":")[1].strip()

        cursor.execute('SELECT * FROM folien WHERE materialnummer = ?', (materialnummer,))
        folie_data = cursor.fetchone()

        if folie_data:
            bearbeitung_window = Toplevel(folie_window)
            bearbeitung_window.title("Folie bearbeiten")
            bearbeitung_window.geometry("400x300")
            bearbeitung_window.geometry(get_main_window_position())

            Label(bearbeitung_window, text="Materialnummer").grid(row=0, column=0, padx=10, pady=10)
            edit_materialnummer = Entry(bearbeitung_window)
            edit_materialnummer.grid(row=0, column=1, padx=10, pady=10)
            edit_materialnummer.insert(0, folie_data[0])

            Label(bearbeitung_window, text="Hersteller").grid(row=1, column=0, padx=10, pady=10)
            edit_hersteller = Entry(bearbeitung_window)
            edit_hersteller.grid(row=1, column=1, padx=10, pady=10)
            edit_hersteller.insert(0, folie_data[1])

            Label(bearbeitung_window, text="Farbe").grid(row=2, column=0, padx=10, pady=10)
            edit_farbe = Entry(bearbeitung_window)
            edit_farbe.grid(row=2, column=1, padx=10, pady=10)
            edit_farbe.insert(0, folie_data[2])

            Label(bearbeitung_window, text="Breite (cm)").grid(row=3, column=0, padx=10, pady=10)
            edit_breite = Entry(bearbeitung_window)
            edit_breite.grid(row=3, column=1, padx=10, pady=10)
            edit_breite.insert(0, folie_data[3])

            Label(bearbeitung_window, text="Länge (cm)").grid(row=4, column=0, padx=10, pady=10)
            edit_laenge = Entry(bearbeitung_window)
            edit_laenge.grid(row=4, column=1, padx=10, pady=10)
            edit_laenge.insert(0, folie_data[4])

            def folie_speichern():
                neue_daten = (
                    edit_materialnummer.get(),
                    edit_hersteller.get(),
                    edit_farbe.get(),
                    float(edit_breite.get()),
                    float(edit_laenge.get()),
                    folie_data[0]  # Alte Materialnummer für WHERE-Bedingung
                )
                cursor.execute('''
                    UPDATE folien
                    SET materialnummer = ?, hersteller = ?, farbe = ?, breite = ?, laenge = ?
                    WHERE materialnummer = ?
                ''', neue_daten)
                conn.commit()
                messagebox.showinfo("Erfolg", "Folie erfolgreich aktualisiert")
                bestand_anzeigen()
                bearbeitung_window.destroy()

            def folie_loeschen():
                if messagebox.askyesno("Bestätigung", "Möchten Sie diese Folie wirklich löschen?"):
                    cursor.execute('DELETE FROM folien WHERE materialnummer = ?', (folie_data[0],))
                    conn.commit()
                    messagebox.showinfo("Erfolg", "Folie erfolgreich gelöscht")
                    bestand_anzeigen()
                    bearbeitung_window.destroy()

            Button(bearbeitung_window, text="Speichern", command=folie_speichern).grid(row=5, column=1, padx=10, pady=10)
            Button(bearbeitung_window, text="Löschen", command=folie_loeschen).grid(row=5, column=0, padx=10, pady=10)

    Button(folie_window, text="Folie hinzufügen", command=folie_hinzufuegen).grid(row=5, column=1, padx=10, pady=10)
    Button(folie_window, text="Zurück", command=lambda: (folie_window.destroy(), main_window.deiconify())).grid(row=5, column=0, padx=10, pady=10)

    Label(folie_window, text="Aktueller Folienbestand").grid(row=6, column=0, columnspan=2, padx=10, pady=10)
    listbox_bestand = Listbox(folie_window, width=90, height=10)
    listbox_bestand.grid(row=7, column=0, columnspan=2, padx=10, pady=10)
    bestand_anzeigen()

    # Doppelklick zum Bearbeiten der Folie
    listbox_bestand.bind("<Double-1>", folie_bearbeiten)

# Funktion zum Öffnen des Fensters zur Projekterstellung
def open_projekt_erstellen():
    main_window.withdraw()
    projekt_window = Toplevel()
    projekt_window.title("Projekt erstellen")
    projekt_window.geometry("600x400")
    projekt_window.geometry(get_main_window_position())

    Label(projekt_window, text="Projektname").grid(row=0, column=0, padx=10, pady=10)
    entry_projektname = Entry(projekt_window)
    entry_projektname.grid(row=0, column=1, padx=10, pady=10)

    Label(projekt_window, text="Folie auswählen").grid(row=1, column=0, padx=10, pady=10)
    folien_combobox = ttk.Combobox(projekt_window, width=30)
    folien_combobox.grid(row=1, column=1, padx=10, pady=10)

    def lade_folien():
        cursor.execute('SELECT materialnummer, hersteller, farbe FROM folien')
        folien = cursor.fetchall()
        folien_combobox['values'] = [f"{folie[0]} - {folie[1]} ({folie[2]})" for folie in folien]
    
    lade_folien()

    Label(projekt_window, text="Plot Breiten (cm, durch Komma getrennt)").grid(row=2, column=0, padx=10, pady=10)
    entry_plot_breite = Entry(projekt_window)
    entry_plot_breite.grid(row=2, column=1, padx=10, pady=10)

    Label(projekt_window, text="Plot Höhen (cm, durch Komma getrennt)").grid(row=3, column=0, padx=10, pady=10)
    entry_plot_hoehe = Entry(projekt_window)
    entry_plot_hoehe.grid(row=3, column=1, padx=10, pady=10)

    Label(projekt_window, text="Verschnitt Zugabe (cm)").grid(row=4, column=0, padx=10, pady=10)
    entry_verschnitt_zugabe = Entry(projekt_window)
    entry_verschnitt_zugabe.grid(row=4, column=1, padx=10, pady=10)

    def projekt_erstellen():
        try:
            projektname = entry_projektname.get()
            folienauswahl = folien_combobox.get()
            if not folienauswahl:
                messagebox.showwarning("Fehler", "Bitte eine Folie auswählen.")
                return
            materialnummer = folienauswahl.split(" - ")[0]

            breite_plaetze = [float(x) for x in entry_plot_breite.get().split(",")]
            hoehe_plaetze = [float(x) for x in entry_plot_hoehe.get().split(",")]
            verschnitt_zugabe = float(entry_verschnitt_zugabe.get()) if entry_verschnitt_zugabe.get() else 0
            
            if sum(breite_plaetze) > 30:
                messagebox.showwarning("Fehler", "Die Gesamtbreite der Plotts überschreitet 30 cm.")
                return

            max_hoehe = max(hoehe_plaetze)
            gesamt_laenge = max_hoehe + verschnitt_zugabe
            
            cursor.execute('SELECT laenge FROM folien WHERE materialnummer = ?', (materialnummer,))
            folien_laenge = cursor.fetchone()
            
            if folien_laenge and folien_laenge[0] >= gesamt_laenge:
                neue_laenge = folien_laenge[0] - gesamt_laenge
                cursor.execute('UPDATE folien SET laenge = ? WHERE materialnummer = ?', (neue_laenge, materialnummer))
                cursor.execute(
                    'INSERT INTO projekte (projektname, materialnummer, projekt_datum, plot_breite, plot_laenge, verschnitt_zugabe) VALUES (?, ?, ?, ?, ?, ?)',
                    (projektname, materialnummer, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), sum(breite_plaetze), max_hoehe, verschnitt_zugabe)
                )
                conn.commit()
                messagebox.showinfo("Erfolg", "Projekt erfolgreich erstellt und Folienbestand aktualisiert.")
                projekt_window.destroy()
                main_window.deiconify()
            else:
                messagebox.showwarning("Fehler", "Nicht genügend Folienlänge für dieses Projekt.")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Erstellen des Projekts: {e}")

    Button(projekt_window, text="Projekt erstellen", command=projekt_erstellen).grid(row=5, column=1, padx=10, pady=10)
    Button(projekt_window, text="Zurück", command=lambda: (projekt_window.destroy(), main_window.deiconify())).grid(row=5, column=0, padx=10, pady=10)

# Funktion zum Öffnen des Projektarchivs
def open_projekt_archiv():
    main_window.withdraw()
    archiv_window = Toplevel()
    archiv_window.title("Projektarchiv")
    archiv_window.geometry("690x400")
    archiv_window.geometry(get_main_window_position())

    Label(archiv_window, text="Projektname:").grid(row=0, column=0, padx=10, pady=5)
    entry_filter_name = Entry(archiv_window)
    entry_filter_name.grid(row=0, column=1, padx=10, pady=5)

    Label(archiv_window, text="Datum (YYYY-MM-DD):").grid(row=0, column=2, padx=10, pady=5)
    entry_filter_datum = Entry(archiv_window)
    entry_filter_datum.grid(row=0, column=3, padx=10, pady=5)

    listbox_archiv = Listbox(archiv_window, width=90)
    listbox_archiv.grid(row=1, column=0, columnspan=4, padx=10, pady=10)

    def filter_projekte():
        listbox_archiv.delete(0, END)
        projektname = entry_filter_name.get().strip()
        datum = entry_filter_datum.get().strip()
        
        query = '''
            SELECT p.projekt_id, p.projektname, f.hersteller, f.farbe, p.projekt_datum
            FROM projekte p
            JOIN folien f ON p.materialnummer = f.materialnummer
        '''
        conditions = []
        parameters = []
        
        if projektname:
            conditions.append("p.projektname LIKE ?")
            parameters.append(f"%{projektname}%")
        if datum:
            conditions.append("p.projekt_datum LIKE ?")
            parameters.append(f"%{datum}%")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        cursor.execute(query, parameters)
        projekte = cursor.fetchall()
        for projekt in projekte:
            listbox_archiv.insert(
                END, f"Projekt ID: {projekt[0]}, Name: {projekt[1]}, Hersteller: {projekt[2]}, Farbe: {projekt[3]}, Datum: {projekt[4]}"
            )

    Button(archiv_window, text="Filter anwenden", command=filter_projekte).grid(row=0, column=4, padx=10, pady=5)
    filter_projekte()
    
    # Funktion zur Anzeige der Projektdetails
    def projekt_details(event):
        selected_item = listbox_archiv.get(listbox_archiv.curselection())
        projekt_id = int(selected_item.split(",")[0].split(":")[1].strip())

        cursor.execute('''
            SELECT p.projektname, f.hersteller, f.farbe, p.projekt_datum, p.plot_breite, p.plot_laenge, p.verschnitt_zugabe
            FROM projekte p
            JOIN folien f ON p.materialnummer = f.materialnummer
            WHERE p.projekt_id = ?
        ''', (projekt_id,))
        projekt_data = cursor.fetchone()

        details_window = Toplevel(archiv_window)
        details_window.title("Projektdetails")
        details_window.geometry("400x330")
        details_window.geometry(get_main_window_position())

        Label(details_window, text="Projektname:").grid(row=0, column=0, padx=10, pady=10)
        Label(details_window, text=projekt_data[0]).grid(row=0, column=1, padx=10, pady=10)

        Label(details_window, text="Hersteller:").grid(row=1, column=0, padx=10, pady=10)
        Label(details_window, text=projekt_data[1]).grid(row=1, column=1, padx=10, pady=10)

        Label(details_window, text="Farbe:").grid(row=2, column=0, padx=10, pady=10)
        Label(details_window, text=projekt_data[2]).grid(row=2, column=1, padx=10, pady=10)

        Label(details_window, text="Datum:").grid(row=3, column=0, padx=10, pady=10)
        Label(details_window, text=projekt_data[3]).grid(row=3, column=1, padx=10, pady=10)

        Label(details_window, text="Plot Breite (cm):").grid(row=4, column=0, padx=10, pady=10)
        Label(details_window, text=f"{projekt_data[4]}").grid(row=4, column=1, padx=10, pady=10)

        Label(details_window, text="Plot Länge (cm):").grid(row=5, column=0, padx=10, pady=10)
        Label(details_window, text=f"{projekt_data[5]}").grid(row=5, column=1, padx=10, pady=10)

        Label(details_window, text="Verschnitt Zugabe (cm):").grid(row=6, column=0, padx=10, pady=10)
        Label(details_window, text=f"{projekt_data[6]}").grid(row=6, column=1, padx=10, pady=10)

        # Funktion zum Löschen des Projekts
        def projekt_loeschen():
            if messagebox.askyesno("Bestätigung", "Möchten Sie dieses Projekt wirklich löschen?"):
                cursor.execute('DELETE FROM projekte WHERE projekt_id = ?', (projekt_id,))
                conn.commit()
                messagebox.showinfo("Erfolg", "Projekt erfolgreich gelöscht.")
                details_window.destroy()
                filter_projekte()  # Aktualisiere die Liste im Projektarchiv

        Button(details_window, text="Projekt löschen", command=projekt_loeschen).grid(row=7, column=1, padx=10, pady=10)
        Button(details_window, text="Schließen", command=details_window.destroy).grid(row=7, column=0, padx=10, pady=10)

    listbox_archiv.bind("<Double-1>", projekt_details)
    Button(archiv_window, text="Schließen", command=lambda: (archiv_window.destroy(), main_window.deiconify())).grid(row=2, column=3, padx=10, pady=10)

# Hauptmenüfenster erstellen
main_window = Tk()
main_window.title("Hauptmenü - Folien- und Projektverwaltung @Kreativbeads")
main_window.geometry("600x400")
main_window.grid_rowconfigure(0, weight=1)
main_window.grid_rowconfigure(3, weight=1)
main_window.grid_columnconfigure(0, weight=1)
main_window.grid_columnconfigure(4, weight=1)

Label(main_window, text="Willkommen im Folien- und Projektverwaltungssystem!").grid(row=0, column=1, columnspan=2, padx=10, pady=20)
Button(main_window, text="Folie hinzufügen", command=open_folie_hinzufuegen).grid(row=1, column=1, padx=20, pady=10)
Button(main_window, text="Projekt erstellen", command=open_projekt_erstellen).grid(row=1, column=2, padx=20, pady=10)
Button(main_window, text="Projektarchiv anzeigen", command=open_projekt_archiv).grid(row=2, column=1, columnspan=2, padx=20, pady=20)

# Hauptschleife der GUI starten
main_window.mainloop()

# Verbindung schließen
conn.close()
