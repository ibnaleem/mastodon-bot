import json
from mastodon import Mastodon

with open("config.json", "r") as f:
    token = json.load(f)


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


class MyClient:
    def __init__(self, client):
        self.client = client
    
    def login_check(self):
        if self.preferences():
            print("LOGGED INTO MASTODON")
        else:
            print("FAILED TO LOGIN TO MASTODON") 
    
    @check_followers
    def follow(self, follower_id=None):
        while follower_id:
            self.account_follow(id=follower_id)
            follower_id = None 


if __name__ == "__main__":
    client = Mastodon(access_token = str(token["token"]), api_base_url="https://mastodon.social/")
    MyClient.login_check(client)

    while True:
        MyClient.follow(client)
