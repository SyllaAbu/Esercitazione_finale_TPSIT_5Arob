from flask import Flask, request, jsonify
import datetime
import sqlite3
import os

dbPath = "data/db.db"  

app = Flask(__name__)


@app.route('/api/v1/send', methods=['GET'])
def send():
    dateFormat = "%m/%d/%Y %H:%M:%S"
# rivezione messaggi
@app.route('/api/v1/receive', methods=['GET'])
def receive():
    messages = {}
    if "id" in request.args:
        if len(request.args['id']) != 0:
            id = request.args['id']
            database = sqlite3.connect(dbPath)
            c = database.cursor()
           
            c.execute(
                f"SELECT mitt, text, time,   FROM MESSAGGI WHERE dest = {id} AND inviato = 'False'")
            messages = c.fetchall()
            c.execute(f"UPDATE MESSAGGI SET inviato = 'True' WHERE dest={id} AND inviato = 'False'")
            database.commit()
            print(messages)
            database.close()

    return jsonify(messages)


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
