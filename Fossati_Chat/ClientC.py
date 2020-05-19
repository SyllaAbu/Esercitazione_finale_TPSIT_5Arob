import flask
import sqlite3
from flask import jsonify,request
from threading import Thread
from datetime import datetime
import requests
import time
import threading



class ClientThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.id = myId
        self.ip = ip

    def run(self):        
        while True:
            time.sleep(15)
            URL = "http://" + self.ip + "/api/v1/receive"
            params = {'id_dest': self.id}

            r = requests.get(url= URL, params = params)

            try:
                sqliteConnection = sqlite3.connect('client.db')

                cursor = sqliteConnection.cursor()

                if len(r.json()) != 0:
                    for i in r.json():
                        cursor.execute(f"INSERT INTO receivedMessages (text,sender,received_at,alreadyRead) VALUES ('{i[1]}','{i[0]}','{i[3]}',{False})")
                        sqliteConnection.commit()

            except sqlite3.Error():
                print('Errore !!' )
            finally:
                if (sqliteConnection):
                    sqliteConnection.close()

def readMessages():
    try:
        sqliteConnection = sqlite3.connect('clientDB.db')
        cursor = sqliteConnection.cursor()

        cursor.execute(f"SELECT * FROM receivedMessages,rubrica where receivedMessages.sender = rubrica.id and rubrica.locked = 0 order by received_at;")
        msg = cursor.fetchall()

        for i in msg:
            cursor.execute(f"SELECT name,surname FROM rubrica where id = {i[2]}")
            name = cursor.fetchall()

            print(str(name[0][0]), str(name[0][1])  +  ": " + i[1] + " alle ore " + str(i[3] + "\n"))

    except sqlite3.Error as error:
        print("Error: " + error)

    finally:
        if (sqliteConnection):
            print('messaggi stampati')
            sqliteConnection.close()

    return

def sendMessage():
    id_dest = int(input("\nInserisci il numero di registro del destinatario"))
    text = input("\nInserisci il messaggio da inviare\n")

    params = {'id_dest' : id_dest,'text' : text, 'id_mitt' : myId}
    text = text.replace(" ", "+")
    URL = "http://" + ip + "/api/v1/send"   

    r = requests.get(url = URL, params=params)
    if r.status_code == 200:
        print("messaggio inviato")
    else:
        print("non sono riuscito ad inviare il messaggio")
    
    return

def getAllUsers():
    URL = "http://" + ip + "/api/v1/user_list" 
    r = requests.get(url = URL)
    data = r.json()
    for i in data:
        print(i[0]," - ", i[1], " - ", i[2])


def main(idReg, newThread):
    while True:
        sel = int(input("\n1: invia messaggio\n2: stampa tutti gli utenti\n3: stampa messaggi\n4: Esci\n>>>>"))

        if sel == 1:
            getAllUsers()
            sendMessage()
        if sel == 2:
            getAllUsers()
        if sel == 3:
            readMessages()
        if sel == 4:
            newThread.join()
            break
    return 


if __name__ == "__main__":
    myId = int(input("inserisci il tuo numero di registro: "))
    ip =  input("\nInserisci ip e porta del server\n")

    newThread = ClientThread()
    newThread.start()

    main(myId, newThread)
    

    
    