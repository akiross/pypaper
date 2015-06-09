# Let's put here the codebase and then move it to the tools/sprite.py module

# Frame Animation First.
# This animation is very simple: updates a float value from 0 to 1 during
# a specified amount of time
#
# 1. fare l'animation, pura e semplice
# 2. 

from PyPaper.core.styleditem import StyledItem
from PyPaper.core.animation import par_anim_cm, seq_anim_cm
from PyQt5.QtCore import QAbstractAnimation, QRectF, QEasingCurve
from functools import partial
from collections import namedtuple
from PyQt5.QtGui import QPainter
import warnings

class TimeAnim(QAbstractAnimation):
	def __init__(self, duration, callback, easing='InOutQuad', parent=None):
		super().__init__(parent)
		self._duration = duration
		self._callback = callback
		# FIXME Abstractanimation non ha l'easing curve, che però ha variant animation
		# Bisogna considerare di sostituirlo. Inoltre, c'é da subclassare meno
		# e forse basta segnare i valori di inizio e fine e durata (duration sparisce)
		# mentre il resto rimarrebbe simile (start in 0, end in duration)
#		if hasattr(QEasingCurve, easing):
#			ec = getattr(QEasingCurve, easing)
#		else:
#			ec = QEasingCurve.Linear
#		self.setEasingCurve(ec)
	
	def duration(self):
		return self._duration

	def updateCurrentTime(self, curr_time):
		self._callback(curr_time, self._duration)

def v_dist(target, orig, offs):
	'''Computes Euclidean distance between (x,y) and (ox,oy)
	and return target absolute position as well as distance'''
	if offs:
		target = [t + ox if t is not None else None for t in target]
	dt = [0 if t is None else (t - ot) ** 2 for t, ot in zip(target, orig)]
	return target, sum(dt) ** 0.5

def sequenced(cls):
	setattr(cls, '_sequences', {})
	for m_name in set(cls.__dict__.keys()):
		method = cls.__dict__[m_name]
		# Filter methods not for sequence
		if not hasattr(method, '__seq'):
			continue
		# Found a sequence method, get the parameters
		name, paint_func, params = getattr(method, '__seq')
	
		# Save the sequence painting function
		cls._sequences[name] = paint_func

		# If there is no action, method just animate frames
		# Params are guaranteed to contain a default duration
		def _nact_seq(self, *args, **kwargs):
			duration = kwargs.get('duration', params['duration'])
			print('Performing sequence', name, 'w/ duration', duration)
			# No animation with zero duration
			if duration <= 0:
				return
			# Create the animation
			with par_anim_cm(self) as grp:
				# Create time dependent animation
				ta = TimeAnim(duration, partial(self._set_current_frame, name))
				grp.addAnimation(ta)

		# If there is an action, method computes duration and
		# execute the action in parallel with frame animation
		# params may contain duration or speed
		def _act_seq(self, *args, **kwargs):
			# Get actions FIXME a better way is required to handle actions and their duration given *args
			action_write, action_read = params['action']
			if 'speed' not in params:
				duration = params['duration']
			else:
				print('Computing state and duration')
				# Get current state (position, rotation, whatever)
				state = action_read(self)
				print('  State is', state)
				# Compute distance between current and desired state
				state, dist = v_dist(state, args, kwargs.get('offset', False))
				print('  State dist', state, dist)
				# Compute duration
				duration = dist * 1000 / params['speed']
			print('Performing sequence', name, 'w/ duration', duration)
			# No animation with zero duration
			if duration <= 0:
				return
			# Create the animation
			with par_anim_cm(self) as grp:
				# Create time dependent animation
				ta = TimeAnim(duration, partial(self._set_current_frame, name))
				# Perform the action
				action_write(self, *args, duration=duration, easing=params['easing'])
				grp.addAnimation(ta)

		if 'action' in params:
			_seq = _act_seq
		else:
			_seq = _nact_seq

		_seq.__name__ = name + '_to'
		_seq.__qualname__ = '.'.join(_seq.__qualname__.split('.')[:-1] + [_seq.__name__])
		setattr(cls, name + '_to', _seq)
	return cls

def sequence(name, speed=None, duration=None, action=None, easing='Linear'):
	# Check that parameters are Ok
	if action is None:
		# When action is None, we cannot compute distances, therefore
		# no speed can be calculated
		if duration is None:
			raise RuntimeError('Trying to define a sequence "{}" with no action and no duration. Duration and action cannot be both None.'.format(name))
		elif speed is not None:
			warnings.warn('Trying to set speed in sequence "{}" with no action. Speed with be ignored.'.format(name))
			speed = None
	elif speed is not None and duration is not None:
		# Speed and duration are in conflict: cannot have both
		warnings.warn('Trying to set speed and duration in sequence "{}". This is not valid, duration will be ignored.'.format(name))
		duration = None

	# Create the decorator function
	def _decorator(func):
		params = {
				'speed': speed,
				'duration': duration,
				'action': action,
				'easing': easing,
				'offset': False
				}
		setattr(func, '__seq', (name, func, params))
		return func
#		def _m_wrapper(self, *args, **kwargs):
#			return func(self, *args, **kwargs)
#		return _m_wrapper
	return _decorator

@sequenced
class Sprite(StyledItem):
	def __init__(self, parent):
		super().__init__(parent)
		self.set_size(30, 30)
		self._frame = (None, None, None)
		self._sequences = {}
	
	def paint(self, painter):
		sname, time, dur = self._frame
		if sname in Sprite._sequences:
			Sprite._sequences[sname](self, painter, time, dur)

	def _set_current_frame(self, sequence, time, duration):
		self._frame = (sequence, time, duration)
		self.update()

	@sequence('run', speed=200, action=(StyledItem.move_to, StyledItem.get_pos))
	def _run_paint(self, painter, time, duration):
		bbox = QRectF(0, 0, *self.get_size()).adjusted(1, 1, -1, -1)
		bbox.setHeight(bbox.height() * time / duration)
		painter.fillRect(bbox, self.get_background_color())

	@sequence('walk', speed=100, action=(StyledItem.move_to, StyledItem.get_pos))
	def _walk_paint(self, painter, time, duration):
		'''
		:type painter: QPainter
		'''
		bbox = QRectF(0, 0, *self.get_size()).adjusted(1, 1, -1, -1)
		bbox.setWidth(bbox.width() * time / duration)
		painter.fillRect(bbox, self.get_background_color())

s = Sprite(_root_)

with seq_anim_cm(s):
	# C'è un problema: questi non vengono messi davvero in sequenza e i valori sono calcolati immediatamente, non al momento della chiamata... WROOONG
	s.walk_to(100, 100)
	s.run_to(0, 0)

