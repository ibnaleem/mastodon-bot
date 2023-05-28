import json
from mastodon import Mastodon

with open("config.json", "r") as f:
    token = json.load(f)

client = Mastodon(access_token = str(token["token"]), api_base_url="https://mastodon.social/")

class MyClient:
    def __init__(self, client):
        self.client = client
    
    def login_check(self):
        if self.preferences():
            print("LOGGED INTO MASTODON")
        else:
            print("FAILED TO LOGIN TO MASTODON")
    
    def check_followers(self, func):
        def wrapper(*args, **kwargs):
            # Fetch notifications for the logged-in user
            notifications = self.notifications()

            # Iterate through the notifications to check for follow events
            for notification in notifications:
                if notification['type'] == 'follow':
                    # User has followed you
                    follower_id = notification['account']['id']
                    follower_username = notification['account']['username']
                    func(follower_id, follower_username, *args, **kwargs)
                    break

        return wrapper


if __name__ == "__main__":
    MyClient.login_check(client)
