import re
import string
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import collections
import emoji
import matplotlib.gridspec as gridspec

# File txt estratto da WhatsApp
filename = "chat2.txt"

# --- Funzioni di supporto ---
def remove_emoji(text):
    """Rimuovere emoji"""
    removed_emoji = emoji.replace_emoji(text)

    if removed_emoji == '':
        return "null"
    else:
        return removed_emoji


def clean_word(word):
    """Rimuove punteggiatura e trasforma la parola in minuscolo."""
    return word.strip(string.punctuation).lower()


# Parole da ignorare nel WordCloud
stopwords = {
    "a", "ad", "adesso", "ai", "al", "alla", "allo", "allora", "altro", "altri", "alcuni", "anche",
    "ancora", "avere", "ben", "bene", "che", "chi", "ci", "come", "con", "cui", "da", "del", "della",
    "dello", "dentro", "di", "dopo", "e", "ed", "ecco", "fare", "fine", "fra", "già", "gli", "ho", "il",
    "in", "indietro", "invece", "io", "la", "là", "le", "lei", "lo", "loro", "ma", "me", "meglio", "molto",
    "ne", "nei", "nella", "no", "noi", "non", "nostro", "nove", "nuovo", "o", "oltre", "per", "perche", "perché",
    "più", "prima", "quello", "questa", "questo", "qui", "sarà", "secondo", "se", "sei", "sembra", "sembrava",
    "senza", "si", "sia", "sono", "sta", "stanno", "stato", "stessa", "stesso", "su", "sua", "suo", "sul", "sulla",
    "ti", "tra", "tu", "tua", "tuo", "un", "una", "uno", "va", "vi", "voi", "volte", "è", "però", "mi", "media",
    "omessi", "c'è", "che", "chi", "ci", "cosa", "come", "con", "contro", "era",
    "cosa", "hai", "ora", "quando", "dove", "solo", "poi", "comunque", "null", "ha", "alcuna", "alcuni", "altre", "ho",
    "oggi", "domani", "quindi", "dopo",
    "tipo", "così", "fatto", "te", "tu", "ti", "tuo", "vi", "voi", "voce", "vostro",
    "questi","li", "i", "hanno", "devo", "alle", "mia", "tua", "miei", "mie", "mio", "tuoi", "tuo",
    "questo", "questa", "casa", "vado", "fa",
    "so", "sto", "sa", "fai", "dei", "di", "delle", "dello", "del", "dalla", "dai", "dalle", "da", "dopo", "e", "ed",
    "è", "tutti", "tutte", "tutto", "sì", "vuoi"}

with open(filename, encoding="utf-8") as file:
    lines = file.readlines()

# Espressione regolare per estrarre: data, ora, mittente e messaggio.
# Il nome dell'utente è quello indicato subito dopo il "-"
pattern = re.compile(r"(\d{2}/\d{2}/\d{2}), (\d{2}:\d{2}) - (.*?): (.*)")

data = []
for line in lines:
    match = pattern.match(line)
    if match:
        date_str, time_str, sender, message = match.groups()
        dt = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%y %H:%M")
        data.append([dt, sender, message])
    else:
        # Se la riga non corrisponde al pattern, è una continuazione del messaggio precedente
        if data:
            data[-1][2] += " " + line.strip()



# Crea un DataFrame e ordina per data/ora
df = pd.DataFrame(data, columns=["datetime", "sender", "message"])
df = df.sort_values("datetime").reset_index(drop=True)

# Statistiche di base
total_messages = len(df)
messages_per_person = df["sender"].value_counts()

# Calcolo del tempo medio di risposta per ogni utente:
# Considera la differenza tra messaggi consecutivi solo se il mittente cambia.
df["time_diff"] = df["datetime"].diff()
df["prev_sender"] = df["sender"].shift()
df["response_time"] = df.apply(
    lambda row: row["time_diff"] if row["sender"] != row["prev_sender"] else pd.NaT,
    axis=1
)
response_time_per_user = (
    df.dropna(subset=["response_time"])
      .groupby("sender")["response_time"]
      .apply(lambda x: sum(x, timedelta()) / len(x))
)

# Calcolo delle parole
df["word_count"] = df["message"].apply(lambda x: len(x.split()))
total_words = df["word_count"].sum()
avg_words_per_message = df["word_count"].mean()
words_per_user = df.groupby("sender")["word_count"].agg(["sum", "mean"])

# Statistiche aggiuntive:
# 1. Messaggi per ora del giorno
df["hour"] = df["datetime"].dt.hour
messages_by_hour = df.groupby("hour").size()

# 2. Messaggi per giorno
df["date"] = df["datetime"].dt.date
messages_per_day = df.groupby("date").size()

# 3. Analisi: Chi inizia una conversazione?
# Definiamo l'inizio di una conversazione se il gap dal messaggio precedente è superiore a 90 minuti.
conversation_threshold = timedelta(minutes=90)
df["conversation_start"] = df["datetime"].diff() > conversation_threshold
# Il primo messaggio va sempre considerato come inizio di conversazione.
df.loc[0, "conversation_start"] = True
conversation_starters = df[df["conversation_start"]]["sender"].value_counts()

# Output delle statistiche
print("=== Statistiche Chat ===")
print(f"Numero totale di messaggi: {total_messages}\n")
print("Numero di messaggi per persona:")
print(messages_per_person, "\n")

