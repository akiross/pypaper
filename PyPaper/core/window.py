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

from PyQt5.QtWidgets import *
from PyQt5.QtQuick import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QFont, QTextCursor, QWheelEvent

from PyPaper.core.styleditem import StyledItem
from PyPaper.core.jedimodel import JediEdit

import os
import sys
import io
import code

class QuickWindow(QQuickWindow):
	def __init__(self, parent=None):
		super().__init__(parent)
		self._tfb = None
	
	def get_size(self):
		return self.width(), self.height()
	
	def fire_first_expose(self, func):
		self._tbf = func
	
	def exposeEvent(self, event):
		super().exposeEvent(event)
		if self._tbf is not None:
			# tbf may be a long-running process
			# that causes the expose event.
			# Therefore, remove it before running
			fun = self._tbf
			self._tbf = None
			fun()

	def resizeEvent(self, event):
		super().resizeEvent(event)
	def keyPressEvent(self, event):
		super().keyPressEvent(event)
	def keyReleaseEvent(self, event):
		super().keyReleaseEvent(event)
	def mouseDoubleClickEvent(self, event):
		super().mouseDoubleClickEvent(event)
	def mouseMoveEvent(self, event):
		super().mouseMoveEvent(event)
	def mousePressEvent(self, event):
		super().mousePressEvent(event)
	def mouseReleaseEvent(self, event):
		super().mouseReleaseEvent(event)
	def wheelEvent(self, event):
		super().wheelEvent(event)

class Window(QWidget):
	def __init__(self, sources=[], command=None, parent=None):
		super().__init__(parent)

		# The QuickWindow used to store the scenegraph and showing the images
		self.qqw_ = QuickWindow()

		# Prompt symbols for normal prompt and continuation prompt
		self.prompts_ = ['>>>', '...']
		# The label containing the symbol
		self.prompt_ = QLabel(self.prompts_[0])
		# A line edit to get user input
		self.console_ = JediEdit('')
		self.console_.returnPressed.connect(self.run_code)
		# A text eitor to store the results (read-only)
		self.output_ = QPlainTextEdit()
		self.output_.setReadOnly(True)
#		self.output_.setMaximumBlockCount(100
		# Make text monospaced
		font = QFont()
		font.setFamily("Monospace")
		font.setStyleHint(QFont.Monospace)
		font.setPointSize(10)
		self.output_.setFont(font)

		# Use output_ to display stdout and stderr
		# TODO check if redirect_stdout/redirect_stderr can help
		class Writer(io.IOBase):
			'''This class is used in place of stdout and stderr to
			print directly to the output window.
			If tee is provided, write also happens on that stream.'''
			def __init__(self, edit, color=None, tee=None):
				self.edit_ = edit
				self.col_ = color
				self._tee = tee
				self._buffer = ''

				self.errors = 'backslashreplace'
				self.encoding = 'UTF-8'

			def write(self, data):
				# If tee is present, write also on that
				if self._tee is not None:
					self._tee.write(data)

				# Buffer the data, we work row-wise
				self._buffer += data
				lines = self._buffer.split('\n')
				for line in lines[:-1]:
					# Move to the end point and insert the text
					if self.col_ is None:
						self.edit_.appendPlainText(line)
					else:
						line = line.replace('&', '&amp;').replace(' ', '&nbsp;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br/>')
						html = "<font color='{}'>{}</font>".format(self.col_, line)
						self.edit_.appendHtml(html)
				# Last line goes in the buffer
				self._buffer = lines[-1]

		# Window container
		container_w = QWidget.createWindowContainer(self.qqw_)
		container_w.setMinimumSize(QSize(50, 50))
		container_w.setFocusPolicy(Qt.TabFocus)
		self._container_wid = container_w

		# Prompt widget (prompt + input)
		hbl = QHBoxLayout()
		hbl.setContentsMargins(0, 0, 0, 0)
		hbl.addWidget(self.prompt_)
		hbl.addWidget(self.console_)
		prompt_w = QWidget()
		prompt_w.setLayout(hbl)

		# Console widget (output + prompt)
		vbl_cons = QVBoxLayout()
		vbl_cons.setContentsMargins(0, 0, 0, 0)
		vbl_cons.addWidget(self.output_)
		vbl_cons.addWidget(prompt_w)
		self.console_w_ = QWidget()
		self.console_w_.setLayout(vbl_cons)

		# Use a splitter to allow terminal resize
		split = QSplitter(Qt.Horizontal)
		split.addWidget(self.console_w_)
		split.addWidget(container_w)

		# Window layout
		hbl_win = QHBoxLayout()
		hbl_win.addWidget(split)
		hbl_win.setContentsMargins(1, 1, 1, 1)
		self.setLayout(hbl_win)

		self.reset_interpreter()

		# After initialization, setup the output streams
		sys.stdout = Writer(self.output_, color='black', tee=sys.__stdout__)
		sys.stderr = Writer(self.output_, color='red', tee=sys.__stderr__)
