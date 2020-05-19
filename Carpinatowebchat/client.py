import flask
from flask import Flask, render_template, redirect, url_for, request,jsonify
import sqlite3 as sq
from threading import Thread
import time

app = flask.Flask(__name__)
app.config["DEBUG"] = True

def main():
        scelta='z'
        while scelta != 'e' :
            scelta=input("a) invio b)lettura c)elenco e)uscita")
            if scelta=='a':
                send()
            elif scelta=='b':
                read()
            elif scelta=='c':
                userlist()
            elif scelta=='e':
                break

class chat(Thread):
    def send():#INVIO
        nome=input("Nome destinatario")
        text=input("Messaggio")
        params={'id_mitt':myId,'text':text,'dest':nome}
        text = text.replace(" ", "+")
        URL = "http://127.0.0.1:5000/api/v1/send"   
        req = request.get(url = URL, params=params)
        return "Inviato"

    

    def read(): #LETTURA
        URL = "http://127.0.0.1:5000/api/v1/receive" 
        req=request.get_data(url=URL,params={'id_dest':myId})
        conn=sq.connect('client.db')
        c=conn.cursor()
        c.execute(f"SELECT text,Name,idMitt FROM Ricevuti,Utenti WHERE idMitt=id and letto='FALSE'")
        text=c.fetchall()
        print(text)
        c.execute(f"UPDATE Messaggi SET letto='TRUE' where idMitt={text[2]}")
        c.close()
        conn.close()

    def userlist():
        URL = "http://127.0.0.1:5000/api/v1/user_list"   
        req = request.get(url = URL) #, params=params
        utenti=req.json
        print(utenti)

   
if __name__ == "__main__":
    myId=3
    tr=Thread()
    tr.start()