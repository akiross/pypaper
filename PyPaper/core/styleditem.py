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

from PyQt5.QtQuick import *
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from PyPaper.core.animation import seq_anim_cm, par_anim_cm, prop_animation
from PyPaper.core.registry import Registry
from PyPaper.tools.tools import *

class Item(QQuickPaintedItem, Registry):
	'''This class is the base class, representing an item
	capable of be used in PyPaper, supporting animations,
	callbacks, interactions, layouts, etc.
	This item extends Qt items to provide PyPaper specific
	functions.
	This item has a position, rotation, size, etc'''

	def __init__(self, parent=None):
		super().__init__(parent)
		self._animations = [] # List of playing animations involving this item
		self._animation_contexts = [] # Groups of animations to be built

		# Ensure that all mouse buttons are accepted
		self.setAcceptedMouseButtons(Qt.AllButtons)
		# Enable hover events (buttons non pressed)
		# self.setAcceptHoverEvents(True)

		self._movable = True
		self._press_pos = None

	def geometryChanged(self, g_new, g_old):
		'''
		Handles the geometry changes, by calling the appropriate callbacks
		:type g_new: QRectF
		:type g_old: QRectF
		'''
		def _test_change(v1, v2, callback):
			'''If v1 and v2 are different, try to call the callback if exists'''
			if v1 != v2:
				self._run_callbacks(callback, self, v1, v2)

		# Check for position changes
		p_new = (g_new.x(), g_new.y())
		p_old = (g_old.x(), g_old.y())
		_test_change(p_new[0], p_old[0], 'on_x_changed')
		_test_change(p_new[0], p_old[1], 'on_y_changed')
		_test_change(p_new, p_old, 'on_pos_changed')

		# Check for size changes
		s_new = (g_new.width(), g_new.height())
		s_old = (g_old.width(), g_old.height())
		_test_change(s_new[0], s_old[0], 'on_width_changed')
		_test_change(s_new[1], s_old[1], 'on_height_changed')
		_test_change(s_new, s_old, 'on_size_changed')
	
	def itemChange(self, change, val):
		'''Handle various item changes, calling the appropriate callbacks'''
		changes = {
			QQuickItem.ItemChildAddedChange: ('on_child_added', 'item'),
			QQuickItem.ItemChildRemovedChange: ('on_child_removed', 'item'),
			QQuickItem.ItemSceneChange: ('on_scene_change', 'window'),
			QQuickItem.ItemVisibleHasChanged: ('on_visibility_changed', 'boolValue'),
			QQuickItem.ItemParentHasChanged: ('on_parent_changed', 'item'),
			QQuickItem.ItemOpacityHasChanged: ('on_opacity_changed', 'realValue'),
			QQuickItem.ItemActiveFocusHasChanged: ('on_focus_changed', 'boolValue'),
			QQuickItem.ItemRotationHasChanged: ('on_rotation_changed', 'realValue')
		}
		cb, vkey = changes[change]
		self._run_callbacks(cb, self, getattr(val, vkey))
	
	def mousePressEvent(self, ev):
		if self._movable:
			self._press_pos = ev.localPos()
		self._run_callbacks('on_mouse_press', self, ev)
	def mouseDoubleClickEvent(self, ev):
		self._run_callbacks('on_double_click', self, ev)
	def mouseReleaseEvent(self, ev):
		self._press_pos = None
		self._run_callbacks('on_mouse_release', self, ev)
	def mouseMoveEvent(self, ev):
		if self._movable and self._press_pos:
			sp = ev.windowPos()
			self.set_pos(sp.x() - self._press_pos.x(), sp.y() - self._press_pos.y())
		self._run_callbacks('on_mouse_move', self, ev)
	def hoverEnterEvent(self, ev):
		print('hover enter')
	def hoverLeaveEvent(self, ev):
		print('hover leave')
	def hoverMoveEvent(self, ev):
		print('hover move')
	def keyPressEvent(self, ev):
		print('key press')
	def keyReleaseEvent(self, ev):
		print('key release')

	def remove(self): # FIXME I removed the unused parameter. If crashes, try to use wrap_skip
		'''Remove the item from the scene and deletes it'''
		self._run_callbacks('on_remove', self)
		# Remove from scenegraph
		self.setParentItem(None)
		# Remove from object hierarchy
		self.setParent(None)
		self.deleteLater()
	
	def detach(self):
		'''Remove item from the scene, but don't delete it'''
		self._run_callbacks('on_detach', self)
		self.setParentItem(None)
	
	def attach(self, parent):
		self._run_callbacks('on_attach', self)
		self.setParentItem(parent)

	def set_pos(self, x, y):
		self.setX(x)
		self.setY(y)
	
	def get_pos(self):
		return (self.x(), self.y())

	def _set_pos(self, point):
		self.setX(point.x())
		self.setY(point.y())
	
	def _get_pos(self):
		return QPointF(self.x(), self.y())

	pos = pyqtProperty(QPointF, fget=_get_pos, fset=_set_pos)
	
	def set_size(self, w, h):
		self.setWidth(w)
		self.setHeight(h)
	
	def get_size(self):
		return (self.width(), self.height())

	def _set_size(self, size):
		self.setWidth(size.width())
		self.setHeight(size.height())
	
	def _get_size(self):
		return QSizeF(self.width(), self.height())

	size = pyqtProperty(QSizeF, fget=_get_size, fset=_set_size)

	def opacity_to(self, end_op, on_finished=None, **kwargs):
		'''Animate item opacity'''
		with seq_anim_cm(self) as agrp:
			if on_finished:
				agrp.finished.connect(on_finished)
			agrp.addAnimation(prop_animation(self, 'opacity', end_op, **kwargs))
	
	def move_to(self, x, y, offset=False, on_finished=None, **kwargs):
		'''Animate the movement of this item toward a given target position.'''
		if offset:
			xo, yo = self.get_pos()
			if x is not None: x += xo
			if y is not None: y += yo

		with par_anim_cm(self) as agrp:
			if on_finished:
				agrp.finished.connect(on_finished)
			if x is not None and y is not None:
				agrp.addAnimation(prop_animation(self, 'pos', QPointF(x, y), **kwargs))
			elif x is not None:
				agrp.addAnimation(prop_animation(self, 'x', x, **kwargs))
			else:
				agrp.addAnimation(prop_animation(self, 'y', y, **kwargs))

	def resize_to(self, w, h, offset=False, on_finished=None, **kwargs):
		'''Animate the resize of this item'''
		if offset:
			wo, ho = self.get_size()
			if w is not None: w += wo
			if h is not None: h += ho

		with par_anim_cm(self) as agrp:
			if on_finished:
				agrp.finished.connect(on_finished)
			if w is not None and h is not None:
				agrp.addAnimation(prop_animation(self, 'size', QSizeF(w, h), **kwargs))
			elif w is not None:
				agrp.addAnimation(prop_animation(self, 'width', w, **kwargs))
			else:
				agrp.addAnimation(prop_animation(self, 'height', h, **kwargs))
	
	def rotate_to(self, a, offset=False, on_finished=None, **kwargs):
		'''Animate the rotation of this item'''
		if offset:
			a += self.rotation()
		with seq_anim_cm(self) as agrp:
			if on_finished:
				agrp.finished.connect(on_finished)
			agrp.addAnimation(prop_animation(self, 'rotation', a, **kwargs))

