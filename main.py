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

if __name__ == "__main__":
    MyClient.login_check(client)
