import sqlite3
from datetime import datetime
import flask
from flask import jsonify,request



app = flask.Flask(__name__)
app.config["debug"] = True

@app.route('/api/v1/user_list', methods=['GET'])
def api_all():
    try:
        sqliteConn = sqlite3.connect('chat.db')
        cursor = sqliteConn.cursor()

        cursor.execute("SELECT * FROM utenti")
        user = cursor.fetchall()

    except sqlite3.Error:
        print("Errore! ")

    finally:
        if (sqliteConn):
            print('chiusura connessione DB')
            sqliteConn.close()

    return jsonify(user)

@app.route('/api/v1/send', methods=["GET"])
def inviare():
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

    return "Messaggio inviato"


@app.route('/api/v1/receive', methods=['GET'])
def messageForMe():
    if 'id_dest' in request.args:
        dest = int(request.args['id_dest'])
        try:
            sqliteConn = sqlite3.connect('chat.db')
            cursor = sqliteConn.cursor()

            cursor.execute(f"SELECT sender_id,text,receiver_id,timestamp FROM messaggi WHERE received=0  AND receiver_id = {dest}")
            anyMessage = cursor.fetchall()

            if len(anyMessage) != 0:
                for i in anyMessage:               
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

    return jsonify(anyMessage)
    
app.run(host="0.0.0.0", port=8082, debug=True) 