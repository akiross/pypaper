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

import jedi
import sys

# TODO tab-completion like zsh:
# if one option is available, tab completes it immediately
# if multiple are available, first tab shows them, subsequent tabs iterate thru them

class JediEdit(QLineEdit):
	tabPressed = pyqtSignal()

	def __init__(self, text="", parent=None):
		super().__init__(parent)
		self._model = QStringListModel()
		self._compl = QCompleter()
		self._compl.setModel(self._model)
		self.setCompleter(self._compl)
		self.textEdited.connect(self.update_model)
		self.setText(text)
		self._hist = '' # No history
		self._ns = [{}]
		self._currentRow = 0

		self.tabPressed.connect(self.next_completion)
#		self._compl.activated.connect(self.insert_completion)
#		self._compl.activated.connect(self.save_and_clear)
	
	def update_locals(self, namespace):
		self._ns = [namespace]

	def add_history(self, code):
		self._hist += code

	def save_and_clear(self):
#		print('Saving and clearing')
#		print('  Current row:', self._compl.currentRow())
#		print('  Current compl:', self._compl.currentCompletion())
#		print('  Complet count:', self._compl.completionCount())
#		print('  Complet pref:', self._compl.completionPrefix())
#		print('  Curr index:', self._compl.currentIndex())

		self.add_history(self.text() + '\n')
		self.clear()
	
	def update_model(self, cur_text):
		code = self._hist + '\n' + cur_text
		script = jedi.Interpreter(code, self._ns)#jedi.Script(code)
		compl = script.completions()
		sign = script.call_signatures()

#		print('Call sign', sign)
#		if not sign:
#			self._model.setStringList([])
#		else:
		strings = list(cur_text + c.complete for c in compl) 
		self._model.setStringList(strings)
	
	def next_completion(self):
		index = self._compl.currentIndex()
		self._compl.popup().setCurrentIndex(index)
		start = self._compl.currentRow()
		if not self._compl.setCurrentRow(start + 1):
			self._compl.setCurrentRow(0)
	
	def insert_completion(self, compl):
#		print('Completing with', compl)
#		self._compl.setCompletionPrefix('')
		self._compl.popup().hide()
		self.clear()

	def event(self, event):
		if event.type() == QEvent.KeyPress:
			if event.key() == Qt.Key_Tab:
				self.tabPressed.emit()
				return True
			if event.key() == Qt.Key_Return:
#				print('Return pressed event, checking popup...')
				if self._compl.popup().isVisible():
#					print('Popup visible')
					self._compl.popup().hide()
					return True
#					event.ignore()
#					return False
#				print('Return pressed')
#				if self._compl.popup().isVisible():
#					self._compl.popup().hide()
#					self._compl.complete()
		return super().event(event)

if __name__ == '__main__':
	app = QApplication(sys.argv)
	line = JediEdit()
	line.show()
	sys.exit(app.exec_())
