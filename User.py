from Stock import Stock
import Date
from InvalidAction import InsufficientBalance, OverLimit
import logging
from TFSA import TFSA

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - '
                                  '%(module)s - %(funcName)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

file_handler = logging.FileHandler("user.log")
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)


class User:
    def __init__(self, first: str, last: str, year_of_birth: int) -> None:
        self.first: str = first
        self.last: str = last
        self.year_of_birth: int = year_of_birth
        self.tfsa: TFSA = TFSA(year_of_birth)

        logger.info(f"Created User: {self.first} {self.last} {self.year_of_birth}")

    @property
    def name_fl(self) -> str:
        return f"{self.first} {self.last}"

    @property
    def name_lf(self) -> str:
        return f"{self.last}, {self.first}"

    # str of user object
    def __str__(self) -> str:
        represent = f"Details for {self.name_lf}:"

        represent += str(self.tfsa)

        represent += str(self.tfsa.portfolio)

        return represent

def main():
    logger.info("\n\n\nBeginning log\n\n")
    joe_biden = User("Joe", "Biden", 2002)

    try:
        joe_biden.tfsa.contribute(Date.gen_random_day(), 15000)
        joe_biden.tfsa.contribute(Date.gen_random_day(), 10000)
        # joe_biden.contribute(SelectDate.gen_random_day(), 10000)
        # print("contributed 3 times")
    except OverLimit as e:
        logger.exception(e)

    try:
        joe_biden.tfsa.withdraw(Date.gen_random_day(), 10000)
        joe_biden.tfsa.withdraw(Date.gen_random_day(), 10000)
        # joe_biden.withdraw(SelectDate.gen_random_day(), 120000)
        # print("withdrew 3 times")
    except InsufficientBalance as e:
        logger.exception(e)

    try:
        ticker = "gooGl".upper()
        joe_biden.tfsa.buy(Date.gen_random_day(), ticker, 10, 160)
        joe_biden.tfsa.buy(Date.gen_random_day(), "GOOGL", 20, 100)
        ticker = "AapL".upper()
        joe_biden.tfsa.buy(Date.gen_random_day(), ticker, 5, 100)
        # joe_biden.tfsa.buy(SelectDate.gen_random_day(), "AAPL", 5, 100)
    except InsufficientBalance as e:
        logger.exception(e)

    # try:
    #     joe_biden.tfsa.sell("GOOGL", 32, 120)
    # except InsufficientShares as e:
    #     logger.exception(e)

    print(f"\n{Stock.header_str()}")
    print(joe_biden.tfsa.portfolio.get_portfolio())

    # try:
    joe_biden.tfsa.sell(Date.gen_random_day(), "GOOGL", 5, 160)
    joe_biden.tfsa.sell(Date.gen_random_day(), "GOOGL", 5, 200)

    #     joe_biden.sell("TSLA", 10, 10)
    # except InsufficientShares as e:
    #     logger.exception(e)

    print()

    joe_biden.tfsa.buy(Date.gen_random_day(), "TEST", 4, 80)
    joe_biden.tfsa.sell(Date.gen_random_day(), "TEST", 4, 60)
    # joe_biden.buy(SelectDate.gen_random_day(), "AMZN", 4, 100)
    print(joe_biden.tfsa.portfolio.stocks["GOOGL"].value_book_sell)
    print(joe_biden)

if __name__ == "__main__":
    main()
