"""
Models for Account

All of the models are stored in this module
"""
import logging
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


# Function to initialize the database
def init_db(app):
    """ Initializes the SQLAlchemy app """
    Account.init_db(app)


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """


class Account(db.Model):
    """
    Class that represents a Account
    """

    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63), nullable=False)
    address = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(63), nullable=False)
    phone_number = db.Column(db.String(32))

    def __repr__(self):
        return f"<Account {self.name} id=[{self.id}]>"

    def create(self):
        """
        Creates a Account to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # pylint: disable=invalid-name
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a Account to the database
        """
        logger.info("Saving %s", self.name)
        if not self.id:
            raise DataValidationError("Update called with empty ID field")
        db.session.commit()

    def delete(self):
        """ Removes a Account from the data store """
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    def serialize(self) -> dict:
        """Serializes a Account into a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "email": self.email,
            "phone_number": self.phone_number
        }

    def deserialize(self, data):
        """
        Deserializes a Account from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            self.address = data["address"]
            self.email = data["email"]
            self.phone_number = data.get("phone_number")
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError("Invalid pet: missing " + error.args[0]) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid pet: body of request contained bad or no data " + str(error)
            ) from error
        return self

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the Accounts in the database """
        logger.info("Processing all Accounts")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """ Finds a Account by it's ID """
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_or_404(cls, pet_id: int):
        """Find a Pet by it's id
        :param pet_id: the id of the Pet to find
        :type pet_id: int
        :return: an instance with the pet_id, or 404_NOT_FOUND if not found
        :rtype: Pet
        """
        logger.info("Processing lookup or 404 for id %s ...", pet_id)
        return cls.query.get_or_404(pet_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all Accounts with the given name

        Args:
            name (string): the name of the Accounts you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)
