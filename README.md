# CineMente

Un'applicazione Python con interfaccia grafica per consigliare film basata sulle preferenze dell'utente.

## Caratteristiche

- **Domande interattive**: sequenza di 7 domande per affinare rapidamente le preferenze.
- **Integrazione TMDB**: utilizza l'API di The Movie Database per scoprire film in base a filtri (genere, periodo, durata, finale, popolarità, nazionalità, saga/franchise).
- **Storico locale**: salva i film già consigliati e visti in un database SQLite (`movies_history.db`) e propone alternative se un film è già stato visto.
- **Interfaccia GUI**: basata su `tkinter`, con pulsanti Avanti/Indietro e finestre di dialogo chiare.
- **Inserimento API Key**: richiede all'avvio la TMDB API Key attraverso un dialog box.

## Struttura del progetto

```
CineMente/                  # Cartella principale del progetto
├── movie_recommender_gui.py  # Script principale
├── movies_history.db         # Database SQLite generato automaticamente
└── README.md                 # Documentazione del progetto
```

## Requisiti

- Python 3.7+
- Moduli Python:
  - `requests`
  - `tkinter` (incluso in molte distribuzioni Python)
  - `sqlite3` (incluso nella libreria standard)

## Installazione

1. Clona la repository:
   ```bash
   git clone https://github.com/<tuo-utente>/CineMente.git
   cd CineMente
   ```
2. Installa le dipendenze:
   ```bash
   python3 -m pip install requests
   ```

## Configurazione e avvio

All'avvio lo script chiederà la tua TMDB API Key.

```bash
python3 movie_recommender_gui.py
```

- Inserisci la tua API Key nel campo di dialogo.
- Rispondi alle domande successive per ottenere un consiglio di visione.

## Personalizzazioni

- Aggiungi o modifica filtri (es. voto minimo, cast, registi) all'interno della funzione `discover_movies`.
- Aggiorna il database `movies_history.db` manualmente o tramite script per importare cronologie preesistenti.

## Contributi

PR e issue sono i benvenuti! Apri una pull request o un issue su GitHub.

## Licenza

Distribuito sotto licenza MIT. Vedi `LICENSE` per dettagli.
