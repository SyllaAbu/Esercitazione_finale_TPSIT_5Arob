import flask
from flask import request, jsonify
import requests
import sqlite3
from threading import Thread 
from config import MyId, dbPath, URL, dbName
import time
import sys
import os


class ClientThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        sqlConn = sqlite3.connect(dbName)
        curs = sqlConn.cursor()
        while True:
            time.sleep(5)   # refresh ogni 5 secondi
            res = requests.get(f"{URL}/api/v1/receive?id={MyId}").json()
            for r in res:
                ris = curs.execute(f"SELECT * FROM Contatti WHERE id = {r[0]} ").fetchone()
                if ris is not None:
                    curs.execute(f"INSERT INTO messaggi_ricevuti (id_mitt, text) VALUES ({r[0]}, '{r[1]}')")
                    sqlConn.commit()

def createDatabase():
    f= open(dbName,"w+")
    f.close()
    fd = open(schema, 'r')
    sqlFile = fd.read()
    fd.close()
    sqlConn = sqlite3.connect(dbName)
    curs = sqlConn.cursor()
    sqlCommands = sqlFile.split(';')    
    for cmd in sqlCommands:      
        try:
            if cmd.strip() != '':
                curs.execute(cmd)
        except IOError:
            print ("Errore")
    sqlConn.commit()       

# Menù
def menu():
    print("\n\n1. Rubrica")
    print("2. Aggiorna Contatti")
    print("3. Invia un messaggio")
    print("4. Visualizzza Messaggi ricevuti")
    print("0. Esci\n")


def Contacts(id):
    sqlConn = sqlite3.connect(dbName)
    curs = sqlConn.cursor()
    contatcs = curs.execute("SELECT * FROM Contatti").fetchall()
    for c in contatcs:
        print(c[0], c[1], c[2], c[3])

# Aggiornamento della rubrica
def updateContacts():
    URL = f"{URL}/api/v1/user_list"       
    contacts = requests.get(URL).json()
    sqlConn = sqlite3.connect(dbName)
    curs = sqlConn.cursor()
    cont  = 0
    for c in contacts:
        
        result = curs.execute(f"SELECT * FROM Contatti WHERE id = '{c[0]}'").fetchall()
        if len(result) == 0:
            cont += 1   
            curs.execute(f"INSERT INTO Contatti (id, name, surname) VALUES ({c[0]}, '{c[1]}', '{c[2]}')")
            sqlConn.commit()
    print(f"\nInseriti {cont} nuovi contatti")

# Invio dei messaggi
def sendMessage(idDest, text):
    sqlConn = sqlite3.connect(dbName)
    curs = sqlConn.cursor()
    ris = curs.execute(f"SELECT * FROM Contatti WHERE id = {idDest}").fetchone()
    if ris is not None:
        
        res = requests.get(f"{URL}/api/v1/send?ID_DEST={idDest}&ID_MITT={MyId}&TEXT={text}")
        if res:
            curs.execute(f"INSERT INTO messaggi_inviati (id_dest, text) VALUES ({idDest}, '{text}')")
            sqlConn.commit()
            print("Messagge sent")
        else:
            print("Error: message not sent")


def receiveMsg():
    sqlConn = sqlite3.connect(dbName)
    curs = sqlConn.cursor()
    res = curs.execute("SELECT * FROM messaggi_ricevuti").fetchall()
    sqlConn.commit()
    if len(res) != 0:
        for r in res:
            mitt = curs.execute(f"SELECT * FROM Contatti WHERE id = {r[1]}").fetchone()
            sqlConn.commit()
            #Stampa del messaggio e name/surname
            print("Mittente: ", mitt[1], mitt[2], "Messaggio: ", r[2])
    else:
        print("No more messages")

def main(thread):
    updateContacts()
    while True:
        menu()
        while True:
            try:
                option = int(input("Scegli un opzione: "))
                break
            except:
                print("Opzione non valida")

        if option == 1:
            Contacts(id)
        elif option == 2:
            updateContacts()
        elif option == 3:
            id_dest = input("Id del destinatario: ")
            textToSend = input("Inserisci il testo del messaggio: ")
            sendMessage(id_dest, textToSend)
        elif option == 4:
            receiveMsg()
        elif option == 0:
            break
    thread.join()

if __name__ == "__main__":

    # Se il file database non esiste ne verrà creato uno
    if not path.exists(dbName):
        createDatabase()
    newthread = ClientThread()
    newthread.start()
    main(newthread)