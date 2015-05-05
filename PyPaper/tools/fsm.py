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
class FSM:
	'''
		Simple Finite State Machine class.
		
		You build it specifying the initial state, the transition map and
		the accepting states.
		
		The transition map is a dictionary where:
			keys are tuples of 2 elements: (state, transition)
			values are tuples of 2 elements: (next state, callback)
		
		The machine starts at the initial state and will change the state
		every time an action is feeded. To tell the machine an action occurred,
		use the method on_action.
		
		If there is no transition from current state with a certain action,
		a RuntimeError is raised. Else, the state is changed and the callback
		is called.
		
		Extra *args and **kwargs passed to on_action, are passed to the callback
		when it's executed.
	'''
	def __init__(self, init, delta):
		'''
		delta is a dictionary that defines the transition function
		like this:
			{ (state, action): (next_state, callback), ... }
		'''
		self.cur_ = init
		self.delta_ = delta
#		self.accept_ = accept # TODO support accepting states. Use accept callback
	
	def on_action(self, event, *args, **kwargs):
		key = (self.cur_, event)
		stat = self.delta_.get(key, None)
		if stat is None:
			raise RuntimeError('No transition is defined for state {} on event {}'.format(self.cur_, event))
		else:
		#	print('action ok, moving from state', self.cur_, 'to state', stat[0])
			self.cur_ = stat[0]
			if stat[1] is not None:
				stat[1](*args, **kwargs)

if __name__ == '__main__':
	# TODO Make an example with input/print
	fsm = {
		('wait', 'coin'): ('menu', None),
		('select', 'next'): ('wait', None),
		('wait', 'prev'): ('select', None),
		('select', 'prev'): ('wait', None),
	}
	

