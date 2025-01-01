from flasktracker.portfolios.models import *


def test_portfolio_all(app, client, auth):
    with client.application.test_request_context():
        auth.create()
        auth.login()
        response = client.get('/portfolio/all')
        assert response.status_code == 200
        assert b"<title>Loonie Ledger - My Portfolios</title>" in response.data

        response = auth.create_port("LeBrons port")
        assert response.status_code == 200
        assert b"LeBrons port" in response.data

    with app.app_context():
        assert Portfolio.query.count() == 1
        assert db.session.get(Portfolio, 1).name == "LeBrons port"


def test_portfolio_long_name(app, client, auth):
    with client.application.test_request_context():
        auth.create()
        auth.login()
        # edge case 40 chars max
        response = auth.create_port("lebrons port with 40 charactersblahblahb")
        assert response.status_code == 200
        assert b"lebrons port with 40 charactersblahblahb" in response.data
        # edge case go over 40 char
        response = auth.create_port("lebrons port with 41 charactersblahblahbl")
        assert response.status_code == 200
        # empty name
        response = auth.create_port("")
        assert response.status_code == 200

        with app.app_context():
            assert Portfolio.query.count() == 1
            assert db.session.get(Portfolio, 1).name == "lebrons port with 40 charactersblahblahb"


def test_portfolio_all_not_auth(app, client, auth):
    with client.application.test_request_context():
        auth.create()
        response = client.get('/portfolio/all')
        assert response.status_code == 302
        assert response.headers['Location'] == "/login?next=%2Fportfolio%2Fall"

        response = auth.create_port("LeBrons port")
        assert response.status_code == 302
        assert response.headers['Location'] == "/login?next=%2Fportfolio%2Fall"

        with app.app_context():
            assert Portfolio.query.count() == 0


def test_portfolio(app, client, auth):
    with client.application.test_request_context():
        auth.create()
        auth.login()
        response = auth.create_port("LeBrons port")
        assert response.status_code == 200
        assert b"<title>Loonie Ledger - My Portfolios</title>" in response.data
        assert b"LeBrons port" in response.data
        # get portfolio
        response = client.get('/portfolio/1')
        assert response.status_code == 200
        assert b"<title>Loonie Ledger - Portfolio</title>" in response.data
        assert b"LeBrons port" in response.data

        # port id 5 doesnt exist
        response = client.get('/portfolio/5')
        assert response.status_code == 404
        assert b"<title>Loonie Ledger - Error</title>" in response.data

        # get while not logged in
        auth.logout()
        response = client.get('/portfolio/1')
        assert response.status_code == 302
        assert response.headers['Location'] == "/login?next=%2Fportfolio%2F1"

        # now go to john doe's account
        auth.login_john()
        response = client.get('/portfolio/1')  # belongs to lebron
        assert response.status_code == 403
        assert b"<title>Loonie Ledger - Error</title>" in response.data

        client.post('/portfolio/all', data={"name": ""})


def test_update_portfolio_name(app, client, auth):
    with client.application.test_request_context():
        auth.create()
        auth.login()
        auth.create_port("LeBrons port")
        response = client.post('portfolio/update/name', data={"port_id": 1, "name": "updated name"})
        assert response.status_code == 302
        assert response.headers['Location'] == "/portfolio/1"
        with app.app_context():
            assert db.session.get(Portfolio, 1).name == "updated name"
        # try empty name
        response = client.post('portfolio/update/name', data={"port_id": 1, "name": ""})
        with app.app_context():
            # check name is not empty
            assert db.session.get(Portfolio, 1).name == "updated name"


def test_update_portfolio_long_name(app, client, auth):
    with client.application.test_request_context():
        auth.create()
        auth.login()
        auth.create_port("LeBrons port")
        # update name to 40 char (max 40 char)
        response = client.post('portfolio/update/name',
                               data={"port_id": 1, "name": "updatednamewith40charactersblahblahblahb"})
        with app.app_context():
            assert db.session.get(Portfolio, 1).name == "updatednamewith40charactersblahblahblahb"
        # update name to 41 char
        response = client.post('portfolio/update/longname',
                               data={"port_id": 1, "name": "updatednamewith41charactersblahblahblahbl"})
        with app.app_context():
            # check name did not change
            assert db.session.get(Portfolio, 1).name == "updatednamewith40charactersblahblahblahb"


