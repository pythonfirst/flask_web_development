from flask import Flask, render_template, session, redirect, url_for, flash
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
import os

from datetime import datetime

from wtforms import StringField, SubmitField
from wtforms.validators import Required

class NameForm(FlaskForm):
    name = StringField("What's you name?", validators=[Required()])
    submit = SubmitField("submit")

basedir = os.path.abspath(os.path.dirname(__file__))  # 设置数据库用

app = Flask(__name__)

app.config["SECRET_KEY"] = "ceshi123456"

# 配置数据库
app.config["SQLALCHEMY_DATABASE_URI"] = \
    "sqlite:///" + os.path.join(basedir, "data.sqlite")
app.config["SQLALCHEMY_COMMIT_ON_TEARDOWN"] = True
db = SQLAlchemy(app)

manager = Manager(app)
Bootstrap = Bootstrap(app)
moment = Moment(app)


@app.route('/', methods=["GET", "POST"])
def index():
    name = None
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        print("user query", user)
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            print("user", user)
            session["known"] = False
        else:
            session["known"] = True
        
        session["name"] = form.name.data 
        form.name.data = ""
        return redirect(url_for("index"))
    return render_template("index.html", current_time=datetime.utcnow(), form=form, \
        name=session.get("name"), known=session.get("known", False))

@app.route('/user/<name>')
def suer(name):
    return render_template("user.html", name=name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


# 定义数据库模型
class Role(db.Model):
    """角色模型"""
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String(64), unique=True)

    users = db.relationship("User", backref="role")
 
    def __repr__(self):
        return "<Role %r>" % self.name

class User(db.Model):
    """用户模型"""
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True) 
    username = db.Column(db.String(64), unique=True, index=True)
 
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))
    def __repr__(self):
        return "User %r>" % self.username
    

if __name__ == "__main__":
    # app.run(debug=True)
    manager.run()