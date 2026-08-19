from app import app
from models import User, Account, Card


with app.app_context():

    users = User.query.all()

    for user in users:

        print("\nUSER")
        print("ID:", user.id)
        print("Name:", user.name)
        print("Email:", user.email)

        for account in user.accounts:

            print("\nACCOUNT")
            print("Account Number:", account.account_number)
            print("Balance:", account.balance)
            print("Status:", account.status)

            if account.card:

                print("\nCARD")
                print("Card Number:", account.card.card_number)
                print("Status:", account.card.status)
                print("Failed Attempts:", account.card.failed_attempts)
                print("PIN Hash:", account.card.pin_hash)

            print("-------------------------")
