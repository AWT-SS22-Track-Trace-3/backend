from passlib.context import CryptContext
from click import pass_context
import pymongo

from ..constants import *

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# pymongo connecting to mongoDB
client = pymongo.MongoClient(
    host=MONGO['DOCKER'],
    port=MONGO['PORT'],
    username=MONGO['USERNAME'],
    password=MONGO['PASSWORD']
)
users = client["Authentication"]["users"]

fake_user = {
    "username": "Admin",
    "password": "test",
    "company": "Bayer",
    "address": "Test Straße 1",
    "access_lvl": 4
}

class Authentication:

#<------------------------>
#     Authentification
#<------------------------>

    def is_user(username, password):
        return True
        #hashed_password = pass_context.hash(password)
        #if users.find_one( { "username": username, "password": hashed_password }, { "password": 0 } ).count() > 0:
        #    return True
        #return False

    def get_user(username):
        return fake_user
        #result = users.find_one( { "username": username }, { "password": 0 } )
        #if result.count() > 0:
        #    return result
        #return None


#<------------------------>
#        API-Signup
#<------------------------>

    def is_username(username):
        if users.find_one( { "username": username } ).count() > 0:
            return { "is_username": True }
        return { "is_username": False }

    def signup(new_user):
        new_user["password"] = pass_context.hash(new_user["password"])
        return users.insert_one(new_user)
