from app import app
from extensions import db
from models import User, Account


with app.app_context():

    user = User(
        name="Mahika Mishra",
        email="mahika@example.com",
        phone="9876543210"
    )

    db.session.add(user)
    db.session.commit()

    account = Account(
        account_number="1000001234",
        balance=25000.00,
        status="active",
        user_id=user.id
    )

    db.session.add(account)
    db.session.commit()

    print("Test customer created!")
    print("Name:", user.name)
    print("Account Number:", account.account_number)
    print("Balance:", account.balance)
