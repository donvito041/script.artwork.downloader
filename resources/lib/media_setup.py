#import modules
import os
import xbmc
import urllib
import simplejson

### import libraries
from resources.lib.utils import _normalize_string as normalize_string
from resources.lib.utils import _log as log
from elementtree import ElementTree as ET
from resources.lib.settings import _settings

### get list of all tvshows and movies with their imdbnumber from library
# Retrieve JSON list
def _media_listing(media_type):
    settings = _settings()
    settings._get()
    log('Using JSON for retrieving %s info' %media_type)
    Medialist = []
    try:
        if media_type == 'tvshow':
            json_response = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetTVShows", "params": {"properties": ["file", "imdbnumber"], "sort": { "method": "label" } }, "id": 1}')
            json_response = unicode(json_response,'utf-8', errors='ignore')
            jsonobject = simplejson.loads(json_response)
            if jsonobject['result'].has_key('tvshows'):
                for item in jsonobject['result']['tvshows']:
                    Media = {}
                    Media['name']       = item['label']
                    Media['path']       = media_path(item['file'])
                    Media['id']         = item['imdbnumber']
                    Media['tvshowid']   = item['tvshowid']
                    ### Search for season numbers
                    json_response_season = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetSeasons", "params": {"tvshowid":%s }, "id": 1}' %Media['tvshowid'])
                    jsonobject_season = simplejson.loads(json_response_season)
                    if jsonobject_season['result'].has_key('limits'):
                        limits = jsonobject_season['result']['limits']
                        Media['seasontotal'] = limits['total']
                        Media['seasonstart'] = limits['start']
                        Media['seasonend'] = limits['end']
                    Medialist.append(Media)
        
        elif media_type == 'movie':
            json_response = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": {"properties": ["file", "imdbnumber", "year", "trailer"], "sort": { "method": "label" } }, "id": 1}')
            json_response = unicode(json_response,'utf-8', errors='ignore')
            jsonobject = simplejson.loads(json_response)
            if jsonobject['result'].has_key('movies'):
                for item in jsonobject['result']['movies']:
                    Media = {}
                    Media['movieid']    = item['movieid']
                    Media['name']       = item['label']
                    Media['year']       = item['year']
                    Media['path']       = media_path(item['file'])
                    Media['trailer']    = item['trailer']
                    Media['id']         = item['imdbnumber']
                    Medialist.append(Media)

        elif media_type == 'musicvideo':
            json_response = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMusicVideos", "params": {"properties": ["file", "artist", "album", "track", "runtime", "year", "genre"], "sort": { "method": "album" } }, "id": 1}')
            json_response = unicode(json_response,'utf-8', errors='ignore')
            jsonobject = simplejson.loads(json_response)
            if jsonobject['result'].has_key('musicvideos'):
                for item in jsonobject['result']['musicvideos']:
                    Media = {}
                    Media['id']         = ''
                    Media['movieid']    = item['musicvideoid']
                    Media['name']       = item['label']
                    Media['artist']     = item['artist']
                    Media['album']      = item['album']
                    Media['track']      = item['track']
                    Media['runtime']    = item['runtime']
                    Media['year']       = item['year']
                    Media['path']       = media_path(item['file'])
                    Medialist.append(Media)
        else:
            log('No JSON results found')
    except:
        log('No JSON results found')
    return Medialist


def media_path(path):
    # Check for stacked movies
    try:
        path = os.path.split(path)[0].rsplit(' , ', 1)[1]
    except:
        path = os.path.split(path)[0]
    # Fixes problems with rared movies
    if path.startswith("rar"):
        path = os.path.split(urllib.url2pathname(path.replace("rar://","")))[0]
    return path