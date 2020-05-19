from flask import Flask, render_template, redirect, url_for, request, jsonify
import json
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def home():
    return "<h1>Server chat</h1>"

@app.route('/api/v1/receive', methods=['GET'])
def receive():
    sqliteConn = sqlite3.connect('DBs/serverDB.db')
    c = sqliteConn.cursor()

    if 'id_dest' in request.args:
        id_dest = int(request.args['id_dest'])
    else:
        return "Errore: Non è stato immesso l'id del destinatario!"

    c.execute(f"SELECT Utenti.surname, Messaggi.text, Messaggi.id_mitt, Messaggi.time FROM Messaggi, Utenti WHERE Messaggi.id_mitt = Utenti.id_utente AND id_dest ='{id_dest}' ORDER BY Messaggi.time;")
    all_mex = c.fetchall()

    for a in all_mex:
        c.execute(f"UPDATE Messaggi SET received = 1 WHERE Messaggi.id_dest = '{a[2]}';")
        sqliteConn.commit()
    return jsonify(all_mex)

@app.route('/api/v1/send', methods=['GET'])
def send():
    if 'id_dest' in request.args and 'id_mitt' in request.args and 'text' in request.args:
        id_dest = int(request.args['id_dest'])
        id_mitt = int(request.args['id_mitt'])
        text = str(request.args['text'])
    else:
        return "Errore: potrebbero mancare dei parametri nell'url!<br/>Assicurarsi di aver inserito correttamente il nickname del destinatario, il proprio id e il testo del messaggio."
    
    time = str(datetime.now().strftime('%H:%M:%S'))

    try:
        sqliteConn = sqlite3.connect("DBs/serverDB.db")
        c = sqliteConn.cursor()

        c.execute(f'INSERT INTO Messaggi(id_mitt, id_dest, text, time) VALUES ("{id_mitt}", "{id_dest}", "{text}", "{time}");')
        sqliteConn.commit()
    except sqlite3.Error as error:
        print(f"Error : {error}")
    finally: 
        sqliteConn.close()

    return ("Messaggio inviato!")

@app.route('/api/v1/user_list', methods=['GET'])
def viewUsers():
    sqliteConn = sqlite3.connect("DBs/serverDB.db")
    c = sqliteConn.cursor()

    c.execute(f'SELECT * FROM Utenti;')
    all_users = jsonify(c.fetchall())
    return all_users

@app.route('/api/v1/add_user', methods=['GET'])
def addUser():
    if 'id_utente' in request.args and 'surname' in request.args:
        id_utente = str(request.args['id_utente'])
        surname = str(request.args['surname'])
    else:
        return "Errore: potrebbero mancare dei parametri nell'url!<br/>Assicurarsi di aver inserito correttamente l'id, l'indirizzo IP, la porta e il nickname del nuovo utente."

    try:
        sqliteConn = sqlite3.connect("DBs/serverDB.db")
        c = sqliteConn.cursor()

        c.execute(f'INSERT INTO Utenti(id_utente, surname) VALUES ("{id_utente}", "{surname}");')
        sqliteConn.commit()
    except sqlite3.Error as error:
        print(f"Error: {error}")
    finally: 
        sqliteConn.close()

    return ("Utente aggiunto alla rubrica!")

app.run()