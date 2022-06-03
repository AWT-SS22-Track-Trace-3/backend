from click import pass_context
import pymongo
from passlib.context import CryptContext

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

#fake_user = {
#    "username": "Pharma",
#    "password": "test",
#    "company": "Bayer",
#    "address": "Test Straße 1",
#    "access_lvl": 1
#}

class Authentication:

#<------------------------>
#     Authentification
#<------------------------>

    def is_user(username, password):
        #return True
        hashed_password = pass_context.hash(password)
        if users.find_one( { "username": username, "password": hashed_password }, { "password": 0 } ) > 0:
            return True
        return False

    def get_user(username):
        #return fake_user
        return users.find_one( { "username": username }, { "password": 0 } )


#<------------------------>
#        API-Signup
#<------------------------>

    def is_username(username):
        if users.find_one( { "username": username } ) > 0:
            return { "is_username": True }
        return { "is_username": False }

    def signup(new_user):
        new_user["password"] = pass_context.hash(new_user["password"])
        return users.insert_one(new_user)
