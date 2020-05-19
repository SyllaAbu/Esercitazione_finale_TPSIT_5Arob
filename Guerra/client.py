'''
NICOLO' GUERRA 5AROB
'''
import flask
from flask import request, jsonify
import sqlite3
import requests
from threading import Thread 
import time
import sys
import os

URL = "http://79.23.65.160:8080/api/v1/"    #parte di URL uguale per tutte le chiamate
MY_ID = 12                                  #il mio id statico
path_db = "static/db_client_chat.db"        #path del bd
stop_thread = False                         #variabie globale per interrompere il "looping thread"
class ReceiveThread(Thread):
    '''Classe per la ricezione in loop dei messaggi'''
    def __init__(self):
        '''Dichiarazione degli attributi del thread'''
        Thread.__init__(self)
        self.connectionURL = URL + 'receive'
        self.PARAMS = {'id_dest' : MY_ID}

    def run(self):
        '''Metodo run del thread'''
        while True:
            if not stop_thread: #controllo per fermare il ciclo
                time.sleep(5)   #esegue ogni 5 sec
                r = requests.get(url = self.connectionURL, params=self.PARAMS)  #richiesta di tipo GET
                data = r.json() #converto in oggetto json = dizionario
            
                try:
                    sqliteConn = sqlite3.connect(path_db)   #connessione al db
                    cursor = sqliteConn.cursor()            #istanziazione del cursore
                    if len(data)!=0:                        #se la risposta ha una lunghezza diversa da 0
                        for d in data:
                            cursor.execute(f'''
                            SELECT bloccato
                            FROM utenti
                            WHERE user_id = {d[0]};''') #eseguo la query
                            
                            if(not cursor.fetchall()[0][0]):#controllo l'unica cella che mi aspetto che ritorni
                                cursor.execute(f'''
                                INSERT INTO Messaggi_RX(Text, IdMitt) 
                                VALUES ("{d[3]}", {d[0]});''')  #inserisco il messaggio nel DB locale

                    sqliteConn.commit()     #confermo le modifiche

                except sqlite3.Error as error:  #eventuali eccezione
                    print("Error: " + error)

                finally:
                    if (sqliteConn):
                        sqliteConn.close()  #chiusura della connessione
            else:
                break
        

def printMenu():
    print("0 - Esci")
    print("1 - Rubrica")
    print("2 - Messaggi ricevuti")
    print("3 - Invia")
    print("4 - Blocca/Sblocca")

def user_list():
    '''Ho scelto di non usare l'API messa a disposizione dal server per poter conservare i nickname nel db'''
    try:
        sqliteConn = sqlite3.connect(path_db)
        cursor = sqliteConn.cursor()

        cursor.execute(f"SELECT * FROM utenti;")    #ritorno la lista intera degli utenti nel DB
        data = cursor.fetchall()    #carico risultati
        for d in data:  
            if d[4]:    #adatto per leggibilità
                s = 'Sì'    
            else:
                s = 'No'
            print(f"ID: {d[0]} - Nome: {d[1]} - Cognome: {d[2]} - Nick: {d[3]} - Bloccato: {s}")    #stampo risultati ottenuti

    except sqlite3.Error as error:  #gestione eccezioni
        print("Error: " + error)

    finally:
        if (sqliteConn):    #se la connessione è attiva la chiudo
            print('Chiusura connessione DB')
            sqliteConn.close()
    
def receivedMessages():
    '''Stampo i record salvati dal thread nel DB'''
    try:
        sqliteConn = sqlite3.connect(path_db)   #apro connessione e istanzio cursore
        cursor = sqliteConn.cursor()

        cursor.execute(f"SELECT Messaggi_RX.text, utenti.nick FROM Messaggi_RX, utenti WHERE utenti.user_id = Messaggi_RX.IdMitt;") #query
        data = cursor.fetchall()
        for d in data:      #scorro per i risultati
            print(f"Messaggio ricevuto da: {d[1]} - Testo: {d[0]}")
            
        sqliteConn.commit()

    except sqlite3.Error as error:  #gestione eccezioni
        print("Error: " + error)

    finally:
        if (sqliteConn):    #se la connnessione è attiva la chiudo
            sqliteConn.close()

