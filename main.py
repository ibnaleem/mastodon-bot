import json
from mastodon import Mastodon
from pymongo import MongoClient
from pymongo.server_api import ServerApi

with open("config.json", "r") as f:
    config = json.load(f)

client = Mastodon(access_token = str(config["token"]), api_base_url="https://mastodon.social/")
mongoClient = MongoClient(str(config["uri"]), server_api=ServerApi('1'))
db = mongoClient.mastodon_db
followers_collection = db.followers

def check_followers(func):
    def wrapper(self, *args, **kwargs):
        # Fetch notifications for the logged-in user
        notifications = self.notifications()

        # Iterate through the notifications to check for follow events
        for notification in notifications:
            if notification['type'] == 'follow':
                # User has followed you
                follower_id = notification['account']['id']
                kwargs['follower_id'] = follower_id
                store_follower_id(follower_id=follower_id)
                break

        return func(self, *args, **kwargs)

    return wrapper

def store_follower_id(follower_id):
    doc = followers_collection.find_one({"account": int(follower_id)})

    if doc is None:
        followers_collection.insert_one({"account": int(follower_id)})
    pass

def check_unfollowers(func):
    def wrapper(self, *args, **kwargs):
        try:
            follower_ids = retrieve_follower_ids()
            for follower_id in follower_ids:
                follower = self.account_followers(follower_id)
                if not follower:
                    following = self.account_following(follower_id)

                    if following:
                        kwargs['follower_id'] = follower_id
                        remove_follower_id(follower_id)
                        break
                    pass

        except sqlite3.OperationalError:
            pass

        return func(self, *args, **kwargs)

    return wrapper

def retrieve_follower_ids():
    cursor = followers_collection.find({}, {"account": 1})
    
    ids = [doc["account"] for doc in cursor]
    return ids


def remove_follower_id(follower_id):
    doc = followers_collection.find_one({"account": int(follower_id)})

    if doc is not None:
        followers_collection.delete_one({"account": int(follower_id)})
    pass

class MyClient:
    def __init__(self, client):
        self.client = client
    
    @staticmethod
    def login_check():
        if client.preferences():
            print("LOGGED INTO MASTODON")
        else:
            print("FAILED TO LOGIN TO MASTODON") 
    
    @check_followers
    def follow(self, follower_id=None):
        while follower_id:
            self.account_follow(id=follower_id)
            follower_id = None

    @check_unfollowers
    def unfollow(self, follower_id=None):
        while follower_id:
            self.account_unfollow(id=follower_id)
            follower_id = None 


if __name__ == "__main__":
    MyClient.login_check()

    while True:
        MyClient.follow(client)
        MyClient.unfollow(client)
