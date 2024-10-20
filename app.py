from flask import Flask, render_template, url_for, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from datetime import datetime
import numpy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from wtforms.fields import DateField, IntegerField, TextAreaField


app = Flask(__name__)

# following https://www.youtube.com/watch?v=45P3xQPaYxc&list=PL8RYI7SclA-ukUZQLkyQQaIsKxmKRdRuR&index=5 for SQLAlchemy
# configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/petraborus/PycharmProjects/flask/database.db'
app.config['SECRET_KEY'] = 'secretkey'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# used to reload the user object from the user id stored in the session
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)  # identity column for the user
    username = db.Column(db.String(20), nullable=False, unique=True)  # username with max 20 characters and can't be left empty
    password = db.Column(db.String(80), nullable=False)  # max 80 characters once it has been hashed
    projects = db.relationship('Project', backref='user', lazy=True)


class UserForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired()])
    username = StringField("Username", validators=[InputRequired()])
    about_author = TextAreaField("About Author")
    profile_pic = FileField("Profile Picture")
    submit = SubmitField("Update")


class RegisterForm(FlaskForm):
    # has to be filled out, minimum and maximum characters set, password has a password field so it shows black dots instead of writing
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Register")

    def validate_username(self, username):
        # queries the database table to check if the same username exists
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError("That username already exists. Please choose a different one.")


class LoginForm(FlaskForm):
    # has to be filled out, minimum and maximum characters set, password has a password field so it shows black dots instead of writing
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")


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


# creating a multidimensional array to store information for different projects?

# a class to set basic attributes to each chapter object created, which will then be added to a tree
class Chapter:
    chapter_count = 0

    def __init__(self, word_goal):
        self.sections = []
        self.word_goal = word_goal
        # self.title = "Chapter " + str(chapter_count)


class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    goal_name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, default=datetime.utcnow)
    target = db.Column(db.Integer, default=0)
    progress = db.Column(db.Integer, default=0)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)


class Project(db.Model):
    # used chatgpt to figure out how to create a new page for each project, suggesting adding ot database for unique id
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    goals = db.relationship('Goal', backref='project', lazy=True)
    word_count_stack = []
    total_wc = 0
    for i in word_count_stack:
        total_wc += i

    def __repr__(self) -> str:
        return f"Project {self.project_name}"


# from chatgpt - form for creating a new project
class ProjectForm(FlaskForm):
    project_name = StringField(validators=[InputRequired(), Length(min=2, max=100)], render_kw={"placeholder": "Project Name"})
    submit = SubmitField("Create Project")


# create a goal
class GoalForm(FlaskForm):
    goal_name = StringField(validators=[InputRequired(), Length(min=2, max=100)], render_kw={"placeholder": "Goal Name"})
    start_date = DateField(format='%Y-%m-%d', render_kw={"placeholder": 'Start Date (DD-MM-YYYY)'})
    end_date = DateField(format='%Y-%m-%d', render_kw={"placeholder": 'End Date (DD-MM-YYYY)'})
    target = IntegerField(validators=[InputRequired()], render_kw={"placeholder": "Goal Target"})
    submit = SubmitField("Add Goal")


# form for adding words
class WordsForm(FlaskForm):
    added_words = StringField(validators=[InputRequired(), Length(min=2, max=100)], render_kw={"placeholder": "Words Written"})
    submit = SubmitField("+ Add wordcount")


@app.route('/plot/<int:project_id>', methods=['GET', 'POST'])
@login_required
def plot(project_id):
    return render_template('plot.html', project_id=project_id)


@app.route('/worldbuilding/<int:project_id>', methods=['GET', 'POST'])
@login_required
def worldbuilding(project_id):
    return render_template('worldbuilding.html', project_id=project_id)


@app.route('/characters/<int:project_id>', methods=['GET', 'POST'])
@login_required
def characters(project_id):
    return render_template('characters.html', project_id=project_id)


