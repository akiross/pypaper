from PyPaper.core.styleditem import StyledItem
from PyPaper.core.animation import *

a = StyledItem(_root_)
b = StyledItem(_root_)

a.resize_to(25, 25)
b.resize_to(25, 25)

with seq_anim_cm(a, b):
	for i in range(4):
		with seq_anim_cm(a, b):
			for pos in (((50, 50), (100, 50)), ((100, 50), (100, 100))):
				with par_anim_cm(a, b):
					a.move_to(*pos[0])
					b.move_to(*pos[1])

