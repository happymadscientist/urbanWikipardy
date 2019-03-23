from pymongo import MongoClient, TEXT, ASCENDING

from datetime import datetime
getCurrentTime = lambda : datetime.now().timestamp()

mongoAddress = "localhost"

class urbanDictionaryDatabaseHandler:

	def __init__(self):
		self.loadUrbanDictDatabase()

	def loadUrbanDictDatabase(self):
		mongoUrl = 'mongodb://' + mongoAddress + ":27017/"
		mongoClient = MongoClient(mongoUrl)
		self.urbanDb = mongoClient["urbanDb"]

	def createTables(self):
		self.urbanDb['DICTIONARY'].create_index(
			[('TAGS',ASCENDING),
			('DEFINITION',ASCENDING),
			('WORD',ASCENDING),
			],
			unique = True)

		self.urbanDb['COMMANDS'].create_index(
			[('SESSION_ID',ASCENDING),
			('TIMESTAMP',ASCENDING)],
			unique = True)

		self.urbanDb['USER_ENTRIES'].create_index(
			[('SESSION_ID',ASCENDING),
			('TIMESTAMP',ASCENDING)],
			unique = True)

		self.urbanDb['GAME_SETTINGS'].create_index(
			[('SESSION_ID',ASCENDING)],unique = True
			)

	def dropCollection(self,COLLECTION_NAME):
		self.urbanDb.drop_collection(COLLECTION_NAME)

	def dropAllCollections(self):
		self.dropCollection("DICTIONARY")
		self.dropCollection("USER_ENTRIES")
		self.dropCollection("COMMANDS")
		self.dropCollection("GAME_SETTINGS")
		self.createTables()

	def addEntryToCollection(self,COLLECTION_NAME,ENTRY):
		try:
			returnCode = self.urbanDb[COLLECTION_NAME].insert_one(ENTRY)
			return 1
		except Exception as e:
			if (e.code == 11000): #the error code for pymongo.errors.DuplicateKeyError)
				return 0
			else:
				print ("UNKNOWN ERROR CODE!")
				return 0


	def upsertEntryToCollection(self,COLLECTION_NAME,ENTRY,UPDATE):
		return self.urbanDb[COLLECTION_NAME].update_one(ENTRY, UPDATE, upsert=True)

	def updateListOfEntry(self,COLLECTION_NAME,ENTRY,UPDATE):
		self.urbanDb[COLLECTION_NAME].update_one(ENTRY, {'$push': UPDATE})

	def findOneEntry(self,COLLECTION_NAME,ENTRY_CRITERIA,MASK_CRITERIA={"_id":0}):
		return self.urbanDb[COLLECTION_NAME].find_one(ENTRY_CRITERIA,MASK_CRITERIA)
	
	def findManyEntries(self,COLLECTION_NAME,ENTRY_CRITERIA,MASK_CRITERIA={"_id":0}):
		return self.urbanDb[COLLECTION_NAME].find(ENTRY_CRITERIA,MASK_CRITERIA)

	def cursorToList(self,cursorIn):
		return list(cursorIn)

	def printAllEntries(self,COLLECTION_NAME):
		for entry in self.urbanDb[COLLECTION_NAME].find({},{"_id":0}):
			print (entry)

	##DICTIONARY FUNCTIONS
	def addWordToDict(self,WORD,DEFINITION,TAGS,UPVOTES,DOWNVOTES,EXAMPLE):
		entryDict = {
			"WORD" : WORD,
			"DEFINITION" : DEFINITION,
			"TAGS" : TAGS,
			"UPVOTES" : UPVOTES,
			"DOWNVOTES" : DOWNVOTES,
			"EXAMPLE" : EXAMPLE,
			"VIEWED" : 0,
			"SESSION_ID_USED" : 0
			}

		return self.addEntryToCollection("DICTIONARY",entryDict)

	def findWordsByTag(self,TAG,NUM_TO_GET = 5):
		wordsCursor = self.findManyEntries("DICTIONARY",
			{"TAGS":{"$in":[TAG]}, "VIEWED":0},
			{"UPVOTES":1,"DEFINITION":1,"WORD":1,"_id":0})
		return self.cursorToJeopardyList(wordsCursor,NUM_TO_GET)

	def findWordsByInWord(self,CRITERIA,NUM_TO_GET = 5):
		wordsCursor = self.findManyEntries("DICTIONARY",
			{"WORD":{"$regex":"^.*%s.*$" % CRITERIA}, "VIEWED":0}
			,{"UPVOTES":1,"DEFINITION":1,"WORD":1,"_id":0})
		return self.cursorToJeopardyList(wordsCursor,NUM_TO_GET)

	def findWordsByInDef(self,CRITERIA,NUM_TO_GET = 5):
		wordsCursor = self.findManyEntries("DICTIONARY",
			{"DEFINITION":{"$regex":"^.*%s.*$" % CRITERIA},"VIEWED":0}
			,{"UPVOTES":1,"DEFINITION":1,"WORD":1,"_id":0})
		return self.cursorToJeopardyList(wordsCursor,NUM_TO_GET)

	def cursorToJeopardyList(self,cursor,NUM_TO_GET,SORT_KEY="UPVOTES"):
		if (cursor.count() < NUM_TO_GET):
			# print ("COULDNT FIND ENOUGH")
			return 0

		#sort by upvotes and only take the top (default to upvotes)
		cursor.sort(SORT_KEY,-1).limit(NUM_TO_GET)

		outputList = []
		for elem in cursor:
			entry = {elem["WORD"]:elem["DEFINITION"]}
			outputList.append(entry)

		# print (outputList)
		return outputList

	def findWords(self,CRITERIA,NUM_TO_GET,MODE):
		if MODE == "Tag": return self.findWordsByTag(CRITERIA,NUM_TO_GET)
		elif MODE == "InWord" : return self.findWordsByInWord(CRITERIA,NUM_TO_GET)
		elif MODE == "InDef" : return self.findWordsByInDef(CRITERIA,NUM_TO_GET)

	def findWordsByCriteria(self,CRITERIA,categories,NUM_TO_GET = 5,INCLUDE_EXAMPLE=True,SORT_KEY = "UPVOTES"):
		#finds a list of word+def pairs according to the CRTIERIA from 
		cursorList = []

		returnCriteria = {SORT_KEY:1,"DEFINITION":1,"WORD":1,"_id":0}
		if INCLUDE_EXAMPLE: 
			#make sure it deosn't include words with blank examples
			returnCriteria["EXAMPLE"] = 1
			extraCriteria = {"EXAMPLE" : {"$ne" : ""}}

		else:
			extraCriteria = {}

		if "Tag" in categories:
			tagCursor = self.findManyEntries("DICTIONARY",
				{**extraCriteria,**{"TAGS":{"$in":[CRITERIA]},"VIEWED" : 0}},
				returnCriteria)
			cursorList.append(tagCursor)

		if "InWord" in categories:
			wordCursor = self.findManyEntries("DICTIONARY",
				{**extraCriteria,**{"WORD":{"$regex":"^.*%s.*$" % CRITERIA},"VIEWED" : 0}},
				returnCriteria)
			cursorList.append(wordCursor)

		if "InDef" in categories:
			defCursor = self.findManyEntries("DICTIONARY",
				{**extraCriteria,**{"DEFINITION":{"$regex":"^.*%s.*$" % CRITERIA},"VIEWED" : 0}},
				returnCriteria)
			cursorList.append(defCursor)

		totalFound = sum([cursor.count() for cursor in cursorList])

		#sort by upvotes and only take the top (default to upvotes)
		[cursor.sort(SORT_KEY,-1).limit(NUM_TO_GET) for cursor in cursorList]

		#if not enough were found, return 0
		if totalFound < NUM_TO_GET:	return 0

		#otherwise get words from each type
		outputList = []
		while len(outputList) < NUM_TO_GET:
			for cursor in cursorList:
				try: nextEntry = cursor.next()
				except: continue
				if INCLUDE_EXAMPLE:	
					word = nextEntry["WORD"]
					censoredExample = (nextEntry["EXAMPLE"].lower()).replace(word,"x"*len(word))
					answer = (nextEntry["DEFINITION"] + "\n\n Example: " + censoredExample)
					questionAnswerDict = {nextEntry["WORD"]:answer}
				else: questionAnswerDict = {nextEntry["WORD"]:nextEntry["DEFINITION"]}

				outputList.append(questionAnswerDict)
	
		# print (outputList)
		return outputList

	def getRandomEntry(self):
		randomTag = self.urbanDb["DICTIONARY"].aggregate([{ "$sample": { "size": 1 } }])
		return list(randomTag)[0]

	def findRandomCategory(self,numEntries = 4):
		tryIndex = 0
		numTries = 10

		modes = ["Tag","InWord","InDef"]

		for tryIndex in range(numTries):
			#get a random word
			randomEntry = self.getRandomEntry()

			#get that word's tags
			randomTags = randomEntry["TAGS"]
			for tag in randomTags:
				for mode in modes:
					categoryDict = self.findWords(CRITERIA = tag,NUM_TO_GET = numEntries,MODE = mode)
					if (categoryDict):
						outputDict = {"MODES":[mode],"NAME":tag,"QUESTIONS":categoryDict}
						return outputDict
		return 0

	def updateWordDifficulty(self,WORD,DEFINITION,DIFFICULTY):
		#updates a wword with the difficulty of it and sets it to has been viewed
		selectionCriteria = {"WORD":WORD,"DEFINITION" : DEFINITION}
		updateCriteria = {"$set":{"DIFFICULTY" : DIFFICULTY}}
		return self.upsertEntryToCollection("DICTIONARY",selectionCriteria,updateCriteria)

	def updateWordViewed(self,WORD,DEFINITION):
		#updates a wword with the difficulty of it and sets it to has been viewed
		selectionCriteria = {"DEFINITION" : DEFINITION,"WORD":WORD}
		updateCriteria = {"$set":{"VIEWED" : 1}}
		self.upsertEntryToCollection("DICTIONARY",selectionCriteria,updateCriteria)

	def postBoardCommand(self,COMMAND_TYPE,COMMAND_DATA,SESSION_ID,SENDER = ""):
		currentTime = getCurrentTime()
		if SENDER: READ = [SENDER]
		else: READ = []
		commandPost = {
			"SESSION_ID" : SESSION_ID,
			"TYPE" : COMMAND_TYPE,
			"DATA" : COMMAND_DATA,
			"READ" : READ,
			"TIMESTAMP" : currentTime
			}

		self.addEntryToCollection("COMMANDS",commandPost)

	def getBuzzerCommands(self,SESSION_ID, TEAM_NAME):
		selectionCriteria = {
			"SESSION_ID" : SESSION_ID,
			"TYPE" : "Hella Wikipardy",
			"READ" : {"$nin":[TEAM_NAME]}
			}

		return self.findOneEntry("COMMANDS",selectionCriteria)

	def getBoardCommands(self,SESSION_ID,TEAM_NAME):
		#gets the newest board status from the database
		selectionCriteria = {
			"SESSION_ID" : SESSION_ID,
			"READ" : {"$nin":[TEAM_NAME]}
			}

		unreadCommandsCursor = self.findManyEntries("COMMANDS",selectionCriteria).sort("TIMESTAMP",1)
		return self.cursorToList(unreadCommandsCursor)

	def incrementBoardCommand(self,SESSION_ID,TIMESTAMP,TEAM_NAME):
		selectionCriteria = {
			"SESSION_ID":SESSION_ID,
			"TIMESTAMP" :TIMESTAMP
			}

		updateCriteria = {"$push" : {"READ": TEAM_NAME}}
		self.upsertEntryToCollection("COMMANDS",selectionCriteria,updateCriteria)

	def wipeSessionIdFlags(self):
		self.urbanDb["DICTIONARY"].update_many({}, {"$set": {"SESSION_ID_USED" : 0 }})

	def generateSessionId(self):
		#generates an unused random word in the dictionary to use as the session id
		minSessionIdLen,maxSessionIdLen = 10,20
		regexFilter = "^[a-zA-Z]{12,20}$"

		#get a word that hasn't been a session id before but has been used
		# (so it can be used as a category by curious players)
		acceptableWord = self.findOneEntry("DICTIONARY",
			{"WORD":{"$regex":regexFilter},"VIEWED":1,"SESSION_ID_USED":0},
			{"WORD":1,"_id":0})

		#if none is found, try an unused one
		if (not acceptableWord):
			acceptableWord = self.findOneEntry("DICTIONARY",
				{"WORD":{"$regex":regexFilter},"VIEWED":0,"SESSION_ID_USED" : 0},
				{"WORD":1,"_id":0})

			#if one is Still not found, reset all words session ids
			if (not acceptableWord):
				self.wipeSessionIdFlags()

				acceptableWord = self.findOneEntry("DICTIONARY",
				{"WORD":{"$regex":regexFilter},"VIEWED":0,"SESSION_ID_USED":0},
				{"WORD":1,"_id":0})

				#if one is STILL not found, just return an "X"
				if (not acceptableWord): return "X"

		#toggle the session_id_used flag and return it
		selectionCriteria = {"WORD":acceptableWord["WORD"]}
		updateCriteria = {"$inc" : {"SESSION_ID_USED": 1}}
		self.upsertEntryToCollection("DICTIONARY",selectionCriteria,updateCriteria)

		return acceptableWord["WORD"]

	def validateSessionId(self,WORD):
		#checks if a word is a valid session id
		validId = self.findOneEntry("DICTIONARY",
			{"WORD":WORD,"SESSION_ID_USED" : 1})

		if validId: return 1

		return 0

	def getGameSettings(self,SESSION_ID):
		return self.findOneEntry("GAME_SETTINGS",
			{"SESSION_ID":SESSION_ID,},
			{"QUESTIONS_PER_CATEGORY" : 1,"CURRENCY": 1,"_id":0}
			)

	def postGameSettings(self,SESSION_ID,QUESTIONS_PER_CATEGORY,CURRENCY):
		self.addEntryToCollection("GAME_SETTINGS",
			{"SESSION_ID":SESSION_ID,
			"QUESTIONS_PER_CATEGORY":QUESTIONS_PER_CATEGORY,
			"CURRENCY":CURRENCY})


	def addUserEntry(self,ENTRY,SESSION_ID):
		TIMESTAMP = getCurrentTime()
		self.addEntryToCollection("USER_ENTRIES",
			{"ENTRY":ENTRY,"SESSION_ID" : SESSION_ID,"TIMESTAMP":TIMESTAMP}
			)

	def findViewedWords(self):
		viewedWords = self.findManyEntries("DICTIONARY",
			{"VIEWED":1},
			{"WORD":1,"_id":0}).distinct('WORD')
		return viewedWords

	def findRatedWords(self):
		ratedCursor = self.findManyEntries("DICTIONARY",
			{"DIFFICULTY": {"$exists" : 1}},
			{"WORD":1,"DIFFICULTY":1,"_id":0})

		ratedDict = {}
		for ratedWord in ratedCursor: ratedDict[ratedWord["WORD"]] = ratedWord["DIFFICULTY"]
		return ratedDict

	def closeConnection(self):
		self.urbanDb.client.close()


