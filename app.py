from flask import Flask, request, render_template, jsonify, redirect, url_for
from hate_detect import *
from hate_audio_video import *
import sqlite3 as sql
import hashlib
from pickle import load, dump
import os
import warnings

app = Flask(__name__)

hash = (lambda pswd: hashlib.sha256(pswd.encode('utf-8')).hexdigest())
check = False
user = ""

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/home")
def home():
    if check:
        return render_template("home.html", username=user)
    else:
        return render_template("index.html", load=True)

@app.route('/login', methods=["POST"])
def login(): 
    global check
    global user
    uname = request.form["uname"]
    pswd = request.form["pswd"]
    user = uname
    try:
        conn = sql.connect("data/user_info.db")
        res = conn.execute(f"SELECT PSWD, FNAME FROM USERS WHERE UNAME='{uname}'").fetchone()
        conn.close()
        if hash(pswd) == res[0]:
            check = True
            return jsonify({'success': True, 'redirect': url_for('home')})
        else:
            return "Invalid password!"
    except Exception as ex:
        return f"{ex}"


@app.route('/logout')
def logout():
    global check
    check = False
    return jsonify({'redirect': url_for('home')})

@app.route('/settings', methods=['POST'])
def settings():
    lp_filter = request.form['lp_filter']
    hp_filter = request.form['hp_filter']
    # rem_silence = request.form['rem_silence']
    lp_freq = request.form['lp_freq']
    hp_freq = request.form['hp_freq']
    energy_thresh = request.form['energy_thresh']
    speech_api = request.form['speech_api']
    try:
        data = {
            "lp_filter": lp_filter,
            "hp_filter": hp_filter,
            # "rem_silence": rem_silence,
            "lp_freq": lp_freq,
            "hp_freq": hp_freq,
            "energy_thresh": energy_thresh,
            "speech_api": speech_api
        }
        with open(r"data/settings.pkl", "wb") as file:
            dump(data, file)
        return "Settings saved successfully!"
    except Exception as ex:
        return f"Settings not saved, error: {ex}"
    

@app.route('/load_default')
def load_default():
    with open(r"data/settings.pkl", "rb") as file:
        config = load(file)
    
    #{'lp_filter': 'true', 'hp_filter': 'true', 'lp_freq': '2100', 'hp_freq': '2600', 'energy_thresh': '-40', 'speech_api': '2'}

    return jsonify({
        'lp_filter': config['lp_filter'],
        'hp_filter': config['hp_filter'],
        'lp_freq': config['lp_freq'],
        'hp_freq': config['hp_freq'],   
        'energy_thresh': config['energy_thresh'],   
        'speech_api': config['speech_api'],   
    })
    

@app.route('/change_password', methods=['POST'])
def change_password():
    cpswd = request.form["cpswd"]
    npswd = request.form["npswd"]
    try:
        conn = sql.connect("data/user_info.db")
        res = conn.execute(f"SELECT PSWD FROM USERS WHERE UNAME='{user}'").fetchone()
        if res == hash(cpswd):
            cursor = conn.cursor()
            cursor.execute(f"UPDATE USERS SET PSWD='{hash(npswd)}' where UNAME='{user}'")
            conn.commit()
            return "Paswword changed successfull"
        else:
            return "Incorrect current password"
    except Exception as ex:
        return f"Password updation failed, error: {ex}"
    

@app.route('/register', methods=["POST"])
def register():
    fname = request.form["fname"]
    uname = request.form["uname"]
    pswd = request.form["pswd"]
    try:
        conn = sql.connect("data/user_info.db")
        cursor = conn.cursor()
        ch = cursor.execute(f"INSERT INTO USERS VALUES ('{fname}','{hash(pswd)}','{uname}')").fetchone()
        conn.commit()
        conn.close()
        print(ch)
        return "User registration successfull"
    except Exception as ex:
        print(f"{ex}")
        return f"User registration failed, {ex}"


@app.route("/analyze_text", methods=["POST"])
def analyze_text():
    text = request.form["text"]  
    data = predict(text)
    return jsonify({
        'class': str(data[0]),
        'label': data[1],
        'HS': str(data[2][0]*100),
        'AB': str(data[2][1]*100),
        'NE': str(data[2][2]*100),
        'prob': str(data[3])
    })


@app.route("/analyze_audio", methods=["POST"])
def analyze_audio():
    audio = request.files['audio']
    audio.save(r"Processed_file/audio.wav")
    with open(r"data/settings.pkl", "rb") as file:
        config = load(file)
    
    #{'lp_filter': 'true', 'hp_filter': 'true', 'lp_freq': '2100', 'hp_freq': '2600', 'energy_thresh': '-40', 'speech_api': '2'}
    filter = None
    if config['lp_filter'] == 'true' and config['hp_filter'] == 'true':
        filter = "BOTH"
    elif config['lp_filter'] == 'true':
        filter = "LOW"
    elif config['hp_filter'] == 'true':
        filter = "HIGH"
    
    text = pySTT(r"Processed_file/audio.wav", filter, int(config['lp_freq']), int(config['hp_freq']), int(config['energy_thresh']), 1, 0, int(config['speech_api']))


    data = predict(text)
    return jsonify({
        'class': str(data[0]),
        'label': data[1],
        'HS': str(data[2][0]*100),
        'AB': str(data[2][1]*100),
        'NE': str(data[2][2]*100),
        'prob': str(data[3])
    })


@app.route("/analyze_video", methods=["POST"])
def analyze_video():
    video = request.files['video']
    video.save(f"Processed_file/{video.filename}")

    video_to_audio(f"Processed_file/{video.filename}")

    with open(r"data/settings.pkl", "rb") as file:
        config = load(file)
    
    #{'lp_filter': 'true', 'hp_filter': 'true', 'lp_freq': '2100', 'hp_freq': '2600', 'energy_thresh': '-40', 'speech_api': '2'}
    filter = None
    if config['lp_filter'] == 'true' and config['hp_filter'] == 'true':
        filter = "BOTH"
    elif config['lp_filter'] == 'true':
        filter = "LOW"
    elif config['hp_filter'] == 'true':
        filter = "HIGH"
    
    text = pySTT(f"Processed_file/{video.filename}", filter, int(config['lp_freq']), int(config['hp_freq']), int(config['energy_thresh']), 1, 0, int(config['speech_api']))

    data = predict(text)

    os.remove(f"Processed_file/{video.filename}")

    return jsonify({
        'class': str(data[0]),
        'label': data[1],
        'HS': str(data[2][0]*100),
        'AB': str(data[2][1]*100),
        'NE': str(data[2][2]*100),
        'prob': str(data[3])
    })


if __name__ == '__main__':
    app.run(debug=True)