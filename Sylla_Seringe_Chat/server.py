import flask
from flask import jsonify, request, send_file
from datetime import datetime
from db import open_db, close_db
import os

app = flask.Flask(__name__)
app.config['DEBUG'] = True


@app.route('/api/v1/send', methods=['GET', 'POST'])     #percorso per ricezione
def send():
    if request.method == 'POST':    # Se la richiesta è di tipo post il client sta inviando un'immagine
        photo = request.files['file']       # prendo il nome della foto es: foto.png

        name, ext = os.path.splitext(photo.filename)    # divido nome file ed estensione
        if ext not in ('.png', '.jpg', '.jpeg'):    # verifico che l'estensione sia valida
            return 'Non hai inviato una foto!'

        save_path = 'Server_photo_storage'  # la path dove salvo le foto dei client da inviare

        if not os.path.exists(save_path):   # se il percorso sopracitato non esiste lo creo
            os.makedirs(save_path)

        file_path = f"{save_path}/{photo.filename}"     # creo il percorso finale dove salvero il file

        photo.save(file_path)       # salvo la foto

        conn = open_db()    # apro il database
        cur = conn.cursor()

        query_parameters = request.args     # parametri dell'url

        text = '📷[%s] salvato in Client_photo_storage/received_photo/%s' % (str(file_path).split('/')[-1], str(file_path).split('/')[1])   # sebbene avrei potuto usare il parametro text come una descrizione della
                                                                                                                                            # foto ho deciso di sfruttarlo per infromare l'utente il percorso di salvataggio
        sender_id = query_parameters.get('sender_id')   # determino chi è il mittente
        receiver_id = query_parameters.get('receiver_id') # determino chi è il destinario

        # inserisco nella tabella del Server il messaggio settando is_received = 0 finche non arriverà la prima richiesta all'url recv da parte del client
        cur.execute(
            'INSERT INTO Server_messages(receiver_id, sender_id, text, time, is_received, is_photo, photo_path) VALUES(?,?,?,?,?,?,?)',
            (receiver_id, sender_id, text, datetime.timestamp(datetime.now()), 0, 1, file_path,))

        conn.commit()

        conn.close()

        return f"Il server ha ricevuto correattamente la foto!"

    else:
        # discorso analogo a sopra
        conn = open_db()
        cur = conn.cursor()

        query_parameters = request.args

        text = str(query_parameters.get('text')).replace('+', ' ')
        sender_id = query_parameters.get('sender_id')
        receiver_id = query_parameters.get('receiver_id')

        cur.execute('INSERT INTO Server_messages(receiver_id, sender_id, text, time, is_received, is_photo) VALUES(?,?,?,?,?,?)', (receiver_id, sender_id, text, datetime.timestamp(datetime.now()), 0, 0))
        conn.commit()

        conn.close()


@app.route('/api/v1/download_photo', methods=['GET'])   # api che mi consente di scaricare l'immagine richiesta
def download_photo():
    query_parameters = request.args     #   parametri url( in questo caso abbiamo ?photo_name=)
    photo_name = str(query_parameters.get('photo_name'))    # il nome della foto

    return send_file('Server_photo_storage/%s' % photo_name, as_attachment=True)    # cerco nella cartella Server_photo l'immagine con il nome ricevuto come parametro
                                                                                    # il programma si puo' migliorare salvando le foto mandate dai client con un nuovo nome generato da token per evitare sovracrivamenti


@app.route('/api/v1/receive', methods=['GET'])      # api per la ricezione di nuovi messaggi
def receive():
    def dict_factory(cursor, row):  # funzione(presa online) che consente di accedere ai valori attraverso i nomi dei campi
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    conn = open_db()    # apro il db
    conn.row_factory = dict_factory      # vedere la funzione

    cur = conn.cursor()

    query_parameters = request.args     # parametri ricevuti

    receiver_id = query_parameters.get('receiver_id')   # prendo il receiver_id per prendere solo i messaggi indirizzati al destinatario richiesto

    messages = cur.execute('SELECT * FROM Server_messages WHERE is_received = 0 AND receiver_id = ?', (receiver_id,)).fetchall()    # assegno a message il dizionario finale da inviare al client
                                                                                                                                    # setto la variabile is_received = 1

    cur.execute('UPDATE Server_messages SET is_received = 1 WHERE receiver_id = ?', (receiver_id,))
    conn.commit()

    close_db(conn)

    return jsonify(messages)    # effettuo il json e lo ritorno


@app.route('/api/v1/user_list', methods=['GET'])    # semplice url per stampare i nome e gli id degli utenti
def users_list():
    def dict_factory(cursor, row):  # funzione spiegata in receive()
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    conn = open_db()
    conn.row_factory = dict_factory

    cur = conn.cursor()

    users_list = cur.execute('SELECT * FROM users WHERE 1=1').fetchall()

    close_db(conn)

    return jsonify(users_list)      # ritorno il json


while __name__ == "__main__":
    app.run(host='0.0.0.0')
