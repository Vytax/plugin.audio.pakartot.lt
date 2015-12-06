#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import urllib

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

from libpakartot import Pakartot

settings = xbmcaddon.Addon(id='plugin.audio.pakartot.lt')

def getParameters(parameterString):
  commands = {}
  splitCommands = parameterString[parameterString.find('?') + 1:].split('&')
  for command in splitCommands:
    if (len(command) > 0):
      splitCommand = command.split('=')
      key = splitCommand[0]
      value = splitCommand[1]
      commands[key] = value
  return commands

def build_main_directory(): 
  
  listitem = xbmcgui.ListItem('Naujausia muzika Pakartot.LT')
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=1&page=0', listitem = listitem, isFolder = True, totalItems = 0)
  
  listitem = xbmcgui.ListItem('Naujausi albumai')
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=2&page=0', listitem = listitem, isFolder = True, totalItems = 0)
  
  listitem = xbmcgui.ListItem('Mylimi albumai')
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=3&page=0', listitem = listitem, isFolder = True, totalItems = 0)
  
  listitem = xbmcgui.ListItem('Stiliai')
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=4', listitem = listitem, isFolder = True, totalItems = 0)
  
  listitem = xbmcgui.ListItem('Vieši grojaraščiai')
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=5&page=1', listitem = listitem, isFolder = True, totalItems = 0)
  
  listitem = xbmcgui.ListItem('Paieška')
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=14', listitem = listitem, isFolder = True, totalItems = 0)
  
  if isLoggedIn:
    listitem = xbmcgui.ListItem('Mano grojaraščiai')
    listitem.setProperty('IsPlayable', 'false')
    xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=70&page=1', listitem = listitem, isFolder = True, totalItems = 0)
    
    listitem = xbmcgui.ListItem('Mano mylimi...')
    listitem.setProperty('IsPlayable', 'false')
    xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=80', listitem = listitem, isFolder = True, totalItems = 0)
  
  else:
    listitem = xbmcgui.ListItem('Prisijungti')
    listitem.setProperty('IsPlayable', 'false')
    xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=69', listitem = listitem, isFolder = True, totalItems = 0)
  
  xbmcplugin.setContent(int( sys.argv[1] ), 'albums')
  xbmc.executebuiltin('Container.SetViewMode(515)')
  xbmcplugin.endOfDirectory(int(sys.argv[1]))

def loadAlbums(mode, page, mid=0):
  
  data = {}
  data2 = {}
  albums = []
  
  album_type = None
  
  if mode == 1:  
    album_type = 'new_music_albums'
  elif mode == 2:
    album_type = 'newest_albums'
  elif mode == 3:
    album_type = 'most_liked_albums'
  elif mode == 20:
    album_type = 'genres'
    
  if mode in [1, 2, 3]:
    data = pakartot.get_albums(album_type, page*2 + 1)
    data2 = pakartot.get_albums(album_type, page*2 + 2)
  elif mode == 20:
    data = pakartot.get_albums(album_type, page*2 + 1, genre = mid)
    data2 = pakartot.get_albums(album_type, page*2 + 2, genre = mid)
  elif mode == 90:
    data = pakartot.get_favorites_albums(page + 1)
  
  if 'albums' in data:
    albums = data['albums']
	
  if 'albums' in data2:
    albums += data2['albums']
      
  for album in albums:
      
    listitem = xbmcgui.ListItem(album['album_name_generated'])
    listitem.setProperty('IsPlayable', 'false')
    listitem.setThumbnailImage(album['photo_path'].replace('225x225','348x348'))
    
    like = False
    if 'like' in album:
      like = album['like']['state'] == 'on'
    
    if isLoggedIn:
      commands = []
      if like:
	commands.append(( 'Pašalinti iš mylimų albumų', 'XBMC.RunPlugin(%s)' % (sys.argv[0] + '?mode=7&id='+album['album_id']), ))
      else:
	commands.append(( 'Pridėti prie mylimų albumų', 'XBMC.RunPlugin(%s)' % (sys.argv[0] + '?mode=7&id='+album['album_id']), ))
      listitem.addContextMenuItems( commands )
      
    info = {}
    info['artist'] = album['performers']
    info['year'] = album['album_year']
    info['album'] = album['album_name']
      
    listitem.setInfo(type = 'music', infoLabels = info )
      
    xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=10&id='+album['album_id'], listitem = listitem, isFolder = True, totalItems = 0)
    
  if len(albums) > 5:
    listitem = xbmcgui.ListItem("[Daugiau... ] %d" % (page+1))
    listitem.setProperty('IsPlayable', 'false')
      
    u = {}
    u['mode'] = mode
    u['page'] = page + 1
    if mid:
      u['id'] = mid
    xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?' + urllib.urlencode(u), listitem = listitem, isFolder = True, totalItems = 0)
      
  
  xbmcplugin.setContent(int( sys.argv[1] ), 'albums')
  xbmc.executebuiltin('Container.SetViewMode(506)')
  xbmcplugin.endOfDirectory(int(sys.argv[1]))
  
