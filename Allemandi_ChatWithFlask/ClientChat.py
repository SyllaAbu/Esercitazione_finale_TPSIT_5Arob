import sqlite3
from threading import Thread
import flask
from flask import jsonify,request
from datetime import datetime
import threading
import requests
import time

class ClientThread(Thread):
    def __init__(self):             #creazione thread per lettura in parallelo alle altre funzioni
        Thread.__init__(self)
        self.id = myId
        self.ip = ip

    def run(self):        
        while True:
            time.sleep(15)
            params = {'id_dest': self.id}
            url = URL + "receive"
            r = requests.get(url= url, params = params)     #creazione url per connessione al server

            try:
                sqliteConnection = sqlite3.connect('clientDB.db')       #connessione al database

                cursor = sqliteConnection.cursor()

                if len(r.json()) != 0:
                    for i in r.json():
                        cursor.execute(f"INSERT INTO receivedMessages (text,sender,received_at,alreadyRead) VALUES ('{i[1]}','{i[0]}','{i[3]}',{False})")
                        sqliteConnection.commit()       #inserimento dei valori letti nel database del client

            except sqlite3.Error() as e:
                print('Error: ' + e)  
            finally:
                if (sqliteConnection):
                    sqliteConnection.close()               

def readMessages():         #funzione per lettura dei messaggi ricevuti
    try:
        sqliteConnection = sqlite3.connect('clientDB.db')
        cursor = sqliteConnection.cursor()

        cursor.execute(f"SELECT * FROM receivedMessages,rubrica where receivedMessages.sender = rubrica.id and rubrica.locked = 0 order by received_at;")
        msg = cursor.fetchall() #lettura dei messaggi ricevuti dagli utenti non bloccati

        for i in msg:
            cursor.execute(f"SELECT name,surname FROM rubrica where id = {i[2]}")       #ciclo per stampare i messaggi
            name = cursor.fetchall()

            print(str(name[0][0]), str(name[0][1])  +  ": " + i[1] + " alle ore " + str(i[3] + "\n"))

    except sqlite3.Error as error:
        print("Error: " + error)

    finally:
        if (sqliteConnection):
            print('messaggi stampati')
            sqliteConnection.close()

    return
        
def sendMessage():  #funzione per inviare messaggi
    id_dest = int(input("\nInserisci il numero di registro del destinatario"))
    text = input("\nInserisci testo del messaggio\n")

    params = {'id_dest' : id_dest,'text' : text, 'id_mitt' : myId}      #creazione dell'url e formattazione del messaggio se contiene spazi vuoti
    text = text.replace(" ", "+")
    url = URL + "send"   

    r = requests.get(url = url, params=params)                  #invio del messaggio al server e conferma usando lo status code della risposta http
    if r.status_code == 200:
        print("messaggio inviato")
    else:
        print("non sono riuscito ad inviare il messaggio")
    
    return 
    
def getAllUsers():      #funzione per leggere tutti gli utenti in rubrica
    url = URL + "user_list" 
    r = requests.get(url = url)
    data = r.json()
    for i in data:
        print(i[0]," -- ", i[1], " -- ", i[2])

def lockUser(): #funzione per bloccare utenti dalla rubrica
    getAllUsers()
    nUser = int(input("inserisci numero di registro del contatto da bloccare: "))
    try:
        sqliteConnection = sqlite3.connect('clientDB.db')
        cursor = sqliteConnection.cursor()

        cursor.execute(f"UPDATE rubrica SET locked = 1 WHERE id = {nUser}") #cambio variabile locked dal database per bloccare il contatto
        sqliteConnection.commit()

        cursor.execute(f"SELECT name,surname FROM rubrica where id = {nUser}")  #per conferma, query al databse e stampa dell'utente appena bloccato
        name = cursor.fetchall()

        print(f"utente bloccato: {name[0][0]} {name[0][1]}")

    except sqlite3.Error as error:
        print("Error: " + error)
    finally:
        if (sqliteConnection):
            print('chiusura connessione DB')
            sqliteConnection.close()

def unlockUser():   #funzione per sbloccare utenti dalla rubrica
    getAllUsers()
    nUser = int(input("inserisci numero di registro del contatto da sbloccare: "))
    try:
        sqliteConnection = sqlite3.connect('clientDB.db')
        cursor = sqliteConnection.cursor()

        cursor.execute(f"UPDATE rubrica SET locked = 0 WHERE id = {nUser}") 
        sqliteConnection.commit()

        cursor.execute(f"SELECT name,surname FROM rubrica where id = {nUser}")
        name = cursor.fetchall()

        print(f"utente sbloccato: {name[0][0]} {name[0][1]}")

    except sqlite3.Error as error:
        print("Error: " + error)
    finally:
        if (sqliteConnection):
            print('chiusura connessione DB')
            sqliteConnection.close()

def showLockedUsers():  #funzione per stampare tutti gli utenti bloccati dalla rubrica
    try:
        sqliteConnection = sqlite3.connect('clientDB.db')
        cursor = sqliteConnection.cursor()

        cursor.execute(f"SELECT name,surname FROM rubrica where locked=1")
        names = cursor.fetchall()

        if len(names) == 0:
            print("nessun utente bloccato")
        else:
            for i in names:
                print(f"-- {i[0]} -- {i[1]}")

    except sqlite3.Error as error:
        print("Error: " + error)
    finally:
        if (sqliteConnection):
            print('chiusura connessione DB')
            sqliteConnection.close()


def main(newThread): #main del programma contenente il menu per la selezione di cosa fare
    while True:
        sel = int(input("\n1: invia messaggio\n2: blocca utente\n3: sblocca utente\n4: stampa tutti gli utenti\n5: stampa messaggi\n6: stampa utenti bloccati\n7: Esci\n>>>>"))

        if sel == 1:
            getAllUsers()
            sendMessage()
        if sel == 2:
            lockUser()
        if sel == 3:
            unlockUser()
        if sel == 4:
            getAllUsers()
        if sel == 5:
            readMessages()
        if sel == 6:
            showLockedUsers()
        if sel == 7:
            newThread.join()
            break
    return 


if __name__ == "__main__":  
    myId = int(input("inserisci il tuo numero di registro: "))
    ip =  input("\nInserisci ip e porta del server (Es xxx.xxx.x.x:xxxx): ")
    URL = "http://" + ip + "/api/v1/"

    newThread = ClientThread()  #creo istanza del nuovo thread per la lettura e lo avvio
    newThread.start()

    main(newThread)   #chiamata alla funzione main
    newThread.join()
    

    
    