'''

Author: Casale Alex 5A^ROB
Project: Flash Chat con API

Flask-Chat: CLIENT

#### IMPORTANTE ####
Prima di eseguire il client settare nel file di configurazione i parametri corretti

'''

import requests
import threading
import sqlite3
import time
import os.path
from os import path
from config import host, myID, dbName, schemaFile   # Import del config file
import base64

# Thread per la ricezione dei messaggi da parte del client
class ClientThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        database = sqlite3.connect(dbName)
        cur = database.cursor()
        while True:
            time.sleep(1)   # Ogni secondo verrà aggiornato il database con il salvataggio di tutti i messaggi ricevuti
            res = requests.get(f"{host}/api/v1/receive?id={myID}").json()
            for r in res:
                # Controllo per indicare se l'utente che ha mandato il messaggio è bloccato nella rubrica del client 
                ris = cur.execute(f"SELECT * FROM Contatti WHERE id = {r[0]} AND bloccato = 'False'").fetchone()
                if ris is not None:
                    cur.execute(f"INSERT INTO messaggi_ricevuti (id_mitt, text) VALUES ({r[0]}, '{r[1]}')")
                    database.commit()
# Funzione per la creazione del database
def createDatabase():
    f= open(dbName,"w+")
    f.close()
    fd = open(schemaFile, 'r')
    sqlFile = fd.read()
    fd.close()
    database = sqlite3.connect(dbName)
    cur = database.cursor()
    sqlCommands = sqlFile.split(';')    #Divido ogni istruzione SQL attraverso il ';' 
    for command in sqlCommands:     #Ogni query viene eseguita sul database 
        try:
            if command.strip() != '':
                cur.execute(command)
        except IOError:
            print ("Errore")
    database.commit()       #Completamennto della creazione del database

# Menù messo a disposizione del CLient/Utente
def menu():
    print("\n\n1. Contatti")
    print("2. Aggiorna Contatti")
    print("3. Blocca contatto")
    print("4. Sblocca contatto")
    print("5. Invia un messaggio")
    print("6. Messaggi ricevuti")
    print("7. Invia un'immagine")
    print("0. Esci\n")

# Funzione che ritorna la rubrica/contatti
def getContacts(id):
    database = sqlite3.connect(dbName)
    cur = database.cursor()
    contatcs = cur.execute("SELECT * FROM Contatti").fetchall()
    for c in contatcs:
        print(c[0], c[1], c[2], "Bloccato: ", c[3])

# Aggiornamento della rubrica/contatti
def updateContacts():
    URL = f"{host}/api/v1/user_list"       #URL api per la ricezione dei contatti
    contacts = requests.get(URL).json()
    database = sqlite3.connect(dbName)
    cur = database.cursor()
    cont  = 0
    for c in contacts:
        #Inserimento dei nuovi contatti (se ce ne sono altrimenti non inserisce nulla)
        result = cur.execute(f"SELECT * FROM Contatti WHERE id = '{c[0]}'").fetchall()
        if len(result) == 0:
            cont += 1   #Contatore che indicherà i nuovi contatti inseriti
            #Inserimento dei nuovi contatti nel database
            cur.execute(f"INSERT INTO Contatti (id, Nome, Cognome, Bloccato) VALUES ({c[0]}, '{c[1]}', '{c[2]}', 'False')")
            database.commit()
    print(f"\nInseriti {cont} nuovi contatti")

# Funzione per bloccare un utente
def lockUser(id):
    database = sqlite3.connect(dbName)
    cur = database.cursor()
    #Setto il campo bloccato a True se l'utente ha invocato questo metodo
    cur.execute(f"UPDATE Contatti SET Bloccato = 'True' WHERE id = {id}")
    database.commit()

    #Query che mi ritorna il nome e cognome dell'utente bloccato
    res = cur.execute(f"SELECT * FROM Contatti WHERE id = {id}").fetchone()
    print("Hai bloccato il contatto: ", res[1], res[2])

