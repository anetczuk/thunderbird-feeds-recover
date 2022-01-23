#!/usr/bin/env python3
#
# MIT License
#
# Copyright (c) 2020 Arkadiusz Netczuk <dev.arnet@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import os
import sys
import logging
import pprint
import datetime

import argparse
import glob
import configparser
import json
import feedparser

import requests
import requests_file

from _collections import defaultdict


script_dir = os.path.dirname(__file__)


logging.basicConfig(stream=sys.stdout,
                    level=logging.INFO)

_LOGGER = logging.getLogger(__name__)


FEEDS_DIR_NAME = "Feeds"
FEEDS_TRASH_PANE_DIR = "Feeds/Trash"


## =====================================================================


def read_file( file_path ):
    with open( file_path, "rb" ) as f:
        content = f.read()
        return content.decode(errors='replace')


def read_url( urlpath ):
    session = requests.Session()
    session.mount( 'file://', requests_file.FileAdapter() )
#     session.config['keep_alive'] = False
#     response = requests.get( urlpath, timeout=5 )
    response = session.get( urlpath, timeout=5 )
#     response = requests.get( urlpath, timeout=5, hooks={'response': print_url} )
    return response.text


## =====================================================================


def deduce_profile_path():
    user_home_dir = os.path.expanduser('~')
    thunderbird_config_dir = os.path.join( user_home_dir, ".thunderbird" )
    profiles_config_path = os.path.join( thunderbird_config_dir, "profiles.ini" )

    config = configparser.ConfigParser()
    config.read( profiles_config_path )

    for key in config:
        if "Profile" not in key:
            ## not profile section -- skip
            continue
        profile_dict = config[key]
        default_field = profile_dict.get( "Default", 0 )
        if not default_field:
            ## not default directory
            continue
        profile_dir = profile_dict.get( "Path", None )
        if profile_dir is None:
            continue
        profile_path = os.path.join( thunderbird_config_dir, profile_dir )
        return profile_path

    return None


def get_pane_path( file_path, feeds_path ):
    relPath = os.path.relpath( file_path, feeds_path )
    subPath = FEEDS_DIR_NAME + "/" + relPath
    subPath = subPath.replace( ".sbd", "" )
    subPath = subPath.replace( ".msf", "" )
    return subPath


def find_message_folder( message_id, feeds_path ):
    pathsList = glob.glob( feeds_path + "/**", recursive=True )
    retList = set()
    for fname in pathsList:
        if os.path.isfile(fname) is False:    # make sure it's a file, not a directory entry
            ## directory -- skip
            continue
        if fname.endswith('.msf') is False:
            ## not msf file -- skip
            continue
        if message_id in read_file( fname ):
            subPath = get_pane_path( fname, feeds_path )
            if FEEDS_TRASH_PANE_DIR in subPath:
                ## skip trash
                continue
            retList.add( subPath )
    return retList


## 'update_timestamp' is given in milliseconds
def create_feed_item( dest_panel_folder, feed_url, feed_title, feed_website_link, update_timestamp ):
    lastDate = datetime.datetime.utcfromtimestamp( update_timestamp / 1000 )
    _LOGGER.info( "creating feed item: %s %s %s %s %s",
                  dest_panel_folder, feed_url, feed_title, feed_website_link, lastDate )

    lastModStr = lastDate.strftime("%a, %d %b %Y %H:%M:%S GMT")

    ## encode space character
    dest_folder = dest_panel_folder.replace( " ", "%20" )

    ## corrupts names containing phrases like "C++"
    ##dest_folder = urllib.parse.quote( dest_panel_folder )

    content = {'destFolder': f'mailbox://nobody@{dest_folder}',
               'lastModified': lastModStr,
               # 'lastModified': 'Sat, 22 Jan 2022 00:34:48 GMT',
               'link': f'{feed_website_link}',
               'options': {'category': {'enabled': False,
                                        'prefix': '',
                                        'prefixEnabled': False},
                           'updates': {'enabled': True,
                                       'lastDownloadTime': None,
                                       'lastUpdateTime': update_timestamp,
                                       'updateBase': '',
                                       'updateFrequency': '',
                                       'updateMinutes': 100,
                                       'updatePeriod': '',
                                       'updateUnits': 'min'},
                           'version': 2},
               'quickMode': False,
               'title': f'{feed_title}',
               'url': f'{feed_url}'}
    return content


