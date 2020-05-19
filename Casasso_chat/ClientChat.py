

import sqlite3
from threading import Thread
import flask
from flask import jsonify, request
from datetime import datetime
import threading
import requests
import time


class ClientThread(Thread):
    def __init__(self):
        Thread.__init__(self)  
        self.id = myId
        self.ip = ip
     
    def run(self):
        while True:
            time.sleep(15)
            params = {'id_dest': self.id}
            URL="http://" + self.ip + "/api/v1/receive"
            r = requests.get(url=URL, params=params)

            try:
                sqliteConn = sqlite3.connect('DatabaseClient.db')
                cursor = sqliteConn.cursor()

                if len(r.json()) != 0:
                    for i in r.json():
                        cursor.execute(
                            f'''
                                INSERT INTO Mess_R(Text, Id_Mitt) 
                                VALUES ("{d[3]}", {d[0]});''') 
                        sqliteConn.commit() 
                    

            except sqlite3.Error() as err:
                print('Error: ' + err)
            finally:
                if (sqliteConn):
                    sqliteConn.close()

def Invio_Messaggi():
    id_dest = int(input("\nInserisci il numero di registro del destinatario"))
    text = input("\nInserire  testo del messaggio\n")

    params = {'id_dest': id_dest, 'text': text, 'id_mitt': myId}
    text = text.replace(" ", "+")
    URL = "http://" + ip + "/api/v1/send"

    r = requests.get(url=URL, params=params)
    if r.status_code == 200:
        print("messaggio inviato")
    else:
        print("messaggio non inviato")

    return
       




def Messaggi_ricevuti(): 
    try:
        sqliteConn = sqlite3.connect(DatabaseClient.db)   
        cursor = sqliteConn.cursor()                            

        cursor.execute(f"SELECT Mess_R.text, utenti.nick FROM Mess_R, utenti WHERE utenti.user_id = Mess_R.Id_Mitt;")
        for d in data:      
            print(f"Messaggio ricevuto da: {d[1]} - Testo del messaggio: {d[0]}")

        sqliteConn.commit()

    except sqlite3.Error as error:
        print("Error: " + error)

    finally:
        if (sqliteConn):
            sqliteConn.close()  


def utenti():
    URL = "http://" + ip + "/api/v1/user_list"
    r = requests.get(url=URL)
    data = r.json()
    for i in data:
        print(i[0], " ", i[1], " ", i[2])


    
    
  

def main(idReg, newThread):
   
    while True:
    
        scelta = int(input("0)esci 1)rubrica 2) 3)messagi ricevuti 4)invia messaggio"))
        if scelta == 0:
            newThread.join()
            break
        elif scelta == 1:
            utenti()

        elif scelta == 2:
            Messaggi_ricevuti()

        elif scelta == 3:
           Invio_Messaggi()

        else:
            pass



if __name__ == "__main__":
    myId = int(input("inserisci il tuo numero di registro: "))
    ip =  input("\nInserisci ip e porta del server \n")

    newThread = ClientThread()
    newThread.start()

    main(myId, newThread)
    

    
    