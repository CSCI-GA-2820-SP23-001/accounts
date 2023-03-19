"""
Test cases for Account Model

"""
import os
import logging
import unittest
from service.models import Account, DataValidationError, db
from service import app
from tests.factories import AccountFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)

######################################################################
#  Account   M O D E L   T E S T   C A S E S
######################################################################
class TestAccount(unittest.TestCase):
    """ Test Cases for Account Model """

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Account.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Account).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_account(self):
        """It should Create a account and assert that it exists"""
        account = Account(
            name="Joe Jones", 
            address="123 Main Street, Anytown USA", 
            email="jones@email.com", 
            phone_number="555-1212"
        )
        self.assertEqual(str(account), "<Account Joe Jones id=[None]>")
        self.assertTrue(account is not None)
        self.assertEqual(account.id, None)
        self.assertEqual(account.name, "Joe Jones")
        self.assertEqual(account.address, "123 Main Street, Anytown USA")
        self.assertEqual(account.email, "jones@email.com")
        self.assertEqual(account.phone_number, "555-1212")

    def test_add_a_account(self):
        """It should Create a account and add it to the database"""
        accounts = Account.all()
        self.assertEqual(accounts, [])
        account = Account(
            name="Joe Jones", 
            address="123 Main Street, Anytown USA", 
            email="jones@email.com", 
            phone_number="555-1212"
        )
        self.assertTrue(account is not None)
        self.assertEqual(account.id, None)
        account.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(account.id)
        accounts = Account.all()
        self.assertEqual(len(accounts), 1)

    def test_read_a_account(self):
        """It should Read a Account"""
        account = AccountFactory()
        logging.debug("Account: %s", account)
        account.id = None
        account.create()
        self.assertIsNotNone(account.id)
        # Fetch it back
        found_account = Account.find(account.id)
        self.assertEqual(found_account.id, account.id)
        self.assertEqual(found_account.name, account.name)
        self.assertEqual(found_account.address, account.address)
        self.assertEqual(found_account.email, account.email)
        self.assertEqual(found_account.phone_number, account.phone_number)

    def test_update_a_account(self):
        """It should Update a Account"""
        account = AccountFactory()
        logging.debug(account)
        account.id = None
        account.create()
        logging.debug(account)
        self.assertIsNotNone(account.id)
        # Change it an save it
        account.address = "unknown"
        original_id = account.id
        account.update()
        self.assertEqual(account.id, original_id)
        self.assertEqual(account.address, "unknown")
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        accounts = Account.all()
        self.assertEqual(len(accounts), 1)
        self.assertEqual(accounts[0].id, original_id)
        self.assertEqual(accounts[0].address, "unknown")

    def test_update_no_id(self):
        """It should not Update a Account with no id"""
        account = AccountFactory()
        logging.debug(account)
        account.id = None
        self.assertRaises(DataValidationError, account.update)

    def test_delete_a_account(self):
        """It should Delete a Account"""
        account = AccountFactory()
        account.create()
        self.assertEqual(len(Account.all()), 1)
        # delete the account and make sure it isn't in the database
        account.delete()
        self.assertEqual(len(Account.all()), 0)

    def test_list_all_accounts(self):
        """It should List all Accounts in the database"""
        accounts = Account.all()
        self.assertEqual(accounts, [])
        # Create 5 Accounts
        for _ in range(5):
            account = AccountFactory()
            account.create()
        # See if we get back 5 accounts
        accounts = Account.all()
        self.assertEqual(len(accounts), 5)

    def test_serialize_a_account(self):
        """It should serialize a Account"""
        account = AccountFactory()
        data = account.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], account.id)
        self.assertIn("name", data)
        self.assertEqual(data["name"], account.name)
        self.assertIn("address", data)
        self.assertEqual(data["address"], account.address)
        self.assertIn("email", data)
        self.assertEqual(data["email"], account.email)
        self.assertIn("phone_number", data)
        self.assertEqual(data["phone_number"], account.phone_number)

    def test_deserialize_a_account(self):
        """It should de-serialize a Account"""
        data = AccountFactory().serialize()
        account = Account()
        account.deserialize(data)
        self.assertNotEqual(account, None)
        self.assertEqual(account.id, None)
        self.assertEqual(account.name, data["name"])
        self.assertEqual(account.address, data["address"])
        self.assertEqual(account.email, data["email"])
        self.assertEqual(account.phone_number, data["phone_number"])

    def test_deserialize_missing_data(self):
        """It should not deserialize a Account with missing data"""
        fake_account = AccountFactory()
        data = fake_account.serialize()
        del data["name"]
        account = Account()
        self.assertRaises(DataValidationError, account.deserialize, data)

    def test_deserialize_bad_data(self):
        """It should not deserialize bad data"""
        data = "this is not a dictionary"
        account = Account()
        self.assertRaises(DataValidationError, account.deserialize, data)

    def test_find_account(self):
        """It should Find a Account by ID"""
        accounts = AccountFactory.create_batch(5)
        for account in accounts:
            account.create()
        logging.debug(accounts)
        # make sure they got saved
        self.assertEqual(len(Account.all()), 5)
        # find the 2nd account in the list
        account = Account.find(accounts[1].id)
        self.assertIsNot(account, None)
        self.assertEqual(account.id, accounts[1].id)
        self.assertEqual(account.name, accounts[1].name)
        self.assertEqual(account.email, accounts[1].email)
        self.assertEqual(account.phone_number, accounts[1].phone_number)

    def test_find_or_404_found(self):
        """It should Find or return 404 not found"""
        accounts = AccountFactory.create_batch(3)
        for account in accounts:
            account.create()

        account = Account.find_or_404(accounts[1].id)
        self.assertIsNot(account, None)
        self.assertEqual(account.id, accounts[1].id)
        self.assertEqual(account.name, accounts[1].name)
        self.assertEqual(account.email, accounts[1].email)
        self.assertEqual(account.phone_number, accounts[1].phone_number)

