# Portfolio Tracker

## Description

- This is a web app designed to help users manage their investment portfolios.
- Track multiple portfolios, and track the performance of each portfolio
- Track a portfolio's underlying stocks, and manage transactions such as buying or selling stocks.
- This app was built using the Flask framework, SQLAlchemy to handle the data in the PostgreSQL database, and an
  external API to fetch live stock prices.

## Features

- User authentication and profile management.
- Management of investment portfolios: Create, Read, Update, Delete portfolios, stocks, and transactions.
- Live tracking of stock prices and portfolio performance.
- Transaction management, including records of buying/selling stocks and profit/loss calculations.

## Tech Stack

### Backend:

- Python, Flask, SQLAlchemy

### Frontend:

- Jinja, Bootstrap, JavaScript

### Database:

- PostgreSQL (Production), SQLite (Early Development and Testing)

## Unit Testing

- Unit testing for this project was conducted using the pytest and unittest frameworks. The corresponding test cases can
  be found in the [tests](tests/) folder.