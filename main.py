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
        messages = []
        unique_names = set()
        total_length = 0

        for tag in hashtags:
            name = tag["name"]
            if name in unique_names:
                continue  # Skip if the name has already been recorded
            unique_names.add(name)

            history = tag["history"]
            
            for entry in history:
                uses = entry["uses"]
                date = entry["day"].strftime("%Y-%m-%d")
                accounts = entry["accounts"]
                message = f"#{name} {uses} uses on {date} from {accounts} accounts"
                
                if total_length + len(message) <= 500:
                    messages.append(message)
                    total_length += len(message)

        kwargs["message"] = "Trending Hashtags:\n" + "\n".join(messages)
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

if __name__ == "__main__":
    MyClient.login_check()
    MyClient.toot_hashtags(client)

    while True:
        MyClient.follow(client)
        MyClient.unfollow(client)
