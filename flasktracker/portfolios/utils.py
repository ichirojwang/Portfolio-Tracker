from flask import abort
from flask_login import current_user

from flasktracker import db
from flasktracker.portfolios.models import Portfolio, Stock, StockTransaction


def validate_port(port_id: int, s_id: int = -1, t_id: int = -1):
    if port_id in [None, -1]:
        abort(400)
    port: Portfolio = db.session.get(Portfolio, port_id)
    if not port:
        abort(404)
    if port.owner != current_user:
        abort(403)

    if s_id not in [None, -1]:
        s = db.session.get(Stock, s_id)
        if not s:
            abort(404)
        if s.portfolio.owner != current_user:
            abort(403)
        return port, s

    if t_id not in [None, -1]:
        t = db.session.get(StockTransaction, t_id)
        if not t:
            abort(404)
        print(t.stock.portfolio.owner)
        print(current_user)
        if t.stock.portfolio.owner != current_user:
            abort(403)
        return port, t

    return port, None


def round_not_whole(value: float | int) -> float | int:
    if value % 1 == 0:
        return int(value)
    return round(value, 2)


def format_dollar(value: float) -> str:
    return f"-${abs(value):,.2f}" if value < 0 else f"${value:,.2f}"


def format_pl(value: float) -> dict[str, str]:
    formatted_value = format_dollar(value)
    direction = "pos" if value >= 0 else "neg"
    return {"value": formatted_value, "direction": direction}


def format_percent(value: float) -> dict[str, str]:
    formatted_perc = f"{value:,.2f}%"
    direction = "pos" if value >= 0 else "neg"
    return {"value": formatted_perc, "direction": direction}
