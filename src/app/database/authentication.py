from passlib.context import CryptContext
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
users = client["track-trace"]["users"]


class Authentication:

    # <------------------------>
    #     Authentification
    # <------------------------>

    def is_user(username, password):
        user = users.find_one({"username": username}, {
                              "password": 1, "access_lvl": 1})
        if user is not None:
            if pwd_context.verify(password, user["password"]):
                return [True, user["access_lvl"]]
        return [False, None]

    def get_user(username):
        result = users.find_one({"username": username}, {"password": 0})
        if result is not None:
            return result
        return None


# <------------------------>
#        API-Signup
# <------------------------>


    def is_username(username):
        if users.find_one({"username": username}) is not None:
            return {"is_username": True}
        return {"is_username": False}

    def signup(new_user):
        if users.find_one({"username": new_user["username"]}) is not None:
            return False

        new_user["password"] = pwd_context.hash(new_user["password"])

        return users.insert_one(new_user).acknowledged