## returns { "feed_url": { "messages":[message_id], "lastSeenTime": 0 } }
def extract_feeds_dict( feeditems_data ):
    # pylint: disable=unnecessary-lambda
    feeditems_dict = defaultdict( lambda: dict() )
    for message_id in feeditems_data.keys():
        val = feeditems_data[ message_id ]
        feedList = val['feedURLs']
        lastSeenTime = val['lastSeenTime']

        for feed in feedList:
            feeditem = feeditems_dict[ feed ]
            messages = feeditem.setdefault( "messages", list() )
            messages.append( message_id )

            currTime = feeditem.get( "lastSeenTime", 0 )
            feeditem["lastSeenTime"] = max( lastSeenTime, currTime )
    return feeditems_dict


def generate_feeds_list( feeditems_dict, feeds_path ):
    feedsList = []
    for feedUrl in feeditems_dict:
        feeditem = feeditems_dict[ feedUrl ]
        feed_dirs = find_message_folder( feedUrl, feeds_path )
        if not feed_dirs:
            message_id_list = feeditem["messages"]
            for message_id in message_id_list:
                message_files = find_message_folder( message_id, feeds_path )
                feed_dirs.update( message_files )

        if len( feed_dirs ) != 1:
            _LOGGER.warning( "unable to determine directory for message: %s %s %s",
                             feedUrl, len( feed_dirs ), feed_dirs )
            continue

        feedContent = read_url( feedUrl )
        parsedDict = feedparser.parse( feedContent )
        if parsedDict.get('bozo', False):
            reason = parsedDict.get('bozo_exception', "<unknown>")
            _LOGGER.warning( "malformed rss detected, reason %s", reason )
            continue

        parsedFeed   = parsedDict['channel']
        feedTitle    = parsedFeed['title']
        feedLink     = parsedFeed['link']
        lastSeenTime = feeditem["lastSeenTime"]

        feed_item = create_feed_item( list(feed_dirs)[0], feedUrl, feedTitle, feedLink, lastSeenTime )
        feedsList.append( feed_item )
    return feedsList


def rebuild_feeds( feeditems_path ):
    _LOGGER.info( "reading feeditems: %s", feeditems_path )
    corrupt_content = read_file( feeditems_path )

    feeditems_data = json.loads( corrupt_content, strict=False )

    ## parse feeditems file -- grab feed urls and message ids
    feeditems_dict = extract_feeds_dict( feeditems_data )

    feedsLastTime = 0
    index = 1
    for feed in feeditems_dict:
        item = feeditems_dict[ feed ]
        lastSeenTime = item[ "lastSeenTime" ]
        feedsLastTime = max( feedsLastTime, lastSeenTime )
        _LOGGER.info( "found feed: %s", feed )
        index += 1

    feeds_path = os.path.dirname( feeditems_path )

    ## create feeds
    feedsList = generate_feeds_list( feeditems_dict, feeds_path )

#     pprint.pprint( feedsList )

    ## output json data
    feed_out_path = os.path.join( feeds_path, "feeds.json.rebuild" )
    with open(feed_out_path, 'w', encoding='utf8') as out_file:
        json.dump( feedsList, out_file, ensure_ascii=True )

    ## output pretty data
    feed_pretty_out_path = feed_out_path + ".pretty"
    with open(feed_pretty_out_path, 'w', encoding='utf8') as out_file:
        pprint.pprint( feedsList, stream=out_file )

    lastTime = int(lastSeenTime / 1000 )
    lastDate = datetime.datetime.utcfromtimestamp( lastTime )
    _LOGGER.info( "last seen timestamp: %s", lastSeenTime )
    _LOGGER.info( "last seen date: %s", lastDate )

    _LOGGER.info( "rebuild feeds to: %s", feed_out_path )

    return 0


def main( args=None ):
    parser = argparse.ArgumentParser(description='Feeds recovery')
    parser.add_argument('--feeditems_path', '-fip', action='store', default=None, help='Path to feeditems.json' )

    args = parser.parse_args()

    feeditems_path = args.feeditems_path
    if feeditems_path is None:
        _LOGGER.info( "'feeditems_path' not passed, deducing the path" )
        profile_path = deduce_profile_path()
        if profile_path is None:
            _LOGGER.warning( "unable to deduce profile path" )
            return 1
        _LOGGER.info( "deduced profile path: %s", profile_path )
        feeds_path = os.path.join( profile_path, "Mail", FEEDS_DIR_NAME )
        feeditems_path = os.path.join( feeds_path, "feeditems.json" )
        _LOGGER.info( "deduced feeditems.json path: %s", feeditems_path )

    succeed = rebuild_feeds( feeditems_path )

    return succeed


## =====================================================================


if __name__ == '__main__':
    ret_code = main()
    sys.exit( ret_code )
