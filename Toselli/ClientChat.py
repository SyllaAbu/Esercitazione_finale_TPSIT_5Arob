import flask
from flask import request, jsonify
import sqlite3
import requests
from threading import Thread 
import time
import sys
import os

URL = "http://127.0.0.1:5076/api/v1/"
Db = "dbClient.db"
stoppaThread = False #variabile per fermare il thread

class ReceiveThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.connectionURL = URL + 'receive'
        self.PARAMS = {'idDestinatario' : NumReg}

    def run(self):
        while True:
            if not stoppaThread: #controllo per fermare il thread
                time.sleep(5)
                r = requests.get(url = self.connectionURL, params=self.PARAMS) #richiesta di tipo GET
                data = r.json() #converto in oggetto json
            
                try:
                    sqliteConn = sqlite3.connect(Db) #connessione al db
                    cursor = sqliteConn.cursor() #cursore
                    if(len(data)!=0): #se risposta più lunga di zero
                        for d in data:
                            cursor.execute(f"SELECT bloccato FROM utenti WHERE user_id = {d[0]};")
                            if(not cursor.fetchall()[0][0]):
                                cursor.execute(f"INSERT INTO messaggi(testo, idMittente, idDestinatario) VALUES ('{d[1]}', {d[2]}, {d[3]});")
                    sqliteConn.commit() #modifico db

                except sqlite3.Error as error:
                    print("Errore: " + error)

                finally:
                    if (sqliteConn):
                        sqliteConn.close()
            else:
                break

    def inviaMessaggio():
        try:
            sqliteConn = sqlite3.connect(Db)
            cursor = sqliteConn.cursor()

            Destinatario = input("Inserire destinatario\n")
            cursor.execute(f"SELECT idUtente FROM utenti WHERE nome = '{Destinatario}';") #trovo id del destinatario
            result = cursor.fetchall()

            if(len(result)==1):
                testo = input("Inserire messaggio da inviare: \n")
                PARAMS={'idDestinatario':result[0][0], 'testo':text.replace(" ", "+"), 'idMittente':NumReg}
                r = requests.get(url=URL+'send', params=PARAMS)
                if(r.status_code==200):
                    cursor.execute(f"INSERT INTO messaggi(testo, idDestinatario) VALUES ('{testo}', {result[0][0]});")
                    print("Messaggio inviato correttamente")    
                else:
                    print("Errore nell' invio")
            else:
                print("Errore nell'inserimento del nome")
                sqliteConn.commit()
                
        except sqlite3.Error as error:
            print("Error: " + error)

        finally:
            if (sqliteConn):
                sqliteConn.close()

    def messaggiRicevuti():
        try:
            sqliteConn = sqlite3.connect(Db)
            cursor = sqliteConn.cursor()

            cursor.execute(f"SELECT messaggi.testo, utenti.idUtente FROM messaggi, utenti WHERE utenti.idUtente = Messaggi.idMittente;")
            data = cursor.fetchall()
            for d in data: #scorro per i risultati
                print(f"Messaggio ricevuto da: {d[2]} - Testo: {d[1]}")
             
            sqliteConn.commit()

        except sqlite3.Error as error:
            print("Error: " + error)

        finally:
            if (sqliteConn):
                sqliteConn.close()

    def rubrica():
        try:
            sqliteConn = sqlite3.connect(Db)
            cursor = sqliteConn.cursor()

            cursor.execute(f"SELECT * FROM utenti;") #ritorno lista utenti
            data = cursor.fetchall()
            for d in data:
                print(f"idUtente: {d[0]} - Nome: {d[1]} - Cognome: {d[2]} - Bloccato: {3}")

        except sqlite3.Error as error:
            print("Error: " + error)

        finally:
            if (sqliteConn): #se connessione attiva, chiudo
                print('Chiusura connessione database')
                sqliteConn.close()

    def bloccaSblocca():
        try:
            sqliteConn = sqlite3.connect(Db)
            cursor = sqliteConn.cursor()

            nome = input("Inserire nome utente da bloccare (o sbloccare): \n")
            cursor.execute(f"SELECT bloccato FROM utenti WHERE nome = '{nome}';")
            data = cursor.fetchall()
            if not data[0][0]:
                print(f"Questo utente è bloccato. Vuoi sbloccarlo? 1 = affermativo")
            else:
                print(f"Questo utente è sbloccato. Vuoi bloccarlo? 1 = affermativo")
        
            if(input()=="1"):
                cursor.execute(f"UPDATE utenti SET bloccato = {(data[0][0]+1)%2} WHERE nome = '{nome}'")
                
            sqliteConn.commit()

        except sqlite3.Error as error:
            print("Error: " + error)

        finally:
            if (sqliteConn):
                sqliteConn.close()

NumReg = input("Inserire numero di registro: ")
recThread = ReceiveThread()
recThread.start()
while True:
    print("1 - Invia")
    print("2 - Messaggi ricevuti")
    print("3 - Rubrica")
    print("4 - Blocca/Sblocca")
    print("5 - Esci")
    scelta = int(input(">>>>>"))    #switch
    if scelta == 1: #Invia
        inviaMessaggio()
    elif scelta == 2: #Messaggi ricevuti
        messaggiRicevuti()  
    elif scelta == 3: #Rubrica
        rubrica()
    elif scelta == 4: #Blocca/Sblocca
        bloccaSblocca() 
    elif scelta == 5: #Esci
        break
    else:
        pass

stoppaThread = True
recThread.join()