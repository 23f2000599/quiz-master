from flask import Flask
from database import db
from database import *
from apis import configure_routes
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_app.db'
app.secret_key='MAD1project'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

configure_routes(app)

with app.app_context():
    db.create_all()
    print("Database and tables created")

if __name__== "__main__":
    app.run(debug=True)


