#!/usr/bin/env python3
# This file is part of PyPaper.
#
# PyPaper is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyPaper is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PyPaper.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2015 Alessandro "AkiRoss" Re

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon

from PyPaper.core.window import Window

import argparse

def main():
	import sys
	app = QApplication(sys.argv)

	parser = argparse.ArgumentParser(description='PyPaper is cwl')
	parser.add_argument('scripts', type=str, nargs='*', help='Source files')
	parser.add_argument('--command', '-c', type=str, help='Command to execute')
	args = parser.parse_args()

	screen = Window(args.scripts, args.command)
	screen.setWindowTitle('PyPaper')
	screen.resize(1024, 768)
	icon = QIcon('Art/icon128.png')
	app.setWindowIcon(icon)
	screen.show()

	sys.exit(app.exec_())

if __name__ == '__main__':
	main()

