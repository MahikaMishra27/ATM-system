from app import app
from extensions import db
from models import Account, Card
from werkzeug.security import generate_password_hash


with app.app_context():

    account = Account.query.filter_by(
        account_number="1000001234"
    ).first()

    if account is None:
        print("Account not found.")
    else:

        existing_card = Card.query.filter_by(
            account_id=account.id
        ).first()

        if existing_card:
            print("This account already has a card.")
        else:

            pin = "1234"

            card = Card(
                card_number="5555444433331111",
                pin_hash=generate_password_hash(pin),
                status="active",
                failed_attempts=0,
                account_id=account.id
            )

            db.session.add(card)
            db.session.commit()

            print("ATM card created successfully!")
            print("Card Number:", card.card_number)
            print("PIN: 1234")
