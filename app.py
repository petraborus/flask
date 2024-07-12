from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_scss import Scss
from flask_admin import Admin
from datetime import datetime



app = Flask(__name__)

# configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# creating a database model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id


# home page
@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/about")
def about():
    return render_template('about.html', title="About")

@app.route('/stats')
def stats():
    return render_template('page.html')

if __name__ == "__main__":
    app.run(debug=True)


