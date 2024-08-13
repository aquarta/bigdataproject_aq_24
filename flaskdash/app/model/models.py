from database import get_database
from bson import json_util
import bson
from bson.objectid import ObjectId

DB = get_database()


dbname = get_database()


class Model:
    """The Model class declare the serialize() method that is
    supposed to serializes the model data. The Model's subclasses
    can provide a implementation of this method."""

    def serialize(self) -> dict:
        """Serialize the object attributes values into a dictionary."""

        return {}

    def remove_session(self):
        """Removes an object from the session its current session."""

        session = inspect(self).session
        if session:
            session.expunge(self)   


class EmailAction( Model):
    """ EmailAction's model class.

    
    """


    def __init__(self, email_action_obj) -> None:
        """ The constructor for User class.

        Parameters:
            username (str): User's username
            password (str): User's password
        """

        self.email_action_obj = email_action_obj
    
    
    def serialize(self) -> dict:
        """Serialize the object attributes values into a dictionary.

        Returns:
           dict: a dictionary containing the attributes values
        """

        data = self.email_action_obj

        return data


    def add(self):
        collection_name = dbname['email_actions']
        res = collection_name.insert_one(self.email_action_obj)
        self.email_action_obj['_id'] = str(res.inserted_id)
        return  self.email_action_obj

    def get_all(self):
        collection_name = dbname['email_actions']
        res = []
        for x in collection_name.find():
            x['_id'] = str(x['_id'])
            res.append(x) 
        
        return res

    def get_one(self, oid):
        [i for i in dbm.neo_nodes.find({"_id": ObjectId(oid)})]