#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib
import urllib2

from StringIO import StringIO
import gzip

import simplejson as json

class Pakartot(object):
  
  def __init__(self):    
    self.api_url = 'https://api.pakartot.lt/'
    self.user_agent = '|User-Agent=stagefright/1.2+(Linux;Android+4.1.2)'
  
  def apiRequest(self, req):
    data = {}
    data['username'] = 'publicUSR'
    data['password'] = 'vka3qaGHowofKcRdTeiV'
    data['platform'] = 'Android'
    data['commercial_user'] = 'true'
    
    for key in req:
      data[key] = req[key]
    
    json_data = {}
    fdata = ''
    
    try:
      data = urllib.urlencode(data)
      req = urllib2.Request(self.api_url, data)
      req.add_header('Accept-encoding', 'gzip')
      response = urllib2.urlopen(req)
      
      
      if response.info().get('Content-Encoding') == 'gzip':
	buf = StringIO(response.read())
	f = gzip.GzipFile(fileobj=buf)
	fdata = f.read()
    
      fdata = response.read()
      json_data = json.loads(fdata)
    except:
      print fdata
      
    return json_data

  def get_albums(self, album_type, page=1, **options):
    
    if album_type in ['new_music_albums', 'newest_albums', 'most_liked_albums']:
      
      data = self.apiRequest({'action': album_type, 'url': 'home', 'page': str(page)})
      if album_type in data:
	data['albums'] = data.pop(album_type)
	
      return data
    elif album_type == 'genres':      
      return self.apiRequest({'url': 'genres', 'action': 'albums', 'id': options.get('genre'), 'page': str(page) })
    
    return {}
  
  def get_album_files(self, album_id):
    
    return self.apiRequest({'action': 'album', 'url': 'play', 'id': album_id})
  
  def get_album_info(self, album_id):
    
    return self.apiRequest({'url': 'album', 'id': album_id})
  
  def get_styles(self):
    
    return self.apiRequest({'url': 'genres'})
  
  def get_album(self, album_id):
    
    info = self.get_album_info(album_id)
    files = self.get_album_files(album_id)
    
    urls = {}    
    
    if 'tracks' in files:
      for track in files['tracks']:
	urls[track['tid']] = track['filename']

    if not urls:
      return info
    
    if 'tracks' in info:
      for track in info['tracks']:
	if track['track_id'] in urls:
	  track.update({'filename': urls[track['track_id']] + self.user_agent })
	
    return info

  def get_public_playlists(self, page=1):
    
    return self.apiRequest({'url': 'home_playlists', 'action': 'playlists', 'page': str(page)})
  
  def get_playlist(self, playlist_id):
    
    print playlist_id
  
    data = self.apiRequest({'id' : playlist_id, 'url': 'play', 'action': 'playlist'})
    tids = []
    tracks = []
    
    if 'tracks' in data:
      for track in data['tracks']:
	
	if 'filename' in track:
	  track['filename'] = track['filename'] + self.user_agent
	  
	if track['tid'] not in tids:
	  tracks.append(track)	  
	tids.append(track['tid'])
    
    data['tracks'] = tracks
    
    return data
  
  def get_track(self, track_id):
    
    data = self.apiRequest({'id': track_id, 'url': 'play', 'action': 'track'})
    
    if 'tracks' in data:
      data['tracks'][0]['filename'] = data['tracks'][0]['filename'] + self.user_agent
    
    return data
  
  def search(self, key, page=1):
    
    return self.apiRequest({'search' : key, 'url': 'search', 'action': 'quick_new', 'page': str(page)})
  