def sendMex():
    try:
        sqliteConn = sqlite3.connect(path_db)
        cursor = sqliteConn.cursor()

        nick = input('A chi vuoi inviare il messaggio? \n')
        choice = input('Che tipo di messaggio vuoi inviare? (f/t)') #chiedo il tipo di messaggio da inviare
         if choice.lower() == 'f':
             pass
        #POSSIBILE IMPLEMENTAZIONE, MA SI DOVREBBE CAMBIARE IL SERVER
        #     cursor.execute(f"SELECT user_id FROM utenti WHERE nick = '{nick}';")
        #     result = cursor.fetchall()
        #     print(result[0][0])
        #     if (len(result)==1):
        #         for photos in os.walk(''):
        #             for p in photos[2]:
        #                 print(p)
                
        #         photo = input('Inserisci il nome della foto che vuoi inviare con estensione: ')
        #         try:
        #             to_send={'img':open(f'{photo}', 'rb')}
        #             PARAMS={'id_dest':result[0][0], 'text':text.replace(" ", "+"), 'id_mitt':MY_ID}
        #             response = requests.post(url=URL+'send', params=PARAMS, files=to_send)
        #         except:
        #             print('Foto non trovata')
        elif choice.lower() == 't':

            cursor.execute(f"SELECT user_id FROM utenti WHERE nick = '{nick}';")    #eseguo query

            result = cursor.fetchall()
            if (len(result)==1):
                text = input('Digita il messaggio che vuoi inviare: \n')    #faccio inserire il testo del messaggio
                PARAMS={'id_dest':result[0][0], 'text':text.replace(" ", "+"), 'id_mitt':MY_ID} #parametri
                r = requests.get(url=URL+'send', params=PARAMS)             #request con il metodo GET
                if(r.status_code==200):
                    cursor.execute(f"INSERT INTO Messaggi_TX(text, IdDest) VALUES ('{text}', {result[0][0]});") #inserisco i valori
                    print("Messaggio inviato correttamente")    
                else:
                    print("Errore nell' invio")
            else:
                print("Errore nell'inserimento del nickname")
                
            sqliteConn.commit()
        else:
            print('Scelta non valida')
            
    except sqlite3.Error as error:
        print("Error: " + error)

    finally:
        if (sqliteConn):    #chiudo connessione
            sqliteConn.close()

def bloccaSblocca():
    '''Funzione per sbloccare o bloccare una persona'''
    try:
        sqliteConn = sqlite3.connect(path_db)
        cursor = sqliteConn.cursor()

        user = input("Seleziona un contatto: \n")   #scrivo il nickname dell'utente in questione
        cursor.execute(f"SELECT bloccato FROM utenti WHERE nick = '{user}';")
        data = cursor.fetchall()    #carico i risultati in questa lista
        if not data[0][0]:          #verifico i risultati e associo una parola
            s = 'bloccato'
        else:
            s = 'sbloccato'
        print(f"Questo utente è {s}. Vuoi cambiare il suo stato? (s/n)")    #chiedo conferma
    
        if(input().lower()=='s'):
            cursor.execute(f'''UPDATE utenti 
                                    SET bloccato = {(data[0][0]+1)%2}
                                    WHERE nick = "{user}"''')   #cambio lo stato
            
        sqliteConn.commit() #salvo le modifiche

    except sqlite3.Error as error:
        print("Error: " + error)

    finally:
        if (sqliteConn):
            sqliteConn.close()

print("BENVENUTI NELLA CHAT")
recThread = ReceiveThread()
recThread.start()
while True:
    printMenu()
    choice = int(input(">>>>>"))    #switch case
    if choice == 0:
        break
    elif choice == 1:
        user_list()
        
    elif choice == 2:
        receivedMessages()
        
    elif choice == 3:
        sendMex()
    
    elif choice == 4:
        bloccaSblocca()
        
    else:
        pass

stop_thread = True
recThread.join()