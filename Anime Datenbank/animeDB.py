from mysql.connector import Error 
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox, PhotoImage, Label
from tkinter import ttk
import json
import sqlite3
import os


class AnimeDatabaseApp:

    def __init__(self, master):
        self.master = master
        self.master.title("Anime Datenbank")
        self.master.configure(bg = 'lightblue')

        self.connection = None
        self.cursor = None
        self.connectDB()
        self.create_table()

        self.frame_input = tk.Frame(master, bg = 'lightblue')
        self.frame_input.pack(pady = 10)

        self.frame_filter = tk.Frame(master, bg = 'lightblue')
        self.frame_filter.pack(pady = 10)
        
        self.frame_listbox = tk.Frame(master, bg = 'lightblue')
        self.frame_listbox.pack(pady = 10)
        
        self.setup_input_fields()
        self.setup_filter_field()
        self.setup_star_rating()
        self.setup_submit_button()
        self.setup_clear_button()
        self.setup_listbox()



    def connectDB(self):
        try:

            self.connection = sqlite3.connect('anime.db')
            self.cursor = self.connection.cursor()
            print("Erfolgreich mit der Datenbank verbunden.")
        except Error as e:
            print(f"Fehler beim Verbinden mit der Datenbank: {e}")


            # self.connection = sqlite3.connect(
            #    host = config['db_host'],
            #    user = config['db_user'],
            #    password = config['db_password'],
            #    database = config['db_name']
            #)

    def create_table(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS anime (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            name TEXT,
            category TEXT,
            rating REAL NOT NULL,
            created_at DATETIME NOT NULL
    );
    """
        self.cursor.execute(create_table_query)

    
    #Erstellt den Table anime
    #def create_table (self):
    #        create_table_query = """
    #        CREATE TABLE IF NOT EXISTS anime (
    #            id INT AUTO_INCREMENT PRIMARY KEY, 
    #            name VARCHAR(100),
    #            category VARCHAR(100),
    #            rating FLOAT NOT NULL,
    #            created_at DATETIME NOT NULL
    #            );
    #            """
    #        self.cursor.execute(create_table_query)

    #Query = Anfrage an DB die abgerufen werden können
    #%s, %s ist quasi ein Platzhalter für Parameter die später ersetzt werden, bezogen auf name & age in dem case
    def insertanime(self, name, category, rating): 
            created_at = datetime.now()
            insert_query = """
            INSERT INTO anime (name, category, rating, created_at) VALUES (?, ?, ?, ?);
            """
    #-^ Die Drei """ erstellt mehrzeilige Strings
    #Die geaddeten Daten zu name & category
            data = (name, category, rating, created_at)

    #Hier wird die Abfrage ausgeführt
            
            try:
                self.cursor.execute(insert_query, data)
                self.connection.commit()
            except Error as e:
                print(f"Fehler beim Hinzufügen{e}")

    def setup_input_fields(self):
        tk.Label(self.frame_input, text ="Name des Anime:", bg = 'lightblue').grid(row=0, column = 0, padx = 5, pady = 5)
        self.entry_name = tk.Entry(self.frame_input)
        self.entry_name.grid(row = 0, column = 1, padx = 5, pady = 5)


        tk.Label(self.frame_input, text="Kategorie:", bg='lightblue').grid(row=1, column=0, padx=5, pady=5)
        self.combo_input_category = ttk.Combobox(self.frame_input, values=self.categories)
        self.combo_input_category.grid(row=1, column=1, padx=5, pady=5)



    categories = [
        "Action", "Adventure", "Comedy", "Drama", "Horror", 
        "Romantic", "Sci-Fi", "Sport", "Slice of Life", 
        "Thriller", "Mecha", "Isekai", "Historical",
        "Psychological", "Music"
    ]

    
    def setup_star_rating(self):
        self.star_rating = StarRating(self.master)


    def setup_submit_button(self):
        submit_button = tk.Button(self.frame_input, text = "Daten einfügen", command = self.submit_data)
        submit_button.grid(row = 2, columnspan = 2, pady = 10)  

    def setup_filter_field(self):
        tk.Label(self.frame_filter, text = "Zeitraum zum Filtern:", bg = 'lightblue').pack()
        
        timeframes = [
            "Vor 7 Tagen", "Vor 1 Monat", "Vor 3 Monaten", 
            "Vor 6 Monaten", "Vor 1 Jahr", "Vor 2 Jahren", 
            "Vor 3 Jahren", "Neuste", "Älteste"
        ]

        self.combo_filter_timeframe=ttk.Combobox(self.frame_filter, values = timeframes)
        self.combo_filter_timeframe.pack()

        tk.Label(self.frame_filter, text = "Kategorie zum Filtern: ", bg = 'lightblue').pack()
        self.combo_filter_category = ttk.Combobox(self.frame_filter, values = self.categories)
        self.combo_filter_category.pack()

        filter_button = tk.Button(self.frame_filter, text = "Filter anwenden", command = self.apply_filter)
        filter_button.pack(pady = 5)

    def setup_listbox(self):
        self.listbox = tk.Listbox(self.frame_listbox, width = 50)
        self.listbox.pack(pady = 10)

        self.refresh_listbox()


    def submit_data(self):
        name = self.entry_name.get()
        category = self.combo_input_category.get()
        rating = self.star_rating.get_rating()

        if name and category and rating:
            try:
                rating = float(rating)
                self.insertanime(name, category, rating)
                self.connection.commit()
                messagebox.showinfo("Erfolg", "Daten erfolgreich eingefügt!")
                self.fetch_anime()
                self.refresh_listbox()
            except ValueError:
                 messagebox.showerror("Ungültige Eingabe", "Bitte geben Sie eine gültige Zahl für das Rating ein.")

            except Error as e:
                messagebox.showerror("Fehler", f"Fehler: '{e}'")

        else:
             messagebox.showwarning("Bitte alle Felder ausfüllen.")


    def fetch_anime(self, filter_created_at=None, filter_category=None):
        try:
            query = "SELECT name, category, rating, created_at FROM anime"
            filters = []
            params = []

            if filter_created_at:
                filters.append("created_at >= %s")
                params.append(filter_created_at)
           
            if filter_category:
                filters.append("category = %s")
                params.append(filter_category)

            if filters:
                query += " WHERE " + " AND ".join(filters)
            else:
                query += " ORDER BY created_at ASC"

            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Error as e:
            messagebox.showerror("Fehler", f"Fehler: '{e}'")




    def refresh_listbox(self, filter_created_at = None, filter_category = None):
        self.listbox.delete(0, tk.END)
        rows = self.fetch_anime(filter_created_at, filter_category)

        if rows:
            for row in rows:
                self.listbox.insert(tk.END, f"{row[0]} - {row[1]} - {row[2]} - {row[3]}")

    def apply_filter(self):
        filter_timeframe = self.combo_filter_timeframe.get()
        filter_category = self.combo_filter_category.get()
        filter_created_at = None

        if filter_timeframe == "Vor 7 Tagen":
            filter_created_at = datetime.now() - timedelta(days=7)
        elif filter_timeframe == "Vor 1 Monat":
            filter_created_at = datetime.now() - timedelta(days=30)
        elif filter_timeframe == "Vor 3 Monaten":
            filter_created_at = datetime.now() - timedelta(days=90)
        elif filter_timeframe == "Vor 6 Monaten":
            filter_created_at = datetime.now() - timedelta(days=180)
        elif filter_timeframe == "Vor 1 Jahr":
            filter_created_at = datetime.now() - timedelta(days=365)
        elif filter_timeframe == "Vor 2 Jahren":
            filter_created_at = datetime.now() - timedelta(days=730)
        elif filter_timeframe == "Vor 3 Jahren":
            filter_created_at = datetime.now() - timedelta(days=1095)
        elif filter_timeframe == "Neueste":
            filter_created_at = datetime.min()  # Setze auf das früheste Datum
        elif filter_timeframe == "Älteste":
            filter_created_at = datetime.now()  # Setze auf das aktuelle Datum
        
        self.refresh_listbox(filter_created_at, filter_category)


    def clear_data(self):
        if messagebox.askyesno("Bestätigung", "Sind Sie sicher, dass Sie alle Daten löschen möchten?"):

            try:
                delete_query = "DELETE FROM anime;"
                self.cursor.execute(delete_query)
                self.connection.commit()
                messagebox.showinfo("Erfolg", "Alle Daten wurden gelöscht!")
                self.refresh_listbox()

            except Error as e:
                messagebox.showerror("Fehler", f"Fehler: '{e}'")


    def setup_clear_button(self):
        clear_button= tk.Button(self.frame_input, text = "Clear Button", command = self.clear_data, width = 8, height = 1, font = ("Arial", 7))
        clear_button.grid(row = 3, columnspan = 2, pady = 10) 

class StarRating:
    def __init__(self, master, initial_rating=0.0):
        self.fullstar_image = PhotoImage(file='images/resized_fullstar.PNG')
        self.halfstar_image = PhotoImage(file='images/resized_halfstar.PNG')
        self.emptystar_image = PhotoImage(file='images/resized_emptystar.PNG')
 
        self.stars = [Label(master, image=self.emptystar_image) for _ in range(5)]
        self.rating = initial_rating
#Master definiert die Beziehung zwischen Widgets
        for i, star in enumerate(self.stars):
            star.pack(side=tk.LEFT, padx = 2, pady = (0, 5))
            star.bind('<Button-1>', lambda event, index = i: self.set_rating(event, index))

        self.update_stars()




    def set_rating(self, event, index):

        x_position = event.x

        if x_position < event.widget.winfo_width() / 2:
            self.rating = index + 0.5
        else:
            self.rating = index + 1
        self.update_stars()

    def update_stars(self):
        full_stars = int(self.rating)
        half_star = self.rating - full_stars >= 0.5

        for i, star in enumerate(self.stars):
            if i < full_stars:
                star.config(image=self.fullstar_image)
            elif i == full_stars and half_star:
                star.config(image=self.halfstar_image)
            else:
                star.config(image=self.emptystar_image)

    def get_rating(self):
        return self.rating
       

if __name__ == "__main__":
    root = tk.Tk()
    app = AnimeDatabaseApp(root)
    root.mainloop()

  



