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

from PyQt5.QtGui import QColor
from collections import namedtuple
import sys

class Rect(namedtuple('Rect', 'x y w h')):
	'''Class representing a Rectangle, used for geometry. READ-ONLY
	x and y, or x1 and y1, can be used to retrieve the top-left corner.
	w and h are used to get width and height of the rectangle
	x2 and y2 are used for the bottom-right corner (top-left + width-height).
	There is a limited support for swizzle: xy, wh (or size), xw, yh'''
	def __getattr__(self, name):
		if name == 'x1': return self.x
		if name == 'x2': return self.x + self.w
		if name == 'y1': return self.y
		if name == 'y2': return self.y + self.h
		if name == 'xy': return (self.x, self.y)
		if name in ['wh', 'size']: return (self.w, self.h)
		if name == 'xw': return self.x, self.w
		if name == 'yh': return self.y, self.h
		if name == 'xyxy': return self.x1, self.y1, self.x2, self.y2
		if name == 'xxyy': return self.x1, self.x2, self.y1, self.y2
		return super().__getattr__(name)

def wrap_skip(func):
	'''Returns a function that wraps func so that, in the wrapped
	function, the second argument is ignored, but all other arguments
	are passed to func'''
	def _skip2(*args):
		return func(args[0], *args[2:])
	return _skip2

def make_rgba(r, g, b, a=1):
	return QColor.fromRgbF(r, g, b, a)

def bind_line(line, item_1, item_2):
	def map_center(pos, size):
		'''Given a position (top-left corner),
		computes the center by adding half size'''
		return map(lambda a, b: a + b / 2, pos, size)

	def _bind_pos(func):
		def on_change(self, obj, xy_new, xy_old):
			func(self, *map_center(xy_new, obj.get_size()))
		return on_change

	def _bind_cent(func):
		def on_change(self, obj, wh_new, wh_old):
			func(self, *map_center(obj.get_pos(), wh_new))
		return on_change

	# Bind item position change to line property update
	line_t = type(line)
	item_1.register('on_pos_changed', line, _bind_pos(line_t.set_start))#_bind(line, 'set_start'))
	item_2.register('on_pos_changed', line, _bind_pos(line_t.set_end))#_bind(line, 'set_end'))
	item_1.register('on_size_changed', line, _bind_cent(line_t.set_start))
	item_2.register('on_size_changed', line, _bind_cent(line_t.set_end))

	# Ensure that line has correct start and end positions
	line.set_start(*map_center(item_1.get_pos(), item_1.get_size()))
	line.set_end(*map_center(item_2.get_pos(), item_2.get_size()))

