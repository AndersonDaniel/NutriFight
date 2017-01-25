from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def hello():
    return "Hello, Nutrition Fighter!"

if __name__ == "__main__":
    app.run()