from PyPaper.core.styleditem import StyledItem
from PyPaper.core.animation import *

items = []
for i in range(1, 10):
	it = StyledItem(_root_)
	it.resize_to(25, 25)
	it.move_to(50 * i, 50)
	items.append(it)

with seq_anim_cm(*items):
	for j in range(4):
		with seq_anim_cm(*items):
			for y in (50, 200):
				with par_anim_cm(*items):
					for i, it in enumerate(items, 1):
						it.move_to(50 * i, y)
