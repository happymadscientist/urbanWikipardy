# urbanWikipardy
Web-based Jeopardy clone sourcing from Urban Dictionary and Wikipedia

![Example game](pics/sampleBoard.PNG?raw=true "Example game")
![Example question](pics/sampleQuestion.PNG?raw=true "Example question")

# Gameplay

## Play Requirements:
* One computer (another one is better)
* 2-12 players

## Gameplay
At a high level, the game involves teams guessing words from certain categories.  Words can be sourced from Urban Dictionary and Wikipedia.  Each word has a question value, and the goal of the game is to get the most points.  A single moderator controls the game.

## Moderator
The one who controls the game.  They add categories and assign points to teams.  When logging in, the moderator is asked whether to the currency in the game is drinks or dollars, and how many questions to include in each category.

![Mod login](pics/modLogin.PNG?raw=true "Mod Login")

Once logged in, the moderator is presented with a blank game board and a control panel. Teams and categories will appear on the game board as they are added.

### Passphrase
To enable other players to join the game remotely, a unique passphrase is generated for each game.  When a moderator game is started, this passphrase appears in the upper box in the control panel.  Tell this passphrase to other players so they can join.

### Adding a category

#### Category select options
These determine how to select questions.
"Tag" includes words which match the category of the query.
"In Word" includes words who contain the query in their word (the answer)
"In Definition" includes words which contain the query in their definition (the question)

![Category select](pics/filterWord.PNG?raw=true "Filter word")

#### Sort options
These determine how the questions are ranked by difficulty.  Choosing "Upvotes" sorts the results so the easiest question has the most upvotes.  Sorting by "Downvotes" results in the easiest question having the least downvotes.

![Sort options](pics/rankQuestions.PNG?raw=true "Rank questions")

#### Defintion/Example options
This determines the form of the question.  Choosing "Definition" uses a word's definition as its question.  Choosing "Example" uses a word's example as its question.  Choosing both includes both, and is typically easier.

![Question form](pics/includeAnswer.PNG?raw=true "Question form")

#### Wikipedia Slider
This determines how many questions in the category to get from Wikipedia.  It will do a seach of the word and return the first two sentences from the top results as the question.


#### Adding Teams without Buzzers
To add a team without a buzzer, type their name in the team box and click "Add Team".  Their name and score will appear in the team window.

![Team add](pics/teamAdd.gif?raw=true "teamAdd")

## Contestant
Contestants can log in to a passive game board that they cannot control, but which responds to moderator and buzzer commands.  After clicking the Contestant login button, enter the passphrase the moderator tells you.  From here, category and team updates will appear automatically as they happen.

## Buzzer
Individual teams can log in a buzzer to ensure temporal fairness and to send in answers for Hella Wikipardy questions.  Phones make good buzzers, but computers work too.  After clicking the Buzzer login button, enter the passphrase the moderator tells you and choose a buzzer sound.  From here, whenever a question is active, buzz in whenever you think your team knows the answer and your team will be buzzed in, sound and all.

### Hella Wikipardy
Buzzers are also used to draw in answers and bets during Hella Wikipardy.  When a Hella Wikipardy qestion is selected, the buzzer will automatically turn into a canvas.  After hearing the question, draw in your team's answer and choose your team's bet.  Press the submit button once finished and the buzzer will return to normal.



# Build

## Prerequisites:
* Python 3
* Mongo DB

### Libraries:
    bokeh
    pymongo
    wikipedia
    numpy
    
