from flask import render_template, Flask, request
from indexer import Index
from playlist import Playlist

index = Index()

app = Flask(__name__)
pl = Playlist()

@app.route('/artist/<artist>/<album>')
def find_songs(artist, album):
  songs = ['']
  songs += (index.getSongsForAlbum(album))
  songs[0] = {'title': "All songs in album (%d tracks)" % (len(songs) - 1), 'id': '0000 ' + album} 
  for song in songs:
    song['title'] = song['title'].decode('utf-8')

  return render_template('songs.html', artist=artist, album=album, songs = songs)

@app.route('/artist/<artist>')
def find_artists(artist):
  return render_template('search.html', artist=artist, albums=index.getAlbumsForArtist(artist))

@app.route('/')
def hello_world():
  return render_template('home.html')

@app.route('/search/<band>')
def search(band):
  return index.searchArtists(band)

@app.route('/popup')
def popup():
#  return request.META.get('HTTP_REFERER')
  return render_template('popup.html')

@app.route('/queue', methods=['POST'])
def queueManagement():
  what = request.form['what'] 
  songID = int(request.form['songID'])
  pl.loadPlaylist()
  if what == 'PlayNow':
    pl.playNow(songID)
  elif what == 'PlayNext':
    pl.playNext(songID)
  else:
    pl.addSongToEnd(songID)

  pl.savePlaylist()


@app.route('/playlist')
def showPlaylist():
  output = ''
  pl.loadPlaylist()
  for item in pl.getSongList():
    output += index.getDetailsForSongID(item)['title'] + '<br>\n'

  return output

  
@app.route('/chooser/<songID>')
def chooser(songID):
  if songID[:4] == '0000':
    infostring = songID[5:]
  else:
    details = index.getDetailsForSongID(int(songID))
    infostring = "%s, %s" % (details['title'], details['artist'])

  return render_template('chooser.html', songID = songID, infostring = infostring, goto = request.referrer)



if __name__ == '__main__':
    app.run()
