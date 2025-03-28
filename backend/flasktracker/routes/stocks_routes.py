from typing import cast
from flask import Blueprint, jsonify
from flask_login import current_user, login_required

from flasktracker.models import User, Stock
from flasktracker import db

stocks = Blueprint("stocks", __name__, url_prefix="/api/stocks")
authenticated_user: User = cast(User, current_user)


# enter stock id to retrieve its associated transactions
@stocks.route("/<int:id>", methods=["GET"])
@login_required
def get_stock_transactions(id: int):
    try:
        stock: Stock = db.session.get(Stock, id)
        if not stock:
            return jsonify({"error": "Stock with given id not found"}), 404
        if stock.portfolio.owner_id != authenticated_user.id:
            return jsonify({"error": "Invalid request"}), 403

        # take all transactions from retrieved stock as a list
        transactions_json = [t.to_json() for t in stock.transactions]

        return jsonify(transactions_json), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# enter stock id to delete
@stocks.route("/delete/<int:id>", methods=["DELETE"])
@login_required
def delete_stock(id: int):
    try:
        stock: Stock = db.session.get(Stock, id)
        if not stock:
            return jsonify({"error": "Stock with given id not found"}), 404
        if stock.portfolio.owner_id != authenticated_user.id:
            return jsonify({"error": "Invalid request"}), 403

        # send portfolio id for frontend react-query
        portfolio_id = stock.portfolio_id

        db.session.delete(stock)
        db.session.commit()
        return jsonify({"deletedId": id, "portfolioId": portfolio_id}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
