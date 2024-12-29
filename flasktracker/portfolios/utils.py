from flask import abort
from flask_login import current_user

from flasktracker.portfolios.models import Portfolio, Stock, StockTransaction


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


def round_not_whole(value: float | int) -> float | int:
    if value % 1 == 0:
        return int(value)
    return round(value, 2)


def format_dollar(value: float) -> str:
    return f"-${abs(value):,.2f}" if value < 0 else f"${value:,.2f}"


def format_pl(value: float) -> dict:
    formatted_value = format_dollar(value)
    direction = "pos" if value >= 0 else "neg"
    return {"value": formatted_value, "direction": direction}


def format_percent(value: float) -> dict:
    formatted_perc = f"{value:,.2f}%"
    direction = "pos" if value >= 0 else "neg"
    return {"value": formatted_perc, "direction": direction}
