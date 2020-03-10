function onLoad(){
	setupWelcomePage();
	setupAudioHandler();
}

// pregame setup
function clearContainer(){
	// remove all children in the container
	container = $("#container");
	childrenToRemove = container.children;
	for (i=0;i<childrenToRemove.length;i++){
		container.removeChild(childrenToRemove[i]);
	}	
}

function backToWelcome(){
	clearContainer();
	setupWelcomePage();
}

function setupWelcomePage(){
	welcomeContainer = createDiv("welcome","welcome");

	welcomeText = createP("welcome",
		"Hello and welcome to Urban Wikipardy! Players: 3+ <br> WARNING: CONTAINS REALLY OFFENSIVE LANGUAGE <br><br>" +
		"Instructions: <br> 1. One person logs in as moderator <br><br> 2. Split into teams. Come up with a fun name.<br><br>" +
		"3. (optional) Login as a spectator on another computer plugged into a TV everyone can see <br><br>" +
		"4. (optional) Each team log in as a contestant");

	moderatorLoginButton = createButton("gridbtn","Login as Moderator",setupModeratorLoginPage);
	spectatorLoginButton = createButton("gridbtn","Login as Spectator",setupSpectatorLoginPage);
	contestantLoginButton = createButton("gridbtn","Login as Contestant",setupContestantLoginPage);

	appendChildren(welcomeContainer,[welcomeText,moderatorLoginButton,spectatorLoginButton,contestantLoginButton]);

	$("#container").appendChild(welcomeContainer);
}

function removeWelcomePage(){
	$("#container").removeChild($("#welcome"));
}

function setupModeratorLoginPage(){
	removeWelcomePage();

	playForText = createP("welcome","Moderator login (Remember, don't let any players see your screen!)<br><br>" +
		"\tAs moderator, you'll control the whole game.<br>  Add categories in the menu that appears after login.<br>" +
		"Tell everyone the login code.<br>Start the game once all teams are added.<br>" +
		"Select questions by tapping the value, and return to the gameboard by tapping the question.<br>"+
		"Assign points to teams by clicking the + or - button.  (Bonus points can be added for good/bad answers)<br><br>Play for");
	playForControls = createRadioButtons("playFor",["drinks","dollars"],0);

	// questionsPerCategoryText = createP("welcome","Questions per category");
	// var questionsPerCategorySlider = createSlider("questionsPerCategory",3,5);
	// questionsPerCategorySlider.value = '4';

	createGameButton = createButton("gridbtn","Create Game!",loginAsModerator);
	backButton = createButton("gridbtn","BACK",backToWelcome);

	var moderatorLoginContainer = createDiv("welcome","moderatorLoginContainer")

	appendChildren(moderatorLoginContainer,[playForText,playForControls,createGameButton,backButton]);

	$("#container").appendChild(moderatorLoginContainer);
}

function getCommands(){
	commandUrl = "getCommands" + "/" + sessionId + "/" + teamName
}

function loginAsModerator(){
	playMode = getChosenRadioValue("playFor");
	if (playMode == "dollars") {dollarMode = true;}
	else {dollarMode = false;}

	// questionsPerCategory = parseInt($("#questionsPerCategory").value);
	questionsPerCategory = 5;

	dataToSend = {"QUESTIONS_PER_CATEGORY": questionsPerCategory, "CURRENCY" : playMode };

	post("login/moderator",dataToSend,moderatorLoginSuccess);
	// moderatorLoginSuccess({"SESSION_ID":"baconwhathtehwathwisi"});
}

function moderatorLoginSuccess(data){
	sessionId = data["SESSION_ID"];
	teamName = "moderator";
	clearContainer();

	setupGameboard();
	setupScoreboard();

	//set question div click to go back to main board
	$("#questionContainer").onclick = gameboardClick;

	setupModeratorSetupControls();
	setupModeratorSessionId(sessionId);

	// schedule the first invocation:
	setTimeout(commandChecker, refreshInterval);

	// getCommands()
	// start getting commands to see if anyone logs in
	// actOnCommands();
}

function setupModeratorSessionId(sessionId){
	sessionIdContainer = createDiv("topMenu","sessionIdContainer");

	showControlButton = createButton("button","Hide controls",hideControlBar);
	showControlButton.id = "showControlButton";
	showControlButton.style.width = "20%";
	sessionIdText = createP("loginCode","Login code:");
	moderatorSessionId = createInput("sessionIdMod","moderatorSessionId");
	moderatorSessionId.disabled = true;
	moderatorSessionId.value = sessionId;

	appendChildren(sessionIdText,[moderatorSessionId]);
	appendChildren(sessionIdContainer,[showControlButton,sessionIdText]);

	document.body.insertBefore(sessionIdContainer,$("#container"));
}