def test_update_port_name_not_auth(app, client, auth):
    with client.application.test_request_context():
        auth.create()
        auth.login()
        auth.create_port("LeBrons port")
        # port id 2 doesnt exist
        response = client.post('portfolio/update/name', data={"port_id": 2, "name": "updated name"})
        assert response.status_code == 404
        assert b"<title>Loonie Ledger - Error" in response.data

        # update when logged out
        auth.logout()
        response = client.post('portfolio/update/name', data={"port_id": 1, "name": "updated name"})
        assert response.status_code == 302
        assert response.headers['Location'] == "/login?next=%2Fportfolio%2Fupdate%2Fname"
        with app.app_context():
            assert db.session.get(Portfolio, 1).name == "LeBrons port"

        auth.login_john()
        response = client.post('portfolio/update/name', data={"port_id": 1, "name": "updated name"})
        assert response.status_code == 403
        assert b"<title>Loonie Ledger - Error" in response.data
        with app.app_context():
            assert db.session.get(Portfolio, 1).name == "LeBrons port"


def test_portfolio_dupe_name(app, client, auth):
    with client.application.test_request_context():
        auth.create()
        auth.login()
        auth.create_port("LeBrons port")
        auth.create_port("LeBrons port 2")
        response = client.post('portfolio/update/name', data={"port_id": 2, "name": "LeBrons port"})
        with app.app_context():
            assert db.session.get(Portfolio, 1).name == "LeBrons port"
            assert db.session.get(Portfolio, 2).name == "LeBrons port 2"
        response = auth.create_port("LeBrons port")
        assert b"You already have a portfolio with that name" in response.data
        with app.app_context():
            assert Portfolio.query.count() == 2


def test_delete_port(app, client, auth):
    with client.application.test_request_context():
        auth.create()
        auth.login()
        auth.create_port("LeBrons port")
        auth.create_port("LeBrons port 2")
        with app.app_context():
            assert Portfolio.query.count() == 2
        assert Portfolio.query.first().name == "LeBrons port"
        response = client.post('/portfolio/delete', data={"port_id": 1})
        assert response.status_code == 302
        assert response.headers['Location'] == "/portfolio/all"
        with app.app_context():
            assert Portfolio.query.count() == 1
            assert Portfolio.query.first().name == "LeBrons port 2"


def test_delete_port_not_auth(app, client, auth):
    with client.application.test_request_context():
        auth.create()
        auth.login()
        auth.create_port("LeBrons port")

        auth.logout()
        response = client.post('/portfolio/delete', data={"port_id": 1})
        assert response.status_code == 302
        assert response.headers['Location'] == "/login?next=%2Fportfolio%2Fdelete"
        with app.app_context():
            assert Portfolio.query.count() == 1

        auth.login_john()
        response = client.post('/portfolio/delete', data={"port_id": 1})
        assert response.status_code == 403
        assert b"<title>Loonie Ledger - Error" in response.data
        with app.app_context():
            assert Portfolio.query.count() == 1
            assert db.session.get(Portfolio, 1).name == "LeBrons port"


# default state if no args given
def create_transaction(client, port_id: int = 1, t_type: str = "buy", date: str = "2024-12-25", ticker: str = "TEST.TO",
                       quantity: float = 10, price: float = 100, fees: float = 0):
    return client.post('/portfolio/transaction',
                       data={"port_id": port_id, "type": t_type, "date": date, "quantity": quantity, "fees": fees,
                             "price": price, "ticker": ticker})


