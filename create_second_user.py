from app import app
from extensions import db
from models import User, Account


with app.app_context():

    existing_user = User.query.filter_by(
        email="rahul@gmail.com"
    ).first()

    if existing_user:
        print("Rahul already exists.")
    else:

        user = User(
            name="Rahul Sharma",
            email="rahul@gmail.com",
            phone="9876543211"
        )

        db.session.add(user)
        db.session.commit()

        account = Account(
            account_number="1000005678",
            balance=10000,
            status="active",
            user_id=user.id
        )

        db.session.add(account)
        db.session.commit()

        print("Second test user created!")
        print("Name:", user.name)
        print("Account:", account.account_number)
        print("Balance:", account.balance)