# Funzione per sbloccare un utente
def unlockUser(id):
    database = sqlite3.connect(dbName)
    cur = database.cursor()
    #Setto a False il contatto interessato
    cur.execute(f"UPDATE Contatti SET Bloccato = 'False' WHERE id = {id}")
    database.commit()
    
    #Ottengo con la seguente query nome e cognome dell'utente bloccato
    res = cur.execute(f"SELECT * FROM Contatti WHERE id = {id}").fetchone()
    print("Hai sbloccato il contatto: ", res[1], res[2])

# Invio dei messaggi
def sendMessage(idDest, text):
    database = sqlite3.connect(dbName)
    cur = database.cursor()
    #Verifico innanzitutto de il contatto a cui si vuole inviare il messaggio non sia bloccato
    ris = cur.execute(f"SELECT * FROM Contatti WHERE id = {idDest} AND bloccato = 'False'").fetchone()
    if ris is not None:
        #Invoco l'API send
        res = requests.get(f"{host}/api/v1/send?ID_DEST={idDest}&ID_MITT={myID}&TEXT={text}")
        if res: #Se mi restituisce True significa che il messaggio è stato inviato
            #Salvo il messaggio che ho inviato nel database locale
            cur.execute(f"INSERT INTO messaggi_inviati (id_dest, text) VALUES ({idDest}, '{text}')")
            database.commit()
            print("Messaggio inviato")
        else:
            print("Errore: il messaggio non è stato inviato")
    else:
        print("Il contatto a cui stai mandando il messaggio è bloccato")

# Funzione che mi ritorna tutti i messaggi ricevuti
def receiveMsg():
    database = sqlite3.connect(dbName)
    cur = database.cursor()
    #seleziono tutti i messaggi che ho nella tabella dei messaggi ricevuti
    res = cur.execute("SELECT * FROM messaggi_ricevuti").fetchall()
    database.commit()
    if len(res) != 0:
        for r in res:
            mitt = cur.execute(f"SELECT * FROM Contatti WHERE id = {r[1]}").fetchone()
            database.commit()
            #Stampa del messaggio e del nome/cognome del mittente
            print("Mittente: ", mitt[1], mitt[2], "Messaggio: ", r[2])
    else:
        print("Non hai nuovi messaggi")

# Invio di un'immagine al server
def sendImage(dest):
    #Apro l'immagine in modalità lettura bytes e la confeziono in un dizionario con key 'img' e 'dest' dove dest sarà 
    #l'id del destinatario (l'invio non avverrà tra client e client ma funzionerà solo tra client e server)
    #Non sono riuscito a implementare questa funzione per problemi di tempistica
    data = {"img" : open('images/apple.jpg','rb'), "dest": dest}
    #Richiesta POST al server tramite l'API send
    r = requests.post(f"{host}/api/v1/send?dest={dest}&mitt={myID}", files=data)
    return r

def main(thread):
    # A ogni avvio del client aggiorno i contatti in modo da avere sempre dei contatti nella rubrica
    updateContacts()
    while True:
        menu()
        while True:
            try:
                option = int(input("Scegli un opzione >>> "))
                break
            except:
                print("Inserisci un opzione valida (1-6)")
        # Varie opzioni selezionabili tramite il menù che verrà messo a disposizione all'utente
        if option == 1:
            getContacts(id)
        elif option == 2:
            updateContacts()
        elif option == 3:
            idToLock = input("Inserisci l'id dell'utente che vuoi bloccare: ")
            lockUser(idToLock)
        elif option == 4:
            idToLock = input("Inserisci l'id dell'utente che vuoi sbloccare: ")
            unlockUser(idToLock)
        elif option == 5:
            id_dest = input("Id del destinatario: ")
            textToSend = input("Inserisci il testo del messaggio: ")
            sendMessage(id_dest, textToSend)
        elif option == 6:
            receiveMsg()
        elif option == 7:
            dest = int(input("A chi vuoi mandare l'immagine? "))
            sendImage(dest)
        elif option == 0:
            break
    thread.join()

if __name__ == "__main__":

    # Se il file database non esiste ne verrà creato uno con apposite tabelle
    if not path.exists(dbName):
        createDatabase()
    # Creazione del thread per la ricezione dei messaggi
    # Il thread girerà in background richiedendo ogni secondo al server se ci sono nuovi messaggi. 
    # Se si li salverà nell'apposito database e nell'apposita tabella
    newthread = ClientThread()
    newthread.start()
    main(newthread)

    