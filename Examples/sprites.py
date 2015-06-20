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
	state, dist = v_dist(self.get_pos(), target, False)
	return dist

@sequenced
class MySprite(Sprite):
	def __init__(self, parent, *args):
		super().__init__(parent, *args)
		self.set_size(50, 50)

	@sequence('run', speed=200, action=StyledItem.move_to, distance_func=pos_dist, easing='OutBounce')
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

s = MySprite(_root_, True)

with seq_anim_cm(s):
	# Show effect of different speed
	for speed in [200, 400, 800]:
		s.resize_to(10, 300)
		s.resize_to(300, 10)
		s.resize_to(50, 50, speed=speed, easing='Linear')

	# Defined sequences
	s.walk_to(300, 0)
	s.run_to(0, 100)
	s.move_to(400, 200, speed=100, easing='Linear')

	# Offset
#	s.walk_to(100, 100, offset=True) TODO

	# Speed works also on colors
	s.background_color_to((0, 1, 0), duration=2000) # This will take fixed time
	s.background_color_to((1, 0, 0), duration=0)
	s.background_color_to((0, 1, 0), speed=1) # This will take some time
	s.background_color_to((1, 0, 0), duration=0)
	s.background_color_to((0.5, 0, 0), speed=1) # This will take less time
