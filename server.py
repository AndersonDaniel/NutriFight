from flask import Flask, jsonify, send_file
import requests
import os
import StringIO

app = Flask(__name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def hello():
    return "Hello, Nutrition Fighter!"

@app.route('/banana')
def banana():
    response = requests.get('https://d3anr8px62ub97.cloudfront.net/ntr_7_19400')
    return send_file(StringIO.StringIO(response.content), mimetype='image/jpg')

if __name__ == "__main__":
    app.run()