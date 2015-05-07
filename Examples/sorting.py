# Visualizing sorting algorithms
#
# This script shall be run inside pypaper:
#     ./pypaper Examples/sorting.py
# or, from the pypaper console:
#     %open Examples/sorting

from PyQt5.QtCore import Qt
from PyPaper.core.styleditem import StyledItem
from PyPaper.core.animation import seq_anim_cm, par_anim_cm

data = []
for i in range(30):
	data.append(StyledItem(_root_))

def reset_data():
	'''Reset data positions and sizes'''
	for i, it in enumerate(data):
		it.move_to(50, 100 + 10 * i)
		it.resize_to(10 * i + 10, 5)
		it.set_border_size(0, 0, 0, 0)

def update_positions(duration=500):
	'''Ensures that current items are
	positioned as they appear in data'''
	with par_anim_cm(*data):
		for i, it in enumerate(data):
			it.move_to(50, 100 + 10 * i, duration=duration)

def swap(i, j):
	'''Swap the items (not their positions)
	i and j in the data list'''
	t = data[i]
	data[i] = data[j]
	data[j] = t

def shuffle():
	'''Shuffle the data and update the positions'''
	from random import shuffle
	shuffle(data)
	update_positions()

def selection_sort():
	'''Insertion sort'''
	SHORT = 25
	LONG = 100
	with seq_anim_cm(*data):
		for i, it in enumerate(data):
			it.background_color_to((0, 0, 1), duration=LONG)
			# Find smallest element
			min_i = i
			# Set minima color to green, because it's a good solution
			data[min_i].background_color_to((0, 1, 0), duration=LONG)
			# Search for better minima
			for j, it2 in enumerate(data[i:], i):
				# Set color to yellow, because it's being tested
				it2.background_color_to((1, 1, 0), duration=SHORT)
				if data[j].get_size()[0] < data[min_i].get_size()[0]:
					# Found a new minima, change colors
					data[min_i].background_color_to((1, 0, 0), duration=SHORT)
					min_i = j
					data[min_i].background_color_to((0, 1, 0), duration=SHORT)
				else:
					it2.background_color_to((1, 0, 0), duration=SHORT)
			# Found minimum
			data[min_i].background_color_to((0, 1, 0), duration=LONG)
			# Swap and update
			swap(i, min_i)
			update_positions(LONG)

def keyPressEvent(self, event):
	if event.text() == 's':
		shuffle()
	elif event.text() == 'r':
		reset_data()
	elif event.text() == '1':
		selection_sort()
	elif event.key() == Qt.Key_Escape:
		_win_.toggle_panel()

print('== Visualizing sorting algorithms ==')
print('Press s to shuffle')
print('Press r to reset')
print('Press 1 for selection sort')
print('Press Esc to toggle the console')

reset_data()
_canvas_.keyPressEvent = keyPressEvent.__get__(_canvas_, _canvas_.__class__)

