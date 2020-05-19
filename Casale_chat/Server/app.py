'''

Author: Casale Alex 5A^ROB
Project: Flask Chat con API

Flask-Chat: SERVER

'''

from flask import Flask, request, jsonify
import datetime
import sqlite3
import base64

dbPath = "instance/db.db"   # Path del database

app = Flask(__name__)

# API Send: Invio messaggi tra Client e Client 
@app.route('/api/v1/send', methods=['GET', 'POST'])
def send():
    dateFormat = "%m/%d/%Y %H:%M:%S"
    TIME = datetime.datetime.now().strftime(dateFormat)
    # Invio immagini (Funzionante in parte: Il client invia un'immagine e il server se la salva nella path delle immagini ricevute)
    if request.method == "POST":
        path = "clientImages/"  # Path della cartella di salvataggio delle immagini
        image = request.files['img']    # Ricezione dell'immagine
        dest = request.args['dest']     # Ricezione del destinatario
        mitt = request.args['mitt']     # Ricezione del mittente
        print(dest, mitt)
        fullPath = f"{path}{image.filename}"    # Path completa
        image.save(fullPath)    # Salvataggio dell'immagine nella determinata path con il determinato nome

        database = sqlite3.connect(dbPath)
        cur = database.cursor()
        # Salvataggio dell'invio dell'immagine nel database con il campo isPhoto settato a True
        cur.execute(f"INSERT INTO MESSAGGI (dest, mitt, text, 'time', len, isPhoto) VALUES ({dest}, {mitt}, '{fullPath}', '{TIME}',{len(fullPath)}, 'True')")
        database.commit()
        database.close()
        return 'Immagine inviata'
    else:
        # Invio vero e proprio del messaggio tra Client e Client
        if "ID_DEST" and "ID_MITT" and "TEXT" in request.args:
            ID_DEST = request.args['ID_DEST']
            ID_MITT = request.args['ID_MITT']
            TEXT = request.args['TEXT']
            if ID_DEST and ID_MITT and TEXT != "":
                database = sqlite3.connect(dbPath)
                c = database.cursor()
                # Salvataggio dei messaggi nel database
                c.execute(f"INSERT INTO MESSAGGI (dest, mitt, text, 'time', inviato, len) VALUES ({ID_DEST}, {ID_MITT}, '{TEXT}', '{TIME}', 'False',{len(TEXT)})")
                database.commit()
                database.close()
                return 'True'
            else:
                return 'False'
        return 'False'

# API Receive: Ricezione dei messaggi da parte dei client
@app.route('/api/v1/receive', methods=['GET'])
def receive():
    messages = {}
    if "id" in request.args:
        if len(request.args['id']) != 0:
            id = request.args['id']
            database = sqlite3.connect(dbPath)
            c = database.cursor()
            # Selezione di tutti i messaggi di quel determinato client che non sono ancora stati letti/ricevuti
            c.execute(
                f"SELECT mitt, text, time, isPhoto  FROM MESSAGGI WHERE dest = {id} AND inviato = 'False'")
            messages = c.fetchall()
            # Update del campo inviato: Quando un client invoca questa API vengono aggiornati tutti i messaggi non ancora letti
            c.execute(f"UPDATE MESSAGGI SET inviato = 'True' WHERE dest={id} AND inviato = 'False'")
            database.commit()
            print(messages)
            database.close()

    return jsonify(messages)

# API Users List: Se invocata restituirà l'elenco di tutti gli utenti salvati nel database del server
@app.route('/api/v1/user_list', methods=['GET'])
def user_list():
    database = sqlite3.connect(dbPath)
    c = database.cursor()
    c.execute(
        f"SELECT * FROM UTENTI ORDER BY id_utente")
    users = c.fetchall()
    database.close()
    return jsonify(users)



if __name__ == '__main__':
    app.run()
