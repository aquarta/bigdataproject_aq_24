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

    collection_name = "email_actions"

    def __init__(self, email_action_obj) -> None:
        """ The constructor for EmailAction class.

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
        collection_name = dbname[self.collection_name]
        res = collection_name.insert_one(self.email_action_obj)
        self.email_action_obj['_id'] = str(res.inserted_id)
        return  self.email_action_obj

    def get_all(self):
        collection_name = dbname[self.collection_name]
        res = []
        for x in collection_name.find():
            x['_id'] = str(x['_id'])
            res.append(x) 
        
        return res

    def update(self, oid, obj):
        collection_name = dbname[self.collection_name]

        query = { "_id": ObjectId(oid) }
        newvalues = { "$set": obj }

        res = collection_name.update_one(query, newvalues)

        after_query = { "_id": res.upserted_id }
        print(res.upserted_id)
        res = collection_name.find(after_query)
        print(res)
        return json_util.loads(json_util.dumps(res))


    def delete(self, oid, obj):
        collection_name = dbname[self.collection_name]

        query = { "_id": ObjectId(oid) }
        newvalues = { "$set": obj }

        res = collection_name.delete_one(query)
       
        return 


class HttpAction( Model):
    """ HttpAction's model class.

    
    """
    collection_name = "http_actions"

    def __init__(self, http_action_obj) -> None:
        """ The constructor for HttpAction class.

        """

        self.http_action_obj = http_action_obj
    
    
    def serialize(self) -> dict:
        """Serialize the object attributes values into a dictionary.

        Returns:
           dict: a dictionary containing the attributes values
        """

        data = self.http_action_obj

        return data


    def add(self):
        collection_name = dbname[self.collection_name]
        res = collection_name.insert_one(self.http_action_obj)
        self.http_action_obj['_id'] = str(res.inserted_id)
        return  self.http_action_obj

    def get_all(self):
        collection_name = dbname[self.collection_name]
        res = []
        for x in collection_name.find():
            x['_id'] = str(x['_id'])
            res.append(x) 
        
        return res

    def update(self, oid, obj):
        collection_name = dbname[self.collection_name]

        query = { "_id": ObjectId(oid) }
        newvalues = { "$set": obj }

        res = collection_name.update_one(query, newvalues)

        after_query = { "_id": res.upserted_id }
        print(res.upserted_id)
        res = collection_name.find(after_query)
        print(res)
        return json_util.loads(json_util.dumps(res))


    def delete(self, oid):
        collection_name = dbname[self.collection_name]

        query = { "_id": ObjectId(oid) }

        res = collection_name.delete_one(query)

        return 