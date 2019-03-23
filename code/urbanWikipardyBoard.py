from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Plot
from bokeh.models.widgets import Div
from bokeh.models.glyphs import Text, MultiLine, Rect
from bokeh.io import curdoc, show

import numpy as np
from datetime import datetime

from jsHandler import jsHandler

class urbanWikipardyBoard():
	#class to display an urban wikipardy board
	def __init__(self,sessionId = "",admin = 0,scoreType = "dollars",questionsPerCategory = 4):
		self.boardJsHandler = jsHandler()

		self.questionsPerCategory = questionsPerCategory
		self.scoreType = scoreType
		self.sessionId = sessionId
		self.admin = admin

		self.startup()

	def startup(self):
		self.setupVariables()

		self.createQuestionWindow()
		self.createBoardWindow()
		self.createScoreWindow()

		self.setupGui()

	def triggerAlert(self,alertText):
		print (alertText)
		self.boardJsHandler.triggerAlert(alertText)

	########## BOARD SETUP ###########################
	def setupVariables(self):
		#questions last 10 seconds
		self.questionDuration = 10

		self.boardHeight = 600
		self.boardWidth = 1200

		self.scoreWidth = self.boardWidth
		self.scoreHeight = self.boardHeight // 2

		self.questions = {}
		self.titles = list(self.questions.keys())

		self.teamNameFontSize = '24pt'
		if self.scoreType == "dollars":
			self.teamScoreFontSize = '60pt'
		else:
			self.teamScoreFontSize = '40pt'

		self.questionFontSize = '30pt'
		self.dollarTextFontSize = '45pt'
		self.titleFontSize = '20pt'

		self.numCategories = len(self.titles)
		self.numQuestions = self.numCategories * self.questionsPerCategory

		self.xRange = (0,self.numCategories)
		self.yRange = (0,self.questionsPerCategory + 1)
		self.numCols = self.numCategories
		self.numRows = self.questionsPerCategory

		self.gameStarted = 0		

		self.hellaWikipardyBets = {}
		self.hellaWikipardyEntries = {}
		self.hellaWikipardyDrawn = False

		self.buzzerSounds = {}

	def generateGridLineCoords(self,xTicks,yTicks):
		#generates coordinates for a grid
		boardWidth, boardHeight = xTicks[-1], yTicks[-1]

		lineXs = []
		lineYs = []

		#add the vertical line coordinates
		for xTick in xTicks:
			xCoords = [xTick,xTick]
			yCoords = [0,boardHeight]

			lineXs.append(xCoords)
			lineYs.append(yCoords)

		for yTick in yTicks:
			xCoords = [0,boardWidth]
			yCoords = [yTick,yTick]

			lineXs.append(xCoords)
			lineYs.append(yCoords)

		return lineXs,lineYs

	def createScoreWindow(self):
		scoreWindow = self.createBlankFigure(xRange = (0,1),yRange = (0,1),height = self.scoreHeight,width = self.scoreWidth)
	
		# scoreWindow.on_event(Tap,self.scoreClickCallback)
		# scoreWindow.on_event(DoubleTap,self.scoreClickCallback)

		self.scoreAdded = 0
		self.numTeams = 0
		self.questionValue = 0

		self.buzzColors = ["green","yellow","red"]
		self.buzzedTeams = []

		self.teamSource = ColumnDataSource(dict(x=[], scoreX =[], nameY=[], scoreY=[], names=[], scores=[],alphas = [],buzzX=[],buzzAlphas = [],buzzColors = []))

		teamNameText = Text(x = "x",y = "nameY",text = "names",text_alpha="alphas",
			text_color = "white", text_font_size = self.teamNameFontSize,
			text_font = "gyparody", text_align="center",text_baseline="middle")
		scoreWindow.add_glyph(self.teamSource, teamNameText)

		teamScoreText = Text(x = "scoreX",y = "scoreY",text = "scores",text_alpha="alphas",
			text_color = "white", text_font_size = self.teamScoreFontSize,
			text_font = "gyparody",text_align="center",text_baseline="middle")
		scoreWindow.add_glyph(self.teamSource, teamScoreText)

		teamBuzzRects = Rect(x = "buzzX", y = .5, width=.8,height=.8, angle=0,line_color="buzzColors",line_width=10,line_alpha="buzzAlphas",fill_alpha = 0)
		scoreWindow.add_glyph(self.teamSource,teamBuzzRects)

		self.scoreWindow = scoreWindow

	def createQuestionWindow(self):
		questionText = "Who was\n blah blah blah"

		questionWindow = self.createBlankFigure(xRange = (0,1),yRange = (0,1),height = self.boardHeight,width = self.boardWidth)
		self.questionSource = ColumnDataSource(dict(x=[0.5], y=[0.5], text=[questionText]))

		# questionWindow.on_event(Tap,self.questionClickCallback)

		questionTextGlyph = Text(x="x", y="y", text="text", angle=0,
			text_font_size = self.questionFontSize, text_align="center",text_baseline="middle",
			text_color="white",text_font = "gyparody")
		questionWindow.add_glyph(self.questionSource, questionTextGlyph)

		#create the glyph for the hella wikipardy window
		self.hellaWikipardySource = ColumnDataSource(data = dict(x=[],y=[]))

		questionWindow.scatter(x="x", y="y",source = self.hellaWikipardySource, radius=.005,
				fill_color="white", fill_alpha=0.8, line_color=None)

		self.hellaWikipardyNameSource = ColumnDataSource(dict(x=[], y=[], names=[]))
		self.hWTeamNameFontSize = "20pt"

		teamNameText = Text(x = "x",y = "y",text = "names",text_color = "white",text_alpha=1.0,text_font_size = self.hWTeamNameFontSize,text_font = "gyparody")
		questionWindow.add_glyph(self.hellaWikipardyNameSource, teamNameText)

		self.questionWindow = questionWindow

	def createBlankFigure(self,xRange,yRange,height,width):
		fig = figure(x_range = xRange,y_range = yRange,
			background_fill_color = "blue",
			title=None, plot_width=width, plot_height=height,
			css_classes = ["hello"],
			toolbar_location=None,tools= "" #, min_border=0,
			)

		fig.grid.visible = False
		fig.axis.visible = False

		return fig

	def createBoardWindow(self):
		mainWindow = self.createBlankFigure(xRange = self.xRange,yRange = self.yRange,height = self.boardHeight,width = self.boardWidth)
		# mainWindow.on_event(Tap,self.boardClickCallback)

		self.titleSource = ColumnDataSource(dict(x=[], y=[], text=[]))

		titleText = Text(x = "x",y = "y",text = "text",text_color = "white",text_font_size = self.titleFontSize,text_font = "gyparody",text_align="center",text_baseline="middle")
		mainWindow.add_glyph(self.titleSource, titleText)

		#dollar signs for questions
		#["$100","$200","$300","$400","$500"][::-1]
		if self.scoreType == 'dollars':
			self.baseVals = ["$%s" % (val*100) for val in range(1,self.questionsPerCategory + 1) ][::-1]
		else:
			drinkVals = ['Huff','Sip','Taste','Swig','Drink','Chug','Guzzle','Finish']
			self.baseVals = drinkVals[:self.questionsPerCategory][::-1]

		self.dollarSource = ColumnDataSource(dict(x=[], y=[], text=[],alpha = []))

		dollarText = Text(x="x", y="y", text="text", angle=0,text_alpha = "alpha",text_font_size = self.dollarTextFontSize, text_color="orange",text_font = "gyparody",text_align="center",text_baseline="middle")
		mainWindow.add_glyph(self.dollarSource, dollarText)

		#draw the gridlines
		xTicks = np.linspace(self.xRange[0],self.xRange[1],self.numCols+1)
		yTicks = np.linspace(self.yRange[0],self.yRange[1],self.numRows+2)

		lineXs,lineYs = self.generateGridLineCoords(xTicks,yTicks)

		self.gridSource = ColumnDataSource(dict(xs=lineXs, ys=lineYs))
		gridLine = MultiLine(xs="xs", ys="ys", line_color="#000000", line_width=2)
		mainWindow.add_glyph(self.gridSource, gridLine)

		self.boardWindow = mainWindow

	def setupGui(self):
		headerDiv = Div(text="<link rel='stylesheet' type='text/css' href='code/static/styles.css'>")

		self.gui = column(
			self.boardWindow,
			self.scoreWindow,
			self.boardJsHandler.div,
			headerDiv,
		name = "User GUI"
		)

	############ GAME SETUP

	def updateBoardWindow(self,categoryName):
		#called when a new category is added, adds a new column to the board

		#update titles
		titleX = self.numCategories + .5
		titleY = self.questionsPerCategory + .5

		#add new lines to the title
		titleCharactersPerLine = 13
		titleText = self.addNewLinesToQuestion(categoryName,charactersPerLine = titleCharactersPerLine)

		newTitleDict = {"x":[titleX],"y":[titleY],"text":[titleText]}
		self.titleSource.stream(newTitleDict)

		#update dollar sign text
		categoryDollarText = self.baseVals
		xs = [self.numCategories + .5] * self.questionsPerCategory

		ys = range(self.questionsPerCategory)
		ys = np.array(ys) + [.5]

		dollarAlphas = [1] * self.questionsPerCategory

		newDollarDict = dict(x=xs, y=ys, text=categoryDollarText,alpha = dollarAlphas)
		self.dollarSource.stream(newDollarDict)

		#update grid lines
		self.xRange = (0,self.numCategories + 1)
		self.yRange = (0,self.questionsPerCategory + 1)

		xTicks = np.linspace(self.xRange[0],self.xRange[1],self.numCategories + 2)
		yTicks = np.linspace(self.yRange[0],self.yRange[1],self.questionsPerCategory+2)

		lineXs,lineYs = self.generateGridLineCoords(xTicks,yTicks)

		self.gridSource.data = dict(xs=lineXs, ys=lineYs)

		self.boardWindow.x_range.end = self.numCategories + 1

	def addTeam(self,teamName):
		teamX = self.numTeams + .2
		teamScoreX = teamX + .2
		teamBuzzX = self.numTeams + .5
		buzzColor = "black"

		if len(teamName) > 10:
			teamName = teamName[:10] + "-\n-" + teamName[10:]

		teamNameY = .75
		teamScoreY = .25
		if self.scoreType == "dollars":
			teamScore = "$0"
		else:
			teamScore = "0 beers"

		teamAlpha = 1.0

		newTeamDict = dict(
			x=[teamX], 
			scoreX =[teamScoreX], 
			nameY=[teamNameY], 
			scoreY=[teamScoreY], 
			names=[teamName], 
			scores=[teamScore],
			alphas = [teamAlpha],
			buzzX = [teamBuzzX],
			buzzAlphas = [0],
			buzzColors = [buzzColor]
			)

		self.teamSource.stream(newTeamDict)

		self.numTeams += 1
		self.scoreWindow.x_range.end = self.numTeams

	def addCategoryDict(self,categoryDict):
		categoryQuestions = categoryDict["QUESTIONS"]
		categoryName = categoryDict["NAME"]
		categoryModes = categoryDict["MODES"]

		newTitle = self.getCategoryTitle(categoryName,categoryModes)

		newCategoryDict = {newTitle: categoryQuestions}

		self.questions = {**self.questions, **newCategoryDict}

		self.titles.append(newTitle)
		self.updateBoardWindow(newTitle)
		self.numCategories +=1


	#GAME START

	def startGame(self):
		if self.gameStarted == 0:
			#if there are no teams, cannot start games
			if self.numTeams == 0:
				return 0

			self.setupGameVariables()
			self.gameStarted = 1
			return 1
		else:
			self.gameStarted = 0

			#restart everyones scores
			# self.teamSource
			#reset every question status
			# self.gui.children[1].children = [self.controlsColumn]

			return 1
	
	def generateHellaWikipardyIndex(self):
		hellaWikipardyIndex = np.random.randint(self.numCategories * self.questionsPerCategory)
		return hellaWikipardyIndex

	def setupGameVariables(self):

		self.xRange = (0,self.numCategories)
		self.yRange = (0,self.questionsPerCategory + 1)
		self.numCols = self.numCategories
		self.numRows = self.questionsPerCategory
		self.numQuestions = self.numCategories * self.questionsPerCategory
		self.activeTeam = self.teamSource.data["names"][0]
		self.updateActiveTeam(self.activeTeam)

	#GAME PLAY
	def updateActiveTeam(self,teamName):
		#check if a team name was passed or if no team is active
		if teamName:
			#find the index of the team
			teamIndex = self.teamSource.data["names"].index(teamName)
			self.activeTeam = teamName
			newAlphas = [.7] * self.numTeams
			newAlphas[teamIndex] = 1.0
		else:
			newAlphas = [1.0] * self.numTeams

			self.activeTeam = ""

		self.teamSource.data["alphas"] = newAlphas

	def updateTeamScore(self,teamScoreDict):
		teamName = list(teamScoreDict.keys())[0]
		score = teamScoreDict[teamName]
		self.addScoreToTeam(teamName,score)

	def addScoreToTeam(self,teamName,score):
		teamIndex = self.teamSource.data["names"].index(teamName)
		prevScores =  self.teamSource.data["scores"]

		#get the current score for the team
		prevTeamScoreStr = prevScores[teamIndex]

		#if hella wikipardy is drawn, then get the bet for this team
		if self.hellaWikipardyDrawn:
			score = self.hellaWikipardyBets[teamName]

		#if score mode is dollars, convert it to int by stripping dollar sign
		if self.scoreType == "dollars":
			#turn it from a dollar amount string to an int
			prevTeamScore = int(prevTeamScoreStr.replace("$",""))
			newTeamScore = prevTeamScore + score

		else:
			prevTeamScore = float(prevTeamScoreStr.replace(" beers",""))
			newTeamScore = prevTeamScore + round(score/600,2)

		newTeamScore = round(newTeamScore,2)

		#check if the buzzed team got it wrong
		if (score < -50):
			#increment buzz orders
			self.deBuzzTeam(teamName)


		#check if the active team got the questions right
		if (score) > 50:
			self.pointsAdded = True
			self.updateActiveTeam(teamName)

			#if correct, remove the buzzers and delete the teams
			self.clearBuzzers()
			self.buzzedTeams = []


		#convert it back to a string
		if self.scoreType == "dollars":
			if newTeamScore<0: newTeamScoreStr = "-$" + str(abs(newTeamScore))
			else: newTeamScoreStr = "$" + str(newTeamScore)
		else:
			newTeamScoreStr = str(newTeamScore) + " beers"
			
		prevScores[teamIndex] = newTeamScoreStr
		self.teamSource.data["scores"] = prevScores

	# def scoreClickCallback(self,event):
	# 	xClick,yClick = int(event.x),int(event.y)
	# 	clickedTeamIndex = int(xClick)
	# 	clickedTeam = self.teamSource.data["names"][clickedTeamIndex]

	# 	baseBonus = 5
	# 	bonusPoints = len(self.bonusPointsControls.active) * baseBonus
	# 	self.bonusPointsControls.active = []

	# 	if (bonusPoints):
	# 		questionValue = bonusPoints

	# 	else:
	# 		#single tap is to add positive score
	# 		if event.event_name == "tap": questionValue = self.questionValue + bonusPoints
	# 		else: questionValue = -self.questionValue + bonusPointsTitle

	# 	self.postScoreUpdate(clickedTeam,questionValue)
	# 	# self.addScoreToTeam(clickedTeam,self.questionValue + bonusPoints)
	# 	# self.addScoreToTeam(clickedTeam,-self.questionValue + bonusPoints)

	#HELPER FUNCTIONS
	def getCategoryTitle(self,categoryName,categoryModes):
		newTitle = ""
		if "InWord" in categoryModes: newTitle += "\"" + categoryName + "\" in word"

		if "InDef" in categoryModes: 
			#if its already been added to, add an & and a new line
			if newTitle: newTitle += " & "
			newTitle += "\"" + categoryName + "\" in def"

		if "Tag" in categoryModes:
			if newTitle: newTitle += " & "
			newTitle += categoryName


		return newTitle

	def getCurrentTime(self):
		return (int(datetime.now().timestamp()))

	def coordsToRowCol(self,xCoord,yCoord):
		xInd = xCoord % (self.xRange[-1])
		yInd = yCoord % (self.yRange[-1])
		return (xInd,yInd)

	def rowColToIndex(self,row,col):
		return self.questionsPerCategory*row + col

	def addNewLinesToQuestion(self,questionText,charactersPerLine = 45):
		# charactersPerLine = 20
		outputQuestion = ""
		lastIndex = 0
		#start at the end of the first line
		characterIndex = charactersPerLine
		while characterIndex < len(questionText):
			#get the character at where your line should end
			charAtIndex = questionText[characterIndex]
			#if it's a space, it's ok it advance to the next character
			if charAtIndex == " ":
				outputQuestion += (questionText[lastIndex:characterIndex] + "\n")
				lastIndex = characterIndex
				characterIndex += charactersPerLine
			characterIndex += 1
		#add the last line
		outputQuestion += questionText[lastIndex:]
		return outputQuestion



	def switchToQuestion(self,category,questionIndex,hellaWikipardy = False):
		#check if hella wikipardy was drawn on the last question, and if so, clear it
		if self.hellaWikipardyDrawn:
			self.hellaWikipardySource.data = dict(x=[],y=[])
			self.hellaWikipardyNameSource.data = dict(x=[],y=[],names=[])
			self.hellaWikipardyDrawn = False

		#returns the word of the question it switched to
		self.pointsAdded = False

		questionAnswerDict = self.questions[category][questionIndex]
		word = list(questionAnswerDict.keys())[0]
		definition = questionAnswerDict[word]

		#if its hella wikipardy, add that to the definition

		self.questionValue = (self.questionsPerCategory-questionIndex) * 100

		#add a callback to see if the question is finished
		# self.questionRefresher = curdoc().add_periodic_callback(self.questionRefreshCallback,100)

		self.startTime = self.getCurrentTime()

		if hellaWikipardy:
			definition = "HELLA wikipardy \n\n" + definition
			self.boardJsHandler.playCustomSound("hellaWikipardy.mp3")

		else:
			self.boardJsHandler.playSound()

		# print ()
		# print ("THE ANSWER:",word)
		# print ("THE QUESTION:", definition)
		# print ()

		spacedQuestionText = self.addNewLinesToQuestion(definition)
		self.questionSource.data["text"] = [spacedQuestionText]

		userGui = self.gui.select_one({"name":"User GUI"})
		userGui.children[0] = self.questionWindow

		return word, definition

	def removeDollarText(self,textIndex):
		currentAlphas = self.dollarSource.data["alpha"]
		currentAlphas[textIndex] = 0
		self.dollarSource.data["alpha"] = currentAlphas

	def switchToBoard(self):
		userGui = self.gui.select_one({"name":"User GUI"})
		userGui.children[0] = self.boardWindow
		self.boardJsHandler.stopSound()

		#remove all buzzed teams
		self.clearBuzzers()
		self.buzzedTeams = []

		gameOver = self.checkGameIsFinished()
		if gameOver:
			self.switchToWinnerScreen()

		else:
			#check if no one scored
			if not self.pointsAdded:
				#rotate active team by 1
				teams = self.teamSource.data["names"]
				currentTeamIndex = teams.index(self.activeTeam)
				newTeamIndex = (currentTeamIndex + 1) % self.numTeams
				newActiveTeam = teams[newTeamIndex]
				self.updateActiveTeam(newActiveTeam) 
				#need to advane the active team clockwise by 1

	#GAME END
	def switchToWinnerScreen(self):
		scoreList = self.teamSource.data["scores"]

		if self.scoreType == 'dollars':
			intScoreList = [int(score.lstrip("$")) for score in scoreList]
		else:
			intScoreList = [float(score.replace(" beers","")) for score in scoreList]

		teamList = self.teamSource.data["names"]

		winningScore = max(intScoreList)
		winningIndex = intScoreList.index(winningScore)
		winningTeam = teamList[winningIndex]

		losingScore = min(intScoreList)
		losingIndex = intScoreList.index(losingScore)
		losingTeam = teamList[losingIndex]

		if self.scoreType == 'dollars':
			endString = "Winner: %s with $%s \n Loser: %s with $%s" % (winningTeam,winningScore,losingTeam,losingScore)
		else:
			endString = "Winner: %s with %s beers \n Loser: %s with %s beers" % (winningTeam,winningScore,losingTeam,losingScore)
		self.questionSource.data["text"] = [endString]
		
		userGui = self.gui.select_one({"name":"User GUI"})
		userGui.children[0] = self.questionWindow

	def checkGameIsFinished(self):
		boardClickStatus = self.dollarSource.data["alpha"]
		if not np.any(np.array(boardClickStatus)): return 1
		return 0

	def questionClickCallback(self,event):
		self.postEndQuestion()
		# self.switchToBoard()

	def buzzCallback(self,teamName):
		if not self.gameStarted: return
		if teamName in self.buzzedTeams: return
		self.buzzInTeam(teamName)

	def buzzInTeam(self,teamName):
		if teamName:
			#check if the team is already buzzed in
			if teamName not in self.buzzedTeams: 
				#add the team to the acitvely buzzed teams
				self.buzzedTeams.append(teamName)

			#find the index of the team
			teamIndex = self.teamSource.data["names"].index(teamName)

			#update its color
			currentBuzzColors = self.teamSource.data["buzzColors"]

			#get the color of the corrosponding buzz place
			buzzPlace = self.buzzedTeams.index(teamName)
			buzzColor = self.buzzColors[buzzPlace]

			currentBuzzColors[teamIndex] = buzzColor

			self.teamSource.data["buzzColors"] = currentBuzzColors

			#update its alpha
			currentBuzzAlphas = self.teamSource.data["buzzAlphas"]

			currentBuzzAlphas[teamIndex] = 1.0
			self.teamSource.data["buzzAlphas"] = currentBuzzAlphas

			#stop the current music
			self.boardJsHandler.stopSound()

			#play that team's buzzer music
			teamBuzzerSound = self.buzzerSounds[teamName]
			self.boardJsHandler.playCustomSound(teamBuzzerSound)

		# else:
			# newBuzzAlphas = [0.0] * self.numTeams
			# self.buzzedTeam = ""

		# self.teamSource.data["buzzAlphas"] = newBuzzAlphas

	def clearBuzzers(self):
		self.teamSource.data["buzzColors"] = ["black"]*self.numTeams
		self.teamSource.data["buzzAlphas"] = [0.0] * self.numTeams

	def deBuzzTeam(self,teamName):
		#removes a teams buzz status and updates anyone elses place

		#clear the buzz status
		self.clearBuzzers()

		#remove the team from the list of buzzed teams
		del self.buzzedTeams[0]

		#redraw the buzzed teams in new order
		for buzzedTeam in self.buzzedTeams:
			self.buzzInTeam(buzzedTeam)

	def resetGame(self):
		#resets the game but keeps session ids and teams the same
		self.startup()

	def drawHellaWikipardyEntries(self,drawingDict):
		#updates the hella wikipardy source with the correctly spaced drawings
		self.boardJsHandler.stopSound()

		#remove the question text
		self.questionSource.data["text"] = [""]

		self.numRows = 2

		teamIndex = 0
		for teamName,teamDrawingDict in drawingDict.items():
			#modifies the team x and y and adds it to its corrosponding place on the full window
			teamXoffset = teamIndex // self.numRows
			teamYoffset = teamIndex % self.numRows
			shiftedDrawingXs = (np.array(teamDrawingDict['x']) + teamXoffset) /self.numRows 
			shiftedDrawingYs = (np.array(teamDrawingDict['y']) + teamYoffset) /self.numRows

			newDrawingDict = {"x":list(shiftedDrawingXs),"y":list(shiftedDrawingYs)}
			self.hellaWikipardySource.stream(newDrawingDict)

			teamNameX = (.2 + teamXoffset) / self.numRows
			teamNameY = (.9 + teamYoffset) / self.numRows
			self.hellaWikipardyNameSource.stream({"x":[teamNameX],"y":[teamNameY],"names":[teamName]})
			teamIndex += 1

		self.hellaWikipardyDrawn = True

	def hellaWikipardyCallback(self,drawingDict,teamName,bet):
		print ("HW entry recieved!")
		
		#add the drawing to the list of drawings
		self.hellaWikipardyBets[teamName] = bet

		self.hellaWikipardyEntries[teamName + " " + str(bet)] = drawingDict

		#play that team's buzzer music
		teamBuzzerSound = self.buzzerSounds[teamName]
		self.boardJsHandler.playCustomSound(teamBuzzerSound)

		#check if all teams have entered
		if (len(self.hellaWikipardyEntries) == self.numTeams):
			#draw the team entries on the questionWindow
			self.drawHellaWikipardyEntries(self.hellaWikipardyEntries)

	def selectQuestion(self,selectedQuestionIndex):
		#check that the game has been started
		if self.gameStarted == 0: 
			# self.triggerAlert("Game not started!")
			return 0

		row = selectedQuestionIndex // self.questionsPerCategory
		col = selectedQuestionIndex % (self.questionsPerCategory)

		#check if this index has already been clicked
		boardClickStatus = self.dollarSource.data["alpha"]
		if not boardClickStatus[selectedQuestionIndex]: return

		if selectedQuestionIndex == self.hellaWikipardyIndex: hellaWikipardy = 1
		else: hellaWikipardy = 0

		#allow the new score to be added
		self.scoreAdded = 0
		self.questionValue = row * 100

		clickCategory = self.titles[row]

		self.removeDollarText(selectedQuestionIndex)

		# if hellaWikipardy:
			#if its hella wikipardy, need to play the hella wikipardy window for a bit
			# self.switchToHellaWikipardyMessage()


		word,definition = self.switchToQuestion(clickCategory,col,hellaWikipardy)
		return word,definition, hellaWikipardy

	def runCommand(self,commandType,commandData):
		if (commandType == "Add Team"):
			newTeamName = commandData
			self.addTeam(newTeamName)

		elif (commandType == "Add Buzzer Sound"):
			(teamName,buzzerSound) = commandData
			self.buzzerSounds[teamName] = buzzerSound

		elif (commandType == "Start Game"):
			self.hellaWikipardyIndex = commandData
			self.startGame()

		elif (commandType == "Update Score"):
			teamScoreDict = commandData
			self.updateTeamScore(teamScoreDict)

		elif (commandType == "Add Category"):
			categoryDict = commandData
			self.addCategoryDict(categoryDict)

		elif (commandType == "Active Team"):
			activeTeam = commandData
			self.updateActiveTeam(activeTeam)

		elif (commandType == "Select Question"):
			selectedQuestionIndex = commandData
			self.selectQuestion(selectedQuestionIndex)

		elif commandType == "End Question":
			self.switchToBoard()

		elif commandType == "Buzz In":
			team = commandData
			self.buzzCallback(team)

		elif commandType == "Hella Wikipardy Entry":
			drawingData,bet,team = commandData["DRAWING"],commandData["BET"],commandData["TEAM"]
			self.hellaWikipardyCallback(drawingData,team,bet)

	def showGui(self):
		curdoc().add_root(self.gui)
		curdoc().title = "Urban Wikipardy"
		show(self.gui)


