# Let's put here the codebase and then move it to the tools/sprite.py module

# Frame Animation First.
# This animation is very simple: updates a float value from 0 to 1 during
# a specified amount of time
#
# 1. fare l'animation, pura e semplice
# 2. 

from PyPaper.core.styleditem import StyledItem
from PyPaper.core.animation import par_anim_cm
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
		print('Processing class method:', m_name)
		method = cls.__dict__[m_name]
		# Filter methods not for sequence
		if not hasattr(method, '__seq'):
			continue
		print('Good method, has __seq info')
		# Found a sequence method, get the parameters
		name, paint_func, params = getattr(method, '__seq')
	
		# Save the sequence painting function
		print('Name is', name)
		cls._sequences[name] = paint_func

		# If there is no action, method just animate frames
		# Params are guaranteed to contain a default duration
		def _nact_seq(self, *args, **kwargs):
			print('Performing sequence w/o action', name)
			duration = kwargs.get('duration', params['duration'])
			# Create the animation
			with par_anim_cm(self) as grp:
				# Create time dependent animation
				ta = TimeAnim(duration, partial(self._set_current_frame, name))
				grp.addAnimation(ta)

		# If there is an action, method computes duration and
		# execute the action in parallel with frame animation
		# params may contain duration or speed
		def _act_seq(self, *args, **kwargs):
			print('Performing sequence', name)
			# Get actions FIXME a better way is required to handle actions and their duration given *args
			action_write, action_read = params['action']

			if 'speed' not in params:
				duration = params['duration']
			else:
				# Get current state (position, rotation, whatever)
				state = action_read(self)
				# Compute distance between current and desired state
				state, dist = v_dist(state, args, kwargs.get('offset', False))
				# Compute duration
				duration = dist * 1000 / params['speed']
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

		print('Found a good method', name)
		_seq.__name__ = name + '_to'
		_seq.__qualname__ = '.'.join(_seq.__qualname__.split('.')[:-1] + [_seq.__name__])
		setattr(cls, name + '_to', _seq)
		print(_seq)
	print('Cls sequences:', cls._sequences.keys())
	return cls

def sequence(name, speed=None, duration=None, action=None, easing='Linear'):
	print('Creating sequence', name)

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
		print('Decorating method', func)
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
	
	# TODO ideale sarebbe avere un decoratore che fa tutto quello che serve
	# sulla classe. Ad esempio
	# @sequence('walk', speed=123, action='move_to', easing='Linear')
	# def _walk_paint(self, painter, time, duration):
	#   definendo qui il codice che fa il painting. Verrebbe quindi definito
	#   automaticamente il metodo walk_to, che esegue l'animazione con quei parametri
	#   segnati di default. Il metodo avrebbe i parametri richiesti da move_to
	#   che verrebbero letti automaticamente (se action viene specificata)
	#   e automaticamente verrebbero passati all'azione al momento dell'esecuzione
	#   eseguendo in parallelo l'animazione dell'azione e di questa sequenza
	#   Essendo una sequenza, non c'é bisogno di un metodo diretto, ma solo del *_to
	#   perché stiamo sempre animando con interpolazione.
	
	def paint(self, painter):
		if self._frame[0] in Sprite._sequences:
			print('Found paint for sequence', self._frame[0])
			Sprite._sequences[self._frame[0]](self, painter, self._frame[1], self._frame[2])
	
	def _paint_walk(self, painter, time, duration):
		'''
		:type painter: QPainter
		'''
		bbox = QRectF(0, 0, *self.get_size()).adjusted(1, 1, -1, -1)
		bbox.setWidth(bbox.width() * time / duration)
		painter.fillRect(bbox, self.get_background_color())
	
	def _set_current_frame(self, sequence, time, duration):
		self._frame = (sequence, time, duration)
		self.update()
	
	def walk_to(self, x, y, speed=100, offset=False):
		print('Walking :) Good!')
		easing = 'Linear'
		# Register the sequence
		self._sequences['walk'] = self._paint_walk
		# Get current position
		pos = self.get_pos()
		# If relative, compute the actual xy values
		(x, y), dist = v_dist((x, y), pos, offset)
		duration = dist * 1000 / speed
		with par_anim_cm(self) as grp:
			ta = TimeAnim(duration, partial(self._set_current_frame, 'walk'))
			self.move_to(x, y, duration=duration, easing=easing)
			grp.addAnimation(ta)
	
	@sequence('run', speed=200, action=(StyledItem.move_to, StyledItem.get_pos))
	def _run_paint(self, painter, time, duration):
		print('Painting run_paint')
		bbox = QRectF(0, 0, *self.get_size()).adjusted(1, 1, -1, -1)
		bbox.setHeight(bbox.height() * time / duration)
		painter.fillRect(bbox, self.get_background_color())
		

s = Sprite(_root_)