import time


def testUDDH():
	uDDH = urbanDictionaryDatabaseHandler()
	# uDDH.wipeSessionIdFlags()
	# uDDH.createTables()
	# print (uDDH.findViewedWords())
	# print (uDDH.findRatedWords())

	# print (uDDH.generateSessionId())
	# print (uDDH.getRandomEntry())
	# startTime = time.perf_counter()

	# numTrials = 10

	# for trial in range(numTrials):
	# 	uDDH.findRandomCategory()

	# uDDH.dropAllCollections()

	# commands = uDDH.getBoardCommands("bootinization")
	# totalTime = time.perf_counter() - startTime
	# print (totalTime/numTrials)

	# print (commands)

	# CRITERIA = "tough"
	# categories = ["InDef","Tag","InWord"]

	# uDDH.findWordsByCriteria(CRITERIA,categories,INCLUDE_EXAMPLE = True,NUM_TO_GET = 5)

	# uDDH.urbanDb.drop_collection("USER_ENTRIES")
	# uDDH.urbanDb.drop_collection("COMMANDS")
	
	# uDDH.createTables()

	# print (uDDH.addWordToDict(
	# 	WORD = WORD,
	# 	DEFINITION = DEFINITION,
	# 	UPVOTES = UPVOTES,
	# 	DOWNVOTES = DOWNVOTES,
	# 	DATE = DATE,
	# 	TAGS = TAGS,
		# EXAMPLE = "Hello"
	# 	)
	# )

	# commandType = "Add Team"
	# commandData = "Tea"
	# uDDH.postBoardCommand(COMMAND_TYPE = commandType,COMMAND_DATA = commandData)

	# commandType = "Add Team"
	# commandData = "Team"
	# uDDH.postBoardCommand(COMMAND_TYPE = commandType,COMMAND_DATA = commandData)

	# commandType = "Active Team"
	# commandData = "Team1"
	# uDDH.postBoardCommand(COMMAND_TYPE = commandType,COMMAND_DATA = commandData)

	# randomCatDict = uDDH.findRandomCategory()
	# print (randomCatDict)
	# commandType = "Add Category"
	# commandData = randomCatDict
	# uDDH.postBoardCommand(COMMAND_TYPE = commandType,COMMAND_DATA = commandData)

	# commandType = "Start Game"
	# commandData = ""
	# uDDH.postBoardCommand(COMMAND_TYPE = commandType,COMMAND_DATA = commandData)

	# commandType = "Select Question"
	# commandData = 0
	# uDDH.postBoardCommand(COMMAND_TYPE = commandType,COMMAND_DATA = commandData)

	# commandType = "Update Score"
	# commandData = {"Tea":500}
	# uDDH.postBoardCommand(COMMAND_TYPE = commandType,COMMAND_DATA = commandData)

	# commandType = "End Question"
	# commandData = 0
	# uDDH.postBoardCommand(COMMAND_TYPE = commandType,COMMAND_DATA = commandData)

	# boardCommands = uDDH.getBoardCommands()
	# print (boardCommands)

	# print (uDDH.findManyEntries("DICTIONARY",{}).count())
	# uDDH.dropCollection("GAME_SETTINGS")
	# uDDH.printAllEntries("DICTIONARY")
	# uDDH.printAllEntries("COMMANDS")

	uDDH.printAllEntries("COMMANDS")

	uDDH.closeConnection()

# testUDDH()