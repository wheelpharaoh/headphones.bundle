import uuid, urllib, re, json as JSON, getlink
#import urllib, re, getlink

"""
"Headphones" Plex Channel code

The API is still pretty new and needs some serious cleaning up on the backend but should be
reasonably functional. There are no error codes yet,
General structure:
http://localhost:8181 + HTTP_ROOT + /api?apikey=$apikey&cmd=$command
Data returned in json format. If executing a command like 'delArtist' or 'addArtist' youll get back an "OK", else, youll get the data you requested
$commands&parameters[&optionalparameters]
"""

class HPURLOpener(urllib.FancyURLopener):
    # read an URL, with automatic HTTP authentication

    def setpasswd(self, user, passwd):
        self.myuser = user
        self.mypasswd = passwd

    def prompt_user_passwd(self, host, realm):
        return self.myuser, self.mypasswd

# get HP prefs
#order these intuitively, by standard URL structure, or mimmick SB/CP bundles
SSL = ""
IP = ""
PORT = ""
API_K = ''	# this is inconvenient for typing into plex
HTTP_ROOT = ""
username = ""
password = ""

def HP_URL():
	""" Craft URL to HP server """
	SSL = Prefs['https']
	IP = Prefs['hpIP']
	PORT = Prefs['hpPort']
	HTTP_ROOT = Prefs['hpURLBase']
	username = Prefs['hpUsername']
	password = Prefs['hpPassword']

	if SSL:
		SSL="https"
	else:
		SSL="http"

	if HTTP_ROOT:
		pass
	else:
		HTTP_ROOT = "/"
	return '%s://%s:%s%s' % (SSL, IP, PORT, HTTP_ROOT)

def getAPI_K(username, password):
	""" return API_KEY """
	urlopener = HPURLOpener()
	urlopener.setpasswd(username, password)
	api_key_page = urlopener.open(HP_URL() + "config").read()
	API_K = re.search('(?<=Current API key: <strong>)[a-z0-9]{32}',api_key_page).group(0)
	Dict['API_K'] = API_K
	return API_K

def API_URL():
	""" Craft API URL to HP """
	return HP_URL() + 'api?apikey=%s' % Dict['API_K']

def HP_API_CALL(cmd, params = None):
	"""
	make API Call to HP server

	http(s)://IP:port/http_root/api?apikey=API_K&cmd=$command&cmdparameters
	"""
	#print "debug1: ", cmd
	Log('cmd argument: %s' % cmd)
	CMD = '&cmd=%s' % cmd
	#print "debug2: ", CMD
	Log('CMD variable: %s' % CMD)
	#print "debug3: ", params
	if(params):
		urllib.urlencode(params)
		for key, value in params.iteritems():
			#print "debug4: ",key
			#print "debug5: ",value
			CMD += '&%s=%s' % (key,value)
			#print "debug6: ",CMD
	url = API_URL() + CMD
	Log('url created: %s' % url)
	#try: hpResult = JSON.ObjectFromURL(url)	#plex-style
	#print "debug1: ",JSON.dumps(JSON.load(urllib.urlopen(url)), indent=4)	#python2.x-style
	try: hpResult = JSON.load(urllib.urlopen(url))
	except:
		## Logging line here, like in the cp.bundle
		hpResult = {'Error':'HP_API_CALL failed'}
	return hpResult

def getIndex():
	"""
	Fetch data from index page of HP DB
	
	return:
	Status, ThumbURL, DateAdded, TotalTracks, 
	IncludeExtras, ArtistName, LastUpdated, ReleaseDate, 
	AlbumID, ArtistID, ArtworkURL, Extras, 
	HaveTracks, LatestAlbum, ArtistSortName
	"""
	return HP_API_CALL('getIndex')


def getArtist(ArtistID):
	"""
	Fetch artist data (artist object and album info) from HP DB
	
	return:	
	Status, AlbumASIN, DateAdded, AlbumTitle, 
	ArtistName, ReleaseDate, AlbumID, ArtistID, 
	Type, ArtworkURL
	"""
	param = {'id': ArtistID}
	return HP_API_CALL('getArtist',param)

def getAlbum(AlbumID):
	"""
	Fetch data from album page in HP

	returns artist object (getArtist) and album info:
	Status, AlbumASIN, DateAdded, AlbumTitle, ArtistName, 
	ReleaseDate, AlbumID, ArtistID, Type, 
	ArtworkURL: hosted image path
	"""
	param = {'id': AlbumID}
	return HP_API_CALL('getAlbum',param)


def getUpcoming():
	"""
	Fetch upcoming albums

	Return 
	Status, AlbumASIN, DateAdded, AlbumTitle, 
	ArtistName, ReleaseDate, AlbumID, ArtistID, Type)
	"""
	return HP_API_CALL('getUpcoming')

