from PyPaper.core.styleditem import StyledItem
from PyPaper.core.animation import par_anim_cm, TimeAnim
from functools import partial
import warnings

def sequenced(cls):
	'''This decorator prepares a Sprite subclass to store sequence methods'''
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
				# TODO Merge kwargs

				def _durat_func():
					'''Determine the duration of the animation, using speed'''
					dist = params['dist_func'](self, *args)
					# TODO check if this computation is necessary or if we can in
					# some way recycle what is done in animation.PropertyAnimation
					# (but I think it is not possible, or not easily)
					duration = dist * 1000 / params['speed']
					print('Duration for sequence', duration, 'distance was', dist, 'speed', params['speed'])
					return duration

				with par_anim_cm(self) as grp:
					ta = TimeAnim(_durat_func, partial(self._set_current_frame, name), easing=params['easing'])
#					print('action is', params['action'], 'on args', args)
					params['action'](self, *args, easing=params['easing'], speed=params['speed'])
					grp.addAnimation(ta)

			_seq.__name__ = name + '_to'
			_seq.__qualname__ = '.'.join(_seq.__qualname__.split('.')[:-1] + [_seq.__name__])
			setattr(cls, name + '_to', _seq)

		# Found a sequence method, get the parameters
		_scope_definition(*getattr(method, '__seq'))
	return cls

def sequence(name, speed=None, distance_func=None, duration=None, action=None, easing='InOutQuad'):
	'''Decorate a method in a sequenced class, creating a new method <name>_to.
	The method will execute a sprite animation of specified speed or duration, executing in parallel
	the specified action (if not None). Action is usually something like move_to or rotate_to.
	The created method will receive some parameters and forward them to the action.
	If speed is specified and duration is not, the duration of the animation will be computed
	at the instant of animation start, using the provided distance_func.
	distance_func takes self argument plus any argument accepted by the action, (e.g. self, x, y)
	and shall return a float representing the distance between the current state of the object
	(e.g. position) and the input (e.g. x, y)
	'''
	# Disable this for now
	if False: # TODO
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
	return _decorator

class Sprite(StyledItem):
	'''Sprite is a general purpose class for items that have
	frame-by-frame animation behavior.
	Sprite can be subclassed to provide custom painting
	for each frame.
	Sprite supports the creation of animation sequences
	which can have different behaviors and can be reused.
	
	Example of usage:

	@sequenced
	class MySprite(Sprite):
		def __init__(self, parent):
			super().__init__(parent)
		@sequence('walk', speed=100, action=Sprite.move_to, distance_func=df)
		def _walk_paint(self, painter, time, duration):
			# Custom painting code
			pass
	s = MySprite(_root_)
	s.walk_to(10, 10)

	df is a "distance function" which takes the same number of parameters
	of the specified action (3, in this case: self, x, y) and computes a
	distance between the current state (e.g. self.get_pos()) and the the input
	state (e.g. x, y). Must return a float
	'''

	def __init__(self, parent):
		super().__init__(parent)
		self._frame = (None, None, None)
	
	def paint(self, painter):
		sname, time, dur = self._frame
		if sname in type(self)._sequences:
			type(self)._sequences[sname](self, painter, time, dur)

	def _set_current_frame(self, sequence, time, duration):
		self._frame = (sequence, time, duration)
		self.update()

