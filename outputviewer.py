from PyQt5.QtWidgets import (
	QHBoxLayout,
	QMainWindow,
	QWidget,
	QLabel,
	QPushButton,
	QScrollArea,
	QVBoxLayout,
	QDesktopWidget,
)

from PyQt5.QtCore import Qt, QProcess
import ansi2html.converter
import ansi2html.style
import tmp
import io
import re
import html

converter = ansi2html.converter.Ansi2HTMLConverter(inline=True)

MAX_LEN = 1024*32

class FileData:

	def __init__(self, filename, header, content, ansi):
		self.filename = filename
		self.header = header
		self.content = content
		self.ansi = ansi

class DiffViewer(QScrollArea):

	def __init__(self, file_left: FileData, file_right: FileData):
		super(DiffViewer, self).__init__()

		self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
		self.setWidgetResizable(True)

		container = QWidget()
		self.setWidget(container)

		diff_container = QHBoxLayout()

		full_content_left = file_left.content
		full_content_right = file_right.content

		if len(file_left.content) > MAX_LEN:
			file_left.content = file_left.content[0:MAX_LEN] + " ... (file is too large to display)"

		if len(file_right.content) > MAX_LEN:
			file_right.content = file_right.content[0:MAX_LEN] + " ... (file is too large to display)"

		label_left = QLabel()
		label_left.setWordWrap(True)
		label_left.setTextInteractionFlags(Qt.TextBrowserInteraction)
		label_left.setCursor(Qt.IBeamCursor)
		label_left.setAlignment(Qt.AlignTop)
		label_left.setProperty("class", "monospaced")
		label_left.setTextFormat(Qt.RichText)
		content_html_left = converter.convert(file_left.content, False) if file_left.ansi else html.escape(file_left.content)
		label_left.setText("<pre><b>%s</b><hr>\n%s</pre>" % (html.escape(file_left.header), content_html_left))
		diff_container.addWidget(label_left, stretch=1)

		label_right = QLabel()
		label_right.setWordWrap(True)
		label_right.setTextInteractionFlags(Qt.TextBrowserInteraction)
		label_right.setCursor(Qt.IBeamCursor)
		label_right.setAlignment(Qt.AlignTop)
		label_right.setProperty("class", "monospaced")
		label_right.setTextFormat(Qt.RichText)
		content_html_right = converter.convert(file_right.content, False) if file_right.ansi else html.escape(file_right.content)
		label_right.setText("<pre><b>%s</b><hr>\n%s</pre>" % (html.escape(file_right.header), content_html_right))
		diff_container.addWidget(label_right, stretch=1)

		button_container = QHBoxLayout()

		vscode_btn = QPushButton("View diff in VS Code")

		def vscode():
			process = QProcess()

			tmp_file_left = tmp.mktmp(file_left.filename)
			tmp_file_right = tmp.mktmp(file_right.filename)

			file = io.open(tmp_file_left, "w")
			file.write(html.unescape(re.sub(r"<.*?>", "", content_html_left)) if file_left.ansi else full_content_left)
			file.close()

			file = io.open(tmp_file_right, "w")
			file.write(html.unescape(re.sub(r"<.*?>", "", content_html_right)) if file_right.ansi else full_content_right)
			file.close()

			process.startDetached("code", ["-d", tmp_file_left, tmp_file_right])

		vscode_btn.clicked.connect(vscode)

		button_container.addWidget(vscode_btn)
		button_container.addStretch()

		layout = QVBoxLayout(container)
		layout.addLayout(diff_container, stretch=1)
		layout.addLayout(button_container)

class OutputViewer(QScrollArea):

	def __init__(self, file: FileData):
		super(OutputViewer, self).__init__()
		self.setWidgetResizable(True)

		container = QWidget()
		self.setWidget(container)

		full_content = file.content

		if len(file.content) > MAX_LEN:
			file.content = file.content[0:MAX_LEN] + " ... (file is too large to display)"

		label = QLabel()
		label.setTextInteractionFlags(Qt.TextBrowserInteraction)
		label.setCursor(Qt.IBeamCursor)
		label.setAlignment(Qt.AlignTop)
		label.setProperty("class", "monospaced")
		label.setTextFormat(Qt.RichText)
		content_html = converter.convert(file.content, False) if file.ansi else html.escape(file.content)
		label.setText("<pre><b>%s</b><hr>\n%s</pre>" % (html.escape(file.header), content_html))

		button_container = QHBoxLayout()

		vscode_btn = QPushButton("View in VS Code")

		def vscode():
			process = QProcess()

			tmp_file = tmp.mktmp(file.filename)

			file = io.open(tmp_file, "w")
			file.write(html.unescape(re.sub(r"<.*?>", "", content_html)) if file.ansi else full_content)
			file.close()

			process.startDetached("code", [tmp_file])

		vscode_btn.clicked.connect(vscode)

		button_container.addWidget(vscode_btn)
		button_container.addStretch()

		layout = QVBoxLayout(container)
		layout.addWidget(label, stretch=1)
		layout.addLayout(button_container)

class OutputViewerWindow(QMainWindow):

	def __init__(self, file: FileData):
		super(OutputViewerWindow, self).__init__()

		self.resize(640, 480)
		self.setWindowTitle("Veryfire - " + file.filename)

		self.setCentralWidget(OutputViewer(file))

		self.center()

	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())
