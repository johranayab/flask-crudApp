from flask import Flask, render_template, redirect, request, session

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask import flash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"
app.config["SECRET_KEY"] = "blob"
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(233), unique=True, nullable=False)
    password = db.Column(db.String(233), nullable=False)


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    author = db.Column(db.String(255), nullable=False)


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    all_blogs = Blog.query.all()
    return render_template("index.html", all_blogs=all_blogs)


@app.route("/register", methods=["POST", "GET"])
def register():

    if request.method == "POST":
        username = request.form.get("username")
        print(username)
        password = request.form.get("password")
        new_password = generate_password_hash(password=password)
        user = User.query.filter_by(username=username).first()
        if not user:
            new_user = User(username=username, password=new_password)
            db.session.add(new_user)
            db.session.commit()
            return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["user"] = username
            flash('Login Successful!', 'success')
            return redirect("/")
        flash('Wrong Username Or Password', 'danger')
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user")
    flash("logout successfully ", "info")
    return redirect("/")


@app.route("/create-blog", methods=["POST", "GET"])
def create_blog():
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        new_blog = Blog(title=title, description=description, author=session["user"])
        db.session.add(new_blog)
        db.session.commit()
        flash('Post created successfully!', 'success')
        return redirect('/')
    return render_template('create_blog.html')

   


if __name__ == "__main__":
    app.run(debug=True)
