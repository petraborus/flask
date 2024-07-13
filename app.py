from flask import Flask, render_template, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_scss import Scss
from flask_admin import Admin
from datetime import datetime

app = Flask(__name__)

# following https://www.youtube.com/watch?v=45P3xQPaYxc&list=PL8RYI7SclA-ukUZQLkyQQaIsKxmKRdRuR&index=5 for SQLAlchemy
# configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# creating a database model
# a model is like each row in the database --> e.g. each task is a model


# data class - row of data
class MyTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # each item has a unique id allowing it to be updated and removed
    content = db.Column(db.String(100), nullable=False)  # content assigned a String data type with max 100 characters
    completed = db.Column(db.Integer, default=0)  # 0 means not completed, 1 means completed
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    # method to return data back from the model
    def __repr__(self) -> str:
        return f"Task {self.id}"


# routes to webpages

@app.route("/", methods=["POST", "GET"])   # POST = send data, GET = receive data
@app.route("/home")
def home():
    # add a task
    if request.method == "POST":
        current_task = request.form["content"]  # information captured from an html
        new_task = MyTask(content=current_task)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect("/")
        except Exception as e:
            print(f"ERROR:{e}")  # caching
            return f"ERROR:{e}"

    # see all current tasks
    else:
        tasks = MyTask.query.order_by(MyTask.date_created).all()
        return render_template('home.html', tasks=tasks)


# delete an item from to do list
@app.route("/delete/<int:id>")
def delete(id:int):
    delete_task = MyTask.query.get_or_404(id)
    try:
        db.session.delete(delete_task)
        db.session.commit()
        return redirect("/")
    except Exception as e:
        return f"ERROR:{e}"


# edit an item in to do list
@app.route("/edit/<int:id>", methods=["GET", "POST"])   # route needs to match in html file (in home.html)
def edit(id:int):
    # creating a task
    task = MyTask.query.get_or_404(id)
    if request.method == "POST":
        task.content = request.form['content']
        try:
            db.session.commit()
            return redirect("/")
        except Exception as e:
            return f"ERROR:{e}"
    else:
        return render_template('edit.html', task=task)



@app.route("/about")
def about():
    return render_template('about.html', title="About")


@app.route('/stats')
def stats():
    return render_template('page.html')


# runner and debugger
if __name__ in "__main__":
    with app.app_context():
        db.create_all()

    app.run(port=8000, debug=True)


