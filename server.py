from flask import Flask, render_template, session, redirect, url_for, flash
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
import os

from flask_script import Shell

from datetime import datetime

from wtforms import StringField, SubmitField
from wtforms.validators import Required

from flask_migrate import Migrate, MigrateCommand

from flask_mail import Mail, Message

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)

class NameForm(FlaskForm):
    name = StringField("What's you name?", validators=[Required()])
    submit = SubmitField("submit")

basedir = os.path.abspath(os.path.dirname(__file__))  # 设置数据库用

app = Flask(__name__)

app.config["SECRET_KEY"] = "ceshi123456"

# 配置邮件
app.config["FLASKY_ADMIN"] = os.environ.get("FLASKY_ADMIN")
app.config["MAIL_SERVER"] = "smtp.163.com"
app.config["MAIL_PORT"] = 25
app.config["MAIL_USR_TLS"] = True 
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")

# 配置数据库
app.config["SQLALCHEMY_DATABASE_URI"] = \
    "sqlite:///" + os.path.join(basedir, "data.sqlite")
app.config["SQLALCHEMY_COMMIT_ON_TEARDOWN"] = True
db = SQLAlchemy(app)

manager = Manager(app)
Bootstrap = Bootstrap(app)
moment = Moment(app)
migrate = Migrate(app, db)
manager.add_command("db", MigrateCommand)
mail  = Mail(app)

manager.add_command("shell", Shell(make_context=make_shell_context))

app.config["FLASKY_MAIL_SUBJECT_PREFIX"] = "[Flasky]"
app.config["FLASKY_MAIL_SENDER"] = "18813035114@163.com"

def send_email(to, subject, template, **kwargs):
    print(app.config["MAIL_PASSWORD"])
    msg = Message(app.config["FLASKY_MAIL_SUBJECT_PREFIX"] + subject,\
        sender=app.config["FLASKY_MAIL_SENDER"], recipients=[to])
    msg.body = render_template(template + ".txt", **kwargs)
    msg.html = render_template(template + ".html", **kwargs)
    mail.send(msg)
    print("send mail successfully")

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
            # print("user", user)
            session["known"] = False
            print("config", app.config["FLASKY_ADMIN"])
            if app.config["FLASKY_ADMIN"]:
                send_email(app.config["FLASKY_ADMIN"], "New User", "mail/new_user", user=user)
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