def loadAlbum(album_id):
  
  data = pakartot.get_album(album_id)
  
  if 'tracks' in data:
    
    thumb = None
    album = None
    if 'album' in data:
      thumb = data['album']['photo_path'].replace('225x225','348x348')
      album = data['album']['album_name']
    
    for track in data['tracks']:
      
      listitem = xbmcgui.ListItem(track['track_name'])      
      
      if thumb:
	listitem.setThumbnailImage(thumb)
      
      info = {}
      info['title'] = track['track_name']
      info['artist'] = track['performers']
      info['tracknumber'] = track['album_track_order']      
      info['duration'] = track['track_length']
      info['year'] = track['track_year']
      
      if album:
	info['album'] = album

      listitem.setInfo(type = 'music', infoLabels = info )
      
      like = False
      if 'like_state' in track:
	like = track['like_state'] == 'on'
      
      if isLoggedIn:
	commands = []
	if like:
	  commands.append(( 'Pašalinti iš mylimų įrašų', 'XBMC.RunPlugin(%s)' % (sys.argv[0] + '?mode=8&id='+track['track_id']), ))
	else:
	  commands.append(( 'Pridėti prie mylimų įrašų', 'XBMC.RunPlugin(%s)' % (sys.argv[0] + '?mode=8&id='+track['track_id']), ))
	listitem.addContextMenuItems( commands )
      
      if 'filename' in track:
	listitem.setProperty('IsPlayable', 'true')
	xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = track['filename'], listitem = listitem, isFolder = False, totalItems = 0)
      else:
	listitem.setProperty('IsPlayable', 'false')
	listitem.setThumbnailImage(os.path.join( settings.getAddonInfo( 'path' ), 'resources', 'media', 'locked.png' ))
	xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]),  url = '', listitem = listitem, isFolder = False, totalItems = 0)
      
  xbmcplugin.setContent(int( sys.argv[1] ), 'songs')
  xbmc.executebuiltin('Container.SetViewMode(506)')
  xbmcplugin.endOfDirectory(int(sys.argv[1]))
  

def loadStyles():
  
  data = pakartot.get_styles()
  
  for genre in data['genres']:
    
    listitem = xbmcgui.ListItem(genre['genre_name'])
    listitem.setThumbnailImage(genre['genre_cover'].replace('225x225','348x348'))
    
    u = {}
    u['mode'] = 20
    u['page'] = 0
    u['id'] = genre['genre_id']
    xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?' + urllib.urlencode(u), listitem = listitem, isFolder = True, totalItems = 0)
  
  xbmcplugin.setContent(int( sys.argv[1] ), 'albums')
  xbmc.executebuiltin('Container.SetViewMode(500)')
  xbmcplugin.endOfDirectory(int(sys.argv[1]))
  
def loadPlaylists(data, page, mode):
  
  for playlist in data['playlists']:
    
    listitem = xbmcgui.ListItem(playlist['playlist_name'])
    if 'playlist_frontend_photo_path' in playlist:
      listitem.setThumbnailImage(playlist['playlist_frontend_photo_path'])
      
    info = {}
    if 'tracks_count' in playlist:
      info['count'] = int(playlist['tracks_count']) 
    elif 'track_count' in playlist:
      info['count'] = int(playlist['track_count']) 
    listitem.setInfo(type = 'music', infoLabels = info )
    
    like = False
    if 'like' in playlist:
      like = playlist['like']['state'] == 'on'
    
    if isLoggedIn:
      commands = []
      if like:
	commands.append(( 'Pašalinti iš mylimų grojaraščių', 'XBMC.RunPlugin(%s)' % (sys.argv[0] + '?mode=9&id='+playlist['playlist_id']), ))
      else:
	commands.append(( 'Pridėti prie mylimų grojaraščių', 'XBMC.RunPlugin(%s)' % (sys.argv[0] + '?mode=9&id='+playlist['playlist_id']), ))
      listitem.addContextMenuItems( commands )
    
    u = {}
    u['mode'] = 6
    u['page'] = 0
    u['id'] = playlist['playlist_id']
    xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?' + urllib.urlencode(u), listitem = listitem, isFolder = True, totalItems = 0)
    
  if 'playlists' in data and len(data['playlists']) >= 12:    
    listitem = xbmcgui.ListItem("[Daugiau... ] %d" % (page))
    listitem.setProperty('IsPlayable', 'false')
    u = {'mode': mode, 'page': page+1}
    xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?' + urllib.urlencode(u), listitem = listitem, isFolder = True, totalItems = 0)  
  
  xbmcplugin.setContent(int( sys.argv[1] ), 'albums')
  xbmc.executebuiltin('Container.SetViewMode(506)')
  xbmcplugin.endOfDirectory(int(sys.argv[1]))

