from pycountry import countries
from pydantic import BaseModel
from typing import Any
import pymongo

from ..routers.authentication import User
from ..constants import *

# pymongo connecting to mongoDB
client = pymongo.MongoClient(
    host=MONGO['DOCKER'],
    port=MONGO['PORT'],
    username=MONGO['USERNAME'],
    password=MONGO['PASSWORD']
)
incidents = client["track-trace"]["incidents"]

# this database persisist security incidents in the supply chain

class Incidents:

    class Incident(BaseModel):
        type: str
        information: Any
        user: User

    def report(incident: Incident):
        return incidents.insert_one(incident).acknowledged

    def heatmap_data():
        heatmap = [ ]
        for c in countries:
            heatmap.append( { c.alpha_2: incidents.count_documents({ "user.country": c.alpha_2 }) } )

        return heatmap
        