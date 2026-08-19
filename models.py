from flask_login import UserMixin
from extensions import db
from datetime import datetime


class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    phone = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    accounts = db.relationship(
        "Account",
        backref="user",
        lazy=True
    )


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    account_number = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    balance = db.Column(
        db.Numeric(12, 2),
        default=0.00,
        nullable=False
    )

    status = db.Column(
        db.String(20),
        default="active",
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    card = db.relationship(
        "Card",
        backref="account",
        uselist=False
    )

    transactions = db.relationship(
        "Transaction",
        backref="account",
        lazy=True
    )


class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    card_number = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    pin_hash = db.Column(
        db.String(255),
        nullable=False
    )

    status = db.Column(
        db.String(20),
        default="active",
        nullable=False
    )

    failed_attempts = db.Column(
        db.Integer,
        default=0,
        nullable=False
    )

    account_id = db.Column(
        db.Integer,
        db.ForeignKey("account.id"),
        nullable=False,
        unique=True
    )


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    type = db.Column(
        db.String(30),
        nullable=False
    )

    amount = db.Column(
        db.Numeric(12, 2),
        nullable=False
    )

    description = db.Column(
        db.String(255)
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    account_id = db.Column(
        db.Integer,
        db.ForeignKey("account.id"),
        nullable=False
    )

