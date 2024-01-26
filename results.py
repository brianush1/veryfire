from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPushButton, QScrollArea, QVBoxLayout
from PyQt5.QtCore import Qt, QSize, QProcess
from flowlayout import FlowLayout
from judge import Verdict
from outputviewer import OutputViewer, DiffViewer, FileData
import io

class ResultsWindow(QMainWindow):

	def __init__(self, compiled_file, tests, language, time_limit, checker):
		super().__init__()

		self.compiled_file = compiled_file
		self.tests = tests
		self.language = language
		self.time_limit = time_limit
		self.checker = checker

		self.resize(640, 480)
		self.setWindowTitle("Veryfire - Results")

		self.setStyleSheet("""
			.caselabel {
				color: #fff;
				padding: 8px;
				font-weight: 700;
				border: 1px solid gray;
			}

			.selected {
				padding: 7px;
				border: 2px solid #07f;
			}
		""")

		scroll_area = QScrollArea()
		scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
		scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		scroll_area.setWidgetResizable(True)
		self.setCentralWidget(scroll_area)

		container = QWidget()
		scroll_area.setWidget(container)

		label = QLabel()
		label.setText("Test case results:")

		hlayout = FlowLayout()

		self.case_btns = []
		self.case_results = []
		self.case_statuses = []
		self.case_vlayouts = []
		for i in range(len(tests)):
			case_btn = QPushButton()
			case_btn.setText(str(i) + "    ...")
			case_btn.setProperty("class", "caselabel")
			case_btn.setStyleSheet("""
				background-color: #888;
			""")
			hlayout.addWidget(case_btn)
			self.case_btns.append(case_btn)

			case_container = QWidget()

			case_vlayout = QVBoxLayout(case_container)

			case_status = QLabel(case_container)
			case_status.setText("This case is still queued")
			case_vlayout.addWidget(case_status)

			case_vlayout.addStretch()

			self.case_results.append(case_container)
			self.case_statuses.append(case_status)
			self.case_vlayouts.append(case_vlayout)

			def get_on_click(i, btn):
				def on_click():
					nonlocal i, btn

					if self.current_page_btn != None:
						self.current_page_btn.setProperty("class", "caselabel")
						self.current_page_btn.style().unpolish(self.current_page_btn)
						self.current_page_btn.style().polish(self.current_page_btn)
						self.current_page_btn.update()

					next_page = self.case_results[i]
					self.vlayout.replaceWidget(self.current_page, next_page)
					self.current_page.hide()
					next_page.show()
					self.current_page = next_page

					self.current_page_btn = btn
					self.current_page_btn.setProperty("class", "caselabel selected")
					self.current_page_btn.style().unpolish(self.current_page_btn)
					self.current_page_btn.style().polish(self.current_page_btn)
					self.current_page_btn.update()

				return on_click

			case_btn.clicked.connect(get_on_click(i, case_btn))

		self.vlayout = QVBoxLayout(container)
		self.vlayout.addWidget(label)
		self.vlayout.addLayout(hlayout)

		dummy = QWidget()
		self.current_page_btn = None
		self.current_page = dummy
		self.vlayout.addWidget(dummy, stretch=1)

		self.judge(0)

	def judge(self, test_index):
		test = self.tests[test_index]

		self.case_statuses[test_index].setText("This case is currently being executed")

		with io.open(test[0], "r") as file:
			input_data = file.read()

		with io.open(test[1], "r") as file:
			expected_output_data = file.read()

		def callback(verdict, output_data, time_taken):
			if verdict == Verdict.ACCEPTED:
				if not self.checker.check(expected_output_data, output_data):
					verdict = Verdict.WRONG_ANSWER

			match verdict:
				case Verdict.ACCEPTED:
					verdict_str = "PASS"
				case Verdict.WRONG_ANSWER:
					verdict_str = "WA"
				case Verdict.TIME_LIMIT:
					verdict_str = "TLE"
				case Verdict.MEMORY_LIMIT:
					verdict_str = "MLE"
				case Verdict.RUNTIME_ERROR:
					verdict_str = "RTE"

			case_btn = self.case_btns[test_index]
			case_btn.setText(str(test_index) + "    " + verdict_str)
			if verdict == Verdict.ACCEPTED:
				case_btn.setStyleSheet("background-color: #0c0;")
			else:
				case_btn.setStyleSheet("background-color: #c00;")

			self.case_statuses[test_index].setText("Time taken: " + time_taken)

			if verdict == Verdict.RUNTIME_ERROR:
				stderr_file = FileData("stderr", "Standard error", output_data, ansi=False)
				self.case_vlayouts[test_index].addWidget(OutputViewer(stderr_file), stretch=1)
			elif output_data != None:
				expected_file = FileData("expected.out", "Expected output", expected_output_data, ansi=False)
				user_file = FileData("user.out", "User output", output_data, ansi=False)
				self.case_vlayouts[test_index].addWidget(DiffViewer(expected_file, user_file), stretch=1)

			if test_index + 1 < len(self.tests):
				self.judge(test_index + 1)

		self.language.run(self.compiled_file, input_data, self.time_limit, callback)
