from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from extensions import db
from models import User, Card, Account, Transaction
from decimal import Decimal, InvalidOperation
import random




app = Flask(__name__)



app.config["SECRET_KEY"] = "dev-secret-key-change-later"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///atm.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)




login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def home():
    return render_template("index.html")

def generate_account_number():

    while True:

        account_number = str(
            random.randint(1000000000, 9999999999)
        )

        existing = Account.query.filter_by(
            account_number=account_number
        ).first()

        if not existing:
            return account_number

def generate_card_number():

    while True:

        card_number = "5555" + "".join(
            str(random.randint(0, 9))
            for _ in range(12)
        )

        existing = Card.query.filter_by(
            card_number=card_number
        ).first()

        if not existing:
            return card_number

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        if len(name)<2:
            flash("Please enter a valid name.","error")
            return redirect(url_for("signup"))
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        if not phone.isdigit() or len(phone) != 10:
            flash("Phone number must contain exactly 10 digits.","error")
            return redirect(url_for("signup"))

        pin = request.form.get("pin", "")
        confirm_pin = request.form.get("confirm_pin", "")

        # Check required fields

        if not name or not email or not phone or not pin:
            flash(
                "Please fill in all fields.",
                "error"
            )

            return redirect(url_for("signup"))

        # Check email

        existing_email = User.query.filter_by(
            email=email
        ).first()

        if existing_email:

            flash(
                "An account with this email already exists.",
                "error"
            )

            return redirect(url_for("signup"))

        # Check phone

        existing_phone = User.query.filter_by(
            phone=phone
        ).first()

        if existing_phone:

            flash(
                "An account with this phone number already exists.",
                "error"
            )

            return redirect(url_for("signup"))

        # Validate PIN

        if not pin.isdigit() or len(pin) != 4:

            flash(
                "PIN must contain exactly 4 digits.",
                "error"
            )

            return redirect(url_for("signup"))

        # Confirm PIN

        if pin != confirm_pin:

            flash(
                "PINs do not match.",
                "error"
            )

            return redirect(url_for("signup"))

        # Create user

        user = User(
            name=name,
            email=email,
            phone=phone
        )

        db.session.add(user)

        db.session.flush()

        # Create account

        account = Account(
            account_number=generate_account_number(),
            balance=Decimal("0.00"),
            status="active",
            user_id=user.id
        )

        db.session.add(account)

        db.session.flush()

        # Create card

        card = Card(
            card_number=generate_card_number(),
            pin_hash=generate_password_hash(pin),
            account_id=account.id
        )

        db.session.add(card)

        db.session.commit()

        return render_template(
            "account_created.html",
            user=user,
            account=account,
            card=card
        )

    return render_template("signup.html")





@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        card_number = request.form.get("card_number")
        pin = request.form.get("pin")

        card = Card.query.filter_by(
            card_number=card_number
        ).first()

        if card is None:
            flash("Invalid card number or PIN.", "error")
            return redirect(url_for("login"))

        if card.status != "active":
            flash("This card is blocked.", "error")
            return redirect(url_for("login"))

        if check_password_hash(card.pin_hash, pin):

            card.failed_attempts = 0

            db.session.commit()

            login_user(card.account.user)

            return redirect(url_for("dashboard"))

        else:

            card.failed_attempts += 1

            if card.failed_attempts >= 3:
                card.status = "blocked"

            db.session.commit()

            if card.status == "blocked":
                flash("Too many failed attempts. Card blocked.", "error")
            else:
                flash("Invalid card number or PIN.", "error")

            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/dashboard")
@login_required
def dashboard():
    account = current_user.accounts[0]
    return render_template(
        "dashboard.html",
        user=current_user
    )

@app.route("/balance")
@login_required
def balance():
    account = current_user.accounts[0]

    return render_template(
        "balance.html",
        account=account
    )

@app.route("/withdraw", methods=["GET", "POST"])
@login_required
def withdraw():

    account = current_user.accounts[0]

    if request.method == "POST":

        amount = request.form.get("amount")

        try:
            amount = Decimal(amount)
        except (TypeError, ValueError, InvalidOperation):
            flash("Please enter a valid amount.", "error")
            return redirect(url_for("withdraw"))

        if amount <= Decimal("0"):
            flash("Amount must be greater than zero.", "error")
            return redirect(url_for("withdraw"))

        if amount > account.balance:
            flash("Insufficient balance.", "error")
            return redirect(url_for("withdraw"))

        account.balance -= amount

        transaction = Transaction(
            type="WITHDRAWAL",
            amount=amount,
            description="ATM cash withdrawal",
            account_id=account.id
        )

        db.session.add(transaction)
        db.session.commit()

        flash(
            f"₹{amount:.2f} withdrawn successfully.",
            "success"
        )

        return redirect(url_for("balance"))

    return render_template(
        "withdraw.html",
        account=account
    )

