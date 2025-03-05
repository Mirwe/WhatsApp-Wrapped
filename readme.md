# WhatsApp Wrapped

Script Python per analizzare le conversazioni da un file di testo estratto da WhatsApp.
Valido solo per chat da due persone.


---

## Funzionalità

- **Calcolo delle Statistiche**  
  - Numero totale di messaggi.
  - Numero di messaggi per utente.
  - Calcolo del tempo medio di risposta.
  - Conteggio totale delle parole e media per messaggio.
  - Analisi delle conversazioni (identifica chi ha avviato le conversazioni basandosi su un gap di 90 minuti tra i messaggi).


- **Grafici**
   
  - Distribuzione dei messaggi per ora del giorno
  - Andamento dei messaggi per giorno
  - Numero messaggi per utente
  - Numero conversazioni avviate per utente
  - Tempo medio di risposta per utente
  - WordCloud per ogni utente per parole pià usate
  - Top 10 parole più usate per utente

---

## Requisiti

- [pandas](https://pandas.pydata.org/)
- [matplotlib](https://matplotlib.org/)
- [seaborn](https://seaborn.pydata.org/)
- [wordcloud](https://amueller.github.io/word_cloud/)
- [emoji](https://pypi.org/project/emoji/)

```bash
pip install -r requirements.txt
