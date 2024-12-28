# app.py
from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
db = SQLAlchemy(app)

@app.route("/")
def hello():
    return "Hello World!"

if __name__ == '__main__':
    # Run the app
    app.run(debug=True)