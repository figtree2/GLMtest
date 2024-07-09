from flask import Flask, render_template, request, Response, stream_with_context
from run_app import *
import io
import sys

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/run_backend', methods = ["POST"])
def run_backend():
    input = request.form.get('user_input')
    if input is None:
        return "请在输入一次", 400
    return Response(stream_with_context(run_app_back(input)), mimetype = 'text/plain')

def run_app_back(input_text):
    buffer = io.StringIO()
    sys.stdout = buffer

    resp = run_app(input_text, {}, "234")

    try:
        #print(resp)
        #yield buffer.getvalue()
        #buffer.truncate(0)
        #buffer.seek(0)
        for chunk in resp:
            print(f"{chunk}", end = "", flush = True)
            yield buffer.getvalue()
            buffer.truncate(0)
            buffer.seek(0)
        #for chunk in resp:
        #    if answer_chunk := chunk.get("answer"):
        #        print(f"{answer_chunk}", end = "", flush = True)
        #        yield buffer.getvalue()
        #        buffer.truncate(0)
        #        buffer.seek(0)
    finally:
        sys.stdout = sys.__stdout__

if __name__ == '__main__':
    app.run(debug = True)