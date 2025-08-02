import spacy
from string import punctuation
from mcp.server.fastmcp import FastMCP
import logging
import email as email_utils
from imapclient import IMAPClient
from collections import Counter
import re

# Initialize the FastMCP server with a name
mcp = FastMCP("Email Retrieval")

#Carica il modello di lingua inglese di spaCy
nlp = spacy.load('en_core_web_sm')
# Configura il logging in modo minimale per non avere output troppo verbose
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

# Add an email retrieval tool

@mcp.tool()
def get_last_email_text(username, password = "anrxlvavrzpnqjqw"):
    """
    Si connette al tuo account su Gmail (se esiste) tramite IMAP, recupera l'ultima email nella casella di posta
    ed estrae il suo testo.
    """
    # 1. Controllo generale del formato email con Regex
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.fullmatch(email_pattern, username):
        error_message = f"Errore: L'indirizzo '{username}' non sembra un'email valida. Per favore, fornisci un indirizzo email corretto."
        print(error_message)
        return error_message

   # 2. Controllo specifico per Gmail
    if not username.lower().endswith('@gmail.com'):
        error_message = f"Errore: Questo strumento funziona solo con account Gmail. L'indirizzo '{username}' non è un account Gmail."
        print(error_message)
        return error_message
  
    
    IMAP_SERVER = 'imap.gmail.com'
    IMAP_PORT = 993

    try:
        with IMAPClient(host=IMAP_SERVER, port=IMAP_PORT, ssl=True) as client:
            client.login(username, password)
            client.select_folder('INBOX')

            messages = client.search()
            print(f"[DEBUG] messages trovati: {messages}")
            if not messages:
                print("Nessun messaggio trovato nella casella di posta.")
                return ("Nessun messaggio trovato nella casella di posta.")

            last_message_uid = messages[-1]
            print(f"[DEBUG] last_message_uid: {last_message_uid}")
            response = client.fetch(last_message_uid, ['RFC822'])
            print(f"[DEBUG] response: {response}")
            raw_email = response[last_message_uid][b'RFC822']
            print(f"[DEBUG] raw_email length: {len(raw_email)}")

            msg = email_utils.message_from_bytes(raw_email)
            email_body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    ctype = part.get_content_type()
                    cdisp = part.get('Content-Disposition')
                    if ctype == 'text/plain' and cdisp is None:
                        try:
                            email_body = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8', errors='ignore')
                            print(f"[DEBUG] email_body estratto (multipart): {email_body[:200]}")
                        except Exception as e:
                            print(f"[DEBUG] Errore decodifica multipart: {e}")
            else:
                if msg.get_content_type() == 'text/plain':
                    try:
                        email_body = msg.get_payload(decode=True).decode(msg.get_content_charset() or 'utf-8', errors='ignore')
                        print(f"[DEBUG] email_body estratto (plain): {email_body[:200]}")
                    except Exception as e:
                        print(f"[DEBUG] Errore decodifica plain: {e}")
            print("\nTesto dell'ultima email:")
            print(email_body)
            return email_body
            
    

    except IMAPClient.Error as e:
        print (f"Errore: {e}. Assicurati che l'IMAP sia abilitato in Gmail e di usare una password dell'app valida.")
    except Exception as e:
        print (f"Si è verificato un errore inatteso: {e}")
    
# Add an summarizing tool
@mcp.tool()
def summarize_text(text: str, num_sentences: int = 3) -> str:
    """
    Genera un riassunto estrattivo di un testo.

    Args:
        text: Il testo da riassumere.
        num_sentences: Il numero di frasi desiderate nel riassunto.

    Returns:
        Il testo riassunto.
    """
    # 1. Analisi del testo con spaCy
    doc = nlp(text)

    # 2. Filtra le parole non utili (stop words) e la punteggiatura
    # e crea una lista di parole chiave
    keywords = [token.text for token in doc if not token.is_stop and not token.is_punct]

    # 3. Calcola la frequenza di ogni parola chiave
    word_frequencies = Counter(keywords)

    # 4. Normalizza le frequenze (dividendo per la più alta)
    max_freq = max(word_frequencies.values())
    for word in word_frequencies:
        word_frequencies[word] = word_frequencies[word] / (max_freq)

    # 5. Assegna un punteggio a ogni frase in base alle parole che contiene
    sentence_scores = {}
    for sent in doc.sents:
        for word in sent:
            if word.text in word_frequencies:
                if sent not in sentence_scores:
                    sentence_scores[sent] = word_frequencies[word.text]
                else:
                    sentence_scores[sent] += word_frequencies[word.text]

    # 6. Ordina le frasi per punteggio e prende le migliori
    sorted_sentences = sorted(sentence_scores, key= sentence_scores.get, reverse=True)
    top_sentences = sorted_sentences[:num_sentences]

    # 7. Unisci le frasi migliori per creare il riassunto finale
    summary = ' '.join([sent.text.strip() for sent in top_sentences])
    # print("\nTesto del riassunto:")
    # print(summary)
    return summary