#		sys.stdin = TODO would be nice to have an object as stdin to use with input()

		# As last thing, it's possible to run the scripts
		def _scripts_on_expose():
			# Run files
			for src in sources:
				self.run_file(src)
			# Run commands
			if command is not None:
				self.console_.setText(command)
				self.run_code(None)
		# To make sure everything is loaded before the scripts
		# and commands are run, wait the first expose event
		self.qqw_.fire_first_expose(_scripts_on_expose)
	
	def reset_interpreter(self):
		self.py_ctx_ = {
			'_root_': self.qqw_.contentItem(),
			'_canvas_': self.qqw_,
			'_win_': self,
		}
		self.interp_ = code.InteractiveConsole(self.py_ctx_)

	def show_panel(self):
		'''Show the console panel'''
		self.console_w_.show()
		# Set focus to the console and highlight text if any
		self.console_.setFocus(Qt.OtherFocusReason)
		self.console_.selectAll()

	def hide_panel(self):
		'''Hide the console panel'''
		self.console_w_.hide()
		# TODO Ensure the window has the focus
		# and that when panel is hidden, focus is exclusively
		# owned by window
		
	def toggle_panel(self):
		'''Toggle the console panel, showing it if not visible and vice-versa'''
		if self.console_w_.isVisible():
			self.hide_panel()
		else:
			self.show_panel()
	
	def run_file(self, path):
		'''Reads a file and execute it as if typed'''
		if os.path.isfile(path):
			src = open(path).read()
			code = compile(src, path, 'exec')
			self.console_.add_history(src)
			self.interp_.runcode(code)
			# Update locals
			self.console_.update_locals(self.py_ctx_)
		else:
			raise RuntimeError('Not a file: {}'.format(path))

	def run_code(self, cmd=None):
		'''Process the code in the console, running it as an interactive terminal'''
		# Get the command to execute
		if cmd is None:
			cmd = self.console_.text()

		# Special command for loading/opening
		# %load loads a module from the source directory
		# open executes a file in the given path (relative)
		if cmd.startswith('%load') or cmd.startswith('%open'):
			path = cmd[6:].strip().replace('.', '/') # dir.module to dir/module
			if cmd.startswith('%load'):
				fullpath = os.path.join(os.path.dirname(__file__), path)
			else:
				fullpath = path
			cmd = 'exec(open("{}.py").read())'.format(fullpath)

		# Lock the console to avoid changes during long running commands
		self.console_.setReadOnly(True)
		# Write and push it to the interactive interpreter
		print(self.prompt_.text() + ' ' + cmd)
		if self.interp_.push(cmd):
			# Restore the prompt
			self.prompt_.setText(self.prompts_[1])
		else:
			# If return is false, command is completed, result goes to stdout
			self.prompt_.setText(self.prompts_[0])
		# Save command to history and clear
#		print('Executing console command')
		self.console_.save_and_clear()
		# Activate the console again
		self.console_.setReadOnly(False)
		# Update Jedi's locals for better completion
		self.console_.update_locals(self.py_ctx_)