function setupSpectatorLoginPage(){
	removeWelcomePage();

	spectatorContainer = document.createElement("div");

	spectatorText = createP("welcome",
		"Spectator login instructions <br><br> Plug this computer into a TV <br>" +
		"Enter the login code the moderator tells you")
	
	sessionIdInput = createInput("sessionId","spectatorSessionId");
	spectatorLoginButton = createButton("gridbtn","Login to game as spectator",spectatorLoginClick);
	backButton = createButton("gridbtn","BACK",backToWelcome);

	appendChildren(spectatorContainer,[spectatorText,sessionIdInput,spectatorLoginButton,backButton]);

	$("#container").appendChild(spectatorContainer);
}

function spectatorLoginClick(){
	sessionId = $("#spectatorSessionId").value.toLowerCase().replace(" ","");

	if (!sessionId){return alert("ENTER AN ID")}

	// make a web call to see if the sessionId is valid
	post("login/spectator",{"SESSION_ID":sessionId},spectatorLoginSuccess);
}

function spectatorLoginSuccess(data){
	teamName = data["TEAM_NAME"]
	currency = data["CURRENCY"]
	if (currency == "dollars"){dollarMode = true;}

	questionsPerCategory = data["QUESTIONS_PER_CATEGORY"]

	clearContainer();
	setupGameboard();
	setupScoreboard();

	setTimeout(commandChecker, refreshInterval);
}

function spectatorLoginFailure(data){
	alert("Invalid login code!");
}

function setupContestantLoginPage(){
	removeWelcomePage();

	contestantContainer = document.createElement("div");

	contestantText = createP("welcome",
		"Contestant login instructions<br><br> Enter a team name<br>");

	teamNameInput = createInput("sessionId","teamNameInput");
 	sessionIdText = createP("welcome","Enter the login code the moderator tells you<br>");
 	sessionIdInput = createInput("sessionId","contestantSessionId");
	buzzerSoundText = createP("welcome","Pick a buzzer sound <br>");

	buzzerNoiseSelect = createDropdown("buzzers",buzzerSounds);
	buzzerNoiseSelect.onchange = buzzerSelectCallback;
	buzzerNoiseSelect.id = "buzzerDropdown";

	contestantGameplayText = createP("welcome","To buzz in, tap the screen during a question");
	 
	contestantLoginButton = createButton("gridbtn","Login to game as contestant",contestantLoginClick);
	backButton = createButton("gridbtn","BACK",backToWelcome);

	appendChildren(contestantContainer,[contestantText,teamNameInput,buzzerSoundText,buzzerNoiseSelect,sessionIdText,sessionIdInput,contestantGameplayText,contestantLoginButton,backButton]);

	$("#container").appendChild(contestantContainer);
}

function buzzerSelectCallback(element){
	buzzerFilename = (element.target.value.replace(/ /g,"").toLowerCase() + ".mp3")
	playBuzzerSound(buzzerFilename);
}

