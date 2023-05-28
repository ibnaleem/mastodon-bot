import json
from mastodon import Mastodon

with open("config.json", "r") as f:
    token = json.load(f)

client = Mastodon(access_token = str(token["token"]), api_base_url="https://mastodon.social/")

def login_check():
    if client.preferences():
        print("LOGGED INTO MASTODON")
    else:
        print("FAILED TO LOGIN TO MASTODON")

if __name__ == "__main__":
    login_check()
