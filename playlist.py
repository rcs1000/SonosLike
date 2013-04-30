class Playlist:
	songlist = []
	playing = False
	index = 0

	def getSongList(self):
		return self.songlist

	def addSongToEnd(self, song):
		self.songlist.append(song)

	def playNow(self, song):
		self.songlist.insert(self.index, song)
		# And change currently playing track...

	def playNext(self, song):
		self.songlist.insert(self.index + 1, song)

	def nowPlaying(self):
		return self.songlist[index]

	def savePlaylist(self):
		import pickle
		pickle.dump( (self.songlist, self.playing, self.index), open('/home/rcs1000/mysite/playlist.pickle', 'wb'))	
		
	def loadPlaylist(self):
		import pickle
		self.songlist, self.playing, self.index = pickle.load(open('/home/rcs1000/mysite/playlist.pickle', 'rb'))	


