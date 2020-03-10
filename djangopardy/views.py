from django.shortcuts import render, render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_http_methods

import json

import sys
sys.path.insert(0, "static/")

from urbanDictionaryDb import UrbanDictionaryDatabaseHandler
uDDH = UrbanDictionaryDatabaseHandler()

def readPostJson(requestIn):
	requestBody = requestIn.body
	requestString = requestBody.decode('utf-8')
	jsonData = json.loads(requestString)
	return jsonData
	
####Jeopardy Functions
@require_http_methods(["GET"])
def randomCategory(request):
	randomCategoryName = uDDH.getRandomEntry()["WORD"].lower()
	return JsonResponse({"CATEGORY" : randomCategoryName})

@require_http_methods(["GET"])
def getCommands(request,sessionId,teamName):
	commands = uDDH.getBoardCommands(sessionId,teamName)

	for command in commands:
		uDDH.incrementBoardCommand(SESSION_ID = sessionId,TIMESTAMP = command["TIMESTAMP"],TEAM_NAME = teamName)
	
	return JsonResponse(commands, safe=False)

@require_http_methods(["POST"])
@csrf_exempt
def postCategory(request,sessionId):
	postData = readPostJson(request)

	categoryName = postData["CATEGORY"]

	# if categoryName == "_RANDOM_":
	# 	categoryName = uDDH.getRandomEntry()["WORD"].lower()
		# categoryName = ""
	# else:

	categoryName = categoryName.lower()

	searchCriteria = postData["SEARCH_CRITERIA"]
	sortKey = postData["SORT_KEY"].upper()
	questionsToGet = postData["QUESTIONS_PER_CATEGORY"]
	includeExample = postData["INCLUDE_EXAMPLE"]

	outputWords = uDDH.findWordsByCriteria(
		CRITERIA = categoryName,
		categories = searchCriteria,
		NUM_TO_GET = questionsToGet,
		INCLUDE_EXAMPLE=includeExample,
		SORT_KEY = sortKey)

	if not outputWords: 
		print ("NOTHING FOUND!")
		return

	commandData = {
		"QUESTIONS" : outputWords,
		"CATEGORY" : categoryName,
		"MODES" : searchCriteria
	}

	uDDH.postBoardCommand(COMMAND_TYPE = "Add Category",COMMAND_DATA = commandData,SESSION_ID = sessionId,SENDER = "moderator")

	# print (outputWords)

	return JsonResponse(commandData)

def moderatorLogin(postData):
	numQuestions = postData["QUESTIONS_PER_CATEGORY"]
	currency = postData["CURRENCY"]

	# get a sessionId
	sessionId = uDDH.generateSessionId()

	# add this games setting's to the db
	uDDH.postGameSettings(SESSION_ID = sessionId,QUESTIONS_PER_CATEGORY= numQuestions,CURRENCY = currency)

	return JsonResponse({"SESSION_ID":sessionId})

def spectatorLogin(postData):
	sessionId = postData["SESSION_ID"]

	#get the game settings and existing spectators
	gameSettings = uDDH.getGameSettings(SESSION_ID = sessionId)

	# check if the session id is valid
	if not gameSettings: return

	questionsPerCategory = gameSettings["QUESTIONS_PER_CATEGORY"]
	currency = gameSettings["CURRENCY"]
	#get the existing number of spectators
	existingSpectators = gameSettings["NUM_SPECTATORS"]

	#create a unique spectator id
	spectatorTeamName = "spectator" + str(existingSpectators + 1)

	#update the number of spectators
	uDDH.incrementSpectatorCount(sessionId)

	return JsonResponse({"TEAM_NAME":spectatorTeamName, "CURRENCY" : currency,"QUESTIONS_PER_CATEGORY": questionsPerCategory})

	# 	def getGameSettings(self,SESSION_ID):
	# return self.findOneEntry("GAME_SETTINGS",
	# 	{"SESSION_ID":SESSION_ID,},
	# 	{"QUESTIONS_PER_CATEGORY" : 1,"CURRENCY": 1,"_id":0}
	# 	)

def contestantLogin(postData):
	sessionId = postData["SESSION_ID"]
	teamName = postData["TEAM_NAME"]
	buzzerSound = postData["BUZZER_SOUND"]

	#get the game settings and existing spectators
	gameSettings = uDDH.getGameSettings(SESSION_ID = sessionId)

	# check if the session id is valid
	if not gameSettings: return

	existingTeams = gameSettings["TEAMS"]
	#check the team name isnt already taken
	if teamName in existingTeams:
		return

	questionsPerCategory = gameSettings["QUESTIONS_PER_CATEGORY"]
	currency = gameSettings["CURRENCY"]

	commandType = "Add Team"
	commandData = {
		"TEAM_NAME" : teamName,
		"BUZZER_SOUND" : buzzerSound,
	}

	uDDH.postBoardCommand(COMMAND_TYPE = commandType,COMMAND_DATA = commandData,SESSION_ID = sessionId,SENDER = teamName)

	return JsonResponse({"CURRENCY" : currency,"QUESTIONS_PER_CATEGORY": questionsPerCategory})

@require_http_methods(["POST"])
@csrf_exempt
def login(request,loginType):
	postData = readPostJson(request)

	if loginType == "moderator":
		return moderatorLogin(postData)
	elif loginType == "spectator":
		return spectatorLogin(postData)
	else:
		return contestantLogin(postData)

@require_http_methods(["POST"])
@csrf_exempt
def postCommand(request,sessionId,teamName):
	postedCommand = readPostJson(request)

	commandType = list(postedCommand.keys())[0]
	commandData = list(postedCommand.values())[0]
	uDDH.postBoardCommand(COMMAND_TYPE = commandType,COMMAND_DATA = commandData,SESSION_ID = sessionId,SENDER = teamName)
	return JsonResponse({});