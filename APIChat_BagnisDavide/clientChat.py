import flask
from flask import jsonify, request
from datetime import datetime
from threading import Thread
import requests
import time
import sqlite3

myId = 2
myIp = "127.0.0.1"
port = 5000
stopThread = False

class ClientThread(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.client_id = myId
        self.ip_address = myIp
        print(f"Thread di ricezione dei messaggi per il client con id = {self.client_id}, ip = {self.ip_address}")
    
    def run(self):
        while True:
            time.sleep(5)
            parameters = {'id_dest' : self.client_id}
            url = "http://" + self.ip_address + ":" + str(port) + "/api/v1/receive"
            r = requests.get(url = url, params = parameters)
            #print(r.json())
            data = r.json()
            
            if r.status_code == 200:
                try:
                    sqliteConn = sqlite3.connect('DBs/clientDB.db')
                    c = sqliteConn.cursor()

                    if len(data) != 0:
                        for i in data:
                            c.execute(f'''SELECT blocked FROM Rubrica WHERE id_utente = {i[2]};''')

                            if(not c.fetchall()[0][0]):
                                c.execute(f"INSERT INTO MessaggiRx (text, id_mitt) VALUES ('{i[1]}','{i[2]}');")
                                sqliteConn.commit()

                except sqlite3.Error() as e:
                    print('Error: ' + e)  
                finally:
                    if (sqliteConn):
                        sqliteConn.close()
            else:
                print('Errore durante la chiamata al Server')

            if not stopThread:
                break
            
def printReceivedMex():
    try:
        sqliteConn = sqlite3.connect('DBs/clientDB.db')
        c = sqliteConn.cursor()

        c.execute(f"SELECT MessaggiRx.text, Rubrica.surname FROM MessaggiRx, Rubrica WHERE Rubrica.id_utente = MessaggiRx.id_mitt;")
        data = c.fetchall()
        for d in data:
            print(f"Messaggio ricevuto da: {d[1]} - Testo: {d[0]}")
            
        sqliteConn.commit()

    except sqlite3.Error as error:
        print("Error: " + error)

    finally:
        if (sqliteConn):
            sqliteConn.close()

def viewAllUsers():
    try:
        sqliteConn = sqlite3.connect("DBs/clientDB.db")
        c = sqliteConn.cursor()

        c.execute(f'SELECT * FROM Rubrica;')
        all_users = c.fetchall()

        for u in all_users:  
                print(f"ID: {u[0]} - Cognome: {u[1]} - Bloccato: {u[2]}")

    except sqlite3.Error as error:
        print("Error: " + error)

    finally:
        if (sqliteConn):
            sqliteConn.close()

def sendMex():
    try:
        sqliteConn = sqlite3.connect('DBs/clientDB.db')
        c = sqliteConn.cursor()

        id = int(input("Inserire l'id del destinatario del messaggio: "))
        c.execute(f"SELECT * FROM Rubrica WHERE id_utente = {id};")

        result = c.fetchall()
        if (len(result)==1):
            text = input('Digita il messaggio che vuoi inviare: \n')
            parameters = {'id_dest':result[0][0], 'text':text.replace(" ", "+"), 'id_mitt':myId}
            url = "http://" + myIp + ":" + str(port) + "/api/v1/send"
            r = requests.get(url = url, params = parameters)
            if(r.status_code==200):
                c.execute(f"INSERT INTO MessaggiTx (text, id_dest) VALUES ('{text}', {result[0][0]});")
                print("Messaggio inviato correttamente")    
            else:
                print("Errore nell' invio")
        else:
            print("Errore nell'inserimento del nickname")
            
        sqliteConn.commit()
    except sqlite3.Error as error:
                    print("Error: " + error)

    finally:
        if (sqliteConn):
            sqliteConn.close()

def bloccaUtente():
    try:
        sqliteConn = sqlite3.connect('DBs/clientDB.db')
        c = sqliteConn.cursor()

        id = int(input("Inserire l'id del destinatario da bloccare: "))
        c.execute(f"SELECT blocked FROM Rubrica WHERE id_utente = {id};")

        data = c.fetchall()
        if not data[0][0]:
            c.execute(f"UPDATE Rubrica SET blocked = 1 WHERE id_utente = {id};")
        else:
            print("Impossibile bloccare l'utente specificato. L'utente è già bloccato!")
        
        sqliteConn.commit()
        
    except sqlite3.Error as error:
        print("Error: " + error)

    finally:
        if (sqliteConn):
            sqliteConn.close()

def sbloccaUtente():
    try:
        sqliteConn = sqlite3.connect('DBs/clientDB.db')
        c = sqliteConn.cursor()

        id = int(input("Inserire l'id del destinatario da sbloccare: "))
        c.execute(f"SELECT blocked FROM Rubrica WHERE id_utente = {id};")

        data = c.fetchall()
        if data[0][0]:
            c.execute(f"UPDATE Rubrica SET blocked = 0 WHERE id_utente = {id};")
        else:
            print("Impossibile sbloccare l'utente specificato. L'utente è già sbloccato!")
        
        sqliteConn.commit()
        
    except sqlite3.Error as error:
        print("Error: " + error)

    finally:
        if (sqliteConn):
            sqliteConn.close()

def main():
    
    while True:
        print("\nMenu:\n0 = Esci\n1 = Vedi i contatti salvati in rubrica\n2 = Invia un messaggio\n3 = Stampa messaggi ricevuti\n4 = Blocca un utente\n5 = Sblocca un utente\n")
        choice = int(input("Insert option code: "))
        if choice == 0:
            break
        elif choice == 1:
            viewAllUsers()
        elif choice == 2:
            sendMex()
        elif choice == 3:
            printReceivedMex()
        elif choice == 4:
            bloccaUtente()
        elif choice == 5:
            sbloccaUtente()

    return

if __name__ == "__main__":
    
    newThread = ClientThread()
    newThread.start()

    main()

    newThread.join()