def getWanted():
	"""
	Fetch wanted albums

	Return: 
	Status, AlbumASIN, DateAdded, AlbumTitle, A
	rtistName, ReleaseDate, AlbumID, ArtistID, Type
	"""
	return HP_API_CALL('getWanted')

def getSimilar():
	"""
	Returns similar artists  - with a higher "Count" being more likely to be similar. 
	
	Return: 
	Count, ArtistName, ArtistID
	"""
	return HP_API_CALL('getSimilar')

def getHistory():
	"""
	Return Headphones history

	Return: 
	Status, DateAdded, Title, URL (nzb), 
	FolderName, AlbumID, Size (bytes)
	"""
	return HP_API_CALL('getHistory')

# getLogs(void)
## not working yet

def findArtist(ArtistName, LIMIT = 10):
	"""
	Perform artist query on musicbrainz DB. 
	
	Return: 
	url, score, name, 
	uniquename (contains disambiguation info),
	id
	"""
	param = {'name': ArtistName, 'limit': LIMIT}
	return HP_API_CALL('findArtist',param)

def findAlbum(AlbumName, LIMIT = 10):
	"""
	Perform album query on musicbrainz DB. 

	Return: 
	title, url (artist), id (artist), albumurl, 
	albumid, score, uniquename (artist - with disambiguation)
	"""
	param = {'name': AlbumName, 'limit': LIMIT}
	return HP_API_CALL('findAlbum',param)

def addArtist(ArtistID):
	"""
	Add an Artist to the HP DB by artistid
	
	"""
	param = {'id': ArtistID}
	return HP_API_CALL('addArtist',param)

def addAlbum(ReleaseID):
	"""
	Add an album to the HP DB by album release ID

	"""
	param = {'id': ReleaseID}
	return HP_API_CALL('addAlbum',param)

def delArtist(ArtistID):
	"""
	Delete artist from HP DB by their ID

	"""
	param = {'id': ArtistID}
	return HP_API_CALL('delArtist',param)

def pauseArtist(ArtistID):
	"""
	Pause (monitoring) an artist in HP DB

	"""
	param = {'id': ArtistID}
	return HP_API_CALL('pauseArtist',param)

def resumeArtist(ArtistID):
	"""
	Resume (monitoring) an artist in HP DB

	"""
	param = {'id': ArtistID}
	return HP_API_CALL('resumeArtist',param)

def refreshArtist(ArtistID):
	"""
	Refresh info for artist in HP DB (w/info from musicbrainz)

	"""
	param = {'id': ArtistID}
	return HP_API_CALL('refreshArtist',param)

def queueAlbum(AlbumID, NEW = None, LOSSLESS = None):
	"""
	Mark an album as wanted and start the searcher
	
	new, look for new version
	lossless, looks only for lossless
	"""
	param = {'id': AlbumID, 'new': NEW, 'lossless': LOSSLESS}
	return HP_API_CALL('queueAlbum',param)

def unqueueAlbum(AlbumID):
	"""
	Unmark album as wanted; mark as 'skipped'

	"""
	param = {'id': AlbumID}
	return HP_API_CALL('unqueueAlbum',param)

def forceSearch():
	"""
	Force search for wanted albums

	not launched in a separate thread)
	"""
	return HP_API_CALL('forceSearch')

def forceProcess():
	"""
	Force Post Process albums in download directory
	
	(not launched in a separate thread)
	"""
	return HP_API_CALL('forceProcess')

def getVersion():
	"""
	Returns version information
	
	return:
	git_path, install_type, current_version
	installed_version, commits_behind
	"""
	return HP_API_CALL('getVersion')

def checkGithub():
	"""
	Updates the 'getVersion()' information and returns getVersion data

	"""
	return HP_API_CALL('checkGithub')

def shutdown():
	"""
	Shutdown Headphones

	"""
	return HP_API_CALL('shutdown')

def restart():
	"""
	Restart Headphones

	"""
	return HP_API_CALL('restart')

def update():
	"""
	Update Headphones

	#FYI: you may want to check the install type in get version 
	and not allow this if type==exe
	"""
	return HP_API_CALL('update')

def getArtistArt(ArtistID):
	"""
	Returns either a relative path to the cached ARTIST image, or a remote url 

	if the image can't be saved to the cache dir)
	"""
	param = {'id': ArtistID}
	return HP_API_CALL('getArtistArt',param)

def getAlbumArt(AlbumID):
	"""
	Returns either a relative path to the cached ALBUM image, or a remote url if the image can't be saved to the cache dir)

	"""
	param = {'id': AlbumID}
	return HP_API_CALL('getAlbumArt',param)

def getArtistInfo(ArtistID):
	"""
	Returns ARTIST Summary and Content, both formatted in html)

	"""
	param = {'id': ArtistID}
	return HP_API_CALL('getArtistInfo',param)

