from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
import string
import random
from flask import redirect
from flask import url_for
from flask import request
from flask_wtf.csrf import CSRFProtect
import os
from flask import session




app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///urls.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

csrf = CSRFProtect(app)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY


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
        rand_letters = random.choices(letters, k=5)
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
            session.clear()
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

@app.route('/all')
def show_all():
    return render_template('all_urls.html', all_url_in_database=Database.query.all())
if __name__ == '__main__':
    app.run()
