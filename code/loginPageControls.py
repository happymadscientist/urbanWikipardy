from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.models.widgets import Div, TextInput,CheckboxButtonGroup, Button, Slider, RadioButtonGroup,DateRangeSlider, Dropdown, Slider
from bokeh.io import curdoc, show
from bokeh.models import ColumnDataSource
from bokeh.events import Tap, DoubleTap, Pan

from datetime import datetime
from urbanWikipardyBoard import urbanWikipardyBoard

from wikipediaHandler import getWikipediaQuestions

class urbanWikipardyLogin:
	def __init__(self,databaseHandler,javascriptHandler):
		self.jser = javascriptHandler

		self.gui = column([
			row([],name = "gui"),
			self.jser.div
			])

		self.databaseHandler = databaseHandler
		self.switchToStartPage()

	#START PAGE
	def switchToStartPage(self):
		#switches the gui to the start page and displays the welcome message
		self.gui.select_one({"name":"gui"}).children = [self.createStartPage()]

	def createStartPage(self):
		#creates a page for a moderator/contestant to login at

		welcomeDiv = Div(text = """
			<b>DISCLAIMER: This game contains offensive language</b>
			<br>
			Hello and welcome to Urban Wikipardy! <br>
			2-30 players <br>
			<b> Instructions: </b> <a href='https://github.com/happymadscientist/urbanWikipardy'>https://github.com/happymadscientist/urbanWikipardy</a>
			""",width = 600)

		moderatorDiv = Div(text = 
			"""
			<b>Moderators:</b> <br>
			Use a laptop only viewable by you
			""",width = 300
			)

		contestantDiv = Div(text = 
			"""
			<b>Contestants</b> <br>
			Use a computer plugged into a TV for everyone to see
			""", width = 300
			)

		buzzerDiv = Div(text = """
			<b>Buzzers</b><br>
			Use your phone or computer as a buzzer for your team
			""")

		moderatorLoginButton = Button(label = "Login as moderator",button_type="primary")
		moderatorLoginButton.on_click(self.switchToModeratorLoginPage)

		contestantLoginButton = Button(label = "Login as contestant",button_type="primary")
		contestantLoginButton.on_click(self.switchToContestantPage)

		buzzerLoginButton = Button(label = "Login as buzzer",button_type = "primary")
		buzzerLoginButton.on_click(self.switchToBuzzerLoginPage)

		startingGui = column(
			welcomeDiv,
			row(moderatorDiv,contestantDiv,buzzerDiv),
			row(moderatorLoginButton,contestantLoginButton,buzzerLoginButton)
			)
		return startingGui

	##### BUZZER PAGE
	def createBuzzerLoginPage(self):
		self.buzzerSessionIdInput = TextInput(value = "",title = "Passphrase", name = "Passphrase")
		self.buzzerNameInput = TextInput(value = "",title = "Team name")

		buzzerSoundOptions = [
			("The other day...", "theOtherDay.mp3"),
			("Do the roar!", "doTheRoar.mp3"),
			("Trolololo","trololo.mp3"),
			("Metal", "metal.mp3"),
			("Beer opening","beerBottleOpening.mp3"),
			("Derek's Mom","dereksMom.mp3"),
			("Royals","royals.mp3"),
			("Wubba-lubba-dub-dub","wubbaLubbaDubDub.mp3")

		]

		self.buzzerOptionsDropdown = Dropdown(
			label="Buzzer sound", button_type="warning",
			menu=buzzerSoundOptions)
		self.buzzerOptionsDropdown.on_change("value",self.dropdownCallback)

		enterButton = Button(label = "Register buzzer",button_type = "success")
		enterButton.on_click(self.buzzerEnterCallback)

		buzzerGui = column(
			self.buzzerSessionIdInput,
			self.buzzerNameInput,
			self.buzzerOptionsDropdown,
			enterButton
			)

		return buzzerGui

	def buzzerCallback(self,event):
		# print ("BuzzerClicked")

		commandType = "Buzz In"
		self.postCommand(COMMAND_TYPE = commandType,COMMAND_DATA = self.teamName)

	def createBuzzerPage(self):
		fig = figure(x_range = (0,1),y_range = (0,1),
			background_fill_color = "blue",
			title=None, plot_width=1000, plot_height=1000,
			css_classes = ["hello"],
			# sizing_mode = "scale_width",
			toolbar_location=None,tools= "" #, min_border=0,
			)

		fig.grid.visible = False
		fig.axis.visible = False

		self.buzzerTextFontSize = "30pt"
		#add text to say Buzz In
		fig.text(x = [.5],y = [.5],text = ["Buzz In"],
			text_color = "white",text_alpha=1.0,text_font_size = self.buzzerTextFontSize,
			text_font = "gyparody",text_align="center",text_baseline="middle")

		fig.on_event(Tap,self.buzzerCallback)

		return fig

	def dropdownCallback(self,attr,old,new):
		#called when buzzer sound dropdown changed
		#plays the chosen sound
		# print (new)
		self.jser.playCustomSound(new)

	def buzzerEnterCallback(self):
		#get the entered passphrase
		enteredSessionId = self.buzzerSessionIdInput.value

		validId = self.databaseHandler.validateSessionId(enteredSessionId)

		if not validId:
			return

		#otherwise get the entered team name
		enteredTeamName = self.buzzerNameInput.value

		self.sessionId = enteredSessionId
		self.teamName = enteredTeamName

		#add team
		commandType = "Add Team"
		commandData = enteredTeamName
		self.postCommand(commandType,commandData)

		#add buzzer sound
		commandType = "Add Buzzer Sound"
		teamBuzzerSound = self.buzzerOptionsDropdown.value
		if not teamBuzzerSound: teamBuzzerSound = "theOtherDay.mp3"
		commandData = (enteredTeamName,teamBuzzerSound)
		self.postCommand(commandType,commandData)

		#switch gui over to the team buzzer
		self.switchToBuzzerPage()

		#continuously check for new buzzer commands in case its hella wikipardy time
		self.buzzerRefresher = curdoc().add_periodic_callback(self.refreshBuzzer,1000)

	def switchToBuzzerPage(self):
		self.gui.select_one({"name":"gui"}).children = [self.createBuzzerPage()]

	def switchToBuzzerLoginPage(self):
		self.gui.select_one({"name":"gui"}).children = [self.createBuzzerLoginPage()]

	#HELLA WIKIPARDY PAGE FOR BUZZER
	def panCallback(self,event):
		x,y = event.x,event.y
		self.drawingSource.stream({"x":[x],"y":[y]})

	def createDrawingWindow(self):
		p = figure(tools="",x_range = (0,1),y_range = (0,.9),
			background_fill_color = "blue",
			toolbar_location=None
			)
		p.grid.visible = False
		p.axis.visible = False

		self.drawingSource = ColumnDataSource(data = dict(x=[],y=[]))

		scatterGlyph = p.scatter(x="x", y="y",source = self.drawingSource,
			radius=.015, fill_color="white",fill_alpha=.8, line_color = "white"
			# line_color="white", line_alpha=0.8,line_width=20., line_color=None
			)

		# p.js_on_event(events.MouseMove,display_event(attributes=point_attributes))
		p.on_event(Pan,self.panCallback)

		p.on_event(Tap,self.betCallback)
		#add a row to modify the user's bet
		self.betControlsSource = ColumnDataSource(data = dict(x=[.1,.5,.9],y=[.1,.1,.1],text=["-","0","+"]))

		self.betTextFontSize = "30pt"
		#add text to say Buzz In
		p.text(x = "x",y = "y",text = "text",source = self.betControlsSource,
			text_color = "white",text_alpha=1.0,text_font_size = self.betTextFontSize,
			text_font = "gyparody",text_align="center",text_baseline="middle")

		return p


	def betCallback(self,event):
		#called when the bet/drawing window is clicked
		#check that the bet window row was clicked
		if event.y > .2 : return
		funNumbers = [69,420,666]

		xTap = event.x

		currentBetTexts = self.betControlsSource.data["text"]

		currentBet =int(currentBetTexts[1])
		#means a minus click
		if (xTap < .2):

			currentBet += -100

		elif (xTap > .8):
			#cannot go higher than 2000
			if currentBet>2000: return

			currentBet += 100

		#cannot go lower than 0
		if currentBet<=0: return

		#check if the result is close to any of the fun numbers, and if so, set it to that instead
		for funNumber in funNumbers:
			if (abs(currentBet - funNumber) < 50):
				currentBet = funNumber
				break

		currentBetTexts[1] = str(currentBet)
		self.betControlsSource.data["text"] = currentBetTexts

	def resetDrawingCallback(self):
		self.drawingSource.data = {"x":[],"y":[]}

	def createHellaWikipardyWindow(self):
		sendButton = Button(label="Send", button_type="success")
		sendButton.on_click(self.sendHellaWikipardyCallback)

		resetDrawingButton = Button(label = "Reset",button_type = "danger")
		resetDrawingButton.on_click(self.resetDrawingCallback)
		#team member		

		drawingWindow = self.createDrawingWindow()
		hellaWikipardyControls = column(
			drawingWindow,
			row(sendButton,resetDrawingButton)
			)

		return hellaWikipardyControls

	def switchToHellaWikipardyWindow(self):
		self.gui.select_one({"name":"gui"}).children = [self.createHellaWikipardyWindow()]

		#stop looking for new commands now that the hella wikipardy has happened
		try: curdoc().remove_periodic_callback(self.buzzerRefresher)
		except: pass

	def sendHellaWikipardyCallback(self):
		commandData = {
			"DRAWING":self.drawingSource.data,
			"BET":int(self.betControlsSource.data["text"][1]),
			"TEAM":self.teamName}

		self.postCommand(COMMAND_TYPE = "Hella Wikipardy Entry",COMMAND_DATA = commandData)

		#switch back to buzzer page
		self.switchToBuzzerPage()

	#CONTESTANT PAGE
	def switchToContestantPage(self):
		self.gui.select_one({"name":"gui"}).children = [self.createContestantLoginPage()]

	def createContestantLoginPage(self):
		self.sessionIdInput = TextInput(value = "",title = "Passphrase", name = "Passphrase")
		self.sessionIdInput.on_change("value",self.sessionIdInputCallback)

		enterButton = Button(label = "Join game",button_type = "success")
		enterButton.on_click(self.contestantEnterButtonCallback)

		contestantGui = column(
			self.sessionIdInput,
			enterButton
			)

		return contestantGui

	def sessionIdInputCallback(self,attr,old,new):
		#callback for the session id input box
		#if the value is correct, will login
		#otherwise will do nothing
		self.testEnteredSessionId()

	def testEnteredSessionId(self):
		# enteredSessionId = self.gui.select_one({"name":"Passphrase"}).value
		enteredSessionId = self.sessionIdInput.value
		validId = self.databaseHandler.validateSessionId(enteredSessionId)
		# print (validId)
		#if its valid start the game
		if validId:
			self.sessionId = enteredSessionId
			self.loadContestantGame(enteredSessionId)
			return enteredSessionId
		else:
			return 0

	def contestantEnterButtonCallback(self):
		if not self.testEnteredSessionId():
			return
			# self.triggerAlert("Invalid ID")

	def loadContestantGame(self,sessionId):
		#create a unique teamname for the contestant viewer
		self.teamName = int(datetime.now().timestamp())

		#get the board setup command
		boardSettings = self.databaseHandler.getGameSettings(SESSION_ID = sessionId)
		questionsPerCategory = boardSettings["QUESTIONS_PER_CATEGORY"]
		scoreType = boardSettings["CURRENCY"]

		self.gameBoard = urbanWikipardyBoard(sessionId = sessionId,admin = 0,scoreType=scoreType,questionsPerCategory=questionsPerCategory)
		self.gui.select_one({"name":"gui"}).children = [self.gameBoard.gui]

		curdoc().add_periodic_callback(self.refreshBoard,1000)

	def refreshBuzzer(self):
		#gets the newest buzzer commands from the database
		newestBuzzerCommands = self.databaseHandler.getBuzzerCommands(self.sessionId,self.teamName)

		#if one was found, switch to it
		if (newestBuzzerCommands):
			self.switchToHellaWikipardyWindow()


	def refreshBoard(self):
		#gets the newest board commands from the database
		newestBoardCommands = self.databaseHandler.getBoardCommands(self.sessionId,self.teamName)

		#act on each command
		for command in newestBoardCommands:
			commandType = command["TYPE"]
			commandData = command["DATA"]

			self.gameBoard.runCommand(commandType = commandType,commandData = commandData)

			timestamp = command["TIMESTAMP"]
			self.databaseHandler.incrementBoardCommand(SESSION_ID=self.sessionId,TIMESTAMP=timestamp,TEAM_NAME = self.teamName)


	###MODERATOR CONTROLS
	def switchToModeratorLoginPage(self):
		self.gui.select_one({"name":"gui"}).children = [self.createModeratorLoginPage()]


	def createModeratorLoginPage(self):
		self.questionsPerCategorySlider = Slider(start=3,end=8,step=1,value=3,title = "Questions Per Category")

		currencyTypeTitle = Div(text = "Play for:",width=200,height=8)
		self.currencyTypeControls = RadioButtonGroup(labels = ["Drinks","Dollars"],active = 0)

		createGameButton = Button(label = "Create game",button_type="primary")
		createGameButton.on_click(self.switchToModPage)

		modLoginControls = column(
			self.questionsPerCategorySlider,
			currencyTypeTitle,
			self.currencyTypeControls,
			createGameButton
			)

		return modLoginControls

	def switchToModPage(self):
		#load moderator page and game board
		self.teamName = "_MOD_"
		self.sessionId = self.databaseHandler.generateSessionId()

		#get the value of the settings
		gameModes = ["drinks","dollars"]
		gameMode = gameModes[self.currencyTypeControls.active]
		self.questionsPerCategory = self.questionsPerCategorySlider.value

		self.databaseHandler.postGameSettings(SESSION_ID = self.sessionId,QUESTIONS_PER_CATEGORY = self.questionsPerCategory,CURRENCY = gameMode)

		self.gameBoard = urbanWikipardyBoard(sessionId = self.sessionId, admin = 1, scoreType = gameMode, questionsPerCategory = self.questionsPerCategory)

		#link callbacks to the game board
		self.gameBoard.boardWindow.on_event(Tap,self.boardClickCallback)
		self.gameBoard.questionWindow.on_event(Tap,self.questionClickCallback)

		self.gameBoard.scoreWindow.on_event(Tap,self.scoreClickCallback)
		self.gameBoard.scoreWindow.on_event(DoubleTap,self.scoreClickCallback)

		gameSetupControls = self.createGameSetupControls()
		self.gui.select_one({"name":"gui"}).children = [
			self.gameBoard.gui,
			column(gameSetupControls,name = "Controls")
			]

		curdoc().add_periodic_callback(self.refreshBoard,1000)


	def scoreClickCallback(self,event):
		xClick,yClick = int(event.x),int(event.y)
		clickedTeamIndex = int(xClick)

		clickedTeam = self.gameBoard.teamSource.data["names"][clickedTeamIndex]

		baseBonus = 5
		bonusPoints = len(self.bonusPointsControls.active) * baseBonus
		self.bonusPointsControls.active = []

		if (bonusPoints):
			questionValue = bonusPoints

		else:
			#single tap is to add positive score
			if event.event_name == "tap": questionValue = self.gameBoard.questionValue + bonusPoints
			else: questionValue = -self.gameBoard.questionValue + bonusPoints

		self.postScoreUpdate(clickedTeam,questionValue)
		# self.addScoreToTeam(clickedTeam,self.questionValue + bonusPoints)
		# self.addScoreToTeam(clickedTeam,-self.questionValue + bonusPoints)


	def questionClickCallback(self,event):
		#check if the question was reviewed
		selectedDifficultyIndex = self.questionDifficultyControls.active
		if (selectedDifficultyIndex):
			selectedDifficulty = self.questionDifficulties[selectedDifficultyIndex]
			#reset controls so it doesnt get auto-rated next question
			self.questionDifficultyControls.active = None

			self.databaseHandler.updateWordDifficulty(self.activeWord,self.activeDef,selectedDifficulty)

		self.answerBox.value = ""


		self.postEndQuestion()


	def boardClickCallback(self,event):
		xClick,yClick = int(event.x),int(event.y)

		#reset the active on the question difficulty
		self.questionDifficultyControls.active = None

		row,col = self.gameBoard.coordsToRowCol(xClick,yClick)

		# check if it was a category title clicked (to delete it)
		if col == (self.gameBoard.questionsPerCategory):
			selectedTitle = self.titleSource.data["text"][row]
			# print ("delete", selectedTitle)
			return

		clickIndex = self.gameBoard.rowColToIndex(row,col)

		self.postQuestionSelect(clickIndex)

	def createGameSetupControls(self):
		#creates controls for setting up the game board
		self.categoryInput = TextInput(value="", title="Category:")
		randomCategoryButton = Button(label="Random Category", button_type="primary")
		randomCategoryButton.on_click(self.randomCategoryCallback)

		categoryModesTitle = Div(text = "Filter results by",width=200,height=8)
		self.categoryModeControls = CheckboxButtonGroup(labels=["Tag","Word contains","Definition contains"], active=[0])
		self.categoryModes = ["Tag","InWord","InDef"]

		sortByTitle = Div(text = "Rank questions by",width=200,height=8)
		self.sortByControls = RadioButtonGroup(labels = ["Upvotes","Downvotes"],active = 0)
		sortByCol = column(sortByTitle,self.sortByControls)

		exampleDefinitionTitle = Div(text = "Include in answer",width=200,height=8)
		self.exampleDefinitionControls = CheckboxButtonGroup(labels = ["Definition","Example"],active = [0])

		addCategoryButton = Button(label="Add Category", button_type="primary")
		addCategoryButton.on_click(self.addCategoryCallback)

		self.teamInput = TextInput(value="", title="Teams:")
		addTeamButton = Button(label="Add Team", button_type="primary")
		addTeamButton.on_click(self.addTeamCallback)

		dateTitle = Div(text = "Date range",width=200,height=8)

		startDate = datetime(2006,2,19)
		endDate = datetime.today()

		wikipediaRatioTitle = Div(text="Wikipedia Questions To Include",width=200,height=8)
		self.wikipediaRatioSlider = Slider(start=0,end=self.questionsPerCategory,value=1)
		wikipediaRatioColumn = column(wikipediaRatioTitle,self.wikipediaRatioSlider)


		dateSlider = DateRangeSlider(start = startDate,end = endDate, value = (startDate,endDate))
		dateCol = column(dateTitle,dateSlider)

		hideControlsButton = Button(label = "Hide Controls",button_type = "danger")
		startGameButton = Button(label = "Start Game",button_type = "success")
		startGameButton.on_click(self.startGameCallback)

		#generate a passphrase and show it
		passphraseBox = TextInput(value = self.sessionId,title = "Passphrase",disabled = True)

		return column([
			passphraseBox,
			self.categoryInput,
			randomCategoryButton,
			categoryModesTitle,
			self.categoryModeControls,
			exampleDefinitionTitle,
			self.exampleDefinitionControls,
			sortByCol,
			dateCol,
			wikipediaRatioColumn,
			addCategoryButton,
			self.teamInput,
			addTeamButton,
			startGameButton
			],
			)

	def createGamePlayControls(self):
		##Sets up controls for the game play

		bonusPointsTitle = Div(text = "Give bonus points",width=200,height=8)
		self.bonusPointsControls = CheckboxButtonGroup(labels = ["Original","Close","Enthusiasm"])

		questionDifficultyTitle =  Div(text = "Question difficulty",width=200,height=8)
		self.questionDifficulties = ["Easy","Med","Hard","Impossible"]
		self.questionDifficultyControls = RadioButtonGroup(labels = self.questionDifficulties)

		self.answerBox = TextInput(value ="",title = "Answer",disabled = True)

		# stopGameButton = Button(label = "Stop Game")

		gameControls = column(
			bonusPointsTitle,
			self.bonusPointsControls,
			questionDifficultyTitle,
			self.questionDifficultyControls,
			self.answerBox,
			# stopGameButton
			)

		return gameControls

	#MODERATOR CALLBACKS
	def randomCategoryCallback(self):
		categoryDict = self.databaseHandler.findRandomCategory()
		self.postCategoryAdd(categoryDict)

	def addTeamCallback(self):
		newTeam = self.teamInput.value
		if not newTeam:
			# self.gameBoard.triggerAlert("Team name blank")
			return

		if newTeam in self.gameBoard.teamSource.data["names"]:
			self.gameBoard.triggerAlert("Team already added")
			return

		self.postTeamAdd(newTeam)

		#reset team entry box so people don't have to delete it
		self.teamInput.value = ""
		# self.addTeam(newTeam)

	def addCategoryCallback(self):
		categoryName = (self.categoryInput.value.lower())

		if not categoryName:
			self.gameBoard.triggerAlert("Blank category")
			return

		self.databaseHandler.addUserEntry(ENTRY = categoryName,SESSION_ID = self.sessionId)

		if self.gameBoard.numCategories > 5:
			self.gameBoard.triggerAlert("Too many categories!")
			return

		#get the active modes
		selectedCategoryOptions = self.categoryModeControls.active
		#if no mode is active, just set it to tag
		if not selectedCategoryOptions:
			self.categoryModeControls.active = [0]
			selectedCategoryOptions = [0]

		categoryModes = [self.categoryModes[optionIndex] for optionIndex in selectedCategoryOptions]

		#see how many wikipedia words to include
		numWikiWords = self.wikipediaRatioSlider.value
		if numWikiWords:
			wikiCategoryList = getWikipediaQuestions(categoryName,numWikiWords)
		else:
			wikiCategoryList = []
		# print (wikiCategoryList)
		
		numWikiWordsFound = len(wikiCategoryList)
		numUdWordsToGet = self.questionsPerCategory - numWikiWordsFound

		#see if to include example, definition or both
		exampleDefinitionChoice = self.exampleDefinitionControls.active
		#if neither are selected, just use definition
		if not exampleDefinitionChoice: 
			self.exampleDefinitionControls.active = [0]
			includeExample = False
		else: 
			if (1 in exampleDefinitionChoice): includeExample = True
			else: includeExample = False

		#check sorting direction
		selectedSort = self.sortByControls.active
		if not selectedSort: sortKey = "UPVOTES"
		else: sortKey = "DOWNVOTES"

		newTitle = self.gameBoard.getCategoryTitle(categoryName,categoryModes)

		#check that this isn't already in the list
		if newTitle in self.gameBoard.questions.keys():
			self.gameBoard.triggerAlert("Category already added")
			return

		udCategoryList = self.databaseHandler.findWordsByCriteria(
			CRITERIA = categoryName.lower(),
			categories = categoryModes,
			NUM_TO_GET = numUdWordsToGet,
			INCLUDE_EXAMPLE=includeExample,
			SORT_KEY = sortKey
			)

		fullCategoryList = wikiCategoryList + udCategoryList

		#check that it successfully return a list of questions
		if len(fullCategoryList) != self.questionsPerCategory:
			self.gameBoard.triggerAlert("Couldn't find the data")
			return

		postDict = {"QUESTIONS":fullCategoryList,"NAME":categoryName,"MODES":categoryModes}

		#clear the cat input
		self.categoryInput.value = ""

		self.postCategoryAdd(postDict)

	def startGameCallback(self):
		startGameSuccess = self.gameBoard.startGame()
		
		if not startGameSuccess:
			self.gameBoard.triggerAlert("There are no teams")
			return

		#create a hella wikipardy index
		self.hellaWikipardyIndex = 	self.gameBoard.generateHellaWikipardyIndex()
		#assign this index to the game board
		self.gameBoard.hellaWikipardyIndex = self.hellaWikipardyIndex

		self.postStartGame(self.hellaWikipardyIndex)

		#update the controls to the gameplay controls
		gamePlayControls = self.createGamePlayControls()
		self.gui.select_one({"name":"Controls"}).children = [gamePlayControls]



	#MODERATOR FUNCTIONS
	def postCommand(self,COMMAND_TYPE,COMMAND_DATA):
		self.databaseHandler.postBoardCommand(
			COMMAND_TYPE = COMMAND_TYPE,
			COMMAND_DATA = COMMAND_DATA,
			SESSION_ID = self.sessionId,
			SENDER = self.teamName)

	def postEndQuestion(self):
		commandType = "End Question"
		commandData = ""
		self.postCommand(commandType,commandData)
		self.gameBoard.switchToBoard()

	def postTeamAdd(self,teamName):
		commandType = "Add Team"
		commandData = teamName
		self.postCommand(commandType,commandData)

		self.gameBoard.addTeam(commandData)

	def postScoreUpdate(self,teamName,score):
		commandType = "Update Score"
		teamScoreDict = {teamName : score}
		commandData = teamScoreDict
		self.postCommand(commandType,commandData)

		self.gameBoard.updateTeamScore(teamScoreDict)

	def postCategoryAdd(self,categoryDict):
		commandType = "Add Category"
		commandData = categoryDict
		self.postCommand(commandType,commandData)

		self.gameBoard.addCategoryDict(categoryDict)

	def postQuestionSelect(self,selectedQuestionIndex):
		commandType = "Select Question"
		commandData = selectedQuestionIndex
		self.postCommand(commandType,commandData)

		#get the word, defintion, and whether or not this one is the hella wikipardy index
		self.activeWord,definition,hellaWikipardy = self.gameBoard.selectQuestion(selectedQuestionIndex)

		self.answerBox.value = self.activeWord

		#update the viewed flag for this word
		#strip away the example if its included
		self.activeDef = definition.split("\n\n Example:")[0]
		self.databaseHandler.updateWordViewed(self.activeWord,self.activeDef)

		if hellaWikipardy:
			self.postCommand("Hellla Wikipardy","")
			# print ("hellaWikipardy")

	def postStartGame(self,hellaWikipardyIndex):
		commandType = "Start Game"
		commandData = hellaWikipardyIndex
		self.postCommand(commandType,commandData)

	def showGui(self):
		show(self.gui)
		curdoc().add_root(self.gui)
		curdoc().title = "Urban Wikipardy"
		curdoc().on_session_destroyed(self.destroySession)

	def destroySession(self,session_context):
		print ("Closing session")
		self.databaseHandler.closeConnection()

def testWikipardyLogin():
	from urbanDictionaryDb import urbanDictionaryDatabaseHandler
	from jsHandler import jsHandler

	databaseHandler = urbanDictionaryDatabaseHandler()
	javascriptHandler = jsHandler()

	uWL = urbanWikipardyLogin(databaseHandler=databaseHandler,javascriptHandler=javascriptHandler)

	# uWL.switchToHellaWikipardyWindow()
	# uWL.switchToModPage()
	# uWL.switchToBuzzerPage()
	# uWL.switchToContestantPage()
	# uWL.loadContestantGame("X")

	uWL.showGui()

# testWikipardyLogin()