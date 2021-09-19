from flask import Flask, render_template, request, make_response, redirect;
from user import User;
import sqlite3;
from time import strftime;
import hashlib;

app = Flask( __name__ );
app.debug = True;

user = User();

def getConnection():
	connection = sqlite3.connect( 'data.db' );
	cursor = connection.cursor();
	
	return ( connection, cursor )

# ... #

def isInstalled():
	( connection, cursor ) = getConnection();
	
	cursor.execute( "SELECT COUNT( 1 ) FROM USERS" );
	hasUser = cursor.fetchone()[ 0 ];

	return ( hasUser > 0 );

def addRequest( reqType ):
	( connection, cursor ) = getConnection();
	
	creationDate = strftime( '%d-%m-%Y %H:%M:%S' );

	cursor.execute( "INSERT INTO UPDATE_REQUESTS( UPDATE_TYPE, DONE, CREATION_DATE ) VALUES ( ?, 'N', ? )", [ reqType, creationDate ]  );

	connection.commit();

@app.before_request
def beforeRequest():
	if request.path == '/install':
		return None;

	if not isInstalled():
		return render_template( 'install_prettypi.html' );

	if request.path == '/login':
		return None;

	if request.cookies.get( 'prettypi_username' ) != None:
		user.setUsername( request.cookies.get( 'prettypi_username' ) );
		user.setHashedPassword( request.cookies.get( 'prettypi_password' ) );

		if not user.hasPermission():
			return render_template( 'login.html' );
		else:
			return None;

	return render_template( 'login.html' );

# ... #

@app.route( '/' )
def main():
		return render_template( 'main_page.html', name = user.getName() );

# ... #

@app.route( '/install', methods = [ 'POST' ] )
def install():
	( connection, cursor ) = getConnection();
	
	if isInstalled():
		return render_template( 'installer_message.html', message = 'PrettyPi Already Installed', type = 'danger' );

	if not request.form[ 'username' ] or not request.form[ 'password' ] or not request.form[ 'name' ]:
		return render_template( 'installer_message.html', message = 'Please fill all fields', type = 'danger' );

	hashFunction = hashlib.md5( request.form[ 'password' ].encode( 'utf-8' ) );

	hashedPassword = hashFunction.hexdigest();

	cursor.execute( "INSERT INTO USERS( USER_ID, USERNAME, PASSWORD, NAME ) VALUES ( NULL, ?, ?, ? )", [ request.form[ 'username' ], hashedPassword, request.form[ 'name' ] ] );

	connection.commit();

	return render_template( 'installer_message.html', message = 'Congratulations! PrettyPi has been initialized. Go back to homepage to start using it', type = 'success' );

# ... #

@app.route( '/login', methods = [ 'POST' ] )
def login():
	user.setUsername( request.form[ 'username' ] );
	user.setPassword( request.form[ 'password' ].encode( 'utf-8' ) );

	if user.hasPermission():
		response = make_response( redirect( '/' ) );
		response.set_cookie( 'prettypi_username', user.getUsername() );
		response.set_cookie( 'prettypi_password', user.getHashedPassword() );

		return response;
	else:
		return 'Invalid';

# ... #

@app.route( '/logout' )
def logout():
	response = make_response( redirect( '/' ) );
	response.set_cookie( 'prettypi_username', '' );
	response.set_cookie( 'prettypi_password', '' );

	return response;

# ... #

@app.route( '/tasks' )
def tasksMain():
	( connection, cursor ) = getConnection();
	
	cursor.execute( "SELECT * FROM TODO WHERE DONE = 'N' ORDER BY CREATION_DATE DESC" );

	tasks = cursor.fetchall();

	# ... #

	cursor.execute( "SELECT * FROM TODO WHERE DONE = 'Y' ORDER BY CREATION_DATE DESC" );

	doneTasks = cursor.fetchall();

	# ... #

	cursor.execute( "SELECT * FROM TODO WHERE WORKING_ON = 'Y'" );

	workingTask = cursor.fetchone();

	print( workingTask );

	# ... #

	return render_template( 'tasks.html', tasks = tasks, doneTasks = doneTasks, name = user.getName(), workingTask = workingTask );

