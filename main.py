from PyQt5.QtWidgets import QApplication
from results import ResultsWindow
from options import OptionsWindow
from outputviewer import OutputViewerWindow
import sys
import tmp

app = QApplication(sys.argv)
app.setStyleSheet("""
	QMainWindow {
		font-size: 11pt;
	}
	
	.monospaced {
		font-family: 'Ubuntu Mono', Consolas, monospace;
	}
""")

options = OptionsWindow()
options.show()

try:
	app.exec()
except KeyboardInterrupt:
	print("interrupt")

tmp.cleanup()
print("Exit")
