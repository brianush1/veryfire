from PyQt5.QtCore import QProcess, QTimer
from pathlib import Path
from enum import Enum
import tempfile
import time

verbose = False

class Verdict(Enum):
	ACCEPTED = 0
	WRONG_ANSWER = 1
	TIME_LIMIT = 2
	MEMORY_LIMIT = 3
	RUNTIME_ERROR = 4

class JavaJudge:

	def __init__(self):
		self.name = "Java"

	def compile(self, filename, callback):
		raise NotImplementedError("TODO: implement java")

	def run(self, compiled_file, input_data, time_limit, callback):
		process = QProcess()

		cmd = "java " + compiled_file[:-6]
		if verbose:
			print(cmd)

		start = time.time()
		process.start("java", [compiled_file[:-6]])
		process.write(input_data.encode("utf-8"))
		process.closeWriteChannel()

		self.kill_timer = QTimer()
		self.kill_timer.start(int(time_limit * 1000))
		self.kill_timer.setSingleShot(True)

		callback_called = False

		def on_timeout():
			nonlocal callback_called

			if not callback_called:
				callback_called = True
				callback(Verdict.TIME_LIMIT, None, ">" + str(int(time_limit * 1000)) + "ms")

			process.kill()

		self.kill_timer.timeout.connect(on_timeout)

		def on_finished(exit_code, exit_status):
			nonlocal callback_called

			if not callback_called:
				callback_called = True
				time_taken = str(int((time.time() - start) * 1000)) + "ms"
				if exit_code == 0 and exit_status == QProcess.NormalExit:
					callback(Verdict.ACCEPTED, process.readAllStandardOutput().data().decode(), time_taken)
				else:
					callback(Verdict.RUNTIME_ERROR, process.readAllStandardError().data().decode(), time_taken)

		process.finished.connect(on_finished)

class CppJudge:

	def __init__(self):
		self.name = "C++"

	def compile(self, filename, callback):
		process = QProcess()

		output_file = tempfile.mktemp()

		cmd = "g++ -O2 -o " + output_file + " \"" + filename + "\""
		if verbose:
			print(cmd)

		process.start("g++", ["-fdiagnostics-color=always", "-O2", "-o", output_file, filename])

		def on_finished(exit_code, exit_status):
			if exit_code == 0 and exit_status == QProcess.NormalExit:
				callback(True, output_file, cmd)
			else:
				err = process.readAllStandardError().data().decode()
				callback(False, err, cmd)

		process.finished.connect(on_finished)

	def run(self, compiled_file, input_data, time_limit, callback):
		process = QProcess()

		cmd = compiled_file
		if verbose:
			print(cmd)

		start = time.time()
		process.start(compiled_file)
		process.write(input_data.encode("utf-8"))
		process.closeWriteChannel()

		self.kill_timer = QTimer()
		self.kill_timer.start(int(time_limit * 1000))
		self.kill_timer.setSingleShot(True)

		callback_called = False

		def on_timeout():
			nonlocal callback_called

			if not callback_called:
				callback_called = True
				callback(Verdict.TIME_LIMIT, None, ">" + str(int(time_limit * 1000)) + "ms")

			process.kill()

		self.kill_timer.timeout.connect(on_timeout)

		def on_finished(exit_code, exit_status):
			nonlocal callback_called

			if not callback_called:
				callback_called = True
				time_taken = str(int((time.time() - start) * 1000)) + "ms"
				if exit_code == 0 and exit_status == QProcess.NormalExit:
					callback(Verdict.ACCEPTED, process.readAllStandardOutput().data().decode(), time_taken)
				else:
					callback(Verdict.RUNTIME_ERROR, process.readAllStandardError().data().decode(), time_taken)

		process.finished.connect(on_finished)

