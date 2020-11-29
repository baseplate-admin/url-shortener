from flask import Flask
from flask import render_template
from flask import request
from flask_sqlalchemy import SQLAlchemy
import string
import random
from flask import redirect
from flask import url_for

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///urls.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Database(db.Model):
    id_ = db.Column("id_", db.Integer, primary_key=True)
    long = db.Column('long', db.String())
    short = db.Column('short', db.String(5))

    def __init__(self, long, short):
        self.long = long
        self.short = short
# @app.route('/')
# def hello_world():
#     return 'Hello World!'


def shorten_url():
    letters = string.ascii_lowercase + string.ascii_uppercase
    while True:
        rand_letters = random.choices(letters, k=10)
        rand_letters = "".join(rand_letters)
        short_url = Database.query.filter_by(short=rand_letters).first()
        if not short_url:
            return rand_letters


@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/', methods=["POST","GET"])
def home():
    if request.method =="POST":
        url_received = request.form["url_request"]
        found_url = Database.query.filter_by(long=url_received).first()
        if found_url:
            return redirect(url_for("display_url", url=found_url.short))
        else:
            short_url = shorten_url()
            new_url = Database(url_received, short_url)
            db.session.add(new_url)
            db.session.commit()
            return redirect(url_for('display_url',url=short_url))
    else:
        return render_template("home.html")
@app.route('/display/<url>')
def display_url(url):
    return render_template('shorturl.html', short_url_display=url)
@app.route('/<short_url>')
def short(short_url):
    long_url = Database.query.filter_by(short=short_url).first()
    if long_url:
        return redirect(long_url.long)
    else:
        return "<h1>Url Doesnot Exist</h1>"
if __name__ == '__main__':
    app.run(port=5000, debug=True)
