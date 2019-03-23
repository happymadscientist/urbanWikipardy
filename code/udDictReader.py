import json
import os

try:
	fileDir = "static"
	os.listdir(fileDir)
except:
	fileDir = os.path.join("urbanWikipardy","static")

filePath = os.path.join(fileDir,"words.json")

# def createQuestionAnswerDict(wordJson):
# 	#check that its somewhat popular
# 	numUpvotes = wordJson["thumbs_up"]
# 	if numUpvotes < 30: return 0
# 	#check thats its not too disliked
# 	if wordJson["thumbs_down"] > 50: return 0

# 	wordDef = wordJson["definition"]

# 	#check that its not too long of a definition
# 	if len(wordDef) > 300: return 0

# 	word = wordJson["lowercase_word"]

# 	#check that the answer is not in the definition
# 	if word.lower() in wordDef.lower(): return 0

# 	definition = wordDef.replace("\n"," ").replace("\r"," ").replace(","," ").replace("\t","").replace("[","").replace("]","")
# 	return {word : definition}


# def getJeopardyDict(criteria,numQuestions,mode):
# 	questionsList = []
# 	lowerCriteria = criteria.lower()

# 	with open(filePath,"r") as file:
# 		while len(questionsList) < (numQuestions+1):
# 			try:
# 				newLine = file.readline()
# 				if not newLine:
# 					print ("End of file")
# 					return 0
# 				fullDef = json.loads(newLine)

# 			except: fullDef = {"lowercase_word":"","definition":"","tags":""}

# 			if mode == "InWord":
# 				word = fullDef["lowercase_word"]
# 				if lowerCriteria in word:
# 					questionDict = createQuestionAnswerDict(fullDef)
# 					if (questionDict): questionsList.append(questionDict)

# 			elif mode == "InDef":
# 				definition = fullDef["definition"]
# 				if lowerCriteria in definition.lower():
# 					questionDict = createQuestionAnswerDict(fullDef)
# 					if (questionDict): questionsList.append(questionDict)

# 			elif mode == "Tag":
# 				tags = fullDef["tags"]
# 				for tag in tags:
# 					if lowerCriteria in tag.lower():
# 						questionDict = createQuestionAnswerDict(fullDef)
# 						if (questionDict): questionsList.append(questionDict)

# 		file.close()
# 		return questionsList

# def populateCategories(categories,questionsPerCategory):
# 	questionsDict = {}
# 	categoriesFull = {}
# 	lowerCategoriesDict = {}

# 	for category in categories:
# 		questionsDict[category] = []
# 		categoriesFull[category] = False
# 		lowerCategoriesDict[category.lower()] = category

# 	lowerCategoriesList = list(lowerCategoriesDict.keys())

# 	allCategoriesFull = 0

# 	with open(filePath,"r") as file:
# 		while allCategoriesFull != True:
# 			try:
# 				fullDef = json.loads(file.readline())
# 			except:
# 				fullDef = {"tags":[]}

# 			tags = fullDef["tags"]
# 			for tag in tags:
# 				if tag.lower() in lowerCategoriesList:
# 					realCategoryName = lowerCategoriesDict[tag]
# 					#check that the word isn't already in there
# 					alreadyAdded = False
# 					for wordDict in questionsDict[realCategoryName]:
# 						if fullDef["lowercase_word"] == list(wordDict.keys())[0]: alreadyAdded = True
# 					if alreadyAdded: continue

# 					#check to make sure this category isn't already full
# 					if categoriesFull[realCategoryName]: continue

# 					questionAnswerDict = createQuestionAnswerDict(fullDef)
# 					if questionAnswerDict:
# 						questionsDict[realCategoryName].append(questionAnswerDict)
# 					# else:
# 						# print ("failed")

# 					#check if this category is full, and if so set its entry to true
# 					if len(questionsDict[realCategoryName]) >= questionsPerCategory:
# 						categoriesFull[realCategoryName] = True

# 						#check if all of them are full
# 						allFull = True
# 						for value in categoriesFull.values():
# 							if not value: allFull = False
# 						if allFull:

# 							for key,value in questionsDict.items():
# 								print (key)
# 								for jeapEntry in value:
# 									print (jeapEntry)
# 							file.close()
# 							return questionsDict
# 	file.close()
# 	print ("NOT ENOUGH")
# 	for key,value in questionsDict.items():
# 		print (key)
# 		for word,definition in value.items():
# 			print (word,definition)

# 	return (questionsDict)

from urbanDictionaryDb import urbanDictionaryDatabaseHandler
uDDH = urbanDictionaryDatabaseHandler()
uDDH.createTables()

maxDefinitionLength = 150
maxExampleLength = 150
minDefinitionLength = 2

def loadJeopardyDictIntoDb():
	index = 0
	wordInDefs = 0
	tooLongs = 0
	tooShorts = 0
	parseIndex = 0
	failIndex = 0
	success = 0
	mongoFail = 0
	exampleTooLongs = 0

	with open(filePath,"r") as file:
		while True :
			index +=1
			try:
				newLine = file.readline()
				if not newLine:
					break

				fullDef = json.loads(newLine)

				try:
					wordDef = fullDef['definition']
					definition = wordDef.replace("\n"," ").replace("\r"," ").replace("\t","").replace("[","").replace("]","")

					#check that its not too long of a definition
					if len(definition) > maxDefinitionLength:
						tooLongs += 1
						continue

					#check that its not too short of a definition
					if len(definition) < minDefinitionLength:
						tooShorts += 1
						continue

					word = fullDef["lowercase_word"]
					tags = fullDef["tags"]

					#check that the answer is not in the definition
					if word.lower() in definition.lower():
						wordInDefs += 1
						continue

					upvotes = fullDef["thumbs_up"]
					downvotes = fullDef["thumbs_down"]
					example = fullDef["example"].replace("\n"," ")

					#check that the example isnt too long
					if len(example) > maxExampleLength:
						exampleTooLongs += 1
						continue

					mongoSuccess = 0
					mongoSuccess = uDDH.addWordToDict(
							WORD = word,
							DEFINITION = definition,
							UPVOTES = upvotes,
							DOWNVOTES = downvotes,
							TAGS = tags,
							EXAMPLE = example
							)

					if not mongoSuccess:
						mongoFail += 1
					else:
						success += 1

				except Exception as e:
					parseIndex += 1
					print (e)
			except Exception as e:
				failIndex += 1
				continue

		file.close()
		print ("End of file", index,parseIndex)
		print ("read fails", failIndex)
		print ("Too long", tooLongs)
		print ("Example too long", exampleTooLongs)
		print ("Too short", tooShorts)
		print ("Word in def", wordInDefs)
		print ("Mongo fail", mongoFail)
		print ("Success",success)
		totalAccountedFor = tooLongs + tooShorts + wordInDefs + mongoFail + success + failIndex
		print ("total" , totalAccountedFor)
		uDDH.closeConnection()


loadJeopardyDictIntoDb()