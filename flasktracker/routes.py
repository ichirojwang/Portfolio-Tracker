from flask import url_for, render_template, redirect, flash, request, abort
from flask_login import login_user, login_required, current_user, logout_user
from flasktracker import app, db, bcrypt
from flasktracker.models import User, Portfolio, Stock, StockTransaction, StockTransactionType, StockWrapper
from flasktracker.forms import SignUpForm, LogInForm, UpdateAccountForm, UpdateYearEligibleForm, CreatePortfolioForm, \
    PortfolioTransactionForm


@app.route('/welcome')
def welcome():
    return render_template("welcome.html")


@app.route('/signup', methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = SignUpForm()
    if form.validate_on_submit():
        # hashing password with bcrypt
        hashed_password: str = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user: User = User(form.name.data, form.email.data, hashed_password)

        # adding to database
        db.session.add(new_user)
        db.session.commit()

        flash(f"Account created for {form.name.data}.", "success")
        return redirect(url_for('login'))

    return render_template("signup.html", form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LogInForm()
    if form.validate_on_submit():
        user: User = User.query.filter_by(email=form.email.data).first()
        # if user found, verify with hashed password
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            # if the user came from a login required page
            next_page = request.args.get('next', url_for('home'))
            return redirect(next_page)
        else:
            flash("Invalid credentials.", "warning")

    return render_template("login.html", form=form)


@app.route('/')
def send_home():
    return redirect(url_for('home'))


@app.route('/home')
@login_required
def home():
    return render_template("home.html")


@app.route('/accounts')
@login_required
def accounts():
    return render_template("accounts.html")


@app.route('/portfolio/all', methods=["GET", "POST"])
@login_required
def portfolios():
    form = CreatePortfolioForm()
    if form.validate_on_submit():
        new_port: Portfolio = Portfolio(form.name.data, current_user.id)
        db.session.add(new_port)
        db.session.commit()
        flash(f"New portfolio '{form.name.data}' created!", "success")
    return render_template("portfolios.html", form=form)


@app.route('/portfolio/<int:port_id>', methods=["GET", "POST"])
@login_required
def portfolio(port_id: int):
    port: Portfolio = Portfolio.query.get_or_404(port_id)
    if port.owner != current_user:
        abort(403)
    port_name_form = CreatePortfolioForm()
    port_name_form.submit.label.text = "Confirm Changes"
    transaction_form = PortfolioTransactionForm()
    edit_form = PortfolioTransactionForm()

    return render_template("portfolio.html", port_name_form=port_name_form, transaction_form=transaction_form,
                           edit_form=edit_form, port=port)


def validate_port(port_id: int, s_id: int = -1, t_id: int = -1):
    if port_id in [None, -1]:
        abort(400)
    port: Portfolio = Portfolio.query.get_or_404(port_id)
    if port.owner != current_user:
        abort(403)

    if s_id not in [None, -1]:
        s = Stock.query.get_or_404(s_id)
        if s.portfolio.owner != current_user:
            abort(403)
        print("valid")
        return port, s

    if t_id not in [None, -1]:
        t = StockTransaction.query.get_or_404(t_id)
        if t.stock.portfolio.owner != current_user:
            abort(403)
        print("valid")
        return port, t

    print("valid")
    return port, None


@app.route('/portfolio/update/name', methods=["POST"])
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
    return redirect(url_for('portfolio', port_id=port.id))


@app.route('/portfolio/delete', methods=["POST"])
@login_required
def delete_portfolio():
    port_id: int = request.form.get("port_id", -1)
    port, _ = validate_port(port_id=port_id)
    # port: Portfolio = Portfolio.query.get_or_404(port_id)
    db.session.delete(port)
    db.session.commit()
    flash(f"Portfolio '{port.name}' deleted!", "success")
    return redirect(url_for('portfolios'))


@app.route('/portfolio/transaction', methods=["POST"])
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
        transaction_type = StockTransactionType(transaction_form.type.data)

        transaction: StockTransaction = StockTransaction(transaction_type,
                                                         transaction_form.date.data,
                                                         ticker,
                                                         transaction_form.quantity.data,
                                                         transaction_form.price.data,
                                                         transaction_form.fees.data, stock.id)
        db.session.add(transaction)
        stock.transactions.append(transaction)
        db.session.commit()

    return redirect(url_for('portfolio', port_id=port.id))


@app.route('/portfolio/stock/delete', methods=["POST"])
@login_required
def delete_stock():
    port_id: int = request.form.get("port_id", -1)
    stock_id: int = request.form.get("stock_id", -1)
    port, stock = validate_port(port_id=port_id, s_id=stock_id)
    db.session.delete(stock)
    db.session.commit()
    flash(f"Stock '{stock.ticker}' deleted!", "success")
    return redirect(url_for('portfolio', port_id=port_id))


@app.route('/portfolio/stock/transaction/delete', methods=["POST"])
@login_required
def delete_transaction():
    port_id: int = request.form.get("port_id", -1)
    t_id: int = request.form.get("t_id", -1)
    port, t = validate_port(port_id=port_id, t_id=t_id)
    db.session.delete(t)
    db.session.commit()
    flash(f"Transaction from '{t.ticker}' deleted!", "success")
    return redirect(url_for('portfolio', port_id=port_id))


@app.route('/portfolio/stock/transaction/edit', methods=["POST"])
@login_required
def edit_transaction():
    print("editting")
    port_id: int = request.form.get("port_id", -1)
    t_id: int = request.form.get("t_id", -1)
    port, t = validate_port(port_id=port_id, t_id=t_id)
    edit_form = PortfolioTransactionForm()
    if edit_form.validate_on_submit():
        print("editting 2")
        ticker: str = edit_form.ticker.data.upper()
        if t.ticker != ticker:
            return redirect(url_for('portfolio', port_id=port_id))
        t.date = edit_form.date.data
        t.quantity = edit_form.quantity.data
        t.price = edit_form.price.data
        t.fees = edit_form.fees.data
        db.session.commit()
    return redirect(url_for('portfolio', port_id=port_id))


@app.route('/profile', methods=["GET", "POST"])
@login_required
def profile():
    form = UpdateAccountForm()
    year_form = UpdateYearEligibleForm()
    if form.validate_on_submit():
        if current_user.name != form.name.data or current_user.email != form.email.data:
            current_user.name = form.name.data
            current_user.email = form.email.data
            db.session.commit()
            flash("Account successfully updated!", "success")
        return redirect(url_for('profile'))
    return render_template("profile.html", form=form, year_form=year_form)


@app.route('/profile/update/year', methods=["POST"])
@login_required
def update_profile_year():
    year_form = UpdateYearEligibleForm()
    if year_form.validate_on_submit():
        if year_form.year.data < 2009 or year_form.year.data > 2100:
            flash("Invalid year.", "warning")
        elif current_user.year_eligible != year_form.year.data:
            current_user.year_eligible = year_form.year.data
            db.session.commit()
            flash("Year has been updated!", "success")
    return redirect(url_for('profile'))


@app.route('/settings')
@login_required
def settings():
    return render_template("settings.html")


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("welcome"))
