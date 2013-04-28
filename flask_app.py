from flask import render_template, Flask
from indexer import Index
index = Index()

app = Flask(__name__)

@app.route('/artist/<artist>/<album>')
def find_songs(artist, album):
	songs = ['']
	songs += (index.getSongsForAlbum(album))
	songs[0] = "All songs in album (%d tracks)" % (len(songs) - 1)
	return render_template('songs.html', artist=artist, album=album, songs = songs)

@app.route('/artist/<artist>')
def find_artists(artist):
    return render_template('search.html', artist=artist, albums=index.getAlbumsForArtist(artist))

@app.route('/')
def hello_world():
	#return 'hello_world'
    return render_template('home.html')

@app.route('/search/<band>')
def search(band):
    return index.searchArtists(band)

@app.route('/popup')
def popup():
	return render_template('popup.html')


if __name__ == '__main__':
    app.run()