def getAlbumInfo(AlbumID):
	"""
	Returns ALBUM Summary and Content, both formatted in html

	"""
	param = {'id': AlbumID}
	return HP_API_CALL('getAlbumInfo',param)

def getArtistThumb(ArtistID):
	"""
	Returns either a relative path to the cached thumbnail ARTIST image

	or an http:// address if the cache dir can't be written to)
	"""
	param = {'id': ArtistID}
	return HP_API_CALL('getArtistThumb',param)

def getAlbumThumb(AlbumID):
	"""
	Returns either a relative path to the cached thumbnail ALBUM image, 

	or an http:// address if the cache dir can't be written to)
	"""
	param = {'id': AlbumID}
	return HP_API_CALL('getAlbumThumb',param)

#print getAlbum('350f8f0c-4dc7-458b-b6af-779ef280c2c4')
#print getSimilar()
#print findArtist('Ross', 2)
#print getArtistArt('dff0d392-4cd5-4052-9fbb-f485df3891e5')
#print getArtist('197450cd-0124-4164-b723-3c22dd16494d')
#print findArtist('Frank Sinatra')
#print getArtistInfo('197450cd-0124-4164-b723-3c22dd16494d')
#print findAlbum('Channel Orange')

# Manage Your Music LibrRY
#1) -Edit
#	OnClick, show:
#		getIndex()
#			[ArtistThumb], [ArtistName]+[Status]+[HaveTracks], [LatestAlbum]
#				[delArtist]
#				[pauseArtist]
#				[resumeArtist]
#				[refreshArtist]
def showLibrary():
	for result in getIndex():
		print result['ArtistThumb'], result['ArtistName'], result['Status'], result['HaveTracks'], result['LatestAlbum']

#	-Show Wanted Albums
#		getWanted()
#			[ThumbURL], [ArtistName], [AlbumName], [ReleaseDate], [Type]
#			OnClick, show:
#				deleteAlbum
#				forceCheck
#				markAlbumAsSkipped
#				chooseAlternateRelease
#				editSearchTerm
def showWanted():
	for result in getWanted():
		print result['ThumbURL'], result['ArtistName'], result['AlbumTitle'], result['ReleaseDate'], result['Type']

#	-Show suggestions
#		getSimilar()
#			ArtistName
#			OnClick, Show:
#				Add Artist to Catalog
#			ArtistName
#				OnClick, Show:
#				Add Artist to Catalog
#			ArtistName
#			...
def showSimilar():
	for result in getSimilar():
		print result['ArtistName']

#Search
#	1) Submit Query
#	2) Select 'type'
#		[album]
#		[artist]
#	3a)	[artist]
#		Onclick, show:
#			//sub-search for 'filtering'
#			findArtist('ArtistName')
#				[getArtistThumb], [uniquename]+[ArtistInfo], [score]
#				OnClick:
#					[option1: addArtist()]
#						select 'ArtistID'
#						check if getArtist(ID) = True
#						print "Artist already in Database"; exit
#						addArtist('ArtistID')
#						print 'success/failure'
#	3b)[album]
#		Onclick, show:
#			//sub-search for 'filtering'
#			findAlbum('AlbumName')
#				[getAlbumThumb], [uniquename]+[score]
#				OnClick:
#					[option1: addAlbum()]
#						select 'AlbumID' from #1
#						check if getAlbum(ID) = True
#						if true: print "we have this already"; exit
#						addAlbum('AlbumID')
#						print 'success/failure'
def search():
	querya = {'AlbumName':'ocean'}
	results = findAlbum(querya['AlbumName'])
	#filter (sub-search loop)
	for result in results:
		#queried-albumart isn't cached for search queries, only HP DB lookups; so 
		#this fetch needs to be abstracted/coded by me
		print getlink.get_image_links(AlbumID=result['albumid'])['thumbnail'], result['uniquename'], result['score']

	queryb = {'ArtistName':'ocean'}
	results = findArtist(queryb['ArtistName'])
	#filter (sub-search loop)
	for result in results:
		print getlink.get_image_links(ArtistID=result['id'])['thumbnail'], result['uniquename'], result['score']


#Upcoming Releases
#	OnClick, show:
#		getUpcoming()
#			[albumThumb], [ArtistName], [AlbumName], [ReleaseDate], [Type], [Status]
def showUpcoming():
	for result in getUpcoming():
		print result['ThumbURL'], result['ArtistName'], result['AlbumTitle'], result['ReleaseDate'], result['Type'], result['Status']

#Show History()
#	OnClick, show:
#		getHistory()
#			[DateAdded], [FileName], [Size], [Processed]
#			//OnClick, show:
#			//	retry()
#			//	new()
def showHistory():
	for result in getHistory():
		print result['DateAdded'], result['FolderName'], result['Size'], result['Status']