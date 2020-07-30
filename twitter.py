import twint
import tweepy
from collections import Counter
from Information import InfoBox
from uuid import uuid4
from datetime import datetime


class TwitterNode(InfoBox):
    def __init__(self, params={}):
        super().__init__()
        self.count_all = Counter()
        self.tweepy_api = None
        if False in [p in params for p in
                             ['consumer_key', 'consumer_secret', 'access_token', 'access_token_secret']]:
            pass
        else:
            self.tweepy_api = self.get_tweepy_api(consumer_key=params.get('consumer_key'),
                                                  consumer_secret=params.get('consumer_secret'),
                                                  access_token=params.get('access_token'),
                                                  access_token_secret=params.get('access_token_secret')
                                                  )

    @staticmethod
    def get_tweepy_api(consumer_key, consumer_secret, access_token, access_token_secret):
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        return api

    def is_tweepy_connected(self):
        return self.tweepy_api is not None

    def get_user(self, screen_name: str):
        return self.tweepy_api.get_user(screen_name=screen_name)._json

    @staticmethod
    def get_followings(username, limit=150):
        c = twint.Config()
        c.Username = username
        c.Store_object = True
        c.Hide_output = True
        c.Limit = limit
        twint.run.Following(c)
        return twint.output.follows_list

    def get_retweeted_users(self, username):
        statuses = [
                        s for s in tweepy.Cursor(
                                                 self.tweepy_api.user_timeline,
                                                 screen_name=username, count=100,
                                                 tweet_mode='extended', retweet_mode='extended').items()
        ]
        return statuses

    def get_favored_users(self, user_id, limit=100):
        statuses = [s for s in tweepy.Cursor(
                                             self.tweepy_api.favorites, id=user_id,
                                             result_type="recent", tweet_mode="extended",
                                             retweet_mode='extended', count=limit).items()
                    ]
        return statuses

    def check_friendship(self, user_tuple, other_user):

        friendship = self.tweepy_api.show_friendship(source_screen_name=other_user[0], target_screen_name=user_tuple[0])
        if friendship[0].following:
            return True
        else:
            return False


class Network:
    def __init__(self, base_accounts: list):
        self.network_id = str(uuid4())
        self.base_accounts = base_accounts  # list of twitter ids (str) or User-Objects that are base of new network


class User:
    def __init__(self, user_id: str, last_time_checked: datetime = None):
        self.user_id = user_id

        self.last_time_checked = last_time_checked

    def set_network_score(self, network_id: str, score: int):
        assert type(score) == int
        self.network_scores[network_id] = score

    def get_network_score(self, network_id: str):
        return self.network_scores.get(network_id)

    def is_in_network(self, network_id: str):
        return type(self.network_scores.get(network_id)) == int
