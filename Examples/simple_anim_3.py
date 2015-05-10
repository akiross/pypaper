from PyPaper.core.styleditem import StyledItem
from PyPaper.core.animation import *

a = StyledItem(_root_)
b = StyledItem(_root_)

a.resize_to(25, 25)
b.resize_to(25, 25)

a.set_pos(50, 50)
b.set_pos(100, 50)

with seq_anim_cm(a) as ag:
	for _ in range(2):
		a.move_to(50, 100)
		with seq_anim_cm(b, parent_ag=ag):
			for _ in range(2):
				b.move_to(100, 100)
				b.move_to(100, 50)
		a.move_to(50, 50)

