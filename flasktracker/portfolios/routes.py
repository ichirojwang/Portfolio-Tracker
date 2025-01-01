from flask import url_for, render_template, redirect, flash, request, abort, Blueprint
from flask_login import login_required, current_user

from flasktracker import db
from flasktracker.portfolios.forms import CreatePortfolioForm, PortfolioTransactionForm
from flasktracker.portfolios.models import Portfolio, Stock, StockTransaction, StockTransactionType, StockWrapper
from flasktracker.portfolios.utils import validate_port

portfolios = Blueprint('portfolios', __name__)


@portfolios.route('/portfolio/all', methods=["GET", "POST"])
@login_required
def portfolio_all():
    form = CreatePortfolioForm()
    if form.validate_on_submit():
        new_port: Portfolio = Portfolio(form.name.data, current_user.id)
        db.session.add(new_port)
        db.session.commit()
        flash(f"New portfolio '{form.name.data}' created!", "success")
    return render_template("portfolios.html", form=form)


@portfolios.route('/portfolio/<int:port_id>')
@login_required
def portfolio(port_id: int):
    port: Portfolio = db.session.get(Portfolio, port_id)
    if not port:
        abort(404)
    if port.owner != current_user:
        abort(403)
    port_name_form = CreatePortfolioForm()
    port_name_form.submit.label.text = "Confirm Changes"
    transaction_form = PortfolioTransactionForm()
    edit_form = PortfolioTransactionForm()

    return render_template("portfolio.html", port_name_form=port_name_form, transaction_form=transaction_form,
                           edit_form=edit_form, port=port)


@portfolios.route('/portfolio/update/name', methods=["POST"])
@login_required
def update_portfolio_name():
    port_id: int = request.form.get("port_id", -1)
    port, _ = validate_port(port_id=port_id)
    form = CreatePortfolioForm()
    if form.validate_on_submit():
        if port.name != form.name.data:
            port.name = form.name.data
            db.session.commit()
            flash("Portfolio name updated!", "success")
    else:
        flash("Name could not be updated.", "warning")
    return redirect(url_for('portfolios.portfolio', port_id=port.id))


@portfolios.route('/portfolio/delete', methods=["POST"])
@login_required
def delete_portfolio():
    port_id: int = request.form.get("port_id", -1)
    port, _ = validate_port(port_id=port_id)
    db.session.delete(port)
    db.session.commit()
    flash(f"Portfolio '{port.name}' deleted!", "success")
    return redirect(url_for('portfolios.portfolio_all'))


def validate_transaction_type(value: str) -> bool:
    return value in [item.value for item in StockTransactionType]


@portfolios.route('/portfolio/transaction', methods=["POST"])
@login_required
def portfolio_transaction():
    port_id: int = request.form.get("port_id", -1)
    port, _ = validate_port(port_id=port_id)

    transaction_form = PortfolioTransactionForm()
    if transaction_form.validate_on_submit():
        ticker: str = transaction_form.ticker.data.upper()

        # see if stock wrapper exists
        stock_wrapper: StockWrapper = StockWrapper.query.filter_by(ticker=ticker).first()
        if not stock_wrapper:
            stock_wrapper = StockWrapper(ticker)
            db.session.add(stock_wrapper)

        # check if stock is already owned in this portfolio
        stock: Stock = Stock.query.filter_by(portfolio_id=port_id, ticker=ticker).first()
        if not stock:
            stock = Stock(ticker, stock_wrapper.id, port_id)
            db.session.add(stock)

        # transaction type based on form input
        if not validate_transaction_type(transaction_form.type.data):
            flash("Invalid transaction type.", "warning")
            return redirect(url_for('portfolios.portfolio', port_id=port.id))
        transaction_type = StockTransactionType(transaction_form.type.data)

        transaction: StockTransaction = StockTransaction(transaction_type,
                                                         transaction_form.date.data,
                                                         ticker,
                                                         transaction_form.quantity.data,
                                                         transaction_form.price.data,
                                                         transaction_form.fees.data,
                                                         stock.id)
        db.session.add(transaction)
        stock.transactions.append(transaction)
        db.session.commit()

    return redirect(url_for('portfolios.portfolio', port_id=port.id))


@portfolios.route('/portfolio/stock/delete', methods=["POST"])
@login_required
def delete_stock():
    port_id: int = request.form.get("port_id", -1)
    stock_id: int = request.form.get("stock_id", -1)
    port, stock = validate_port(port_id=port_id, s_id=stock_id)
    db.session.delete(stock)
    db.session.commit()
    flash(f"Stock '{stock.ticker}' deleted!", "success")
    return redirect(url_for('portfolios.portfolio', port_id=port_id))


@portfolios.route('/portfolio/stock/transaction/delete', methods=["POST"])
@login_required
def delete_transaction():
    port_id: int = request.form.get("port_id", -1)
    t_id: int = request.form.get("t_id", -1)
    port, t = validate_port(port_id=port_id, t_id=t_id)
    db.session.delete(t)
    db.session.commit()
    flash(f"Transaction from '{t.ticker}' deleted!", "success")
    return redirect(url_for('portfolios.portfolio', port_id=port_id))


@portfolios.route('/portfolio/stock/transaction/edit', methods=["POST"])
@login_required
def edit_transaction():
    port_id: int = request.form.get("port_id", -1)
    t_id: int = request.form.get("t_id", -1)
    port, t = validate_port(port_id=port_id, t_id=t_id)
    edit_form = PortfolioTransactionForm()
    if edit_form.validate_on_submit():
        ticker: str = edit_form.ticker.data.upper()
        if t.ticker != ticker or not validate_transaction_type(edit_form.type.data):
            return redirect(url_for('portfolios.portfolio', port_id=port_id))
        transaction_type = StockTransactionType(edit_form.type.data)
        t.type = transaction_type
        t.date = edit_form.date.data
        t.quantity = edit_form.quantity.data
        t.price = edit_form.price.data
        t.fees = edit_form.fees.data
        db.session.commit()
    return redirect(url_for('portfolios.portfolio', port_id=port_id))