def testUrbanWikipardyBoard():
	uwBoard = urbanWikipardyBoard(scoreType = "drinks")

	from urbanDictionaryDb import urbanDictionaryDatabaseHandler
	uDDH = urbanDictionaryDatabaseHandler()

	uwBoard.addTeam("Test 1")
	uwBoard.addTeam("Test 2")
	uwBoard.addTeam("Test 3")
	# uwBoard.updateActiveTeam("Test 1")

	# randomCategory = uDDH.findRandomCategory()
	# uwBoard.addCategoryDict(randomCategory)

	uwBoard.buzzInTeam("Test 1")
	uwBoard.buzzInTeam("Test 2")
	uwBoard.buzzInTeam("Test 3")

	# uwBoard.deBuzzTeam("Test 1")
	# uwBoard.deBuzzTeam("Test 2")

	# randomCategory = uDDH.findRandomCategory()
	# uwBoard.addCategoryDict(randomCategory)

	# randomCategory = uDDH.findRandomCategory()
	# uwBoard.addCategoryDict(randomCategory)

	# uwBoard.addScoreToTeam("Test 1",100)
	# randomCatName = randomCategory["NAME"]

	# uwBoard.startGame()
	# uwBoard.removeDollarText(0)
	# uwBoard.selectQuestion(0)

	uwBoard.showGui()

