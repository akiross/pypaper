# Let's put here the codebase and then move it to the tools/sprite.py module

from PyPaper.core.styleditem import StyledItem
from PyPaper.core.animation import seq_anim_cm
from PyPaper.tools.sprite import *
from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QPainter

def v_dist(target, orig, offs):
	'''Computes Euclidean distance between (x,y) and (ox,oy)
	and return target absolute position as well as distance'''
	if offs:
		target = [t + ox if t is not None else None for t in target]
	dt = [0 if t is None else (t - ot) ** 2 for t, ot in zip(target, orig)]
	return target, sum(dt) ** 0.5

def pos_dist(self, x, y, *args):
	target = (x, y)
#	print('Computing distance for self', self, 'and target', target, 'with extra args', args)
	# FIXME this distance is not the same distance used for animating the properties
	# properties are animated one at time, thus requiring less time than a single animation
	# of all of them. This is euclidean distance, the other is not
	state, dist = v_dist(self.get_pos(), target, False)
#	print('  Distance is', dist)
	return dist

@sequenced
class MySprite(Sprite):
	def __init__(self, parent):
		super().__init__(parent)
		self.set_size(50, 50)

	@sequence('run', speed=200, action=StyledItem.move_to, distance_func=pos_dist, easing='Linear')
	def _run_paint(self, painter, time, duration):
		bbox = QRectF(0, 0, *self.get_size()).adjusted(1, 1, -1, -1)
		if duration > 0:
			nehe = bbox.height() * time / duration
			bbox.setHeight(nehe)
		painter.fillRect(bbox, self.get_background_color())

	@sequence('walk', speed=100, action=StyledItem.move_to, distance_func=pos_dist)
	def _walk_paint(self, painter, time, duration):
		'''
		:type painter: QPainter
		'''
		bbox = QRectF(0, 0, *self.get_size()).adjusted(1, 1, -1, -1)
		if duration > 0:
			bbox.setWidth(bbox.width() * time / duration)
		painter.fillRect(bbox, self.get_background_color())

s = MySprite(_root_)

with seq_anim_cm(s):
	# C'è un problema: questi non vengono messi davvero in sequenza e i valori sono calcolati immediatamente, non al momento della chiamata... WROOONG
	s.walk_to(300, 0)
	s.run_to(0, 0)

