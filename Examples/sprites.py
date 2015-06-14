# Let's put here the codebase and then move it to the tools/sprite.py module

from PyPaper.core.styleditem import StyledItem
from PyPaper.core.animation import par_anim_cm, seq_anim_cm
from PyQt5.QtCore import QVariantAnimation, QRectF, QEasingCurve, pyqtSignal
from functools import partial
from collections import namedtuple
from PyQt5.QtGui import QPainter
import warnings

class TimeAnim(QVariantAnimation):
	'''When animation starts, the duration_func is called to get
	the duration of the animation.'''
	def __init__(self, duration_func, callback, easing='Linear', parent=None):
		super().__init__(parent)
		self._duration_f = duration_func
		self._callback = callback

		# Set the easing curve
		if hasattr(QEasingCurve, easing):
			ec = getattr(QEasingCurve, easing)
		else:
			ec = QEasingCurve.Linear
		self.setEasingCurve(ec)
	
	# Signal sent when starting, sending duration of animation as parameter
	starting = pyqtSignal(int)

	def updateCurrentValue(self, new_val):
		self._callback(new_val, self._duration)

	def updateState(self, new_state, old_state):
		super().updateState(new_state, old_state)
		print('Changing state')
		# When starting, change current value and end value
		if new_state == QVariantAnimation.Running and old_state == QVariantAnimation.Stopped:
			self._duration = float(self._duration_f())
			self.setStartValue(0.0)
			print('Ending value is', self._duration)
			self.setEndValue(self._duration)
			self.setDuration(self._duration)
			# Send the signal to begin
		#	self.started.emit(self._duration)

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

		def _scope_definition(name, paint_func, params):
			# Save the sequence painting function
			cls._sequences[name] = paint_func

			def _seq(self, *args, **kwargs):
				'''Perform the animation of the frame and the action'''
#				print('Sequence requested for name', name, args)

				# TODO Merge kwargs

				def _durat_func():
					'''Determine the duration of the animation, using speed'''
					dist = params['dist_func'](self, *args)
					# TODO check if this computation is necessary or if we can in
					# some way recycle what is done in animation.PropertyAnimation
					# (but I think it is not possible, or not easily)
					duration = dist * 1000 / params['speed']
					return duration

				with par_anim_cm(self) as grp:
					ta = TimeAnim(_durat_func, partial(self._set_current_frame, name))
#					print('action is', params['action'], 'on args', args)
					params['action'](self, *args, easing=params['easing'], speed=params['speed'])
					grp.addAnimation(ta)

			_seq.__name__ = name + '_to'
			_seq.__qualname__ = '.'.join(_seq.__qualname__.split('.')[:-1] + [_seq.__name__])
			setattr(cls, name + '_to', _seq)

		# Found a sequence method, get the parameters
		_scope_definition(*getattr(method, '__seq'))
	return cls

def sequence(name, speed=None, distance_func=None, duration=None, action=None, easing='Linear'):
	# Disable this for now
	if False:
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
				'dist_func': distance_func, # Computes the distance from a state
				'action': action,
				'easing': easing,
				'offset': False,
				}
		setattr(func, '__seq', (name, func, params))
		return func
#		def _m_wrapper(self, *args, **kwargs):
#			return func(self, *args, **kwargs)
#		return _m_wrapper
	return _decorator

def pos_dist(self, x, y, *args):
	target = (x, y)
	print('Computing distance for self', self, 'and target', target, 'with extra args', args)
	state, dist = v_dist(self.get_pos(), target, False)
	print('  Distance is', dist)
	return dist

@sequenced
class Sprite(StyledItem):
	def __init__(self, parent):
		super().__init__(parent)
		self.set_size(50, 50)
		self._frame = (None, None, None)
		self._sequences = {}
	
	def paint(self, painter):
#		super().paint(painter)
		sname, time, dur = self._frame
		if sname in Sprite._sequences:
			Sprite._sequences[sname](self, painter, time, dur)

	def _set_current_frame(self, sequence, time, duration):
#		print('Setting current frame', sequence, time, duration)
		self._frame = (sequence, time, duration)
		self.update()
	
#	@sequence('stand', duration=1000)
#	def _stand_paint(self, painter, time, duration):
#		pass

#	@sequence('turn', speed=10, action=StyledItem.rotate_to, distance_func=rot_dist)
#	def _turn_paint(self, painter, time, duration):
#		pass

	@sequence('run', speed=200, action=StyledItem.move_to, distance_func=pos_dist)
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

s = Sprite(_root_)

with seq_anim_cm(s):
	# C'è un problema: questi non vengono messi davvero in sequenza e i valori sono calcolati immediatamente, non al momento della chiamata... WROOONG
	s.walk_to(300, 0)
	s.run_to(0, 0)