# comparing with above default state if no args given
def assert_transaction(transaction, t_type: str = "buy", date: str = "2024-12-25", ticker: str = "TEST.TO",
                       quantity: float = 10, price: float = 100, fees: float = 0, stock_id: int = 1):
    assert transaction.type.value == t_type
    assert transaction.date.strftime("%Y-%m-%d") == date
    assert transaction.ticker == ticker
    assert transaction.quantity == quantity
    assert transaction.price == price
    assert transaction.fees == fees
    assert transaction.stock.id == stock_id


def test_port_transaction(app, client, auth):
    with client.application.test_request_context():
        auth.create()
        auth.login()
        auth.create_port("LeBrons port")
        auth.create_port("LeBrons port 2")
        response = create_transaction(client)
        assert response.status_code == 302
        assert response.headers['Location'] == "/portfolio/1"
        create_transaction(client, 2, "buy", "2024-12-26", "TEST2.TO", 5, 200)
        create_transaction(client, 1, "sell", "2024-12-26", "TEST.TO", 3, 300)
        create_transaction(client, 2, "sell", "2024-12-27", "TEST2.TO", 4, 400)

        with app.app_context():
            assert Stock.query.count() == 2
            assert db.session.get(Stock, 1).ticker == "TEST.TO"
            assert db.session.get(Stock, 2).ticker == "TEST2.TO"

            assert StockTransaction.query.count() == 4

            assert_transaction(db.session.get(StockTransaction, 1))
            assert_transaction(db.session.get(StockTransaction, 2), "buy", "2024-12-26", "TEST2.TO", 5, 200, 0, 2)
            assert_transaction(db.session.get(StockTransaction, 3), "sell", "2024-12-26", "TEST.TO", 3, 300, 0, 1)
            assert_transaction(db.session.get(StockTransaction, 4), "sell", "2024-12-27", "TEST2.TO", 4, 400, 0, 2)


def test_port_transaction_multiple(app, client, auth):
    with client.application.test_request_context():
        auth.create()
        auth.login()
        auth.create_port("LeBrons port")
        response = create_transaction(client)
        assert response.status_code == 302
        assert response.headers['Location'] == "/portfolio/1"
        create_transaction(client, 1, "buy", "2024-12-26", "TEST2.TO", 5, 200)
        create_transaction(client, 1, "sell", "2024-12-26", "TEST.TO", 3, 300)
        create_transaction(client, 1, "sell", "2024-12-27", "TEST2.TO", 4, 400)

        with app.app_context():
            assert Stock.query.count() == 2
            assert db.session.get(Stock, 1).ticker == "TEST.TO"
            assert db.session.get(Stock, 2).ticker == "TEST2.TO"

            assert StockTransaction.query.count() == 4

            assert_transaction(db.session.get(StockTransaction, 1))
            assert_transaction(db.session.get(StockTransaction, 2), "buy", "2024-12-26", "TEST2.TO", 5, 200, 0, 2)
            assert_transaction(db.session.get(StockTransaction, 3), "sell", "2024-12-26", "TEST.TO", 3, 300, 0, 1)
            assert_transaction(db.session.get(StockTransaction, 4), "sell", "2024-12-27", "TEST2.TO", 4, 400, 0, 2)


def test_port_transaction_bad_fields(app, client, auth):
    with client.application.test_request_context():
        auth.create()
        auth.login()
        auth.create_port("LeBrons port")
        # normal (20 chars max for ticker)
        create_transaction(client, ticker="TESTWITH20CHARACTERS")
        # non existent port
        response = create_transaction(client, port_id=2)
        assert response.status_code == 404
        assert b"<title>Loonie Ledger - Error" in response.data
        # bad type
        response = create_transaction(client, t_type="type")
        assert response.status_code == 302
        assert response.headers['Location'] == "/portfolio/1"
        # bad date
        create_transaction(client, 1, date="2100-12-25")
        # long ticker (exceed 20 char)
        create_transaction(client, 1, ticker="TESTWITH21CHARACTERSS")
        # negative qty
        create_transaction(client, quantity=-0.01)
        # negative price
        create_transaction(client, price=-0.01)
        # negative fee
        create_transaction(client, fees=-0.01)

        with app.app_context():
            assert StockTransaction.query.count() == 1
            assert_transaction(db.session.get(StockTransaction, 1), "buy", "2024-12-25", "TESTWITH20CHARACTERS", 10,
                               100, 0, 1)


