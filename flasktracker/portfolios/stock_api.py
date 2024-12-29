def get_price(ticker: str) -> dict:
    test = {"market": 13, "change": 1.00}
    test_values = {"VFV": {"market": 150, "change": 1.04}, "RY": {"market": 175, "change": 0.39},
                   "SHOP": {"market": 110, "change": -1.64}, "TD": {"market": 80, "change": 0.26},
                   "TEST": test}
    return test_values.get(ticker, test)
