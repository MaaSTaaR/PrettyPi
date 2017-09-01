import sqlite3;
import md5;

class User:
	__username = None;
	__password = None;
	__name = None;
	__cursor = None;

	def __init__( self ):
		connection = sqlite3.connect( 'data.db' );
		self.__cursor = connection.cursor();

	def hasPermission( self ):
		print ( self.__username, self.__password );

		self.__cursor.execute( 'SELECT * FROM USERS WHERE USERNAME = ? AND PASSWORD = ?', ( self.__username, self.__password ) );

		result = self.__cursor.fetchall();

		if len( result ) > 0:
			self.__name = result[ 0 ][ 3 ];

			return True;

		return False;

	def setUsername( self, username ):
		self.__username = username;

	def setPassword( self, password ):
		hashFunction = md5.new();
		hashFunction.update( password );

		self.__password = hashFunction.hexdigest();

	def setHashedPassword( self, hashedPassword ):
		self.__password = hashedPassword;

	def getUsername( self ):
		return self.__username;

	def getHashedPassword( self ):
		return self.__password;

	def getName( self ):
		return self.__name;
