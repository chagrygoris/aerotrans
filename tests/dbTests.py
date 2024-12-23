import unittest
from unittest.mock import patch
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from src import User, TRequest, TFlight, TCart
from src import already_registered, add_flight, add_to_cart, add_user, cart_item_exists, have_saved_routes
from adapters.viewResults import create_rectangles
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

#without mocking

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        User.metadata.create_all(self.engine)
        TRequest.metadata.create_all(self.engine)
        TFlight.metadata.create_all(self.engine)
        TCart.metadata.create_all(self.engine)

    @patch("src.models.session.execute")
    def test_already_registered(self, mock_execute):
        mock_execute.return_value.first.return_value = User(name="John Doe", email="johndoe@example.com", telegram_id=1234567)
        self.assertTrue(already_registered("John Doe", "johndoe@example.com", 1234567))
        mock_execute.return_value.first.return_value = None
        self.assertFalse(already_registered("Jane Doe", "janedoe@example.com", 1234567))

    @patch("src.models.session.execute")
    def test_cart_item_exists(self, mock_execute):
        mock_execute.return_value.first.return_value = TCart(user_id=1, flight_id=123)
        self.assertTrue(cart_item_exists(1, 123))
        mock_execute.return_value.first.return_value = None
        self.assertFalse(cart_item_exists(1, 999))

    @patch("src.checkers.already_registered")
    def test_add_user(self, mock_already_registered):
        mock_already_registered.return_value = False
        new_user = add_user("John Doe", "johndoe@example.com", b"password123", 12345)
        self.assertIsNotNone(new_user)
        self.assertEqual(new_user.name, "John Doe")
        self.assertEqual(new_user.email, "johndoe@example.com")
        self.assertEqual(new_user.telegram_id, 12345)

        mock_already_registered.return_value = True
        self.assertIsNone(add_user("Jane Doe", "johndoe@example.com", b"password456", 67890))

    @patch("src.checkers.have_saved_routes")
    def test_add_flight(self, mock_have_saved_routes):
        mock_have_saved_routes.return_value = False
        new_flight = add_flight("New York", "Los Angeles", datetime.now(), datetime.now() + timedelta(hours=5), 500.0,
                                "United Airlines")
        self.assertIsNotNone(new_flight)
        self.assertEqual(new_flight.origin, "New York")
        self.assertEqual(new_flight.destination, "Los Angeles")
        self.assertEqual(new_flight.price, 500.0)
        self.assertEqual(new_flight.company, "United Airlines")

        mock_have_saved_routes.return_value = True
        self.assertIsNone(
            add_flight("New York", "Los Angeles", datetime.now(), datetime.now() + timedelta(hours=5), 550.0, "Delta"))

    @patch("src.checkers.cart_item_exists")
    def test_add_to_cart(self, mock_cart_item_exists):
        mock_cart_item_exists.return_value = False
        new_cart_item = add_to_cart(1, 123)
        self.assertIsNotNone(new_cart_item)
        self.assertEqual(new_cart_item.user_id, 1)
        self.assertEqual(new_cart_item.flight_id, 123)

        mock_cart_item_exists.return_value = True
        self.assertIsNone(add_to_cart(1, 123))


# mock-session example for create_rectangles

class TestCreateRectangles(unittest.TestCase):
    def setUp(self):
        self.db_mock = MagicMock(Session)
    def test_create_rectangles(self):
        from_city = "New York"
        to_city = "Los Angeles"
        flight_1 = MagicMock()
        flight_1.flight_id = 1
        flight_1.origin = "New York"
        flight_1.destination = "Los Angeles"
        flight_1.departure_time = datetime(2024, 12, 1, 10, 30)
        flight_1.price = 150.0
        flight_2 = MagicMock()
        flight_2.flight_id = 2
        flight_2.origin = "New York"
        flight_2.destination = "Los Angeles"
        flight_2.departure_time = datetime(2024, 12, 1, 14, 0)
        flight_2.price = 200.0
        self.db_mock.query().filter().all.return_value = [flight_1, flight_2]
        result = create_rectangles(from_city, to_city, self.db_mock)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], {
            "id": 1,
            "origin": "New York",
            "destination": "Los Angeles",
            "departure_time": "2024-12-01T10:30:00",
            "price": 150.0
        })
        self.assertEqual(result[1], {
            "id": 2,
            "origin": "New York",
            "destination": "Los Angeles",
            "departure_time": "2024-12-01T14:00:00",
            "price": 200.0
        })

    def test_no_flights(self):
        from_city = "New York"
        to_city = "Los Angeles"
        self.db_mock.query().filter().all.return_value = []
        result = create_rectangles(from_city, to_city, self.db_mock)
        self.assertEqual(result, [])
