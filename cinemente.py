import os
import sqlite3
import random
import requests
import tkinter as tk
from tkinter import messagebox, simpledialog

# Config
TMDB_API_URL = 'https://api.themoviedb.org/3'
DB_PATH = 'movies_history.db'

# Local DB initialization for user history
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS history (
            film_id INTEGER PRIMARY KEY,
            title TEXT,
            seen_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# TMDB API helper functions
def tmdb_request(path, api_key, params=None):
    if params is None:
        params = {}
    params['api_key'] = api_key
    resp = requests.get(f"{TMDB_API_URL}{path}", params=params)
    resp.raise_for_status()
    return resp.json()

# Fetch genre list
def get_genre_map(api_key):
    data = tmdb_request('/genre/movie/list', api_key, {'language': 'it-IT'})
    return {g['name']: g['id'] for g in data['genres']}

# Discover movies based on filters
def discover_movies(api_key, filters):
    params = {
        'language': 'it-IT',
        'sort_by': 'popularity.desc'
    }
    if filters.get('genre_id'):
        params['with_genres'] = filters['genre_id']
    if filters.get('period_gte'):
        params['primary_release_date.gte'] = filters['period_gte']
    if filters.get('period_lte'):
        params['primary_release_date.lte'] = filters['period_lte']
    if filters.get('famous') is not None:
        if filters['famous']:
            params['vote_count.gte'] = 1000
        else:
            params['vote_count.lte'] = 200
    if filters.get('original_language'):
        params['with_original_language'] = filters['original_language']
    movies = []
    for page in range(1, 6):
        params['page'] = page
        data = tmdb_request('/discover/movie', api_key, params)
        movies.extend(data.get('results', []))
        if page >= data.get('total_pages', 1):
            break
    return movies

# Filter by runtime and series
def filter_movies(api_key, movies, filters):
    results = []
    for m in movies:
        details = tmdb_request(f"/movie/{m['id']}", api_key, {'language': 'it-IT'})
        runtime = details.get('runtime')
        dur = filters.get('duration')
        if dur == 'Meno di 90 minuti' and (runtime is None or runtime >= 90):
            continue
        if dur == 'Circa 90-120 minuti' and (runtime is None or runtime < 90 or runtime > 120):
            continue
        if dur == 'Più di 2 ore' and (runtime is None or runtime <= 120):
            continue
        series_pref = (filters.get('series') == 'Saga/franchise')
        belongs = details.get('belongs_to_collection') is not None
        if series_pref != belongs:
            continue
        results.append({'id': m['id'], 'title': m['title']})
    return results

# Record seen film
def record_history(film_id, title):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO history(film_id, title) VALUES(?,?)', (film_id, title))
    conn.commit()
    conn.close()

# Check history
def is_seen(film_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT 1 FROM history WHERE film_id = ?', (film_id,))
    seen = c.fetchone() is not None
    conn.close()
    return seen

# Main GUI
class RecommenderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Movie Recommender")
        self.geometry("600x450")
        self.resizable(True, True)
        # Prompt API key
        self.api_key = simpledialog.askstring("TMDB API Key", "Inserisci la tua TMDB API Key:", parent=self)
        if not self.api_key:
            messagebox.showerror("Errore", "API Key necessaria per continuare.")
            self.destroy()
            return
        # Load genre map
        try:
            self.genre_map = get_genre_map(self.api_key)
        except Exception as e:
            messagebox.showerror("Errore API", f"Impossibile caricare i generi: {e}")
            self.destroy()
            return
        # Questions setup
        self.questions = [
            ("Quale genere di film preferisci?", list(self.genre_map.keys())),
            ("Qual è il periodo preferito per la produzione del film?", ["Classici (prima del 1980)", "Anni ’80 e ’90", "Anni 2000-2010", "Recenti (dal 2010 a oggi)"]),
            ("Quanto tempo hai a disposizione per guardare un film?", ["Meno di 90 minuti", "Circa 90-120 minuti", "Più di 2 ore"]),
            ("Che tipo di finale preferisci?", ["Finale aperto", "Finale lieto", "Finale tragico", "Finale imprevedibile"]),
            ("Preferisci un film famoso o uno meno conosciuto?", ["Famoso", "Poco conosciuto"]),
            ("Hai una preferenza sulla nazionalità del film?", ["Americana", "Europea", "Asiatica", "Nessuna preferenza"]),
            ("Preferisci film singoli o facenti parte di una saga/franchise?", ["Singolo", "Saga/franchise"]),
        ]
        self.answers = {}
        self.current = 0
        # UI Elements
        self.question_label = tk.Label(self, text="", wraplength=550, font=(None, 14))
        self.question_label.pack(pady=20)
        self.var = tk.StringVar()
        self.options_frame = tk.Frame(self)
        self.options_frame.pack(pady=10)
        self.btn_frame = tk.Frame(self)
        self.btn_frame.pack(pady=20)
        self.back_btn = tk.Button(self.btn_frame, text="Indietro", command=self.prev_question, state='disabled')
        self.back_btn.pack(side='left', padx=5)
        self.next_btn = tk.Button(self.btn_frame, text="Avanti", command=self.next_question)
        self.next_btn.pack(side='left', padx=5)
        self.show_question()

    def show_question(self):
        for w in self.options_frame.winfo_children():
            w.destroy()
        q, opts = self.questions[self.current]
        self.question_label.config(text=q)
        self.var.set(None)
        for o in opts:
            tk.Radiobutton(self.options_frame, text=o, variable=self.var, value=o).pack(anchor='w')
        self.back_btn.config(state='disabled' if self.current == 0 else 'normal')

    def next_question(self):
        choice = self.var.get()
        if not choice:
            messagebox.showwarning("Attenzione", "Seleziona un'opzione per procedere.")
            return
        self.answers[self.current] = choice
        self.current += 1
        if self.current < len(self.questions):
            self.show_question()
        else:
            self.recommend()

    def prev_question(self):
        if self.current > 0:
            self.current -= 1
            self.answers.pop(self.current, None)
            self.show_question()

    def recommend(self):
        f = {}
        gen = self.answers[0]
        f['genre_id'] = self.genre_map.get(gen)
        p = self.answers[1]
        if p == 'Classici (prima del 1980)':
            f['period_lte'] = '1979-12-31'
        elif p == "Anni ’80 e ’90":
            f['period_gte'], f['period_lte'] = '1980-01-01', '1999-12-31'
        elif p == 'Anni 2000-2010':
            f['period_gte'], f['period_lte'] = '2000-01-01', '2010-12-31'
        else:
            f['period_gte'] = '2010-01-01'
        f['duration'] = self.answers[2]
        f['famous'] = (self.answers[4] == 'Famoso')
        nat = self.answers[5]
        if nat == 'Americana':
            f['original_language'] = 'en'
        f['series'] = self.answers[6]
        movies = discover_movies(self.api_key, f)
        filtered = filter_movies(self.api_key, movies, f)
        unseen = [(m['id'], m['title']) for m in filtered if not is_seen(m['id'])]
        if unseen:
            mid, title = random.choice(unseen)
            record_history(mid, title)
            messagebox.showinfo("Consiglio", f"Ti consiglio: {title}")
        else:
            titles = [m['title'] for m in filtered]
            if titles:
                msg = "Hai già visto tutti i titoli disponibili. Prova con:" + ''.join(f"\n- {t}" for t in titles)
                messagebox.showinfo("Alternative", msg)
            else:
                messagebox.showinfo("Nessun risultato", "Nessun film trovato con queste preferenze.")
        self.current = 0
        self.answers.clear()
        self.show_question()

if __name__ == '__main__':
    init_db()
    app = RecommenderApp()
    app.mainloop()