function contestantLoginClick(){
	teamName = $("#teamNameInput").value.toLowerCase().replace(/[^a-z0-9áéíóúñü \.,_-]/gim,"");
	if (!teamName){return alert("Enter a team name");}

	sessionId = $("#contestantSessionId").value.toLowerCase().replace(" ","").replace(/\//g, "");
	if (!sessionId){return alert("Enter a login code")}

	buzzerSound = $("#buzzerDropdown").value;

	// make a web call with the contestant settings to see if they're valid
	post("login/contestant",{"SESSION_ID":sessionId,"TEAM_NAME":teamName,"BUZZER_SOUND":buzzerSound},contestantLoginSuccess)
}

function contestantLoginSuccess(data){
	currency = data["CURRENCY"]
	if (currency == "dollars") {dollarMode = true;}

	questionsPerCategory = data["QUESTIONS_PER_CATEGORY"];

	// if the call was good, load the contestant page
	clearContainer();

	setupGameboard();
	setupScoreboard();

	addTeam(teamName,buzzerSound);

	//set the question click callback to buzz in
	questionDiv = $("#questionContainer");
	questionDiv.onclick = buzzInCallback;

	setTimeout(commandChecker, refreshInterval);
}

function contestantLoginFail(data){
	return alert("Invalid login code!");
}

//GAME SETUP

//common
function setupGameboard(){
	var questionContainer = createDiv("questionContainer","questionContainer");
	questionTitle = createDiv("question title","questionTitle");
	questionContent = createDiv("question question","question");
	questionAnswer = createDiv("question answer","questionAnswer");

	questionContainer.appendChild(questionTitle);

	questionContainer.append(document.createElement("hr"));
	questionContainer.appendChild(questionContent);
	questionContainer.appendChild(questionAnswer);

	questionContainer.style.display = "none";
	$("#container").appendChild(questionContainer);

	var gameboard = createDiv("container gameboard","gameboard");
	$("#container").appendChild(gameboard);
}

function setupScoreboard(){
	var scoreboard = createDiv("scoreboard","scoreboard");
	$("#container").appendChild(scoreboard);
}

function removeTeam(teamName){
	$("#scoreboard").removeChild($("#" + teamName));
}

// moderator
function setupModeratorSetupControls(){
	messageBox = createP("controls message","Add a category");
	messageBox.id = "messageBox";

	questionRankText = 	createP("controls","Rank questions by:<br>");
	questionRankControls = createRadioButtons("questionRank",["downvotes","upvotes"],0);
	searchCriteriaText = createP("controls","Include in search");
	searchCriteriaControls = createRadioButtons("searchCriteria",["in word","in definition","tag"],1,1);	
	includeInAnswerText = createP("controls","Include in answer");
	includeInAnswerControls = createRadioButtons("includeInAnswer",["example","definition"],1);
	randomCategoryButton = createButton("button","Random Category!",randomCategoryCallback);
	categoryInputText = createP("controls","Category name:");
	categoryInput = createInput("input","categoryInput");
	addCategoryButton = createButton("button","Add Category",addCategoryCallback);
	startGameButton = createButton("button","Start game",startGameCallback);

	addTeamText = createP("controls", "Team name:");
	addTeamInput = createInput("input","teamNameInput");
	addTeamButton = createButton("button","Add Team",addTeamCallback);

 	var moderatorSetupContainer = createDiv("sidebar bar-block collapse card","moderatorSetupContainer");

	appendChildren(moderatorSetupContainer,[
		messageBox,
		categoryInputText,
		categoryInput,
		randomCategoryButton,
		questionRankText,
		questionRankControls,
		searchCriteriaText,
		searchCriteriaControls,
		includeInAnswerText,
		includeInAnswerControls,
		addCategoryButton,
		startGameButton,
		addTeamText,
		addTeamInput,
		addTeamButton
	])

	$("#container").appendChild(moderatorSetupContainer);
}

function randomCategoryCallback(){
	updateMessageBox("Working...");
	get("randomCategory",randomCategorySuccess,randomCategoryFailure)

	// categoryOptions = getCategoryOptions();

	// // set the categoryname to _RANDOM_
	// categoryOptions["CATEGORY"] = "_RANDOM_";

	// validOptions = validateCategoryOptions(categoryOptions);
	// // check the options are valid, if not, throw an error
	// if (!validOptions){return alert("You messed up, fix some options");}

	// // make a web call with the category options
	// post("category/" + sessionId,categoryOptions,categorySuccessCallback)
}

function randomCategorySuccess(data){
	randomCat = data["CATEGORY"]
	$("#categoryInput").value = randomCat;
	updateMessageBox("Done!");
}

function randomCategoryFailure(){
	updateMessageBox("Failed!")
}

function showControlBar() {
	$("#moderatorSetupContainer").style.display = "block";
	showControlButton = $("#showControlButton");
	showControlButton.innerHTML = "Hide controls";
	showControlButton.onclick = hideControlBar;

}

function hideControlBar() {
  $("#moderatorSetupContainer").style.display = "none";
  showControlButton = $("#showControlButton");
  showControlButton.innerHTML = "Show controls";
  showControlButton.onclick = showControlBar;
}

function removeTeamCallback(element){
	clickedTeamName = (element.target.parentElement.id);
	commandData = {"Remove Team" : clickedTeamName};
	post("command/" + sessionId + "/" + teamName,commandData);
	removeTeam(clickedTeamName);
}

function scoreButtonCallback(element){
	clickedTeamName = (element.target.parentElement.id);
	clickedScoreButtonText = (element.target.innerText);

	var modifiedScore = scoreToAward * scoreModifiers[clickedScoreButtonText];

	commandData = {"Update Score" : {"TEAM_NAME" : clickedTeamName,"SCORE": modifiedScore}};
	post("command/" + sessionId + "/" + teamName,commandData);
	updateTeamScore(clickedTeamName,modifiedScore);
}

function addTeamCallback(element){
	var enteredTeamName = $("#teamNameInput").value.toLowerCase().replace(/\//g, "");

	if (!enteredTeamName)
		{return updateMessageBox("Enter a team name!");}

	// check the team wasn't already added
	if (Object.keys(teamScores).indexOf(enteredTeamName) != -1)
		{return updateMessageBox("Already added");}

	addTeam(enteredTeamName,"Dereks mom");

	commandData = {"Add Team": {"TEAM_NAME":enteredTeamName, "BUZZER_SOUND" : "Dereks mom"}};
	post("command/" + sessionId + "/" + teamName,commandData);
}

function removeModeratorSetupControls(){
	document.body.removeChild($("#moderatorSetupContainer"));
}

function startGameCallback(element){
	commandData = {"Start Game":""}
	post("command/" + sessionId + "/" + teamName,commandData,startGameSuccess)
}

function startGameSuccess(data){
	// console.log("Starting game");
	// startGameButton = $("#startGameButton");
	// startGameButton.innerHTML = "Reset Game";
	// startGameButton.onclick = resetGame;

	// hide the controls to remove stuff once the game has begun
	jQuery(".remove").hide();

	startGame();
}

function updateMessageBox(newMessage){
	$("#messageBox").innerHTML = newMessage;
}

function addCategoryCallback(){
	categoryOptions = getCategoryOptions();
	validOptions = validateCategoryOptions(categoryOptions);

	// check the options are valid, if not, throw an error
	if (!validOptions){return updateMessageBox("You messed up, fix some options");}

	updateMessageBox("Working...");
	// make a web call with the category options
	post("category/" + sessionId,categoryOptions,categorySuccessCallback,categoryFailureCallback)
}

function categorySuccessCallback(data){
	categoryName = data["CATEGORY"];
	categoryQuestions = data["QUESTIONS"];
	categoryCriteria = data["MODES"];
	// categoryCriteria = getCategoryOptions()["SEARCH_CRITERIA"];
	updateMessageBox("Category added!");

	addCategory(categoryName,categoryCriteria,categoryQuestions);
}

function categoryFailureCallback(data){updateMessageBox("Not found!");}

function validateCategoryOptions(optionsIn){
	if (!optionsIn["CATEGORY"]){
		return 0;
	}

	// if (!optionsIn[])
	// 	optionsJson = {
	// 	"SEARCH_CRITERIA" : includeInSearchValues,
	// 	"SORT_KEY" : questionRankValue,
	// 	"CATEGORY" : category,
	// 	"INCLUDE_EXAMPLE" : includeExample,
	// 	"QUESTIONS_PER_CATEGORY" : questionsPerCategory,
	// }

	// if (!opt)
	// alreadyChosenCategories = Object.keys(chosenCategories);

	// // if the category has already been chosen, check that its 
	// if (alreadyChosenCategories.indexOf(optionsIn["CATEGORY"])
	return 1;
}

function getCategoryOptions(){
	// upvote/downvote ranking
	questionRankValue = getChosenRadioValue("questionRank");
	includeInSearchValues = getChosenCheckboxValues("searchCriteria");

	category =  $("#categoryInput").value.toLowerCase();
	includeExampleValues = getChosenCheckboxValues("includeInAnswer");

	includeExample = false;
	if (includeExampleValues.indexOf("example") != -1){includeExample = true;}

	optionsJson = {
		"SEARCH_CRITERIA" : includeInSearchValues,
		"SORT_KEY" : questionRankValue,
		"CATEGORY" : category,
		"INCLUDE_EXAMPLE" : includeExample,
		"QUESTIONS_PER_CATEGORY" : questionsPerCategory,
	}

	return optionsJson
}

function createCategoryOptionDiv(categoryName,categoryOptions){
	categoryOptionsContainer = createDiv("category-options",categoryName+"options");

	tagOptionText = createP("category-option","#tag");
	if (categoryOptions.indexOf("tag") != -1){tagOptionText.style.color = "red";}

	wordOptionText = createP("category-option","in word");
	if (categoryOptions.indexOf("in word") != -1){wordOptionText.style.color = "red";}

	defOptionText = createP("category-option","in def");
	if (categoryOptions.indexOf("in definition") != -1){defOptionText.style.color = "red";}

	appendChildren(categoryOptionsContainer,[tagOptionText,wordOptionText,defOptionText]);
	return categoryOptionsContainer;
}

function removeCategoryCallback(element){
	categoryName = element.target.id.split("_")[0];

	commandData = {"Remove Category":categoryName};
	post("command/" + sessionId + "/" + teamName,commandData);

	removeCategory(categoryName);
}

// commands
function addCategory(categoryName,categoryCriteria,questionAnswers){
	questionsRemaining += questionsPerCategory;

	var categoryContainer = createDiv("category-column",categoryName);

	var titleContainer = createDiv("category",categoryName + " title");
	titleContainer.style.height = "100%";

	categoryTitleText = createP("category title",categoryName);

	var removeCategoryText = createP("category remove","X");
	removeCategoryText.id = categoryName + "_remove";
	removeCategoryText.title = "Remove category";
	removeCategoryText.onclick = removeCategoryCallback;

	optionsDiv = createCategoryOptionDiv(categoryName,categoryCriteria);

	if (teamName=="moderator"){titleContainer.appendChild(removeCategoryText);}

	appendChildren(titleContainer,[categoryTitleText,optionsDiv]);
	categoryContainer.appendChild(titleContainer);

	buttonHeight = "18%";

	var incrementer = 0;

	var stride = Math.floor(drinkValues.length/(questionsPerCategory-1));
	var drinkIndex = 0;

	if (dollarMode == false){var questionMultiplier = 1/questionsPerCategory;}
	else{var questionMultiplier = 100;}

	// first create all the buttons
	questionAnswers.forEach(function (item, index) {
		question = Object.values(item)[0];
		answer = Object.keys(item)[0];

		questionValue = (questionMultiplier * (incrementer + 1)).toFixed(2);
		if (dollarMode==true){var questionText = createScoreText(questionValue);}
		else{
			var questionText = drinkValues[drinkIndex];
			drinkIndex = drinkIndex + stride;
		}

		var questionButton = createButton("gridbtn",questionText,questionClick);
		questionButton.id = categoryName + incrementer;
		// questionButton.style.height = buttonHeight;
		incrementer = incrementer + 1; 

		// set the id so you can disable later on selected question
		questionButton.dataset.question = question
		questionButton.dataset.answer = answer;
		questionButton.dataset.questionValue = questionValue;
		categoryContainer.appendChild(questionButton)
	});

	$("#gameboard").appendChild(categoryContainer);
}

function removeCategory(categoryName){
	$("#gameboard").removeChild($("#" + categoryName));
	questionsRemaining -= questionsPerCategory;
}

function addTeam(teamToAdd,buzzerSound){
	var teamDiv = createDiv("teamContainer",teamToAdd);
	teamDiv.dataset.buzzer = buzzerSound;

	var teamP = createP("team",teamToAdd);

	// add an entry in the storage to keep track of score
	teamScores[teamToAdd] = 0;

	if (dollarMode) {startingScore = "$0";}
	else {startingScore = "0 drinks";}
	var scoreP = createP("score",startingScore);

	scoreP.id = teamToAdd + "_score";
	scoreP.dataset.buzzer = buzzerSound;

	var removeTeamText = document.createElement("p");
	removeTeamText.innerHTML = "X";
	removeTeamText.className = "team remove";
	removeTeamText.id = teamToAdd + "_remove";
	removeTeamText.title = "Remove team";
	removeTeamText.onclick = removeTeamCallback;

	if (teamName=="moderator"){teamDiv.appendChild(removeTeamText);}

	appendChildren(teamDiv,[teamP,scoreP]);

	var addScoreButton = createButton("scorebutton","+",scoreButtonCallback);
	var removeScoreButton = createButton("scorebutton","-",scoreButtonCallback);
	var creativityButton = createButton("scorebutton","Creativity",scoreButtonCallback);
	var spiteButton = createButton("scorebutton","Spite",scoreButtonCallback);

	if (teamName=="moderator"){appendChildren(teamDiv,[addScoreButton,removeScoreButton,document.createElement("br"),creativityButton,spiteButton]);}
	$("#scoreboard").appendChild(teamDiv);
}

function startGame(){
	gameStarted = true;
}

function endGame(){
	teamNames = Object.keys(teamScores);
	var teamScoreValues = (Object.values(teamScores)).map(Number);

	maxScore = (Math.max(...teamScoreValues));

	winnerIndex = teamScoreValues.indexOf(maxScore);
	secondWinnerIndex = teamScoreValues.lastIndexOf(maxScore);

	if (winnerIndex != secondWinnerIndex){winningTeam = teamNames[winnerIndex]+ "&" + teamNames[secondWinnerIndex];}
	else {winningTeam = teamNames[winnerIndex];}

	minScore = Math.min(...teamScoreValues);
	loserIndex = teamScoreValues.indexOf(minScore);
	secondLoserIndex = teamScoreValues.lastIndexOf(minScore);

	if (loserIndex != secondLoserIndex){losingTeam = teamNames[loserIndex]+ "&" + teamNames[secondLoserIndex];}
	else {losingTeam = teamNames[loserIndex]}

	var questionP = $("#question");
	questionP.innerHTML = "<span>" + "GAME OVER!<br><br>Winner:"+winningTeam+"<br><br>Loser:"+losingTeam + "</span>";

	var questionContainer = $("#questionContainer");
	questionContainer.onclick = resetGame;

	questionContainer.style.display = "block";
}

function resetGame(){
	clearContainer();
}

// GAMEPLAY

// common
function commandChecker(){
	getCommands();
}

function getCommands(){
	url = "commands/" + sessionId + "/" + teamName;
	periodicGet(url,actOnCommands,commandChecker);
}

function actOnCommands(commandsList){
	// Add Team			{"TEAM_NAME":str(teamName),"BUZZER_SOUND":str(buzzerSound)}
	// Update Score		{str(teamName):float(teamScore)}
	// Add Category		{"QUESTIONS" : [{str(Q):str(A),...,{str(Q):str(A)}]}
	// Start Game		{str(HellaWikipardyCategory) : int(helllaWikipardyIndex)}
	// Select Question	{str(category):int(selectedQuestionIndex)}
	// End Question		""
	// Remove Team 		str(teamName)
	// Remove Category 	str(catName)
	// Hella Wikipardy	""
	// Reset			""

	for (var i = 0; i < commandsList.length; i++) {
		commandJson = commandsList[i];
		// console.log(commandJson);

		commandType = commandJson["TYPE"];
		commandData = commandJson["DATA"];

		if (commandType=="Add Team")
			{addTeam(commandData["TEAM_NAME"],commandData["BUZZER_SOUND"])}
		else if (commandType=="Update Score")
			{updateTeamScore(commandData["TEAM_NAME"],commandData["SCORE"])}
		else if (commandType=="Add Category")
			{addCategory(commandData["CATEGORY"],commandData["MODES"],commandData["QUESTIONS"])}
		else if (commandType=="Start Game")
			{startGame();}
		else if (commandType=="Select Question")
			{selectQuestion(commandData["ID"]);}
		else if (commandType=="End Question")
			{switchToGameboard();}
		else if (commandType=="Buzz In")
			{buzzInTeam(commandData);}
		else if (commandType=="Remove Category")
			{removeCategory(commandData);}
		else if (commandType=="Remove Team"){
			{removeTeam(commandData)}
		}
	}
}

function debuzzTeams(){
	buzzedIn = false;
	numberBuzzedIn = 0;
	scoreboardTeams = $("#scoreboard").children;
	for (i = 0; i < scoreboardTeams.length; i++) {
		scoreboardTeams[i].style.border = "";
	}
}

function buzzInTeam(teamToBuzzIn){
	var teamScoreDom = $("#"+teamToBuzzIn);
	teamScoreDom.style.border = "solid " + buzzColors[numberBuzzedIn];
	numberBuzzedIn += 1;
	stopJeopardyTheme();

	if (teamName == teamToBuzzIn) {playTeamBuzzerSound(teamToBuzzIn);}
	if (teamName == "moderator") {playTeamBuzzerSound(teamToBuzzIn);}
}

function selectQuestion(questionId){
	switchToQuestion(questionId);
}

function updateTeamScore(teamToUpdate,deltaScore){
	var teamScoreElement = $("#"+teamToUpdate + "_score");

	newScore = (Number(teamScores[teamToUpdate]) + Number(deltaScore)).toFixed(2);
	teamScores[teamToUpdate] = newScore;

	currentScoreText = teamScoreElement.innerHTML;

	newScoreText = getNewScoreText(currentScoreText,deltaScore);

	teamScoreElement.innerText = newScoreText;
}

function setupAudioHandler(){
	// onClick of first interaction on page before I need the sounds
	soundHandler.play();
	themeHandler.play();
	themeHandler.src = "theme.mp3";
}

function playTeamBuzzerSound(teamNameToPlay){
	var buzzerName = $("#" + teamNameToPlay).dataset.buzzer;

	buzzerFilename = (buzzerName.replace(/ /g,"").toLowerCase() + ".mp3")
	soundHandler.src = "buzzerSounds/" + buzzerFilename;
	soundHandler.play();
}

function playJeopardyTheme(){themeHandler.play();}

function stopJeopardyTheme(){
	themeHandler.pause();
	themeHandler.currentTime = 0;
	}

function switchToQuestion(questionId){
	var questionButton = $("#" + questionId);

	question = questionButton.dataset.question;
	answer = questionButton.dataset.answer;

	questionCategory = (questionButton.parentNode.id);
	questionValue = questionButton.innerHTML;

	// disable the chosen question's button
	questionButton.disabled = true;
	questionButton.innerHTML = "";

	var gameboard = $("#gameboard");
	gameboard.style.display = 'none';

	var questionP = $("#question");
	questionP.innerHTML = "<span>" + question + "</span>";

	var questionTitle = $("#questionTitle");
	questionTitle.innerHTML = "<span>" + questionCategory +" for " + questionValue + "</span>";

	if (teamName=="moderator"){
		var questionAnswer = $("#questionAnswer");
		questionAnswer.innerHTML = "<hr><span>" + answer + "</span>";
	}

	var questionContainer = $("#questionContainer");
	questionContainer.style.display = "block";
}

function switchToGameboard(){
	// debuzz every team
	debuzzTeams();
	questionsRemaining -= 1;
	if (questionsRemaining == 0){ 
		endGame();
		return;}

	var questionContainer = $("#questionContainer");
	questionContainer.style.display = "none";

	var gameboard = $("#gameboard");
	gameboard.style.display = "grid";
}

// moderator
function gameboardClick(element){
	switchToGameboard();
	stopJeopardyTheme();

	commandData = {"End Question" : ""}
	post("command/" + sessionId + "/" + teamName,commandData)
}

function questionClick(element){
	if (!gameStarted) {return};
	if (teamName != "moderator"){return;}
	buttonId = element.target.id;
	buttonIndex = 1 + parseInt(buttonId[buttonId.length - 1]);

	questionScore = element.target.dataset.questionValue;

	scoreToAward = questionScore;

	commandData = {"Select Question" : {"ID" : buttonId}}
	post("command/" + sessionId + "/" + teamName,commandData)

	//play jeopardy sound
	playJeopardyTheme();

	switchToQuestion(buttonId);
}

function createScoreControls(){
	scoreAmountText = createP("controls","Award amount:");

	scoreAmountPrintout = createP("gameplay-text",0);
	scoreAmountPrintout.id = "scoreAmountPrintout";

	scoreAmountControls = createRadioButtons("scoreAmount",["question","creativity"]);
	scoreAmountControls.className = "radio inline";
	scoreAmountControls.addEventListener("click", scoreTypeClick);

	scoreControlContainer = createDiv("scorecontrol","scoreControlContainer");
	appendChildren(scoreControlContainer,[
		scoreAmountPrintout,
		scoreAmountControls,])

	return scoreControlContainer;
}

function createScoreText(score){
	if (dollarMode){
		if (score<0){return "-$" + -1*score;}
		else {return "$" + score;}
	}
	return score + " drinks";
}

function getNewScoreText(oldScoreText,deltaScore){
	if (dollarMode)
		{newScore = parseInt(oldScoreText.replace("$","")) + deltaScore;}

	else 
		{newScore = (parseFloat(oldScoreText.split(" ")[0]) + parseFloat(deltaScore)).toFixed(2);}

	return createScoreText(newScore);
}

function buzzInCallback(element){
	// dont allow double buzzing in
	if (buzzedIn){return;}

	buzzedIn = true;
	dataToSend = {"Buzz In": teamName};
	post("command/" + sessionId + "/" + teamName,dataToSend,buzzInSuccess);
}

function buzzInSuccess(data){
	buzzInTeam(teamName);
}