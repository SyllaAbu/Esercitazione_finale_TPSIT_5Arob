import flask
from flask import request, jsonify
import sqlite3
from datetime import datetime
import os

app = flask.Flask(__name__)
path_db = 'static/db_server_chat.db'    #salvo il path del db relativo a questo programma

@app.route('/api/v1/receive', methods=['GET'])
def messageForMe():     
    '''Funzione che ritorna i messaggi ricevuti di un certo utenti'''
    if (flask.request.method == 'GET'):
        if 'id_dest' in request.args:   
            dest = int(request.args['id_dest']) #salvo l'id di destinazione
        try:
            sqliteConn = sqlite3.connect(path_db)   #connessione e istanziazione del cursore
            cursor = sqliteConn.cursor()

            cursor.execute(f"SELECT sender_id,text,receiver_id,timestamp FROM messaggi WHERE received=0  AND receiver_id = {dest}")
            anyMessage = cursor.fetchall()

            if len(anyMessage) != 0:    #se il numero dei messaggi è diverso da zero (ovvero se si sono ricevuti dei messaggi)
                for a in anyMessage:               
                    cursor.execute(f'''UPDATE messaggi 
                                        SET received = 1 
                                        WHERE messaggi.receiver_id = {a[2]}''') #update dello stato

                    sqliteConn.commit() #salvo modifiche

                if(len(res)==0):    #se non ho messaggi ritorno una lista vuota
                    return []
            else:
                return []

        except sqlite3.Error as error:
            print("Error: " + error)

        finally:
            if (sqliteConn):
                print('Chiusura connessione DB')
                sqliteConn.close()
                return jsonify(anyMessage)  #ritorno la lista con i messaggi

@app.route('/', methods=['GET'])
def home():
    return "<h1>CHAT</h1><p>Prototipo di chat con Flask.</p>"


@app.route('/api/v1/user_list', methods=['GET'])
def api_all():
    '''Funzione che ritorna tutti gli utenti del database'''
    try:
        sqliteConn = sqlite3.connect(path_db)
        cursor = sqliteConn.cursor()

        cursor.execute("SELECT * FROM utenti")  #query per avere la lista di tutti gli utenti
        user = cursor.fetchall()

    except sqlite3.Error as error:
        print("Error: " + error)

    finally:
        if (sqliteConn):
            print('chiusura connessione DB')
            sqliteConn.close()
            return jsonify(user)    #ritorno la lista degli utenti

@app.route('/api/v1/send', methods=['GET', 'POST'])
def api_send():
    if request.method == 'GET':
        if 'id_dest' in request.args and 'text' in request.args and 'id_mitt' in request.args:  #verifico che nell'URL ci siano alcuni campi
            dest = int(request.args['id_dest'])
            text = request.args['text']
            mitt = int(request.args['id_mitt'])
        else:
            return 'Error missing arguments'
        
        try:
            sqliteConn = sqlite3.connect(path_db)   #connessione DB e istanziazione cursore
            cursor = sqliteConn.cursor()
            
            cursor.execute(f'''SELECT user_id
                                FROM utenti
                                WHERE user_id = {dest} or user_id = {mitt};''') #verifico che esistano tutti e due gli utenti

            user = cursor.fetchall()

            if (len(user)>1):   #se la risposta comprende più di un utente
                date = datetime.now() 
                time = date.strftime("%H:%M:%S")    #creo la stringa del timestamp

                len_text = len(text)    #misuro la lunghezza del testo del messaggio simulando un campo di header di molti protocolli

                cursor.execute(f'''
                    INSERT INTO messaggi(receiver_id, sender_id, timestamp, text, length, received) 
                    VALUES ({dest}, {mitt}, "{text}", "{time}", {len_text}, {False});''')   #inserisco i dati settando il received false poiché non è ancora stato letto dall'utente

                sqliteConn.commit() #salvo le modifiche
            else:
                return 'Utenti non registrati'

        except sqlite3.Error as error:
            print('Error: ' + error)
        
        finally:
            if (sqliteConn):    #chiusura connessione
                sqliteConn.close()
                return 'Messaggio inviato'
    # else:
    #     photo = request.files['file']

    #     name, ext = os.path.splitext(photo.filename)
    #     if ext in ('.png','.jpg', '.jpeg'):
    #         path = 'images_directory/'

    #         if os.path.exists(path):
    #             img_path = f'{save_path}/{photo.filename}'
    #             photo.save(img_path)
                
    #             try:
    #                 sqliteConn = sqlite3.connect(path_db)
    #                 cursor = sqliteConn.cursor()

    #                 sender_id = request.args.get('sender_id')
    #                 receiver_id = request.args.get('receiver_id')
    #                 img_name = str(request.args.get('text')).replace('+', ' ')
                    
    #                 cursor.execute(f'''INSERT INTO immagini(id_mitt, id_dest, path) VALUES ({sender_id}, {receiver_id}, {img_name})''')

    #                 sqliteConn.commit()

    #             except sqlite3.Error as error:
    #                 print('Error: ' + error)
                
    #             finally:
    #                 if (sqliteConn):
    #                     sqliteConn.close()
    #                     return 'Foto inviata'
    #         else:
    #             os.mkdir(path)
    #     else:
    #         return 'Formato non valido'

if __name__== "__main__":   #chiamata al main "riciclabile" 
    app.run(host="192.168.1.140", port=int(8080), debug=True)