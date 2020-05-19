import sqlite3
import flask
from flask import jsonify,request
from datetime import datetime


app = flask.Flask(__name__)
app.config["debug"] = True

@app.route('/api/v1/user_list', methods=['GET'])        #funzione che restituisce la lista di tutti gli utenti salvati nel database
def api_all():
    try:
        sqliteConn = sqlite3.connect('chatDB.db')
        cursor = sqliteConn.cursor()

        cursor.execute("SELECT * FROM utenti")
        user = cursor.fetchall()

    except sqlite3.Error as error:
        print("Error: " + error)

    finally:
        if (sqliteConn):
            print('chiusura connessione DB')
            sqliteConn.close()

    return jsonify(user)    #restituisco un json con i file letti dal db

@app.route('/api/v1/send', methods=["GET"]) #funzione che salva nel db i messaggi ricevuti dai client
def save():
    date = datetime.now()
    time = date.strftime("%H:%M:%S")

    if 'id_dest' in request.args and 'text' in request.args and 'id_mitt' in request.args:
        dest = int(request.args['id_dest'])
        text = request.args['text']
        mitt = int(request.args['id_mitt'])
    else:
        return("error: missing args")

    try:
        sqliteConn = sqlite3.connect('chatDB.db')
        cursor = sqliteConn.cursor()

        cursor.execute(f"SELECT user_id from utenti WHERE user_id = {mitt} or user_id = {dest} ")
        users = cursor.fetchall()

        if len(users) > 1:
            cursor.execute(f"INSERT INTO messaggi(text,timestamp,length,received,receiver_id,sender_id) VALUES ('{text}','{time}',{len(text)},{False},{dest},{mitt})")
            sqliteConn.commit()
        else:
            return "utenti non registrati nel database"

    except sqlite3.Error as error:
        print("Error: " + error)

    finally:
        if (sqliteConn):
            print('chiusura connessione DB')
            sqliteConn.close()

    return 


@app.route('/api/v1/receive', methods=['GET'])  #funzione che controlla se ci sono nuovi messaggi per il client che richiede
def messageForMe():
    if 'id_dest' in request.args:
        dest = int(request.args['id_dest'])
        try:
            sqliteConn = sqlite3.connect('chatDB.db')
            cursor = sqliteConn.cursor()

            cursor.execute(f"SELECT sender_id,text,receiver_id,timestamp FROM messaggi WHERE received=0  AND receiver_id = {dest}") #legge se ci sono nuovi messaggi salvati nel database
            anyMessage = cursor.fetchall()

            if len(anyMessage) != 0:
                for i in anyMessage:               #imposta il campo received ad 1 quando il messaggio viene letto da un client
                    cursor.execute(f'''UPDATE messaggi 
                                        SET received = 1 
                                        WHERE messaggi.timestamp < datetime('now') and messaggi.receiver_id = {i[2]}''')

                    sqliteConn.commit()

        except sqlite3.Error as error:
            print(error)

        finally:
            if (sqliteConn):
                print('chiusura connessione DB')
                sqliteConn.close()
    else:
        return "invalid user id"

    return jsonify(anyMessage)  #restituisce un json con i messaggi da leggere
    
app.run(host="0.0.0.0", port=8082, debug=True) 