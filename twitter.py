from __future__ import annotations

from abc import ABC

import twint
import tweepy
from collections import Counter
from Information import InfoBox
from uuid import uuid4
from datetime import datetime
from typing import Dict, Union
import logging
import os



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


class Tweet(InfoBox):
    def __init__(self, raw: dict):
        super().__init__()
        self.raw = raw

    def __dict__(self) -> dict:
        if self.raw is not None:
            return super().__dict__().update({'raw': self.raw})
        else:
            return super().__dict__()


class User(InfoBox):
    def __init__(self, raw: dict = None):
        super().__init__()
        self.raw = raw

    def __dict__(self) -> dict:
        if self.raw is not None:
            return super().__dict__().update({'raw': self.raw})
        else:
            return super().__dict__()

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
        u = User(raw=d)
        object_id = d.get(id)
        assert object_id is not None
        u.id = d.get(id)
        return u

    def make_restored_state(self, dt: datetime) -> InfoBox:
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
                    d = InfoBox.undo(d, undo_list=undo_list)
            return User.from_raw_data(d)

    def get(self, value):
        if self.raw is not None:
            return self.raw.get(value)

UserDict = Dict[str, User]
TweetDict = Dict[str, Tweet]
NetworkDict = Dict[str, Network]


class TwitterDB(InfoBox):    # Holds all information
    def __init__(self, users: UserDict = None, tweets: TweetDict = None, networks: NetworkDict = None, params: dict = None):
        super().__init__()
        self.users = users
        self.tweets = tweets
        self.networks = networks
        self.twitter_api = TwitterApi(params=params)

    def update_user(self, user: User):
        if user.get('user_id') in self.users:
            self.users[user.user_id].update(user)
        else:
            self.users.update({user.user_id: user})

    @staticmethod
    def from_files(file_paths: list) -> TwitterDB:
        users = {}
        tweets = {}

        for path in file_paths:
            file = TwitterDB.load_json(path)
            if 'error' in file['user']:
                user_name = path.split("\\")[-1][:-5]
                users.update({user_name: User(raw=file['user'])})
            else:
                user_id = file['user']['id_str']
                user_data = file['user']
                favorites = file['favs']
                network = file['network']
                user_tweets = file['tweets']

                user_data.update({'followings': file['followings']})
                user_data.update({'favorites': favorites.keys()})
                user_data.update({'network': network})

                users.update({user_id: user_data})
                tweets.update({key: Tweet(raw=val) for key, val in user_tweets.items()})
                tweets.update({key: Tweet(raw=val) for key, val in favorites.items()})
        return TwitterDB(users=users, tweets=tweets)

    @staticmethod
    def from_folder(folder_path) -> TwitterDB:
        if os.path.exists(folder_path):
            paths_list = [os.path.join(folder_path, f) for f in os.listdir(folder_path)]
            return TwitterDB.from_files(paths_list)
        else:
            raise FileNotFoundError
        """
        Deprecated soon, for importing old format
        :param file_path: 
        :return: 
        """
        return TwitterDB()

    def get_user(self, user_name) -> Union[User, None]:
        for u in self.users.values():
            if u.get('username') == user_name:
                return u
        return None





if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    parameters = TwitterApi.load_params(file_path='C:\\Users\\Nicolas Schilling\\Twitter\\params.json')
    tw_db = TwitterDB.from_folder("C:\\Users\\Nicolas Schilling\\Documents\\DATA_IBD_final\\Data")
    u = tw_db.get_user("ibdeutschland")
    print(u.raw.keys())