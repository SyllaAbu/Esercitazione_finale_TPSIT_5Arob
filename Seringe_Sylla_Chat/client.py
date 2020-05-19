import schedule as schedule
from db import open_db, close_db
from requests import get, post
from conf import send_url, recv_url, download_url, users_list_url, MY_ID, Server_ip
from datetime import datetime
from time import sleep
import os
from threading import Thread
import schedule


# Questo Thread viene avviato non appena il programma è in esecuzione e serve per tenere attivo lo schedule e fargli controllare i nuovi messaggi ogni 5 secondi
# per maggiori info https://pypi.org/project/schedule/

class Schedule(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        schedule.every(5).seconds.do(check_new_messages_and_photo)
        while True:
            schedule.run_pending()
            sleep(1)


# Menu, funzione che ritorna l'opzione scelta

def menu():
    print("----------------------  Flask-Chat Sylla Seringe (Client menu) ----------------------")
    print("1. Invia messaggi")
    print("2. Invia foto")
    print("3. Leggi messaggi non letti e scarica eventuali foto")
    print("4. Mostra lista utenti")

    select = input('>>>')

    return select

# funzione che serve per controllare ogni 5 secondi l'invio di foto e testi
# questa funzione è chiamata ogni 5 secondi dal modulo schedule che gira continuamente grazie al Thread Schedule


def check_new_messages_and_photo():
    conn = open_db()  # guardardare gli import e db.py
    cur = conn.cursor()

    messages = get(recv_url % (Server_ip, MY_ID)).json()  # guardare file conf.py   faccio la richiesta
    # effettuo una get all'url http://%s:5000/api/v1/receive?receiver_id=%s passando i parametri come nome host(ip) e il mio ID

    # scorro tra i singoli messaggi accedendo ai valori del dizionario messages e li inserisco nella tabella tabella.
    for msg in messages:
        cur.execute(
            'INSERT INTO Client_messages(receiver_id, sender_id, text, time, is_read, is_photo, photo_path) VALUES(?,?,?,?,?,?,?)',
            (MY_ID, msg['sender_id'], msg['text'], msg['time'], 0, msg['is_photo'], msg['photo_path']))     # setto receiver_id a MY_ID=14 per ricevere esclusivamente i messaggi diretti a me
        if msg['is_photo'] == 1:    # verifico se il messaggio corrente sia una foto(avrà campo photo_path = 1)
            photo = str(msg['photo_path']).split('/')[1]    # se lo è salvo il nome del file
            r = get(download_url % (Server_ip, photo))  # questa url l'ho aggiunto per permettere lo scaricamento delle foto,
                                                        # quindi faccio la get e mi viene ritornata come risposta la foto stessa che salvo nella directory Client_photo_storage/received_photo

            if r.status_code == 200:    # se lo status code è 200 procedo a salvare il file
                with open(f"Client_photo_storage/received_photo/{photo}", 'wb') as f:
                    f.write(r.content)

        print('\nHai nuovi messaggi da leggere!(Scegli 3 per leggerli!)  >>>')  # invio una notifica

        conn.commit()   # salvo le modifiche effettuate nel database

    close_db(conn)  # chiudo il database


def sendText():     # funzione per inviare testi
    conn = open_db()
    cur = conn.cursor()

    host_name = input(f'Inserisci l\'del server, premi invio per confermare questo({Server_ip}): ')     # visto che si cambiera spesso server ho deciso di metterlo tra gli input, in caso
                                                                                                        # stessi testando in locale effettua semplicemente invio
    if host_name == '': host_name = Server_ip  # quindi se fai invio assegno l'ip della macchina, controlla conf.py per vedere come prendo l'ip.

    receiver_id = input(f'Inserisci l\'ID del destinatario, premi invio per confermare questo({MY_ID}): ')  # inserisco il destinatario, siccome sono il num. 14 nel registro durante i test ho settato questo valore
                                                                                                            # vale lo stesso discorso per l'ip, invio per confermare
    if receiver_id == '': receiver_id = MY_ID

    if cur.execute('SELECT * FROM users WHERE id = ?', (receiver_id,)).fetchone():      #verifico che l'id inserito sia esistente nel db
        text = input('Inserisci il testo: ').replace(' ', '+')      # sostituisco eventuali spazio con il +
        print(send_url % (host_name, MY_ID, text, receiver_id))
        get(send_url % (host_name, MY_ID, text, receiver_id))       # faccio la chiamata all'url http://%s:5000/api/v1/send?sender_id=%s&text=%s&receiver_id=%s passando i valori necessari
        print('Messaggio inviato!')
    else:
        print('Non c\'e\' nessun utente con questo id')


def sendPhoto():    # Funzione per inviare immagini
    conn = open_db()
    cur = conn.cursor()

    host_name = input(f'Inserisci l\'del server, premi invio per confermare questo({Server_ip}): ')     # discorso analogono a sendText()
    if host_name == '': host_name = Server_ip

    receiver_id = input(f'Inserisci l\'ID del destinatario, premi invio per confermare questo({MY_ID}): ') # discorso analogono a sendText()
    if receiver_id == '': receiver_id = MY_ID

    # Per inviare immagini quest'ultime dovranno essere salvate nella directory Client_phosto_storage/to_sent_photo

    if cur.execute('SELECT * FROM users WHERE id = ?', (receiver_id,)).fetchone(): # discorso analogono a sendText()
        print('\n')
        for photos in os.walk('Client_photo_storage/to_sent_photo/'):   # scorro tra i contenuti di questa cartella e mostro i nomi dei file
            for photo in photos[2]: print(photo)

        x = input('Inserisci il nome della foto che vuoi inviare(estensione compresa): ')   # chiedo di inserire il file che si desidera mandare

        try:    #  si come ho a che fare con dei file utilizzo la try-except
            files = {
                'file': open(f'Client_photo_storage/to_sent_photo/{x}', 'rb'),  # se la foto è presente la assegno al dizionario files
            }

            response = post(send_url % (host_name, MY_ID, 'foto', receiver_id), files=files)    # faccio la post sempre all'url send che saprà distinguere.
            print(response.text)    # verifico cosa mi ha ritornato il server

        except:
            print('Foto non trovata!')

    else:
        print('Non c\'e\' nessun utente con questo id')


def receiveText():      # Funzione per leggere i messaggi piu recenti(quelli con il campo is_read = 1) che verrano successivamente settati a 0  1=True|0=False
    conn = open_db()
    cur = conn.cursor()

    print('------------------------------------------M E S S A G G I--------------------------------------------\n')
    if cur.execute('SELECT * FROM Client_messages WHERE is_read = 0').fetchall():       # Verifico se ci sono nuovi messaggi, se non ce ne sono ritorna lista vuota
        for msg in cur.execute('SELECT * FROM Client_messages WHERE is_read = 0').fetchall():       # Seleziono quindi tutti i messaggi non letti(is_read = 0)
            name = cur.execute('SELECT name FROM Users WHERE id = ?', (msg[2],)).fetchone()[0]      # Seleziono il nome del mittente attraverso l'id
            print(
                f"{name}[id: {msg[2]}]: {msg[3]}          at {datetime.fromtimestamp(float(msg[4])).strftime('%H:%M')}"     # effettuo la print finale
            )

        cur.execute('UPDATE Client_messages SET is_read = 1 WHERE is_read = 0')     # setto quindi i messaggi a letto(is_read=1) per non mostrarli in seguito
        conn.commit()
    else:
        print('Non ci sono messaggi nuovi!')

    print('\n\n--------------------------------------------------------------------------------------------------')

    close_db(conn)


def users_list_func():      # funzione per tornare tutti gli unteti presenti nel database
    users_list = get(users_list_url % Server_ip).json()     # richiesta all'url users_list che restituira un json

    for user in users_list:
        print(f"user: {user['name']}             id: {user['id']}")     # stampo gli utenti(nome e id)


if __name__ == "__main__":
    s = Schedule()      # faccio partire il Thread Schedule per predisponere il client a riceve messaggi
    s.start()
    while True:
        select = menu()
        if select == '1':
            sendText()
        elif select == '2':
            sendPhoto()
        elif select == '3':
            receiveText()
        elif select == '4':
            users_list_func()
