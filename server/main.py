#!/usr/bin/python
# -*- coding: utf8 -*-

# [MQH] 16 June 2017. It has been a while since last code I have written in Python! :-)
from kivy.app import App
from kivy.lang import Builder
from kivymd.theming import ThemeManager
from kivy.properties import ObjectProperty
from kivymd.label import MDLabel
from kivy.animation import Animation
from ArabicLabel import ArabicLabel
import arabic_reshaper
import sqlite3
import threading;
from kivy.clock import Clock

class PrettyPiApp( App ):
	theme_cls = ThemeManager();
	mainBox = None;
	connection = None;
	cursor = None;

	kvMain = '''
#:import Toolbar kivymd.toolbar.Toolbar
#:import NavigationLayout kivymd.navigationdrawer.NavigationLayout
#:import MDNavigationDrawer kivymd.navigationdrawer.MDNavigationDrawer

NavigationLayout:
	id: navLayout

	MDNavigationDrawer:
        id: navDrawer
        NavigationDrawerToolbar:
            title: "Navigation Drawer"
        NavigationDrawerIconButton:
			id: quitBtn
            icon: 'checkbox-blank-circle'
            text: "Quit"

	BoxLayout:
		id: topBox
		orientation: 'vertical'
		Toolbar:
			id: toolbar
			title: 'My Pretty Pi!'
			md_bg_color: app.theme_cls.primary_color
			background_palette: 'Primary'
			background_hue: '500'
			left_action_items: [['menu', lambda x: app.root.toggle_nav_drawer()]]
			right_action_items: [['dots-vertical', lambda x: app.root.toggle_nav_drawer()]]

		Toolbar:
			id: titlebar
			title: 'Current TODO'
			md_bg_color: app.theme_cls.primary_color
			background_palette: 'Primary'
			background_hue: '900'

		ScreenManager:
			id: screenManager

			Screen:
				name: 'mainScreen'

				BoxLayout:
					id: mainBox
					orientation: 'vertical'
	''';

	def build( self ):
		mainWidget = Builder.load_string( self.kvMain );

		self.connection = sqlite3.connect( 'data.db' );
		self.cursor = self.connection.cursor();
		self.mainBox = mainWidget.ids.mainBox;
		self.quitBtn = mainWidget.ids.quitBtn;

		self.quitBtn.bind( on_press = lambda e: exit() );

		# ... #

		self.refreshList();

		# .. #

		Clock.schedule_interval( self.checkUpdates, 0.5 );

		# ... #

		return mainWidget;

	def refreshList( self ):
		self.mainBox.clear_widgets();

		self.cursor.execute( "SELECT * FROM TODO WHERE DONE = 'N'" );
		tasks = self.cursor.fetchall();

		for task in tasks:
			taskText = task[ 1 ];

			if task[ 5 ] == 'Y':
				taskText += " (Working On)";

			self.mainBox.add_widget( ArabicLabel( text = taskText, halign = 'center', font_style = 'Display1' ) );

	def checkUpdates( self, dt ):
		self.cursor.execute( "SELECT COUNT( 1 ) FROM UPDATE_REQUESTS WHERE UPDATE_TYPE = 'UPDATE_TODO_LIST' AND DONE = 'N'" );

		result = self.cursor.fetchone();

		if result[ 0 ] > 0:
			self.refreshList();

			self.cursor.execute( "UPDATE UPDATE_REQUESTS SET DONE = 'Y' WHERE UPDATE_TYPE = 'UPDATE_TODO_LIST'" );
			self.connection.commit();


if __name__ == '__main__':
	PrettyPiApp().run();
