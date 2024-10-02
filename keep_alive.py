from flask import Flask, render_template
from threading import Thread

app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is alive"

def run():
    app.run(host="localhost", port=8080)
    

def keep_alive():  
    t = Thread(target=run)
    t.start()