def test_delete_stock(app, client, auth):
    with client.application.test_request_context():
        auth.create()
        auth.login()
        auth.create_port("LeBrons port")
        create_transaction(client)
        create_transaction(client, date="2024-12-26")
        create_transaction(client, date="2024-12-27")
        with app.app_context():
            assert Stock.query.count() == 1
            assert Stock.query.first().ticker == "TEST.TO"

            assert StockTransaction.query.count() == 3
            assert_transaction(db.session.get(StockTransaction, 1))
            assert_transaction(db.session.get(StockTransaction, 2), date="2024-12-26")
            assert_transaction(db.session.get(StockTransaction, 3), date="2024-12-27")

        response = client.post('/portfolio/stock/delete', data={"port_id": 1, "stock_id": 1})
        assert response.status_code == 302
        assert response.headers['Location'] == "/portfolio/1"

        with app.app_context():
            # cascade should delete transactions with the stock
            assert Stock.query.count() == 0
            assert StockTransaction.query.count() == 0


def test_delete_stock_not_auth(app, client, auth):
    with client.application.test_request_context():
        auth.create()
        auth.login()
        auth.create_port("LeBrons port")
        create_transaction(client)
        # delete non existent stock id
        response = client.post('/portfolio/stock/delete', data={"port_id": 1, "stock_id": 2})
        assert response.status_code == 404
        assert b"<title>Loonie Ledger - Error" in response.data

        auth.logout()
        response = client.post('/portfolio/stock/delete', data={"port_id": 1, "stock_id": 1})
        assert response.status_code == 302
        assert response.headers['Location'] == "/login?next=%2Fportfolio%2Fstock%2Fdelete"

        auth.login_john()
        response = client.post('/portfolio/stock/delete', data={"port_id": 1, "stock_id": 1})
        assert response.status_code == 403
        assert b"<title>Loonie Ledger - Error" in response.data


def test_delete_transaction(app, client, auth):
    with client.application.test_request_context():
        auth.create()
        auth.login()
        auth.create_port("LeBrons port")
        response = create_transaction(client)
        response = create_transaction(client, 1, "sell", "2024-12-25", "TEST2.TO", 5, 200, 0)
        with app.app_context():
            assert StockTransaction.query.count() == 2
            assert_transaction(StockTransaction.query.first())
        response = client.post('/portfolio/stock/transaction/delete', data={"port_id": 1, "t_id": 1})
        with app.app_context():
            assert StockTransaction.query.count() == 1
            assert_transaction(StockTransaction.query.first(), "sell", "2024-12-25", "TEST2.TO", 5, 200, 0, 2)


def test_delete_transaction_not_auth(app, client, auth):
    with client.application.test_request_context():
        auth.create()
        auth.login()
        auth.create_port("LeBrons port")

        response = create_transaction(client)
        # delete non existent transaction
        response = client.post('/portfolio/stock/transaction/delete', data={"port_id": 1, "t_id": 2})
        assert response.status_code == 404
        assert b"<title>Loonie Ledger - Error" in response.data

        with app.app_context():
            assert StockTransaction.query.count() == 1
            assert_transaction(StockTransaction.query.first())

        # delete while not logged in
        auth.logout()
        response = client.post('/portfolio/stock/transaction/delete', data={"port_id": 1, "t_id": 1})
        assert response.status_code == 302
        assert response.headers['Location'] == "/login?next=%2Fportfolio%2Fstock%2Ftransaction%2Fdelete"
        response = client.post('/login?next=%2Fportfolio%2Fstock%2Ftransaction%2Fdelete',
                               data={"email": "lebron@gmail.com", "password": "akronohio"})
        assert response.status_code == 302
        assert response.headers['Location'] == "/portfolio/stock/transaction/delete"
        with app.app_context():
            assert StockTransaction.query.count() == 1
            assert_transaction(StockTransaction.query.first())

        # delete from wrong account
        auth.logout()
        auth.login_john()
        response = client.post('/portfolio/stock/transaction/delete', data={"port_id": 1, "t_id": 1})
        assert response.status_code == 403
        assert b"<title>Loonie Ledger - Error" in response.data
        with app.app_context():
            assert StockTransaction.query.count() == 1
            assert_transaction(StockTransaction.query.first())


