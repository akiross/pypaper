# PyPaper
Simple thing to make visual thinks thingy.

Basically it is a screen with a console. With the console you can create
items and place them on the screen, move them around, animate them and
change their properties.

## Dependencies
Written in Python 3.3+ and it is scriptable in Python 3.

I like Python 3. Please use Python 3.

Nevertheless, I developed and tested on my machine only, and the code may
be not work anywhere else.

You will need PyQt5 or something compatible, because I use QtQuick 2.
Also, I used jedi to provide autocompletion. I did not provide a fallback,
so if jedi is missing, the code will (probably (I didn't test this)) fail.

## Disclaimer
The code contains horrible things, please wash your eyes after reading it.
Running this code or watching it for too long may cause irreparable
brain damage, loss of consciousness or make your pet vomit on your most
precious carpet.

And, BTW, I use tabs for indentation (4 spaces if you care).
I know PEP8 suggest spaces, but I. Don't. Care. Tabs. Are. Better.

## Semi-serious tutorial
Step 0: launching PyPaper

Launching the PyPaper GUI is easy and a file named `pypaper.py` should
be present to show you how. You should be able to run it and see a
window divided in two; left side is the console, right side is the paper.

The console should have a nice autocompletion, which is naturally bugged.
When completing, you probably will need to press Enter twice, to accept
and execute the code. This is horrible and I will fix one day or another.

### Step 1: creating an item

On PyPaper you can only place items. It is not a canvas with pixels: it is
a continuum space. In fact, it is exacly a QtQuick2 window containing
QtQuick items. Theoretically, you can add any QtQuick item to it, but in
this application I will probably use only StyledItem, which is a basic item
with a shape.

Write this on the console to 

	from PyPaper.core.styleditem import StyledItem

	it = StyledItem(_root_)
	it.set_size(30, 30)
	it.set_pos(50, 50)

While typing this code, you will see things happen on the screen. This is
why I say that PyPaper is interactive.

`_root_` is an invisible element which is the root of the tree. As you can
guess, items are organized in a hierarchy, and `_root_` is the topmost
element. When creating a new element directly, set the root, or you will
not see the element appear. The element will exist, but will not be in the
scene. For example, run this:

	it2 = StyledItem()
	it2.set_size(20, 20)
	it2.setParentItem(_root_) # It will appear

Note that some methods `use_underscores` while others `useCamelCase`.
This is, usually, because the formers are implemented in PyPaper, while
the latters are accessing directly to PyQt methods.

### Step 2: manipulating items

StyledItems are neat and they have lots of nice properties: position and
size, as you saw in "Step 1", but you can control other things:
	rotation
	background color
	background image
	background image offset
	border color
	border size
	margin
	padding
	text
	rounded borders

For example, continuing the code above:
	
	it.set_background_color((0.5, 1.0, 0.4)) # A tuple with RGB(A)

Note that RGBA will not work as you expect, and basically because now
the method for painting the content is extremely stupid. Try

	it2.set_background_color((1, 0, 0, 0.5))
	it2.set_border_color((0, 0, 0, 0))

Border is not just a border, but it is actually a filled rectangle.
Yes, will be fixed. Someday.

I hate to use other color formats, so I will try to stick with
RGB(A) floats tuples, 3 channels mandatory, alpha defaulting to 1.

Finally, an example that use images and text:

	it.set_background_image('Art/icon128.png')
	help(it.set_background_mode) # Check this out

	it.set_text("Hello, World")

	it.set_size(100, 100)

### Step 3: animation

Being interactive, I wanted animations to be easy made in PyPaper.
I did my best, and maybe I will come up with better solutions, but for
now, I'm satisfied and I like it (altough it's probably bug filled).

At the most basic level, you can do animations with specific item's
methods, in particular the one ending with `_to`, which is a convention
which I would like to use to show that a progressive change will be made.

Try this:

	it.move_to(0, 0) # Default, 500ms duration
	it.move_to(100, 100, duration=3000)
	it.move_to(0, 0, duration=200, easing='linear')

Easing is a stringification of the qt easing functions.

Now, the part I like most: composing animations. You will have noted that
animations are non-blocking. If you didn't try this:

	it.move_to(100, 0); it.move_to(0, 100)

The animations are not done in sequence, but the secord "override"
the first, because the change in the position property is updated by
the second animation. Different behavior is this one:

	it.move_to(200, 200); it.rotate_to(360)

In this case, no override is performed, because the animations are
accessing two different properties.

To have a finer control over the animations, I used context managers.
Basically, you create a context manager saying which items you are
animating, and which type of animation do you want (parallel or
sequential, blocking or non-blocking), and everything is nicely composed
for you.

Animation are performed at the `__exit__` of the context manager.

	from PyPaper.core.animation import par_anim_cm, seq_anim_cm

	with seq_anim_cm(it):
		it.move_to(0, 100)
		it.move_to(100, 0)
	
In this case, will compose the two animations in sequence.

Best thing: you can compose context managers!

	with with par_anim_cm(it, it2):
		with seq_anim_cm(it):
			it.move_to(0, 100, duration=2000)
			it.move_to(100, 0, duration=2000)
		with seq_anim_cm(it2):
			it2.move_to(100, 100, duration=2000)
			it2.rotate_to(360, duration=2000)

Until now, my code seems to run. I didn't do any stress test on the
animation code, but I think it can be made robust.

BTW, context managers returns a QAnimationGroup, which can be used
if you want to add custom animations to the sequence. For example, I use
it directly when implementing `_to` methods, or for more advanced things.

Somewhere, `on_finished` callbacks are provided to perform things when
the animation is done. It *should* work where `duration` works, but code
has been changed a lot and I don't guarantee it.

### Step 4: interaction

Naturally, interaction is not done *only* using code.
By default, you can move around objects with the mouse. You can disable
this by setting the items to not accept mouse buttons (I think).

Input management, right now, is very, very stupid and raw: to handle
events you can basically write a method that replaces the item's event
handler. For example:

	def control(self, event):
		if event.key() == Qt.Key_Escape:
			_win_.toggle_panel() # _win_ is the handler for the window
		else:
			print('Pressed key', event.text())

	_canvas_.keyPressEvent = control.__get__(_canvas_, _win_.__class__)

And it's done. Similar approaches can be used with item events; check out
the StyledItem source code to see which events are available.

## Library

I provided some code which I found useful in my applications. You can find
them in the PyPaper.tools module:
	finite state machines
	graphs
	non-standard items (check it out to see how to create custom items)
and other random tools and data types.

## Author
I am a basically monkey who learned how to code.
Please do not be mad with me for my poor coding skills, or my
bad English, or if I re-invented the wheel or if you think that
a browser can do this and much more. I know.

Anyway, feel free to open issues and instruct me about how to properly
write program, package them or anything on the like that may be useful.

