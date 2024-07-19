from flask import Flask, render_template, request, Response, stream_with_context, jsonify
from run_app import *
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import io
import sys

app = Flask(__name__)

CORS(app)
socketio = SocketIO(app, cors_allowed_origins = '*')


@app.route('/api/chatbot', methods = ["POST"])
def run_bot():
    input = request.json.get('input')
    store = request.json.get('store')
    if store:
        for key, value in store.items():
            store[key] = json.loads(value)
        store = convertJsonToHist(store)
    id = request.json.get('id')
    if input is None:
        return "请在输入一次", 400
    socketio.start_background_task(target = run_app_back, input_text = input, store = store, id = id)
    return {'status': 'started'}

def run_app_back(input_text, store, id):
    with app.app_context():
        resp, store2 = run_app(input_text, store, id)
        socketio.emit('message', {'data': '\n'})
        for chunk in resp:
            if answer_chunk := chunk.get("answer"):
                socketio.emit('message', {'data': f'{answer_chunk}'})
        if store2:
            store2 = convertHistToJson(store2)
        socketio.emit('message', {'data': '\n'})
        socketio.emit('history', {'history': store2})

@socketio.on('getVecs')
def get_dbs():
    try: 
        emit('vectors', get_vecs())
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('connect')
def handle_connect():
    print("connected")

@socketio.on('disconenct')
def handle_disconnect():
    print('disconnected')

if __name__ == '__main__':
    socketio.run(app, debug = True)