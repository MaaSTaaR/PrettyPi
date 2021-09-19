import sqlite3;
import hashlib;

class User:
	__username = None;
	__password = None;
	__name = None;
	__cursor = None;
		
	def getConnection( self ):
		connection = sqlite3.connect( 'data.db' );
		cursor = connection.cursor();
		
		return ( connection, cursor )
	
	def hasPermission( self ):
		( connection, cursor ) = self.getConnection();
		
		print ( self.__username, self.__password );

		cursor.execute( 'SELECT * FROM USERS WHERE USERNAME = ? AND PASSWORD = ?', ( self.__username, self.__password ) );

		result = cursor.fetchall();

		if len( result ) > 0:
			self.__name = result[ 0 ][ 3 ];

			return True;

		return False;

	def setUsername( self, username ):
		self.__username = username;

	def setPassword( self, password ):
		hashFunction = hashlib.md5( password );

		self.__password = hashFunction.hexdigest();

	def setHashedPassword( self, hashedPassword ):
		self.__password = hashedPassword;

	def getUsername( self ):
		return self.__username;

	def getHashedPassword( self ):
		return self.__password;

	def getName( self ):
		return self.__name;