# testUrbanWikipardyBoard()



##DEPRECATED
	# def questionRefreshCallback(self):
	# 	#called periodcally to see if the question is over
	# 	timeElapsed = self.getCurrentTime() - self.startTime
	# 	print (timeElapsed)
	# 	if (timeElapsed > self.questionDuration):
	# 		#stop the question sound
	# 		jSP.stopSound()
	# 		#play the buzzer
	# 		# jSP.startSound("Buzzer")
	# 		#remove the periodic callback
	# 		curdoc().remove_periodic_callback(self.questionRefresher)

	# def addCategory(self,categoryName,categoryMode):
	# 	newTitle = self.getCategoryTitle(categoryName,categoryMode)

	# 	#check that this isn't already in the list
	# 	if newTitle in self.questions.keys():
	# 		self.triggerAlert("Category already added")
	# 		return

	# 	newCategoryList = uDDH.findWords(categoryName.lower(),self.questionsPerCategory,categoryMode)

	# 	#check that it successfully return a list of questions
	# 	if not newCategoryList:
	# 		self.triggerAlert("Couldn't find the data")
	# 		return

	# 	newCategoryDict = {newTitle: newCategoryList}

	# 	self.questions = {**self.questions, **newCategoryDict}

	# 	self.titles.append(newTitle)
	# 	self.updateBoardWindow(newTitle)
	# 	self.numCategories +=1

# 	#CONTROL FUNCTIONS
# 		# self.addCategory(newCategoryName,categoryMode)
# 		# categoryName = categoryDict["NAME"]
# 		# categoryMode = categoryDict["MODE"]
# 		# newTitle = self.getCategoryTitle(categoryName,categoryMode)

# 		# newCategoryDict = {}
# 		# newCategoryDict = {newTitle: categoryDict["QUESTIONS"]}

# 		# self.questions = {**self.questions, **newCategoryDict}

# 		# self.titles.append(newTitle)
# 		# self.updateBoardWindow(newTitle)
# 		# self.numCategories +=1