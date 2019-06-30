from flask import Flask 

app = Flask(__name__)


@app.route('/')
def index():
    return '<h1>Hello zhaocanxiang</h1>'

@app.route('/user/<name>')
def suer(name):
    return '<h1>Hello, %s!</h1>' % name

if __name__ == "__main__":
    app.run(debug=True)