class Python3Judge:

	def __init__(self):
		self.name = "Python 3"

	def compile(self, filename, callback):
		callback(True, filename, "none")

	def run(self, compiled_file, input_data, time_limit, callback):
		process = QProcess()

		cmd = "python3 " + compiled_file
		if verbose:
			print(cmd)

		start = time.time()
		process.start("python3", [compiled_file])
		process.write(input_data.encode("utf-8"))
		process.closeWriteChannel()

		self.kill_timer = QTimer()
		self.kill_timer.start(int(time_limit * 1000))
		self.kill_timer.setSingleShot(True)

		callback_called = False

		def on_timeout():
			nonlocal callback_called

			if not callback_called:
				callback_called = True
				callback(Verdict.TIME_LIMIT, None, ">" + str(int(time_limit * 1000)) + "ms")

			process.kill()

		self.kill_timer.timeout.connect(on_timeout)

		def on_finished(exit_code, exit_status):
			nonlocal callback_called

			if not callback_called:
				callback_called = True
				time_taken = str(int((time.time() - start) * 1000)) + "ms"
				if exit_code == 0 and exit_status == QProcess.NormalExit:
					callback(Verdict.ACCEPTED, process.readAllStandardOutput().data().decode(), time_taken)
				else:
					callback(Verdict.RUNTIME_ERROR, process.readAllStandardError().data().decode(), time_taken)

		process.finished.connect(on_finished)

languages = [JavaJudge(), CppJudge(), Python3Judge()]

class TokenChecker:

	def __init__(self):
		self.name = "Token Checker"
		self.case_sensitive = True

	def check(self, expected, provided):
		expected_tokens = expected.split()
		provided_tokens = provided.split()
		if len(expected_tokens) != len(provided_tokens):
			return False
		for i in range(len(expected_tokens)):
			expected_token = expected_tokens[i]
			provided_token = provided_tokens[i]
			if self.case_sensitive:
				if expected_token != provided_token:
					return False
			else:
				if expected_token.lower() != provided_token.lower():
					return False
		return True

class DiffChecker:

	def __init__(self):
		self.name = "Diff Checker"
		self.ignore_trailing_whitespace = True
		self.ignore_trailing_newlines = True

	def check(self, expected, provided):
		expected_lines = expected.splitlines()
		provided_lines = provided.splitlines()

		if self.ignore_trailing_whitespace:
			for i in range(len(expected_lines)):
				expected_lines[i] = expected_lines[i].rstrip()
			for i in range(len(provided_lines)):
				provided_lines[i] = provided_lines[i].rstrip()

		if self.ignore_trailing_newlines:
			while expected_lines[-1] == "":
				expected_lines.pop()
			while provided_lines[-1] == "":
				provided_lines.pop()

		if len(expected_lines) != len(provided_lines):
			return False
		for i in range(len(expected_lines)):
			expected_line = expected_lines[i]
			provided_line = provided_lines[i]
			if expected_line != provided_line:
				return False
		return True

class EpsilonChecker:

	def __init__(self):
		self.name = "Epsilon Checker"
		self.relative_epsilon = 1e-6
		self.absolute_epsilon = 1e-6

	def check(self, expected, provided):
		expected_tokens = expected.split()
		provided_tokens = provided.split()
		if len(expected_tokens) != len(provided_tokens):
			return False
		for i in range(len(expected_tokens)):
			expected_token = expected_tokens[i]
			provided_token = provided_tokens[i]
			try:
				expected_num = float(expected_token)
				provided_num = float(provided_token)

				if abs(expected_num) > 0:
					within_threshold = abs((expected_num - provided_num) / expected_num) <= self.relative_epsilon
				else:
					within_threshold = False

				if not within_threshold:
					within_threshold = abs(expected_num - provided_num) <= self.absolute_epsilon

				if not within_threshold:
					return False
			except ValueError:
				pass
		return True

checkers = [TokenChecker(), DiffChecker(), EpsilonChecker()]

def find_cases(root_dir):
	files = []
	for p in Path(root_dir).iterdir():
		if p.is_dir():
			yield from find_cases(p)
		elif p.is_file():
			files.append(p.resolve())

	input_file = list(filter(lambda x: x.name.endswith(".in"), files))
	output_file = list(filter(lambda x: x.name.endswith(".out"), files))
	if len(input_file) == 1 and len(output_file) == 1:
		yield (input_file[0], output_file[0])
	else:
		input_files = dict()
		for file in files:
			if file.name.endswith(".in"):
				input_files[file.name[:-3]] = file
		for file in files:
			if file.name.endswith(".out") and file.name[:-4] in input_files:
				yield (input_files[file.name[:-4]], file)