@app.route("/deposit", methods=["GET", "POST"])
@login_required
def deposit():

    account = current_user.accounts[0]

    if request.method == "POST":

        amount = request.form.get("amount")

        try:
            amount = Decimal(amount)
        except (TypeError, ValueError, InvalidOperation):
            flash("Please enter a valid amount.", "error")
            return redirect(url_for("deposit"))

        if amount <= Decimal("0"):
            flash("Amount must be greater than zero.", "error")
            return redirect(url_for("deposit"))

        account.balance += amount

        transaction = Transaction(
            type="DEPOSIT",
            amount=amount,
            description="ATM cash deposit",
            account_id=account.id
        )

        db.session.add(transaction)
        db.session.commit()

        flash(
            f"₹{amount:.2f} deposited successfully.",
            "success"
        )

        return redirect(url_for("balance"))

    return render_template(
        "deposit.html",
        account=account
    )

@app.route("/transactions")
@login_required
def transactions():

    account = current_user.accounts[0]

    transaction_list = (
        Transaction.query
        .filter_by(account_id=account.id)
        .order_by(Transaction.created_at.desc())
        .all()
    )

    return render_template(
        "transactions.html",
        account=account,
        transactions=transaction_list
    )

@app.route("/transfer", methods=["GET", "POST"])
@login_required
def transfer():

    sender = current_user.accounts[0]

    if request.method == "POST":

        recipient_account_number = request.form.get(
            "recipient_account"
        )

        amount_input = request.form.get("amount")

        # Convert amount to Decimal
        try:
            amount = Decimal(amount_input)
        except (TypeError, ValueError, InvalidOperation):

            flash(
                "Please enter a valid amount.",
                "error"
            )

            return redirect(url_for("transfer"))

        # Check amount
        if amount <= Decimal("0"):

            flash(
                "Amount must be greater than zero.",
                "error"
            )

            return redirect(url_for("transfer"))

        # Find recipient
        recipient = Account.query.filter_by(
            account_number=recipient_account_number
        ).first()

        if recipient is None:

            flash(
                "Recipient account not found.",
                "error"
            )

            return redirect(url_for("transfer"))

        # Prevent transferring to yourself
        if recipient.id == sender.id:

            flash(
                "You cannot transfer money to yourself.",
                "error"
            )

            return redirect(url_for("transfer"))

        # Check balance
        if amount > sender.balance:

            flash(
                "Insufficient balance.",
                "error"
            )

            return redirect(url_for("transfer"))

        # Transfer money
        sender.balance -= amount
        recipient.balance += amount

        # Sender transaction
        sender_transaction = Transaction(
            type="TRANSFER",
            amount=amount,
            description=f"Transfer to {recipient.account_number}",
            account_id=sender.id
        )

        # Recipient transaction
        recipient_transaction = Transaction(
            type="TRANSFER",
            amount=amount,
            description=f"Transfer from {sender.account_number}",
            account_id=recipient.id
        )

        db.session.add(sender_transaction)
        db.session.add(recipient_transaction)

        db.session.commit()

        flash(
            f"₹{amount:.2f} transferred successfully.",
            "success"
        )

        return redirect(url_for("transactions"))

    return render_template(
        "transfer.html",
        account=sender
    )

@app.route("/change-pin", methods=["GET", "POST"])
@login_required
def change_pin():

    account = current_user.accounts[0]
    card = account.card

    if request.method == "POST":

        current_pin = request.form.get("current_pin")
        new_pin = request.form.get("new_pin")
        confirm_pin = request.form.get("confirm_pin")

        # Check current PIN
        if not check_password_hash(card.pin_hash, current_pin):

            flash(
                "Current PIN is incorrect.",
                "error"
            )

            return redirect(url_for("change_pin"))

        # Check new PIN
        if not new_pin.isdigit() or len(new_pin) != 4:

            flash(
                "New PIN must contain exactly 4 digits.",
                "error"
            )

            return redirect(url_for("change_pin"))

        # Confirm PIN
        if new_pin != confirm_pin:

            flash(
                "New PINs do not match.",
                "error"
            )

            return redirect(url_for("change_pin"))

        # Don't allow same PIN
        if check_password_hash(card.pin_hash, new_pin):

            flash(
                "New PIN must be different from your current PIN.",
                "error"
            )

            return redirect(url_for("change_pin"))

        # Save new PIN
        card.pin_hash = generate_password_hash(new_pin)

        db.session.commit()

        flash(
            "PIN changed successfully.",
            "success"
        )

        return redirect(url_for("dashboard"))

    return render_template("change_pin.html")

@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(url_for("login"))
if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)