print("Tempo medio di risposta per ogni utente:")
for user, rt in response_time_per_user.items():
    seconds = rt.total_seconds()
    formatted_rt = str(timedelta(seconds=round(seconds)))
    print(f"{user}: {formatted_rt}")

print(f"\nTotale parole: {total_words}")
print(f"Media parole per messaggio: {avg_words_per_message:.2f}\n")
print("Statistiche sul conteggio delle parole per utente:")
print(words_per_user, "\n")

print("Conversazioni avviate per utente:")
print(conversation_starters, "\n")

# Plotting
sns.set_theme(style="whitegrid")

fig = plt.figure(figsize=(15, 12))
gs = gridspec.GridSpec(2, 3, figure=fig)

# Prima riga
ax1 = fig.add_subplot(gs[0, 0])  # Grafico 1: Messaggi per Persona
ax2 = fig.add_subplot(gs[0, 1])  # Grafico 4: Conversazioni Avviate per Utente
ax3 = fig.add_subplot(gs[0, 2])  # Grafico 5: Tempo medio di risposta

# Seconda riga
ax4 = fig.add_subplot(gs[1, 0])    # Grafico 3: Messaggi per Ora del Giorno
ax5 = fig.add_subplot(gs[1, 1:3])  # Grafico 2: Messaggi per Giorno (ora occupa due colonne)

# Grafico 1: Messaggi per Persona
messages_per_person = messages_per_person.sort_index()
sns.barplot(x=messages_per_person.index, y=messages_per_person.values, ax=ax1, palette="Blues")
ax1.set_title("Messaggi per Persona")
ax1.set_xlabel("Utente")
ax1.set_ylabel("Numero di Messaggi")
ax1.tick_params(axis='x', rotation=45)

# Grafico 4: Conversazioni Avviate per Utente
conversation_starters = conversation_starters.sort_index()
sns.barplot(x=conversation_starters.index, y=conversation_starters.values, ax=ax2, palette="Blues")
ax2.set_title("Conversazioni Avviate per Utente")
ax2.set_xlabel("Utente")
ax2.set_ylabel("Numero di Conversazioni")
ax2.tick_params(axis='x', rotation=45)

# Grafico 5: Tempo medio di risposta per Utente
a = response_time_per_user.apply(lambda x: x.total_seconds() / 60).sort_index()
sns.barplot(x=a.index, y=a.values, ax=ax3, palette="Blues")
ax3.set_title("Tempo medio di risposta")
ax3.set_xlabel("Utente")
ax3.set_ylabel("Minuti")
ax3.tick_params(axis='x', rotation=45)

# Grafico 3: Messaggi per Ora del Giorno
sns.barplot(x=messages_by_hour.index, y=messages_by_hour.values, ax=ax4, palette="coolwarm")
ax4.set_title("Messaggi per Ora del Giorno")
ax4.set_xlabel("Ora del Giorno")
ax4.set_ylabel("Numero di Messaggi")

# Grafico 2: Messaggi per Giorno
messages_per_day_sorted = messages_per_day.sort_index()
ax5.plot(messages_per_day_sorted.index, messages_per_day_sorted.values, marker=',', linestyle='-')
ax5.set_title("Messaggi per Giorno")
ax5.set_xlabel("Data")
ax5.set_ylabel("Numero di Messaggi")
ax5.tick_params(axis='x', rotation=45)

plt.subplots_adjust(hspace=0.415, left=0.05, right=0.985, top=0.97, bottom=0.115)
plt.show()


# --- Word Cloud per ogni utente ---
# TOP 10 parole più usate per ogni utente
fig_word, ax_word = plt.subplots(2,2,figsize=(15, 12))

unique_users = df["sender"].unique()
for i, user in enumerate(unique_users):
    messages = " ".join(df[df["sender"] == user]["message"])
    words = [clean_word(word) for word in messages.split() if clean_word(word) not in stopwords and clean_word(word)]

    words_without_emojis = [remove_emoji(word) for word in words]
    cleaned_words = [word for word in words_without_emojis if word != "null"]

    # Rimozione parole "akeeeelaa"
    # akela_regex = re.compile(r"^ak(e)+l(a)+$")
    #
    # for j, w in enumerate(cleaned_words):
    #     match = akela_regex.match(w)
    #
    #     if match:
    #         cleaned_words[j] = "akila"

    wc = WordCloud(width=400, height=300, background_color="white").generate(" ".join(cleaned_words))

    row = i
    col = 0
    ax_word[row, col].imshow(wc, interpolation="bilinear")
    ax_word[row, col].set_title(f"Words {user}")
    ax_word[row, col].axis("off")

    # Top 10 parole più usate
    word_counts = collections.Counter(cleaned_words)
    top_words = word_counts.most_common(10)
    top_words_df = pd.DataFrame(top_words, columns=["Parola", "Conteggio"])

    col = 1

    sns.barplot(y=top_words_df["Parola"], x=top_words_df["Conteggio"], ax=ax_word[row, col], color="green")

    ax_word[row, col].set_title(f"Top 10 parole di {user}")
    ax_word[row, col].set_xlabel("Frequenza")
    ax_word[row, col].set_ylabel("Parola")




plt.subplots_adjust(hspace=0.27, left=0.03, right=0.97, top=0.97, bottom=0.03)
plt.show()
