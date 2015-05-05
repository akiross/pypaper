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

from PyPaper.tools.items import *

class Node:
	def __init__(self, graph, root_item, radius=10):
		self.item = CircleItem(root_item)
		self.item.set_radius(radius) # Start with a default radius
		self.graph = graph

	def remove(self):
		self.graph.remove(self)
	
	def outbound_edges(self):
		'''Returns the set of edges for which this node is a start'''
		oe = set()
		for edge in self.graph._edges:
			if edge.start is self:
				oe.add(edge)
		return oe

	def inbound_edges(self):
		'''Returns the set of edges for which this node is an end'''
		ie = set()
		for edge in self.graph._edges:
			if edge.end is self:
				ie.add(edge)
		return ie

	def successors(self):
		'''Returns the set of direct-successors of this node'''
		return set(e.end for e in self.outbound_edges())

	def predecessors(self):
		'''Returns the set of direct-predecessors of this node'''
		return set(e.start for e in self.inbound_edges())

	def __str__(self):
		if self.name:
			return str(self.name)
		return super().__str__()

class Edge:
	def __init__(self, start, end, graph, root_item):
		self.start = start
		self.end = end
		self.item = LineItem(parent=root_item)#make_line(start.item, end.item, graph._item_root)
		self.item.setZ(-1) # Under the circles
		bind_line(self.item, start.item, end.item)
		self.graph = graph
	
	def remove(self):
		self.graph.remove(self)

class Graph:
	def __init__(self, root_item, radius=10):
		self._nodes = set()
		self._edges = set()
		self._item_root = root_item
		self._def_radius = radius

	def add_node(self, name=None):
		n = Node(self, self._item_root, self._def_radius)
		n.name = name
		self._nodes.add(n)
		return n

	def add_edge(self, n1, n2, name=None):
		# Ensure nodes are valid
		if n1 not in self._nodes:
			raise RuntimeError('Node n1 not belonging to this graph')
		if n2 not in self._nodes:
			raise RuntimeError('Node n2 not belonging to this graph')
		# Create an edge object
		e = Edge(n1, n2, self, self._item_root)
		e.name = name
		self._edges.add(e)
		# Create a line for this edge
#		e.item = make_line(n1.item, n2.item)
#		def _bind(line):
#			rem = lambda it: line.remove()
#			opa = lambda it, op: line.setOpacity(op)
#			return rem, opa
		# Line is removed on node removed
#		rem, opa = _bind(e.item)
		n1.item.register('on_remove', e.item, LineItem.remove)
		n1.item.register('on_opacity_changed', e.item, wrap_skip(LineItem.setOpacity))# lambda s,o,op: s.setOpacity(op))
		n2.item.register('on_remove', e.item, LineItem.remove)
		n2.item.register('on_opacity_changed', e.item, wrap_skip(LineItem.setOpacity))

		# Return the edge
		return e
	
	def remove(self, element):
		# Find the element in the graph
		if element in self._nodes:
			# Remove the edges
			to_remove = set()
			for edge in self._edges:
				if edge.start is element or edge.end is element:
					to_remove.add(edge)
			for edge in to_remove:
				self._edges.remove(edge)
				# Remove the item, will remove the line
				edge.item.remove()
			element.item.remove()
			self._nodes.remove(element)
		elif element in self._edges:
			# Remove the edge and unbind it from the node
			element.item.remove()
			self._edges.remove(element)
		else:
			raise RuntimeError('Element not belonging to this graph')
	
	def nodes(self):
		return set(self._nodes)

	def edges(self):
		return set(self._edges)

def test_graph():
	g1 = Graph(_root_)

	n1 = g1.add_node()
	n1.item.radius_to(10)
	n1.item.move_to(100, 100)

	n2 = g1.add_node()
	n2.item.radius_to(20)
	n2.item.move_to(200, 100)

	n3 = g1.add_node()
	n3.item.radius_to(30)
	n3.item.move_to(150, 200)

	e1 = g1.add_edge(n1, n2)
	e2 = g1.add_edge(n1, n3)
	e3 = g1.add_edge(n3, n2)

	return g1, n1, n2, n3, e1, e2, e3


