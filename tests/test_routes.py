"""
TestAccount API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch
from service import app
from service.models import db, init_db, Account
from service.common import status  # HTTP Status Codes
from tests.factories import AccountFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/accounts"

######################################################################
#  T E S T   C A S E S
######################################################################
class TestAccountServer(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Account).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        db.session.remove()

    def _create_accounts(self, count):
        """Factory method to create accounts in bulk"""
        accounts = []
        for _ in range(count):
            test_account = AccountFactory()
            response = self.client.post(BASE_URL, json=test_account.serialize())
            self.assertEqual(
                response.status_code, status.HTTP_201_CREATED, "Could not create test account"
            )
            new_account = response.get_json()
            test_account.id = new_account["id"]
            accounts.append(test_account)
        return accounts

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ It should call the home page """
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_create_account(self):
        """It should Create a new Account"""
        test_account = AccountFactory()
        logging.debug("Test Account: %s", test_account.serialize())
        response = self.client.post(BASE_URL, json=test_account.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_account = response.get_json()
        self.assertEqual(new_account["name"], test_account.name)
        self.assertEqual(new_account["address"], test_account.address)
        self.assertEqual(new_account["email"], test_account.email)
        self.assertEqual(new_account["phone_number"], test_account.phone_number)

        # TODO: Uncomment after get_accounts is implemented

        # Check that the location header was correct
        # response = self.client.get(location)
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # new_account = response.get_json()
        # self.assertEqual(new_account["name"], test_account.name)
        # self.assertEqual(new_account["address"], test_account.address)
        # self.assertEqual(new_account["email"], test_account.email)
        # self.assertEqual(new_account["phone_number"], test_account.phone_number)

    def test_create_account_no_data(self):
        """It should not Create a Account with missing data"""
        response = self.client.post(BASE_URL, json={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_account_no_content_type(self):
        """It should not Create a Account with no content type"""
        response = self.client.post(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_account_wrong_content_type(self):
        """It should not Create a Account with the wrong content type"""
        response = self.client.post(BASE_URL, data="hello", content_type="text/html")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_method_not_allowed(self):
        """It should not call an endpoint by a method that is not allowed"""
        response = self.client.put(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
