import tempfile
import os
import shutil
from random import randint

root_dir = tempfile.mkdtemp()

def mktmp(name):
	directory = root_dir + "/" + str(randint(0, 1_000_000_000))
	os.mkdir(directory)
	return directory + "/" + name

def cleanup():
	shutil.rmtree(root_dir)
