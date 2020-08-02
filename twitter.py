from __future__ import annotations
import twint
import tweepy
from collections import Counter
from Information import InfoBox
from uuid import uuid4
from datetime import datetime
from typing import Dict, List
import logging
import json


twitter_token_params = ['consumer_key', 'consumer_secret', 'access_token', 'access_token_secret']


class TwitterApi(InfoBox):
    def __init__(self, params: dict = None):
        super().__init__()
        self.count_all = Counter()
        self.tweepy_api = None
        if not self.twitter_token_is_valid(params):
            logging.debug("Tweepy not connected")
        else:
            self.tweepy_api = self.get_tweepy_api(consumer_key=params.get('consumer_key'),
                                                  consumer_secret=params.get('consumer_secret'),
                                                  access_token=params.get('access_token'),
                                                  access_token_secret=params.get('access_token_secret')
                                                  )
            logging.debug("Tweepy connected")

    @staticmethod
    def twitter_token_is_valid(params):
        if type(params) != dict:
            return False
        return False not in [i in params for i in twitter_token_params]

    @staticmethod
    def load_params(file_path):
        file = InfoBox.load_json(file_path)
        print(file)
        assert TwitterApi.twitter_token_is_valid(file)
        return file

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
    def __init__(self, name: str, base_accounts: list):
        """
        Contains metadata of all affiliation-scores connected to given base_accounts with timestamp
        :param base_accounts:
        """
        self.network_id = str(uuid4())
        self.name = name
        self.base_accounts = base_accounts  # list of twitter ids (str) or User-Objects that are base of new network


UndoQueue = Dict[datetime, List[callable]]  # Contains dates with all undo information to restore a past state


class User:
    def __init__(self, user_id: str, undo_information: UndoQueue = None):
        self.user_id = user_id
        self.likes = []
        if undo_information is None:
            self.undo_information = dict()
        else:
            self.undo_information = undo_information

    def __dict__(self) -> dict:
        raise NotImplementedError

    def update(self, user: User):
        """
        :param user:
        :return:

        Updates all new information to raw-dict and stores diff as undo_information
        ToDo: Implement recursive diff-searcher that returns UndoQueue
        """
        raise NotImplementedError

    def calculate_affiliation(self, other_user: User) -> float:

        """
        :param other_user:
        :return:

        returns float between 0 and 1
        where 1 means the accounts follow each other, are friends and
        every tweet is a retweet or contains a mention of the other
        """
        raise NotImplementedError

    @staticmethod
    def from_dict(d: dict) -> User:   # import json status from Twitter directly
        raise NotImplementedError

    @staticmethod
    def from_raw_data(d: dict) -> User:
        raise NotImplementedError

    @staticmethod
    def undo(d: dict, undo_list: List[callable]) -> dict:
        raise NotImplementedError

    def make_restored_user(self, dt: datetime) -> User:
        """
        Returns the restored User from a given timestamp
        :param dt:
        :return:
        """
        if dt not in self.undo_information:
            raise ValueError("Timestamp not in Undo-Queue")
        else:
            d = self.__dict__()
            for timestamp, undo_list in self.undo_information:
                if timestamp <= dt:
                    d = User.undo(d, undo_list=undo_list)
            return User.from_raw_data(d)


UserDict = Dict[str, User]
NetworkDict = Dict[str, Network]


class TwitterDB(InfoBox):    # Holds all information
    def __init__(self, users: UserDict = None, networks: NetworkDict = None, params: dict = None):
        super().__init__()
        self.users = users
        self.networks = networks
        self.twitter_api = TwitterApi(params=params)

    def update_user(self, user: User):
        if user.user_id in self.users:
            self.users[user.user_id].update(user)
        else:
            self.users.update({user.user_id: user})


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    parameters = TwitterApi.load_params(file_path='C:\\Users\\Nicolas Schilling\\Twitter\\params.json')
    tw_db = TwitterDB(params=parameters)

    try:
        user = tw_db.twitter_api.get_user(screen_name="@AngelaMerkel")
        TwitterApi.save_json({'user': user}, "user.json")

    except:
        pass

    try:
        favored = tw_db.twitter_api.get_favored_users(user['id_str'])
        TwitterApi.save_json({'favored': user}, "favored.json")

    except:
        pass

    try:
        followings = tw_db.twitter_api.get_followings("@AngelaMerkel")
        TwitterApi.save_json({'followings': user}, "followings.json")

    except:
        pass

    try:

        retweeted = tw_db.twitter_api.get_retweeted_users("@AngelaMerkel")
        TwitterApi.save_json({'retweeted': user}, "retweeted.json")

    except:
        pass


    print(user)
