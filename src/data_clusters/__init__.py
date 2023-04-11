from pymongo import MongoClient
from pymongo.collection import Collection
import ssl
from src.data_clusters.configuration.server_vars import server


atlas_uri: str = "mongodb+srv://{mongo_user}:{mongo_pass}@{mongo_hostname}.mongodb.net/{mongo_clustername}?retryWrites=true&w=majority".format(
    **{
        "mongo_user": server.get("mongo_user"),
        "mongo_pass": server.get("mongo_pass"),
        "mongo_hostname": server.get("mongo_hostname"),
        "mongo_clustername": server.get("mongo_clustername"),
    }
)

client: MongoClient = MongoClient(
    atlas_uri, ssl=True, ssl_cert_reqs=ssl.CERT_NONE
)  # ? connecting to mongo atlas

db = client.get_database("bot-main")  # ? database

# ? collections
confessions_blocks_coll: Collection = db.get_collection("confessions_blocks")
confessions_msgs_coll: Collection = db.get_collection("confessions_msgs")
mutes_coll: Collection = db.get_collection("mutes")
