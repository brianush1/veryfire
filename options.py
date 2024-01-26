from PyQt5.QtWidgets import (
	QMainWindow,
	QWidget,
	QLabel,
	QPushButton,
	QDoubleSpinBox,
	QLineEdit,
	QScrollArea,
	QGridLayout,
	QComboBox,
	QFileDialog,
	QHBoxLayout,
	QMessageBox,
	QDesktopWidget,
)

from judge import languages, checkers, find_cases
from os.path import exists, isdir
from pathlib import Path
from outputviewer import OutputViewerWindow, FileData
from results import ResultsWindow

class OptionsWindow(QMainWindow):

	def __init__(self):
		super().__init__()

		self.setWindowTitle("Veryfire")

		scroll_area = QScrollArea()
		scroll_area.setWidgetResizable(True)
		self.setCentralWidget(scroll_area)

		container = QWidget()
		scroll_area.setWidget(container)

		layout = QGridLayout(container)
		layout.addWidget(QLabel("Solution:"), 0, 0)

		self.solution_edit = QLineEdit()
		layout.addWidget(self.solution_edit, 0, 1)

		def browse_solution():
			solution_path, filter_used = QFileDialog.getOpenFileName(None, "Select Solution", "", "Java, Python, or C++ files (*.java *.py *.cpp)")
			self.solution_edit.setText(solution_path)

			if solution_path != "":
				basename = Path(solution_path).name

				if basename.endswith(".java"):
					self.language_selector.setCurrentIndex(0)
					basename = basename[:-5]
				elif basename.endswith(".cpp"):
					self.language_selector.setCurrentIndex(1)
					basename = basename[:-4]
				elif basename.endswith(".py"):
					self.language_selector.setCurrentIndex(2)
					basename = basename[:-3]

				candidate_data_path = Path(Path(solution_path).parent, "data", basename)
				if candidate_data_path.is_dir():
					self.data_edit.setText(str(candidate_data_path.resolve()))

		browse_solution_btn = QPushButton("Browse")
		browse_solution_btn.clicked.connect(browse_solution)
		layout.addWidget(browse_solution_btn, 0, 2)

		layout.addWidget(QLabel("Data folder:"), 1, 0)

		self.data_edit = QLineEdit()
		layout.addWidget(self.data_edit, 1, 1)

		def browse_data():
			data_path = QFileDialog.getExistingDirectory(None, "Select Data Folder", "")
			self.data_edit.setText(data_path)
		browse_data_btn = QPushButton("Browse")
		browse_data_btn.clicked.connect(browse_data)
		layout.addWidget(browse_data_btn, 1, 2)

		layout.addWidget(QLabel("Language:"), 2, 0)

		self.language_selector = QComboBox()
		self.language_selector.addItems(map(lambda x: x.name, languages))
		layout.addWidget(self.language_selector, 2, 1)

		layout.addWidget(QLabel("Time limit (in seconds):"), 3, 0)

		self.time_limit = QDoubleSpinBox()
		self.time_limit.setValue(1)
		self.time_limit.setSingleStep(0.1)
		self.time_limit.setMaximum(60)
		self.time_limit.setMinimum(0.1)
		layout.addWidget(self.time_limit, 3, 1)

		layout.addWidget(QLabel("Checker:"), 4, 0)

		self.checker_selector = QComboBox()
		self.checker_selector.addItems(map(lambda x: x.name, checkers))
		layout.addWidget(self.checker_selector, 4, 1)

		# layout.addWidget(QLabel("Case sensitive:"), 5, 0)
		# layout.addWidget(QLineEdit("test"), 5, 1)

		btn_layout = QHBoxLayout()

		self.judge_btn = QPushButton("Judge")
		btn_layout.addWidget(self.judge_btn, 5)

		layout.addLayout(btn_layout, 6, 0, 1, 3)

		layout.addWidget(QWidget(), 7, 0)
		layout.setRowStretch(7, 1)

		self.resize(640, self.sizeHint().height())

		self.judge_btn.clicked.connect(lambda: self.judge())

		self.center()

	def judge(self):
		solution_path = self.solution_edit.text()
		data_path = self.data_edit.text()

		if not exists(solution_path):
			QMessageBox.warning(self, "File not found", "No file was found at the provided path to the solution file")
			return

		if not exists(data_path) or not isdir(data_path):
			QMessageBox.warning(self, "Directory not found", "The provided path to the data directory doesn't name a directory")
			return

		tests = list(find_cases(data_path))
		if len(tests) == 0:
			QMessageBox.warning(self, "No test cases", "The provided path to the data directory doesn't contain any test cases")
			return

		language = languages[self.language_selector.currentIndex()]

		self.judge_btn.setText("Compiling...")
		self.judge_btn.setDisabled(True)

		def compile_callback(success, output, cmd):
			self.judge_btn.setText("Judge")
			self.judge_btn.setDisabled(False)

			if not success:
				self.viewer = OutputViewerWindow(FileData("stderr", cmd, output, ansi=True))
				self.viewer.show()
			else:
				self.results = ResultsWindow(
					compiled_file=output,
					tests=tests,
					language=language,
					time_limit=self.time_limit.value(),
					checker=checkers[self.checker_selector.currentIndex()],
				)
				self.results.showMaximized()

		language.compile(solution_path, compile_callback)

	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

