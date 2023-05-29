import json, asyncio, datetime
from mastodon import Mastodon

with open("config.json", "r") as f:
    config = json.load(f)

client = Mastodon(access_token = str(config["token"]), api_base_url="https://mastodon.social/")

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
                break

        return func(self, *args, **kwargs)

    return wrapper

def check_unfollowers(func):
    def wrapper(self, *args, **kwargs):
        following_list = self.account_following(self.me())
        followers_set = set(follower["id"] for follower in self.account_followers(self.me()))

        for following in following_list:
            if following["id"] not in followers_set:
                kwargs['following_id'] = following["id"]
                break
            pass

        return func(self, *args, **kwargs)

    return wrapper

def check_trending_hashtags(func):
    def wrapper(self, *args, **kwargs):
        hashtags = self.trending_tags()
        names = hashtags["name"]
        histories = hashtags["history"]
        for name, history in zip(names, histories):
            kwargs["message"] = f"Trending Hastags:\n#{name} {history['uses']} uses on {history['date']} from {history['accounts']} accounts"

        return func(self, *args, **kwargs)

    return wrapper

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
    def unfollow(self, following_id=None):
        while following_id:
            self.account_unfollow(id=following_id)
            following_id = None

    @check_trending_hashtags
    def toot_hashtags(self, message=None):
        if message:
            self.toot(message)
            asyncio.sleep(3600)

if __name__ == "__main__":
    MyClient.login_check()

    while True:
        MyClient.follow(client)
        MyClient.unfollow(client)
        MyClient.toot_hashtags(client)