# routes to webpages
@app.route('/create_project', methods=['GET', 'POST'])
@login_required
def create_project():
    form = ProjectForm()
    if form.validate_on_submit():
        new_project = Project(project_name=form.project_name.data, user_id=current_user.id)
        db.session.add(new_project)
        db.session.commit()
        return redirect(url_for('project_page', id=new_project.id))
    return render_template('create_project.html', form=form)


@app.route('/add_goal/<int:project_id>', methods=['GET', 'POST'])
@login_required
def add_goal(project_id):
    form = GoalForm()
    if form.validate_on_submit():
        new_goal = Goal(goal_name=form.goal_name.data, start_date=form.start_date.data, end_date=form.end_date.data, target=form.target.data, progress=0, project_id=project_id)
        db.session.add(new_goal)
        db.session.commit()
        return redirect(url_for('project_page', id=project_id))
    return render_template('add_goal.html', form=form, project_id=project_id)


@app.route('/add_words', methods=['GET', 'POST'])
@login_required
def add_words():
    form = WordsForm()
    # project = Project.query.get_or_404(id)
    if form.validate_on_submit():
        # project.word_count_stack.push(form.added_words.data)
        # db.session.add(projects.word)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('add_word.html', form=form)


# login authentication system uses a SQLite database that contains a user table
# when registering, there is a form into which they can type in a username and a password, which will then be stored in the database when pressed submit
# loging in checks whether the username is in the database (meaning it is valid) and then checks the password
@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    # query the user to check if they exist, if so check password hash
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for("home"))
            else:
                flash("Incorrect password")
                print("password incorrect")
        else:
            flash("Incorrect username")
            print("username not found")
    else:
        print("Form validation failed!")  # Debugging statement
        print(form.errors)
    return render_template("login.html", form=form)


@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)  # new user with username set to what is typed in the field
        db.session.add(new_user)  # adds new user to the database
        db.session.commit()
        print("User registered successfully!")  # Debugging statement
        return redirect(url_for("login"))  # redirects user to login page

    if form.errors:
        print("Form validation failed!")
        print(form.errors)  # Prints the exact form errors
    return render_template("register.html", form=form)


@app.route("/dashboard", methods=["POST", "GET"])
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route("/project/<int:id>")
@login_required
def project_page(id):
    # retrieves project from the database based on id
    project = Project.query.get_or_404(id)
    user_goals = Goal.query.filter_by(project_id=id).all()

    if project.user_id != current_user.id:
        flash("No access to this project")
        return redirect(url_for('projects'))
    return render_template("project_page.html", project=project, goals=user_goals)


@app.route("/logout", methods=["POST", "GET"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/welcome")
def welcome():
    return render_template("welcome.html")


# @app.route("/", methods=["POST", "GET"])   # POST = send data, GET = receive data
@app.route("/", methods=["POST", "GET"])
@app.route("/home")
@login_required
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
        user_projects = Project.query.filter_by(user_id=current_user.id).order_by(Project.date_created).all()
        return render_template('home.html', tasks=tasks, projects=user_projects)


# delete an item from to do list
@app.route("/delete/<int:id>")
@login_required
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
@login_required
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
@login_required
def about():
    return render_template('about.html', title="About")


@app.route('/stats')
@login_required
def stats():
    return render_template('stats.html')


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


@app.route('/projects')
@login_required
def projects():
    # all_projects = Project.query.order_by(Project.date_created).all()
    # only show projects created by the user
    user_projects = Project.query.filter_by(user_id=current_user.id).order_by(Project.date_created).all()
    return render_template('projects.html', projects=user_projects)


# runner and debugger
if __name__ in "__main__":
    with app.app_context():
        try:
            print("Creating database tables...")
            db.create_all()  # Ensure all tables are created
            print("Database tables created successfully!")
        except Exception as e:
            print(f"Error creating tables: {e}")
    app.run(port=8000, debug=True)





