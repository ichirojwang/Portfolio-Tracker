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


def get_price(ticker: str) -> dict:
    test = {"market": 13, "change": 1.00}
    test_values = {"VFV": {"market": 150, "change": 1.04}, "RY": {"market": 175, "change": 0.39},
                   "SHOP": {"market": 110, "change": -1.64}, "TD": {"market": 80, "change": 0.26},
                   "TEST": test}
    return test_values.get(ticker, test)
