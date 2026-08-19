from app import app
from extensions import db
from models import User


with app.app_context():

    user = User.query.filter_by(
        email="john@example.com"
    ).first()

    if user:
        user.name = "Mahika Mishra"
        user.email = "mahika@gmail.com"

        db.session.commit()

        print("User updated successfully!")
        print("Name:", user.name)
        print("Email:", user.email)

    else:
        print("User not found.")
