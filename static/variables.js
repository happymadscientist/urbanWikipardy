buzzColors = ["green","yellow","red","orange","black"];
beerMultiplier = .2;
buzzerSounds = ["Do The Roar","Royal","Beer bottle","Dereks mom","Metal","The other day","Trololo","wubbalubbadubdub"];
refreshInterval = 1200;
scoreModifiers = {"+":1,"-":-1,"Creativity":.2,"Spite":-.2}
drinkValues = ["Huff","Sip","Swill","Taste","Slurp","Swig","Glug","Gulp","Drink","Chug","Guzzle","Finish","Finish"];

var chosenCategories = {};
var teamScores = {};
var questionsRemaining = 0;
var questionScore = 100;
var scoreToAward = 0;
var dollarMode = false;
var questionsPerCategory = 6;
var scoreMultiplier = 1;
var gameStarted = false;
var numberBuzzedIn = 0;
var teamName = "";
var sessionId = "";
var scoreToAward = 100;
var buzzedIn = false;
const soundHandler = new Audio();
const themeHandler = new Audio();