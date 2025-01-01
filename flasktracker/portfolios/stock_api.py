import os
import requests


def get_data(ticker: str):
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": ticker,
        "apikey": os.getenv('STOCK_API')
    }
    # print(requests.get(url, params=params))
    return requests.get(url, params=params)


def get_price(ticker: str):
    ticker = ticker.upper()
    if ticker == "TEST.TO":
        return {"market": 200, "change": 1.00}
    if ".TO" in ticker:
        ticker = ticker.replace(".TO", ".TRT")

    response = get_data(ticker)
    if not response.ok:
        return None
    data = response.json()
    global_quote = data.get("Global Quote", None)
    if not global_quote:
        return None
    price = float(data["Global Quote"]["05. price"])
    change_percent = float(data["Global Quote"]["10. change percent"].strip("%"))
    return {"market": price, "change": change_percent}
