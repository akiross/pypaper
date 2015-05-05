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

from PyQt5.QtQuick import *
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from PyPaper.core.styleditem import StyledItem
from PyPaper.tools.tools import *

# TODO add text facilities to StyledItem

class CircleItem(StyledItem):
	def __init__(self, parent=None):
		super().__init__(parent)
		# Set radius relative to size
		self.set_rect_radius_mode(True)
		# 100% of the half-side
		self.set_rect_radius(100, 100)
		# Better drawing with a lil margin
		self.set_margins(1, 1, 1, 1)
	
	def set_radius(self, r):
		self.set_size(2 * r, 2 * r)
	
	def get_radius(self):
		return self.get_size()[0] / 2

	def radius_to(self, r):
		self.resize_to(2 * r, 2 * r)

class LineItem(StyledItem):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.start_ = (0, 0)
		self.end_ = (0, 0)

		self._start_mark = None
		self._end_mark = None

		self.lw_ = 2
	
	def set_start(self, x, y):
		self.start_ = (x, y)
		self._update_geometry()

	def set_end(self, x, y):
		self.end_ = (x, y)
		self._update_geometry()
	
	def set_line_width(self, lw):
		self.lw_ = lw
		self._update_geometry()
	
	def set_start_marker(self, mark):
		self._start_mark = mark
		self.update()

	def set_end_marker(self, mark):
		self._end_mark = mark
		self.update()
	
	def _update_geometry(self):
		'''Update item geometry using start and end points'''
		# Get start and end points
		sx, sy = self.start_
		ex, ey = self.end_
		# Get max and min values, because we can't use negative values
		mx, my = min(sx, ex), min(sy, ey)
		Mx, My = max(sx, ex), max(sy, ey)
		# Update geometry
		self.setX(mx - self.lw_)
		self.setY(my - self.lw_)
		self.setWidth(Mx - mx + self.lw_ * 2)
		self.setHeight(My - my + self.lw_ * 2)
	
	def paint(self, painter):
		'''
		:type painter: QPainter
		'''
		painter.setRenderHint(QPainter.Antialiasing, True)
		pen = QPen()
		pen.setColor(self.get_border_color())
		lw = self.lw_
		pen.setWidth(lw)
		painter.setPen(pen)

		sx, sy = self.start_
		ex, ey = self.end_

		x, x2 = lw, self.width() - lw
		if sx > ex:
			x, x2 = x2, x
		y, y2 = lw, self.height() - lw
		if sy > ey:
			y, y2 = y2, y

		if hasattr(self, 'line_offset'):
			offs = self.line_offset
		else:
			offs = 0

		if offs > 0:
			from math import atan2, sin, cos
			# Compute angle for the line
			ang = atan2(y2 - y, x2 - x)
			# TODO negative lines shall not exist
			x += cos(ang) * offs
			y += sin(ang) * offs
			x2 -= cos(ang) * offs
			y2 -= sin(ang) * offs

		painter.drawLine(x, y, x2, y2)

		if self._start_mark:
			painter.fillRect(x - 5, y - 5, 10, 10, self.get_border_color())
		if self._end_mark:
			painter.fillRect(x2 - 5, y2 - 5, 10, 10, self.get_border_color())

		painter.drawText((x + x2) * 0.5, (y + y2) * 0.5, self.get_text())