# default edit fields
def edit_transaction(client, port_id: int = 1, t_id: int = 1, t_type: str = "sell", date="2024-12-31",
                     ticker: str = "TEST.TO", quantity: float = 20, price: float = 200, fees: float = 10):
    return client.post('/portfolio/stock/transaction/edit',
                       data={"port_id": port_id, "t_id": t_id, "type": t_type, "date": date, "ticker": ticker,
                             "quantity": quantity, "price": price, "fees": fees})


def test_edit_transaction(app, client, auth):
    with client.application.test_request_context():
        auth.create()
        auth.login()
        auth.create_port("LeBrons port")
        response = create_transaction(client)
        with app.app_context():
            assert_transaction(StockTransaction.query.first())
        response = edit_transaction(client)
        assert response.status_code == 302
        assert response.headers['Location'] == "/portfolio/1"
        with app.app_context():
            assert_transaction(StockTransaction.query.first(), "sell", "2024-12-31", "TEST.TO", 20, 200, 10, 1)


def test_edit_transaction_bad_fields(app, client, auth):
    with client.application.test_request_context():
        auth.create()
        auth.login()
        auth.create_port("LeBrons port")
        response = create_transaction(client)
        with app.app_context():
            assert_transaction(StockTransaction.query.first())
        # non existent port
        response = edit_transaction(client, port_id=2)
        assert response.status_code == 404
        assert b"<title>Loonie Ledger - Error" in response.data
        # non existent transaction
        response = edit_transaction(client, t_id=2)
        assert response.status_code == 404
        assert b"<title>Loonie Ledger - Error" in response.data
        # bad transaction type
        response = edit_transaction(client, t_type="type")
        assert response.status_code == 302
        assert response.headers['Location'] == "/portfolio/1"
        # bad date
        edit_transaction(client, date="2100-12-25")
        # change ticker
        edit_transaction(client, ticker="NEWTICKER.TO")
        # bad qty
        edit_transaction(client, quantity=-0.01)
        # bad price
        edit_transaction(client, price=-0.01)
        # bad fee
        edit_transaction(client, fees=-0.01)

        with app.app_context():
            # transaction should still be in default state
            assert_transaction(StockTransaction.query.first())


def test_edit_transaction_not_auth(app, client, auth):
    with client.application.test_request_context():
        auth.create()
        auth.login()
        auth.create_port("LeBrons port")

        response = create_transaction(client)
        # delete non existent transaction
        response = edit_transaction(client, port_id=2)
        assert response.status_code == 404
        assert b"<title>Loonie Ledger - Error" in response.data

        with app.app_context():
            assert StockTransaction.query.count() == 1
            assert_transaction(StockTransaction.query.first())

        # delete while not logged in
        auth.logout()
        response = edit_transaction(client)
        assert response.status_code == 302
        assert response.headers['Location'] == "/login?next=%2Fportfolio%2Fstock%2Ftransaction%2Fedit"
        response = client.post('/login?next=%2Fportfolio%2Fstock%2Ftransaction%2Fedit',
                               data={"email": "lebron@gmail.com", "password": "akronohio"})
        assert response.status_code == 302
        assert response.headers['Location'] == "/portfolio/stock/transaction/edit"
        with app.app_context():
            # should be in default state
            assert_transaction(StockTransaction.query.first())

        # delete from wrong account
        auth.logout()
        auth.login_john()
        response = edit_transaction(client)
        assert response.status_code == 403
        assert b"<title>Loonie Ledger - Error" in response.data
        with app.app_context():
            # should be in default state
            assert_transaction(StockTransaction.query.first())
