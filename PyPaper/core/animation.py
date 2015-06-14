# This file is part of PyPaper.
#
# PyPaper is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyPaper is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PyPaper.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2015 Alessandro "AkiRoss" Re

from PyQt5.QtCore import QPropertyAnimation, QParallelAnimationGroup, QSequentialAnimationGroup, QEasingCurve, QEventLoop, QAbstractAnimation

def qvariant_distance(v1, v2):
	'''This method computes the distance between two QVariants value,
	it is used to calculate the duration of animations based on speed.
	This function has to return a float'''
	assert(type(v1) == type(v2))

	from PyQt5.QtGui import QColor
	# TODO do the same for the other types: rect(f), line(f), point(f), size(f)

	if isinstance(v1, QColor):
		return ((v1.redF() - v2.redF()) ** 2 + (v1.greenF() - v2.greenF()) ** 2 + (v1.blueF() - v2.blueF()) ** 2 + (v1.alphaF() - v2.alphaF()) ** 2) ** 0.5
	else:
		return abs(v2 - v1)

class PropertyAnimation(QPropertyAnimation):
	'''This class extends QPropertyAnimation to support "speed",
	it adds a method to set speed, instead of duration, which will cause
	the duration to be set automatically when starting the animation.
	Duration will vary dependently from the speed and the start-end values
	set by the user.'''

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._speed = None
	
	def set_speed(self, speed):
		self._speed = speed
	
	def compute_duration(self, start_val, end_val):
		return 1000 * qvariant_distance(start_val, end_val) / self._speed
	
	def updateState(self, new_state, old_state):
		super().updateState(new_state, old_state)
		# When starting, change current value and end value
		if new_state == QPropertyAnimation.Running and old_state == QPropertyAnimation.Stopped and self._speed:
			# Get start and end values
			sv, ev = self.startValue(), self.endValue()
			# Get current value for property
			cv = self.targetObject().property(self.propertyName())
			if sv is None:
				sv = cv
			elif ev is NOne:
				ev = cv
			duration = self.compute_duration(sv, ev)
			self.setDuration(duration)

def prop_animation(obj, prop, end, duration=500, easing='InOutQuad', start=None, speed=None):#, on_finished=None):
	'''Builds a property animation for an object'''
	if hasattr(QEasingCurve, easing):
		ec = getattr(QEasingCurve, easing)
	else:
		ec = QEasingCurve.Linear
	
	an = PropertyAnimation(obj, prop)
	if start is not None:
		an.setStartValue(start)
	an.setEndValue(end)
	an.set_speed(speed)
	an.setDuration(duration)
	an.setEasingCurve(ec)

	return an

class AnimContextManager:
	'''Builds a context manager to handle animation groups'''
	def __init__(self, sequential, blocking, *items, parent=None):
		self._its = set(items) # Unique items
		self._seq = sequential
		self._block = blocking
		self._parent = parent

	def _clear_anims(self, item):
		def is_not_stopped(a):
			return a.state() != QAbstractAnimation.Stopped
		item._animations = list(filter(is_not_stopped, item._animations))

	def __enter__(self):
		'''When entering the context, each item subject to animation
		will have a property set to the current animation group'''
		if self._seq:
			self._animation_group = QSequentialAnimationGroup()
		else:
			self._animation_group = QParallelAnimationGroup()

		for item in self._its:
			self._clear_anims(item)
			# Save to current item
			item._animation_contexts.append(self)
		return self._animation_group

	def __exit__(self, excep_type, excep_value, excep_traceback):
		'''Start the animation and clean the property in the subject items'''
		for item in self._its:
			# Let's close the current context
			ctx = item._animation_contexts.pop()
			if ctx is not self:
				print('WARNING: I think this should never happen :|')
			if self._parent:
				# If a parent context manager has been provided, use it
				self._parent.addAnimation(ctx._animation_group)
			elif item._animation_contexts:
				# If there was a previous group, add to that group
				item._animation_contexts[-1]._animation_group.addAnimation(ctx._animation_group)
			else:
				# If it's the last one, save into animations and start
				item._animations.append(self._animation_group)
				# Start animation
				if self._block:
					loop = QEventLoop()
					# Connect signal termination to end of event
					self._animation_group.finished.connect(loop.quit)
					# Start animation and wait
					#anim.start()
					self._animation_group.start()
					# FIXME exec_ should use ExcludeUserInputEvents to prevent
					# other events to be fired while this is still running
					# but using it produce sloppy animations... Don't know why.
					# FIXME as a temporary fix, we are using flags to prevent 
					# nested loops, but it is so fragile...
					loop.exec_()
					# Callback if necessary
					#if on_finished is not None:
					#	on_finished()
				else:
					self._animation_group.start()

def seq_anim_cm(*items, **kwargs):
	return AnimContextManager(True, False, *items, **kwargs)

def par_anim_cm(*items, **kwargs):
	return AnimContextManager(False, False, *items, **kwargs)

def block_seq_anim_cm(*items, **kwargs):
	return AnimContextManager(True, True, *items, **kwargs)

def block_par_anim_cm(*items, **kwargs):
	return AnimContextManager(False, True, *items, **kwargs)
