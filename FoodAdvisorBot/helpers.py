#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime, timedelta
from time import sleep

from InstagramAPI import InstagramAPI

from . import config
from .MySQLConnector import MySQLConnector

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'


def log(message):
    print('[%s] %s' % (datetime.now().strftime(DATETIME_FORMAT), message))


def wait_for(seconds):
    dt = datetime.now() + timedelta(seconds=seconds)
    log('Resting for %.2f seconds until %s' % (seconds, dt.strftime(DATETIME_FORMAT)))
    sleep(seconds)


def get_media_by_users():
    with MySQLConnector() as db:
        users = db.select_users()
    MIN_TIMESTAMP = (datetime.now() - timedelta(days=365)).timestamp()

    db = MySQLConnector()
    for i, user in enumerate(users):
        if user['updated']:
            continue
        more_available = True
        media_max_id = ''
        count = 0
        while more_available:
            try:
                api.getUserFeed(user['id_user'], media_max_id)
            except:
                continue
            more_available = api.LastJson['more_available']
            media_max_id = api.LastJson['next_max_id']
            if api.LastResponse.status_code != 200:
                continue
            items = api.LastJson['items']
            for i, media in enumerate(items):
                if db.is_media_updated(media['id']):
                    continue
                if media['taken_at'] < MIN_TIMESTAMP:
                    more_available = False
                    break
                if 'location' not in media:
                    if user['latitude'] is None:
                        continue
                    media['location'] = {
                        'lat': user['latitude'],
                        'lng': user['longitude']
                    }
                db.insert_media(media)
                count += 1
                log('%s. Inserted media: %d/%d (total: %d)' %
                    (user['username'], i, len(items), count))

                has_more_comments = True
                comment_max_id = ''
                while has_more_comments:
                    api.getMediaComments(media['id'], comment_max_id)
                    if 'comments_disabled' in api.LastJson:
                        break
                    has_more_comments = api.LastJson['has_more_comments']
                    if has_more_comments:
                        comment_max_id = json.loads(api.LastJson['next_max_id'])['server_cursor']
                    for comment in api.LastJson['comments']:
                        db.insert_comment(media['id'], comment)
                db.set_media_updated(media['id'])
            wait_for(2)
        db.set_user_updated(user['id_user'])
    db.close()


def get_media_by_tags(tags):
    for tag in tags:
        pass


def insert_users_to_db(usernames=None):
    if usernames is None:
        usernames = data['usernames']
    username_ids = []
    db = MySQLConnector()
    for i, username in enumerate(usernames):
        log('Seaching for users: %d/%d' % (i, len(data['usernames'])))
        api.searchUsername(username)
        if api.LastResponse.status_code != 200:
            log('User %s not found' % username)
            continue
        db.insert_user(api.LastJson['user'])
        username_ids.append(api.LastJson['user']['pk'])
        if i % 20 == 19:
            wait_for(10)
    db.close()


__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
api = InstagramAPI(config.LOGIN, config.PASSWORD)
api.login()
with open(os.path.join(__location__, 'data.json'), 'r', encoding='utf-8') as f:
    data = json.load(f)
