from bokeh.models.callbacks import CustomJS
from bokeh.io import curdoc, show
from bokeh.layouts import column
from bokeh.models.widgets import Button, Div
from bokeh.models import ColumnDataSource

class jsHandler:
	def __init__(self):
		self.setupVariables()
		# self.setupGui()
 	
	def setupVariables(self):
		self.playSoundJs = """
			var audio = new Audio('code/static/theme.mp3');
			source.data[0] = audio;
			audio.play();
			"""
		self.alertJs = "alert(\"%s\");"

		self.stopSoundJs = """
			var audio = source.data[0];
			audio.pause();
			"""

		self.source = ColumnDataSource({})

		self.div  = Div(text = " ",	width = 600, height = 50)
		self.callback = CustomJS(
			args=dict(source=self.source),
			code="")

		self.div.js_on_change('text', self.callback)

	def triggerJavascript(self):
		if (self.div.text) : self.div.text = ""
		else: self.div.text = " "

	def runJsCode(self,jsCode):
		self.callback.code = jsCode  # update js code
		self.triggerJavascript()# trigger the javascript code by changing the 'text' prooperty of the div

	def triggerAlert(self,alertString):
		self.runJsCode(self.alertJs % alertString)

	def playSound(self):
		self.runJsCode(self.playSoundJs)

	def playCustomSound(self,soundFile):
		customSoundJs = """
			var audio = new Audio('code/static/buzzerSounds/%s');
			source.data[0] = audio;
			audio.play(); 
			""" % soundFile
		self.runJsCode(customSoundJs)

	def stopSound(self):
		self.runJsCode(self.stopSoundJs)

	def setupGui(self):
		testButton = Button(label="Test",button_type="danger")
		testButton.on_click(self.raiseAlert)
		self.gui = column([self.textButton,self.div])

	def showGui(self):
		curdoc().add_root(self.gui)
		show(self.gui)


# def testJsSound():
# 	jsSoundPlayer().showGui()