def loadPublicPlaylists(page):
  
  data = pakartot.get_public_playlists(page)  
  loadPlaylists(data, page, 5)

def loadUserPlaylists(page):
  
  data = pakartot.get_user_playlists(page)
  loadPlaylists(data, page, 70)

def loadFavoritelaylists(page):
  
  data = pakartot.get_favorites_playlists(page)
  loadPlaylists(data, page, 92)

def loadPlaylist(mid):
  
  data = pakartot.get_playlist(mid)
  
  if 'tracks' in data:
    
    for track in data['tracks']:
      listitem = xbmcgui.ListItem(track['title'])      
 
      info = {}
      info['title'] = track['title']
      info['artist'] = track['artist']
      info['duration'] = track['length']

      listitem.setInfo(type = 'music', infoLabels = info )
      
      like = False
      if 'like_state' in track:
	like = track['like_state'] == 'on'
      
      if isLoggedIn:
	commands = []
	if like:
	  commands.append(( 'Pašalinti iš mylimų įrašų', 'XBMC.RunPlugin(%s)' % (sys.argv[0] + '?mode=8&id='+track['tid']), ))
	else:
	  commands.append(( 'Pridėti prie mylimų įrašų', 'XBMC.RunPlugin(%s)' % (sys.argv[0] + '?mode=8&id='+track['tid']), ))
	listitem.addContextMenuItems( commands )
      
      if 'filename' in track:
	listitem.setProperty('IsPlayable', 'true')
	xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = track['filename'], listitem = listitem, isFolder = False, totalItems = 0)
      else:
	listitem.setProperty('IsPlayable', 'false')
	xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]),  url = '', listitem = listitem, isFolder = False, totalItems = 0)
	
  xbmcplugin.setContent(int( sys.argv[1] ), 'songs')
  xbmc.executebuiltin('Container.SetViewMode(506)')
  xbmcplugin.endOfDirectory(int(sys.argv[1]))

def loadFavoriteTracks(page=1):
  
  data = pakartot.get_favorites_tracks(page)
  
  if 'tracks' in data:
    
    for track in data['tracks']:
      listitem = xbmcgui.ListItem(track['track_name'])      
 
      info = {}
      info['title'] = track['track_name']
      info['artist'] = track['performers']
      info['duration'] = track['track_length']

      listitem.setInfo(type = 'music', infoLabels = info )
      listitem.setProperty('IsPlayable', 'true')
      
      commands = []
      commands.append(( 'Pašalinti iš mylimų įrašų', 'XBMC.RunPlugin(%s)' % (sys.argv[0] + '?mode=8&id='+track['track_id']), ))
      listitem.addContextMenuItems( commands )
      
      xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=50&id='+ track['track_id'], listitem = listitem, isFolder = False, totalItems = 0)
      
    if len(data['tracks']) >= 20:
      listitem = xbmcgui.ListItem("[Daugiau... ] %d" % (page))
      listitem.setProperty('IsPlayable', 'false')
      xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=91&page=' + str(page + 1), listitem = listitem, isFolder = True, totalItems = 0)
      	
  xbmcplugin.setContent(int( sys.argv[1] ), 'songs')
  xbmc.executebuiltin('Container.SetViewMode(506)')
  xbmcplugin.endOfDirectory(int(sys.argv[1]))

def loadFavorites():
  
  listitem = xbmcgui.ListItem('Mylimi albumai')
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=90&page=0', listitem = listitem, isFolder = True, totalItems = 0)
  
  listitem = xbmcgui.ListItem('Mylimi įrašai')
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=91&page=1', listitem = listitem, isFolder = True, totalItems = 0)
  
  listitem = xbmcgui.ListItem('Mylimi grojaraščiai')
  listitem.setProperty('IsPlayable', 'false')
  xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=92&page=1', listitem = listitem, isFolder = True, totalItems = 0)
  
  xbmcplugin.setContent(int( sys.argv[1] ), 'albums')
  xbmc.executebuiltin('Container.SetViewMode(515)')
  xbmcplugin.endOfDirectory(int(sys.argv[1]))

