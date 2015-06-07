from PyPaper.core.styleditem import StyledItem

class Sprite(StyledItem):
	'''Sprite is a general purpose class for items that have
	frame-by-frame animation behavior.
	Sprite can be subclassed to provide custom painting
	for each frame.
	Sprite supports the creation of animation sequences
	which can have different behaviors and can be reused.'''
	def __init__(self, parent):
		super().__init__(parent)
	
	# L'idea sarebbe quella di usare un generatore o cose simili
	# in modo pythonico, vorremmo poter decidere noi quali frame
	# mostrare per una certa animazione. Potremmo fare così:
	# quando un metodo di sequenza viene creato, si può chiamare una funzione
	# definita dall'utente che riceve in input dei parametri (da definire)
	# e che ritorna un generatore di frame. La Sprite, quindi, userebbe quel
	# generatore per eseguire l'animazione.
	#
	# (valutare anche la possibilità di usare un decorator per
	# creare la sequenza, così da avere una sintassi potenzialmente più
	# conveniente, che associa ad un metodo la sua sequenza)
	#
	# Il problema è come gestire questa animazione col generatore, come far
	# interagire i due componenti... Perché l'animazione viene fatta per forza
	# di cose da una QAnimation, e dentro a quella serve chiamare il generatore
	# per capire di quale frame fare il render.
	# 
	# Assumiamo di avere una QAbstractAnimation di fondo. Questa dovrà sapere
	# quando si inizia e quando si intende finire. Quindi, ogni tanto, questa
	# manderà un segnale "aggiornata!", però non sappiamo quando lo manderà.
	# Al ricevimento di tale segnale, serve una funzione che dica in quale frame
	# ci troviamo e quindi cosa disegnare.
	# Non vogliamo che questa funzione re-inventi le cose che esistono già (easing)
	# quindi questa funzione riceverà un certo valore già "mappato" nello spazio finale
	# e dovrà dire solo in quale frame ci troviamo.
	# Non può essere un generatore, perché il generatore va in sequenza, mentre qui
	# può essere che scopriamo i frame in ordine non lineare.
	def add_sequence(self):
		pass

	def paint_frame(self, painter, sequence, frame):
		'''To be implemented by the user to draw a given frame in a given sequence'''
		pass

def looped_generator():
	pass

class DrawnSprite(Sprite):
	'''This is an example sprite to test the class.'''
	def __init__(self, parent):
		super().__init__(parent)
	
		self.add_sequence(
			name='bubble', # name of the sequence (will create a method)
			frame_gen=looped_generator, # the generator of frames
			n_frames=10, # number of frames composing the sequence
			frame_gen=asd, # this generator 
			loop=True, # After end frame begin from start again
			frame_delay=100,
			start_frame=None,
			end_frame=10
		)


ds = DrawnSprite(_root_)
ds.bubble_to(some_param, duration_or_speed=100)
