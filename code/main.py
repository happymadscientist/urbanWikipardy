from loginPageControls import urbanWikipardyLogin 
from urbanDictionaryDb import urbanDictionaryDatabaseHandler
from jsHandler import jsHandler

databaseHandler = urbanDictionaryDatabaseHandler()
javascriptHandler = jsHandler()

uWL = urbanWikipardyLogin(databaseHandler=databaseHandler,javascriptHandler=javascriptHandler)
uWL.showGui()