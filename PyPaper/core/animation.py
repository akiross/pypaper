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


def prop_animation(obj, prop, end, duration=500, easing='InOutQuad', start=None):#, on_finished=None):
	'''Builds a property animation for an object'''
	if hasattr(QEasingCurve, easing):
		ec = getattr(QEasingCurve, easing)
	else:
		ec = QEasingCurve.Linear
	
	an = QPropertyAnimation(obj, prop)
	if start is not None:
		an.setStartValue(start)
	an.setEndValue(end)
	an.setDuration(duration)
	an.setEasingCurve(ec)

	return an

class AnimContextManager:
	'''Builds a context manager to handle animation groups'''
	def __init__(self, sequential, blocking, *items):
		self._its = items
		self._seq = sequential
		self._block = blocking

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
			if item._animation_contexts:
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

def seq_anim_cm(*items):
	return AnimContextManager(True, False, *items)

def par_anim_cm(*items):
	return AnimContextManager(False, False, *items)

def block_seq_anim_cm(*items):
	return AnimContextManager(True, True, *items)

def block_par_anim_cm(*items):
	return AnimContextManager(False, True, *items)