class StyledItem(Item):
	'''StyledItem, this is a multi-purpose item which probably
	will be used for basically everything'''
	def __init__(self, parent=None):
		super().__init__(parent)
		self.bord_col_ = QColor.fromRgbF(0, 0, 0)
		self.backg_col_ = QColor.fromRgbF(1, 0, 0)
		self._font_col = QColor.fromRgbF(0, 0, 0)
		self._font_size = None
		self._backgr_img_path = None
		self._backgr_img = None
		self._bg_img_fit_mode = 'full'
		self._bg_img_stretch = True
		self._x_rad = 0
		self._y_rad = 0
		self._rel_rad = True
		self._text = None

		self._bord = (1, 1, 1, 1)
		self._marg = (0, 0, 0, 0)
		self._padd = (5, 5, 5, 5)
	
	def get_border_color(self):
		return self.bord_col_

	def set_border_color(self, col):
		if hasattr(col, '__iter__'):
			col = make_rgba(*col)
		# Update if changed
		if self.bord_col_ != col:
			self.bord_col_ = col
			self.update()
	
	border_color = pyqtProperty(QColor, fget=get_border_color, fset=set_border_color)

	def get_background_color(self):
		return self.backg_col_

	def set_background_color(self, col):
		# If iterable is provided, convert to QColor
		if hasattr(col, '__iter__'):
			col = make_rgba(*col)
		# Update only if color changes
		if self.backg_col_ != col:
			self.backg_col_ = col
			self.update()
	
	background_color = pyqtProperty(QColor, fget=get_background_color, fset=set_background_color)

	def get_font_color(self):
		return self._font_col

	def set_font_color(self, col):
		if hasattr(col, '__iter__'):
			col = make_rgba(*col)
		if self._font_col != col:
			self._font_col = col
			self.update()
	
	font_color = pyqtProperty(QColor, fget=get_font_color, fset=set_font_color)

	def set_font_size(self, size):
		self._font_size = size
		self.update()

	def get_font_size(self):
		return self._font_size

	def set_background_image(self, image_path):
		import os
		if image_path != self._backgr_img_path:
			self._backgr_img_path = image_path
			if os.path.isfile(image_path):
				self._backgr_img = QImage(image_path)
			else:
				self._backgr_img = None
			self.update()
	
	def get_background_image(self):
		return self._backgr_img # TODO shall return path if path was saved

	def set_background_mode(self, fit_mode):
		'''fit_mode is a str
			'none': image has its original size or stretched to fit
			'full': image is never cropped
			'width': image's width never exceeds rectangle's width
			'height': similar to width
		'''
		self._bg_img_fit_mode = fit_mode

	def set_background_stretch(self, stretch):
		''' stretch is a bool
			True: the image is enlarged if too small for the rectangle
			False: image will never be larger than its original dimension
		'''
		self._bg_img_stretch = stretch

	def set_paint_callback(self, cb):
		'''Use a different method for painting'''
		self.paint_ = self.paint
		self.paint = cb

	def paint(self, painter):
		'''
		:type painter: QPainter
		'''
		painter.setRenderHint(QPainter.Antialiasing, True)

		# Compute box model

		# From the bounding rect, remove margin spaces
		marg_l, marg_t, marg_r, marg_b = self._marg
		br = self.contentsBoundingRect().adjusted(marg_l, marg_t, -marg_r, -marg_b)

		bord_col = self.get_border_color()
		br_bg = br # Rectangle for border is initially the same
		# Border may be used even if color is none
		bord_l, bord_t, bord_r, bord_b = self._bord
		br_bg = br.adjusted(bord_l, bord_t, -bord_r, -bord_b)
		# If not none, draw the border
		if bord_col is not None:
			painter.setBrush(bord_col)
			painter.setPen(Qt.NoPen)
			painter.drawRoundedRect(br, self._x_rad, self._y_rad, self._rel_rad)

		backg_col = self.get_background_color()
		br_text = br_bg
		if backg_col is not None:
			padd_l, padd_t, padd_r, padd_b = self._padd
			br_text = br_bg.adjusted(padd_l, padd_t, -padd_r, -padd_b)
			painter.setBrush(backg_col)
			painter.setPen(Qt.NoPen)
			painter.drawRoundedRect(br_bg, self._x_rad, self._y_rad, self._rel_rad)

		# If a background image is set
		if self._backgr_img is not None:
			# If a clipping region has been specified, copy the image 
			# FIXME this is not really efficient I think
			if hasattr(self, 'bg_clip_rect'):
				bg_img = self._backgr_img.copy(*self.bg_clip_rect)
			else:
				bg_img = self._backgr_img

			# Get rendering parameters
			fit_mode = self._bg_img_fit_mode
			enlarge_image = self._bg_img_stretch
			# Get sizes
			img_size = bg_img.size()
			box_size = br_bg.size().toSize()
			# Compute target size
			if fit_mode == 'full':
				# Full mode will preserve aspect ratio
				if enlarge_image:
					target_size = box_size
				else:
					tw = min(img_size.width(), box_size.width())
					th = min(img_size.height(), box_size.height())
					target_size = QSize(tw, th)
				target_ar = Qt.KeepAspectRatio
				scaled_img = bg_img.scaled(target_size, target_ar)
			elif fit_mode == 'width':
				# Width mode will never render the image wider than the box
				if enlarge_image:
					targ_w = box_size.width()
				else:
					targ_w = min(img_size.width(), box_size.width())
				scaled_img = bg_img.scaledToWidth(targ_w)
			elif fit_mode == 'height':
				if enlarge_image:
					targ_h = box_size.height()
				else:
					targ_h = min(img_size.height(), box_size.height())
				scaled_img = bg_img.scaledToHeight(targ_h)
			else: # none/stretch
				if enlarge_image:
					target_size = box_size
					target_ar = Qt.IgnoreAspectRatio
					scaled_img = bg_img.scaled(target_size, target_ar)
				else:
					scaled_img = bg_img 

			# Draw image
			painter.drawImage(bord_l, bord_t, scaled_img)

		# Draw text, after setting padding
		if self._text is not None:
			# Set the font if necessary
			if self._font_size is not None:
				font = painter.font()
				font.setPointSizeF(self._font_size)
				painter.setFont(font)
			# Compute text space
			flags = Qt.TextWordWrap | Qt.AlignCenter
			painter.setPen(QPen(self.get_font_color()))
			painter.drawText(br_text, flags, self._text)

	def set_x_radius(self, x):
		self._x_rad = x
		self.update()

	def get_x_radius(self):
		return self._x_rad

	x_radius = pyqtProperty(float, fget=get_x_radius, fset=set_x_radius)

	def set_y_radius(self, y):
		self._y_rad = y
		self.update()

	def get_y_radius(self):
		return self._y_rad

	y_radius = pyqtProperty(float, fget=get_y_radius, fset=set_y_radius)

	def set_text(self, t):
		self._text = str(t)
		self.update()
	
	def get_text(self):
		return self._text

	text = pyqtProperty(str, fget=get_text, fset=set_text)

	def set_margins(self, left, top, right, bottom):
		self._marg = (left, top, right, bottom)
		self.update()
	
	def set_border_size(self, left, top, right, bottom):
		self._bord = (left, top, right, bottom)
		self.update()

	def set_padding(self, left, top, right, bottom):
		self._padd = (left, top, right, bottom)
		self.update()
	
	def set_rect_radius(self, x, y=None):
		'''Set the radius of the rounded rect'''
		if y is None:
			y = x
		self.set_x_radius(x)
		self.set_y_radius(y)
	
	def rect_radius_to(self, x, y, on_finished=None, **kwargs):
		'''Animate radius change'''
		with par_anim_cm(self) as agrp:
			if on_finished:
				agrp.finished.connect(on_finished)
			agrp.addAnimation(prop_animation(self, 'x_radius', x, **kwargs))
			agrp.addAnimation(prop_animation(self, 'y_radius', y, **kwargs))
	
	def set_rect_radius_mode(self, relative):
		if relative:
			self._rel_rad = Qt.RelativeSize
		else:
			self._rel_rad = Qt.AbsoluteSize

	def background_color_to(self, color, on_finished=None, **kwargs):
		'''Animate the background color (if previous color was animatable, e.g. RGB).
		You can use a tuple for the color.'''
		if hasattr(color, '__iter__'):#type(color) is tuple or type(color) is list:
			color = make_rgba(*color)
		with seq_anim_cm(self) as agrp:
			if on_finished:
				agrp.finished.connect(on_finished)
			agrp.addAnimation(prop_animation(self, 'background_color', color, **kwargs))

	def border_color_to(self, color, on_finished=None, **kwargs):
		'''Animate the border color of this item. You can use a RGB(A) tuple for color'''
		if hasattr(color, '__iter__'):#type(color) is tuple or type(color) is list:
			color = make_rgba(*color)
		with seq_anim_cm(self) as agrp:
			if on_finished:
				agrp.finished.connect(on_finished)
			agrp.addAnimation(prop_animation(self, 'border_color', color, **kwargs))
	
