import sqlite3
import flask
from flask import jsonify,request
from datetime import datetime


app = flask.Flask(__name__)
app.config["debug"] = True

@app.route('/api/v1/user_list', methods=['GET'])
def api_all():
    try:
        sqliteConn = sqlite3.connect('DatabaseChat.db')
        cursor = sqliteConn.cursor()

        cursor.execute("SELECT * FROM utenti")
        user = cursor.fetchall()

    except sqlite3.Error as error:
        print("Error: " + error)

    finally:
        if (sqliteConn):
            print('chiusura connessione ')
            sqliteConn.close()

    return jsonify(user)

@app.route('/api/v1/send', methods=["GET"])
def invio():
    date = datetime.now()
    time = date.strftime("%H:%M:%S")

    if 'id_dest' in request.args and 'text' in request.args and 'id_mitt' in request.args:
        dest = int(request.args['id_dest'])
        text = request.args['text']
        mitt = int(request.args['id_mitt'])
    else:
        return("error: missing args")

    try:
        sqliteConn = sqlite3.connect('DatabaseChat.db')
        cursor = sqliteConn.cursor()

        cursor.execute(f"SELECT user_id from utenti WHERE user_id = {mitt} or user_id = {dest} ")
        users = cursor.fetchall()

        if len(users) > 1:
            cursor.execute(f"INSERT INTO messaggi(text,timestamp,length,received,receiver_id,sender_id) VALUES ('{text}','{time}',{len(text)},{False},{dest},{mitt})")
            sqliteConn.commit()
        else:
            return "utenti non registrati"

    except sqlite3.Error as error:
        print("Error: " + error)

    finally:
        if (sqliteConn):
            print('chiusura connessione DB')
            sqliteConn.close()

    return "Messaggio inviato"

if __name__== "__main__":

    app.run(host="0.0.0.0", port=8082, debug=True) 