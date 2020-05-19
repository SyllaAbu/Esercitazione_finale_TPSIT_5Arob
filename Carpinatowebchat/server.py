import flask
from flask import Flask, render_template, redirect, url_for, request,jsonify
import sqlite3 as sq
import datetime

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/api/v1/receive',methods=['GET','POST']) #metto sia get che post per future implementazioni
def receive():
    idDest=int(request.args['idDest'])
    conn=sq.connect('data.db')
    c=conn.cursor()
    c.execute(f"SELECT testo,idMitt,ora FROM Messaggi WHERE idDest={idDest} AND ricevuto='FALSE' ")
    results=c.fetchall()
    c.execute(f"UPDATE Messaggi SET ricevuto='TRUE' where idDest={idDest}")
    c.execute('commit') #salva modifiche db
    c.close()
    conn.close()
    return jsonify(results)

@app.route('/api/v1/send',methods=['GET','POST'])
def send():
    t = datetime.datetime.now() #ora invio messaggio
    nameDest=request.args['dest']
    testo=request.args['text']
    idMitt=int(request.args['idMitt'])
    conn=sq.connect('data.db')
    c=conn.cursor()
    c.execute(f'Select id FROM Utenti WHERE name="{nameDest}" ')
    idDest=c.fetchall()
    c.execute(f'Insert INTO Messagi("idDest","idMitt","testo","ora","ricevuto") VALUES ("{idDest}", "{idMitt},"{testo}","{t}","FALSE")')
    c.execute('commit') #salva modifiche db
    c.close()
    conn.close()
    return "Inviato"


@app.route('/',methods=['GET','POST'])
def __main__():
    return render_template('homepage.html')

@app.route('/api/v1/user_list',methods=['GET']) 
def lista():
    conn=sq.connect('data.db')
    c=conn.cursor()
    c.execute("SELECT * FROM Utenti")
    users=c.fetchall()
    c.close()
    conn.close() 
    c=0  
    utenti=[]
    for c in range(0,len(users)): #procedimento per non stampare la password
        x=users[c][0]
        y=users[c][1]
        a={'id':x,'Nome':y}
        utenti.append(a)
        print(x,y)
    return jsonify(utenti)

    

app.run()


''' IMPLEMENTAZIONE DA TERMINARE
def usernameEsistente(username):
    esistente=False
    with sqlite3.connect('data.db') as con:
                cur = con.cursor()
                cur.execute("SELECT * FROM Utenti")
                rows = cur.fetchall()
                for row in rows:
                    dbUser = row[0]
                    if dbUser==username:
                        esistente= True
    return esistente



@app.route('/iscrizione',methods=['GET','POST'])
def iscrizione():
    error = None
    if request.method == 'POST':
        name=request.form['name']
        password=request.form['password']
        #verifica se cè gia nome utente,inserisci quindi nome in db
        userEsiste=usernameEsistente(username)
        if userEsiste == True:
            error='username gia usato'
            username = request.form['username']
        else :
            conn=sq.connect('data.db')
            c=conn.cursor()
            print(f'INSERT INTO Utenti("Nome","password") VALUES ("{name}", "{password}")')
            c.execute(f'INSERT INTO Utenti("Nome","password") VALUES ("{name}", "{password}")')
            c.execute('commit') #salva modifiche db
            c.close()
            conn.close()

            return accesso()
@app.route('/accesso',methods=['GET','POST'])
def accesso():

    return render_template(index.html)
'''