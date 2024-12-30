import unittest
from unittest.mock import patch
from flasktracker.portfolios.stock_api import get_data, get_price


class TestStockAPI(unittest.TestCase):
    def setUp(self):
        print("setUp")

    def tearDown(self):
        print("tearDown")

    def test_get_data(self):
        with patch('flasktracker.portfolios.stock_api.requests.get') as mock_get:
            mock_get.return_value.ok = True
            mock_get.return_value.json.return_value = {
                "Global Quote": {
                    "05. price": "150.00",
                    "10. change percent": "1.50%"
                }
            }
            result = get_data("lebron").json()
            self.assertEqual(result, {"Global Quote": {"05. price": "150.00", "10. change percent": "1.50%"}})

    def test_get_price(self):
        with patch('flasktracker.portfolios.stock_api.requests.get') as mock_get:
            mock_get.return_value.ok = True
            mock_get.return_value.json.return_value = {
                "Global Quote": {
                    "05. price": "150.00",
                    "10. change percent": "1.50%"
                }
            }
            result = get_price("lebron")
            self.assertEqual(result, {"market": 150, "change": 1.5})

    def test_get_price_bad_response(self):
        with patch('flasktracker.portfolios.stock_api.requests.get') as mock_get:
            mock_get.return_value.ok = False
            mock_get.return_value.json.return_value = {
                "Global Quote": {
                    "05. price": "150.00",
                    "10. change percent": "1.50%"
                }
            }
            result = get_price("lebron")
            self.assertIsNone(result)

            mock_get.return_value.ok = True
            mock_get.return_value.json.return_value = {}
            result = get_price("lebron")
            self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