# ... #

@app.route( '/add_task', methods = [ 'POST' ] )
def newTask():
	( connection, cursor ) = getConnection();
	
	if not request.form[ 'task_details' ]:
		return render_template( 'message.html', message = 'The details should not be empty', type = 'warning' );

	creationDate = strftime( '%d-%m-%Y %H:%M:%S' );

	cursor.execute( "INSERT INTO TODO( TASK_ID, TASK, CREATION_DATE ) VALUES ( NULL, ?, ? )", [ request.form[ 'task_details' ], creationDate ] );

	connection.commit();

	addRequest( "UPDATE_TODO_LIST" );

	return redirect( 'tasks' );

# ... #

@app.route( '/delete_task', methods = [ 'GET' ] )
def deleteTask():
	( connection, cursor ) = getConnection();
	
	taskId = request.args.get( 'task_id', None );

	if taskId is None:
		return 'Invalid';

	cursor.execute( "DELETE FROM TODO WHERE TASK_ID = ?", [ taskId ] );
	cursor.execute( "DELETE FROM TASKS_LOG WHERE TASK_ID = ?", [ taskId ] );

	connection.commit();

	addRequest( "UPDATE_TODO_LIST" );

	return redirect( 'tasks' );

@app.route( '/task_done', methods = [ 'GET' ] )
def markTaskAsDone():
	( connection, cursor ) = getConnection();
	
	taskId = request.args.get( 'task_id', None );

	if taskId is None:
		return 'Invalid';

	currentDate = strftime( '%d-%m-%Y %H:%M:%S' );

	cursor.execute( "UPDATE TODO SET WORKING_ON = 'N', DONE = 'Y', DONE_AT = ? WHERE TASK_ID = ?", [ currentDate, taskId ] );

	connection.commit();

	addRequest( "UPDATE_TODO_LIST" );

	return redirect( 'tasks' );

@app.route( '/start_task', methods = [ 'GET' ] )
def startWorkingOnTask():
	( connection, cursor ) = getConnection();
	
	taskId = request.args.get( 'task_id', None );

	if taskId is None:
		return 'Invalid';

	# ... #

	cursor.execute( "SELECT COUNT( 1 ) FROM TODO WHERE WORKING_ON = 'Y' AND TASK_ID <> ?", [ taskId ] );

	currentlyWorkingOn = cursor.fetchone()[ 0 ];

	if currentlyWorkingOn > 0:
		return render_template( 'message.html', message = "You're already working on another task!", type = 'warning' );

	# ... #

	creationDate = strftime( '%d-%m-%Y %H:%M:%S' );

	cursor.execute( "UPDATE TODO SET WORKING_ON = 'Y' WHERE TASK_ID = ?", [ taskId ] );
	cursor.execute( "INSERT INTO TASKS_LOG( TASK_ID, START_AT ) VALUES ( ?, ? )", [ taskId, creationDate ] );

	connection.commit();

	# ... #

	addRequest( "UPDATE_TODO_LIST" );

	return redirect( 'tasks' );

# ... #

@app.route( '/stop_task', methods = [ 'GET' ] )
def stopWorkingOnTask():
	( connection, cursor ) = getConnection();
	
	taskId = request.args.get( 'task_id', None );

	if taskId is None:
		return 'Invalid';

	# ... #

	cursor.execute( "SELECT MAX( log_id ) FROM tasks_log WHERE TASK_ID = ? AND ENDED_AT IS NULL", [ taskId ] );

	currTaskLogId = cursor.fetchone()[ 0 ];

	# ... #

	currentDate = strftime( '%d-%m-%Y %H:%M:%S' );

	cursor.execute( "UPDATE TODO SET WORKING_ON = 'N' WHERE TASK_ID = ?", [ taskId ] );
	cursor.execute( "UPDATE TASKS_LOG SET ENDED_AT = ? WHERE LOG_ID = ?", [ currentDate, currTaskLogId ] );

	connection.commit();

	# ... #

	addRequest( "UPDATE_TODO_LIST" );

	return redirect( 'tasks' );