def startSearch():
  
  dialog = xbmcgui.Dialog()
  searchKey = dialog.input('Muzikos paieška', type=xbmcgui.INPUT_ALPHANUM)
  
  if searchKey:
    xbmc.executebuiltin('ActivateWindow(Music,"%s")' % (sys.argv[0] + '?mode=15&page=1&searchKey=' + searchKey))

def search(searchKey, page):
  
  if not page:
    page = 1
  
  data = pakartot.search(searchKey, page)
  
  if 'tracks' in data and data['tracks']:
    for track in data['tracks']:
      listitem = xbmcgui.ListItem(track['track_name'])
      if 'photo_path' in track:
	listitem.setThumbnailImage(track['photo_path'].replace('164x164','348x348'))
 
      info = {}
      info['title'] = track['track_name']
      info['artist'] = track['performers']
      info['duration'] = track['track_length']

      listitem.setInfo(type = 'music', infoLabels = info )
      
      like = False
      if 'like_state' in track:
	like = track['like_state'] == 'on'
      
      if isLoggedIn:
	commands = []
	if like:
	  commands.append(( 'Pašalinti iš mylimų įrašų', 'XBMC.RunPlugin(%s)' % (sys.argv[0] + '?mode=8&id='+track['track_id']), ))
	else:
	  commands.append(( 'Pridėti prie mylimų įrašų', 'XBMC.RunPlugin(%s)' % (sys.argv[0] + '?mode=8&id='+track['track_id']), ))      
	listitem.addContextMenuItems( commands )
      
      listitem.setProperty('IsPlayable', 'true')
      xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?mode=50&id='+ track['track_id'], listitem = listitem, isFolder = False, totalItems = 0)
      
    listitem = xbmcgui.ListItem("[Daugiau... ] %d" % (page))
    listitem.setProperty('IsPlayable', 'false')
      
    u = {}
    u['mode'] = 15
    u['page'] = page + 1
    u['searchKey'] = searchKey
    xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]), url = sys.argv[0] + '?' + urllib.urlencode(u), listitem = listitem, isFolder = True, totalItems = 0)
      
  xbmcplugin.setContent(int( sys.argv[1] ), 'songs')
  xbmc.executebuiltin('Container.SetViewMode(506)')
  xbmcplugin.endOfDirectory(int(sys.argv[1]))
  
def play_track(mid):
  
  data = pakartot.get_track(mid)
  
  if 'tracks' not in data:
    return
  
  track = data['tracks'][0]
  
  listitem = xbmcgui.ListItem(label = track['title'])
  listitem.setPath(track['filename'])
  xbmcplugin.setResolvedUrl(handle = int(sys.argv[1]), succeeded = True, listitem = listitem)

def login():
  
  xbmc.executebuiltin('Addon.OpenSettings(plugin.audio.pakartot.lt)')
  xbmc.executebuiltin('Container.Refresh')

def favoriteAlbum(aid):
  
  pakartot.favorite_album(aid)
  xbmc.executebuiltin('Container.Refresh')
  
def favoriteTrack(tid):
  
  pakartot.favorite_track(tid)
  xbmc.executebuiltin('Container.Refresh')
  
def favoritePlaylist(pid):
  
  pakartot.favorite_playlist(pid)
  xbmc.executebuiltin('Container.Refresh')

# **************** main ****************

username = settings.getSetting('username')
password = settings.getSetting('password')

pakartot = Pakartot()
pakartot.setCredentials(username, password)

isLoggedIn = pakartot.isLoggedIn()

path = sys.argv[0]
params = getParameters(sys.argv[2])
mode = None
mid = None
page = None
searchKey = None

try:
  mode = int(params["mode"])
except:
  pass

try:
  mid = int(params["id"])
except:
  pass

try:
  page = int(params["page"])
except:
  pass

try:
  searchKey = params["searchKey"]
except:
  pass

if mode == None:
  build_main_directory()
elif mode in [1, 2, 3, 20, 90]:
  loadAlbums(mode, page, mid)
elif mode == 4:
  loadStyles()
elif mode == 5:
  loadPublicPlaylists(page)
elif mode == 6:
  loadPlaylist(mid)
elif mode == 7:
  favoriteAlbum(mid)
elif mode == 8:
  favoriteTrack(mid)
elif mode == 9:
  favoritePlaylist(mid)
elif mode == 10:
  loadAlbum(mid)
elif mode == 14:
  startSearch()
elif mode == 15:
  search(searchKey, page)
elif mode == 50:
  play_track(mid)
elif mode == 69:
  login()
elif mode == 70:
  loadUserPlaylists(page)
elif mode == 80:
  loadFavorites()
elif mode == 91:
  loadFavoriteTracks(page)
elif mode == 92:
  loadFavoritelaylists(page)
elif mode == 100:
  loadTrack(mid)
  