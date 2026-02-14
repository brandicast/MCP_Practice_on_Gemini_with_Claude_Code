from flask import Flask, request 

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

import gemini.agent as AI

import time
 
app = Flask(__name__) 
 
@app.route('/') 
def home(): 
    return  "Hello"

@app.route('/chat/id/<user>')
def askWithLineID(user):
    ask = request.args.get('ask')

    answer = AI.ask (user, ask) 


    return (str(answer).strip())

@app.route('/chat/history/<user>')
def historyWithLineID(user):
    history = AI.history (user)
    return ('<pre>' + history + '</pre>')




if __name__ == '__main__': 
    AI.loadChatSession()
    app.run(host='0.0.0.0') 
