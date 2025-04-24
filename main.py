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
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        # Create admin user
        admin_user = User(
            username='admin',
            email="admin@gmail.com",
            password="admin123",
            role="admin",
            dob="2000-01-01",  
        )
        
        # Add to database
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created")


if __name__== "__main__":
    app.run(debug=True)


