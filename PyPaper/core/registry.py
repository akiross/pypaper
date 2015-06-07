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

class Registry:
	def __init__(self):
		self._callbacks = {}

	def register(self, event, target_obj, callback):
		'''Register a callback for the specified event.
		When the event happens in self, the callback is called in target_obj.

		If target_obj is None, the callback is called once and then removed.
			No first argument is passed to the callback
		If target_obj is not None, the callback is called until removed,
			and callback is automatically removed on event target_obj.on_remove
		'''
		if target_obj is None:
			def _call_once(*args, **kwargs):
				callback(*args, **kwargs)
				self.unregister(event, None, _call_once)
			self._callbacks.setdefault(event, []).append((None, _call_once))
		else:
			self._callbacks.setdefault(event, []).append((target_obj, callback))
			def _remove_cb(unused, obj):
				self.unregister(event, target_obj, callback)
			target_obj.register('on_remove', None, _remove_cb)

	def unregister(self, event, target_obj, callback):
		'''Unregister a callback for the specified event'''
		self._callbacks[event].remove((target_obj, callback))
	
	def _run_callbacks(self, event, *args, **kwargs):
		'''Run the callbacks associated to event, passing the specified parameters'''
		# What if a callback calls unregister while iterating? Copy the list before iterating
		for obj, cb in list(it for it in self._callbacks.get(event, [])):
			cb(obj, *args, **kwargs)


