import json, sqlite3
from mastodon import Mastodon

with open("config.json", "r") as f:
    token = json.load(f)

client = Mastodon(access_token = str(token["token"]), api_base_url="https://mastodon.social/")


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

def store_follower_id(follower_id):
    # Connect to the SQLite database
    conn = sqlite3.connect('followers.db')
    cursor = conn.cursor()

    # Create a table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS followers
                      (id INTEGER PRIMARY KEY)''')

    # Insert the follower_id into the table
    cursor.execute("INSERT INTO followers (id) VALUES (?)", (follower_id,))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def check_unfollowers(func):
    def wrapper(self, *args, **kwargs):

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

        return func(self, *args, **kwargs)

    return wrapper

def retrieve_follower_ids():
    # Connect to the SQLite database
    conn = sqlite3.connect('followers.db')
    cursor = conn.cursor()

    # Retrieve all follower IDs from the table
    cursor.execute("SELECT id FROM followers")
    follower_ids = cursor.fetchall()

    # Close the connection
    conn.close()

    # Return the follower IDs as a list
    return [follower_id[0] for follower_id in follower_ids]

def remove_follower_id(follower_id):
    # Connect to the SQLite database
    conn = sqlite3.connect('followers.db')
    cursor = conn.cursor()

    # Delete the follower_id from the table
    cursor.execute("DELETE FROM followers WHERE id=?", (follower_id,))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

# - Store IDs in db
# - Check if the IDs in the Db are found in followers
# - Not found? Check following if ID is there
# - Found? Unfollow, else return

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

    @check_unfollowers
    def unfollow(self, follower_id=None):
        while follower_id:
            self.account_unfollow(id=follower_id)
            follower_id = None 


if __name__ == "__main__":
    MyClient.login_check(client)

    while True:
        MyClient.follow(client)
        MyClient.unfollow(client)
