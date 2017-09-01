from kivymd.label import MDLabel
import arabic_reshaper
from bidi.algorithm import get_display

class ArabicLabel( MDLabel ):
	#def __init__( self, **kwargs ):
	#	super( ArabicLabel, self ).__init__( **kwargs );

		#self.on_font_style( None, self.font_style )

	# Overridden
	def on_font_style( self, instance, style ):
		super( ArabicLabel, self ).on_font_style( instance, style );

		self.text = get_display( arabic_reshaper.reshape( self.text ) );
		self.font_name = 'fonts/KacstPenE';
