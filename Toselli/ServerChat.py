import flask
from flask import request, jsonify
import sqlite3
from datetime import datetime
import os

app = flask.Flask(__name__)
Db = "dbServer.db"

@app.route("/api/v1/invia", methods=["GET", "POST"])
def ivia():
    if request.method == "GET":
        if "idDestinatario" in request.args and "testo" in request.args and "idMittente" in request.args:
            Destinatario = int(request.args["idDestinatario"])
            Testo = request.args["testo"]
            Mittente = int(request.args["idMittente"])
        else:
            return "Errore"
        
        try:
            sqliteConn = sqlite3.connect(Db)
            cursor = sqliteConn.cursor()
            
            cursor.execute(f"SELECT idUtente FROM utenti WHERE idUtente = {Destinatario} or idUtente = {Mittente};") #verifico esistenza entrambi utenti

            user = cursor.fetchall()

            if (len(user)>1):
                date = datetime.now() 
                time = date.strftime("%H:%M:%S") #creo stringa timestamp

                lunghezzatTesto = len(Testo) #lunghezza messaggio

                cursor.execute(f"INSERT INTO messaggi(idDestinatario, idMittente, timestamp, testo, lunghezzaTesto, ricevuto)" + 
                "VALUES ({Destinatario}, {Mittente}, '{Testo}', '{time}', {lunghezzatTesto}, {0});")   
                #setto ricevuto a 0 perchè non ancora letto dal destinatario

                sqliteConn.commit()
            else:
                return "Utenti non registrati"

        except sqlite3.Error as error:
            print("Errore: " + error)
        
        finally:
            if (sqliteConn):
                sqliteConn.close()
                return "Messaggio inviato"

@app.route("/api/v1/ricevuto", methods=["GET"])
def messaggioRicevuto():     
    if (flask.request.method == "GET"):
        if "idDestinatario" in request.args:   
            Destinatario = int(request.args["idDestinatario"]) #salvo id destinatario
        try:
            sqliteConn = sqlite3.connect(Db)
            cursor = sqliteConn.cursor()

            cursor.execute(f"SELECT idMittente,testo,idDestinatario,timeStamp FROM messaggi WHERE ricevuto=0  AND idDestinatario = {Destinatario}")
            anyMessage = cursor.fetchall()

            if len(anyMessage) != 0: #se vengono ricevuti messaggi
                for a in anyMessage:               
                    cursor.execute(f"UPDATE messaggi SET ricevuto = 1 WHERE messaggi.idDestinatario = {a[2]}") #update dello stato

                    sqliteConn.commit()

                if(len(res)==0):    #se non ho messaggi ritorno lista vuota
                    return []
            else:
                return []

        except sqlite3.Error as error:
            print("Error: " + error)

        finally:
            if (sqliteConn):
                print("Chiusura connessione DB")
                sqliteConn.close()
                return jsonify(anyMessage)  #ritorno lista con i messaggi

if __name__== "__main__":
    app.run(host="0.0.0.0", port=int(5076), debug=True)