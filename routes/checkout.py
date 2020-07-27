from flask import *
from app import app

@app.route('/first')
def first():
    return "okk"
if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 5000)