#!/usr/bin/env python
import os
import sys
import mutagen
import sqlite3
import unicodedata
import re
import time

# change this path to your sqlite database
#dsn = '/Users/rcs1000/Dropbox/development/Flask and Javascript/mysite/id3.sqlite'
dsn = '/home/rcs1000/mysite/id3.sqlite'

class Analyzer:
    """
    Analyze string and remove stop words
    """
    def __init__(self):
        self.stop_words = ['los','las','el','the','of','and','le','de','a','des','une','un','s','is','www','http','com','org']

    def analyze(self, text):
        words = []
        text = self.strip_accents(text)
        text = re.compile('[\'`?"]').sub(" ", text)
        text = re.compile('[^A-Za-z0-9]').sub(" ", text)
        for word in text.split(" "):
            word = word.strip()
            if word != "" and not word in self.stop_words:
                if not isinstance(word, unicode):
                    words.append(word.lower())
                else:
                    words.append(word.lower())
        return words

    def strip_accents(self,s):
        s = unicode(s)
        return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))


class ID3:
    def __init__(self,path):
        self._load(path)

    def _load(self, filename):
        short_tags = full_tags = mutagen.File(filename)
        comments = []
        if isinstance(full_tags, mutagen.mp3.MP3):
            for key in short_tags:
                if key[0:4] == 'COMM':
                    if(short_tags[key].desc == ''):
                        comments.append(short_tags[key].text[0])
            short_tags = mutagen.mp3.MP3(filename, ID3 = mutagen.easyid3.EasyID3)
        comments.append('');
        self.album = short_tags.get('album', [''])[0]
        self.artist = short_tags.get('artist', [''])[0]
        self.duration = "%u:%.2d" % (full_tags.info.length / 60, full_tags.info.length % 60)
        self.length = full_tags.info.length
        self.title = short_tags.get('title', [''])[0]
        self.comment = comments[0]
        self.genre = ''
        genres = short_tags.get('genre', [''])
        if len(genres) > 0:
            self.genre = genres[0]
        self.size = os.stat(filename).st_size


class Index:
    def build(self,start):
        errors = []
        analyzer = Analyzer()
        cnx = self.db()
        cursor = cnx.cursor()
        cursor.execute("DELETE FROM id3index;")
        cursor.execute("DELETE FROM id3;")
        for root, dir, files in os.walk(start):
            for name in files:
                if name[-4:].lower() == '.mp3':
                    path = os.path.join(root,name)
                    print name
                    try:
                        id3 = ID3(path)
                    except:
                        errors.append(path)
                        id3 = None
                    if id3 != None:
                        cursor.execute("INSERT INTO id3(location, artist, title, album, genre, comment, duration, length, size) VALUES(?,?,?,?,?,?,?,?,?)",
                                       (path,id3.artist,id3.title,id3.album,id3.genre,id3.comment,id3.duration,id3.length,id3.size))
                        last_id3_id = cursor.lastrowid
                        for field in ['artist', 'title', 'album', 'comment', 'genre']:
                            words = analyzer.analyze(getattr(id3, field))
                            for word in words:
                                cursor.execute("INSERT INTO id3index(id3_id,keyword,field) VALUES (?,?,?);", (str(last_id3_id), word, field))
        cursor.execute('SELECT COUNT(*) AS nbrows FROM id3index LIMIT 1;')
        for line in cursor:
            print 'index size: ' + str(line["nbrows"])
        cnx.commit()
        if len(errors) > 0:
            print ""
            print "---- Errors ----"
            print ""
            for error in errors:
                print error

    def search(self,query):
        cnx = self.db()
        analyzer = Analyzer()
        clauses = []
        for word in analyzer.analyze(query):
            clauses.append("id3_id IN(SELECT id3_id FROM id3index WHERE keyword LIKE '" + str(word) + "')")
        cursor = cnx.cursor()
        q = 'SELECT COUNT(id3index.id) AS score, id3_id, id3.* from id3index join id3 on id3.id = id3index.id3_id  where ' + ' AND '.join(clauses) + ' GROUP BY id3_id ORDER BY score DESC'
        cursor.execute(q)

        output = ""

        for line in cursor:
            output += line["artist"] + ', ' + line["album"] + ': ' + line["title"] + '<br>' + chr(10) + chr(13)

        return output

        listi = ["artist", "album", "title", "location"]

        output = []

        for line in cursor:
            dicti = {}
            for item in listi:
                #print item
                dicti[item] = line[item]

            output.append(dicti)

        return output

    def searchToo(self, type, title):
        cnx = self.db()
        cursor = cnx.cursor()
        q = 'SELECT * from id3 WHERE ' + type + ' LIKE "' + title + '%"'
        cursor.execute(q)

        output = ""

        for line in cursor:
            output += line["artist"] + ', ' + line["album"] + ': ' + line["title"] + '<br>' + chr(10) + chr(13)

        return output

    def searchArtists(self, name):
        cnx = self.db()
        cursor = cnx.cursor()
        q = 'SELECT DISTINCT artist FROM id3 WHERE artist LIKE "' + name + '%"'
        cursor.execute(q)

        output = ""

        for line in cursor:
            output += '<li>'+line["artist"] + '</li>' + chr(10) + chr(13)

        return output

    def searchAlbums(self, name):
        cnx = self.db()
        cursor = cnx.cursor()
        q = 'SELECT DISTINCT album FROM id3 WHERE album LIKE "' + name + '%"'
        cursor.execute(q)

        output = ""

        for line in cursor:
            output += line["album"] + '<br>' + chr(10) + chr(13)

        return output

    def getAlbumsForArtist(self, name):
        cnx = self.db()
        cursor = cnx.cursor()
        q = 'SELECT DISTINCT album FROM id3 WHERE artist LIKE "' + name + '%"'
        cursor.execute(q)

        output = []

        for line in cursor:
            output.append(line["album"])

        return output

    def getSongsForAlbum(self, name):
        cnx = self.db()
        cursor = cnx.cursor()
        q = 'SELECT DISTINCT title FROM id3 WHERE album LIKE "' + name + '%"'
        cursor.execute(q)

        output = []

        for line in cursor:
            output.append(line["title"])

        return output


    def db(self):
        if getattr(self,"database", None) == None:
            self.database = sqlite3.connect(dsn)
            self.database.row_factory = sqlite3.Row
            self.database.text_factory = str
            cursor = self.database.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS id3index(id INTEGER PRIMARY KEY AUTOINCREMENT,id3_id, keyword, field)")
            cursor.execute("CREATE TABLE IF NOT EXISTS id3(id INTEGER PRIMARY KEY AUTOINCREMENT,location UNIQUE, artist, title, album, genre, comment, duration, length, size)")
            cursor.execute("CREATE INDEX IF NOT EXISTS keyword_idx ON id3index(keyword)")
        return self.database


__name__ = 'blah!'
if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'Usage: tags.py index-build [your music dir]'
    else:
        index = Index()
        if sys.argv[1] == 'index-build':
            index.build(sys.argv[2])
        elif sys.argv[1] == 'search':
            index.search(sys.argv[2])



index = Index()

# print index.searchToo('album', 'amn')

#print index.searchArtists('radio')

print index.getSongsForAlbum('The Virg')

#print index.getAlbumsForArtist('The Be')