import pygame
import os
import PyQt5.QtWidgets as qtw
import PyQt5.QtGui     as qtg
import PyQt5.QtCore    as qtc
from  time import sleep as tsleep
from  sys  import exit  as sysExit  


# Importing the player class;
from PlayerClass import PlayerClass

# Importing the obstacle class;
from ObstacleClass import ObstacleClass

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global app data;

# Widget Settings;
WIDTH, HEIGHT = 800, 500

# Game settings / physics;
PERCENTAGEPLAYERSTARTLOCATIONONMAP = 30
MAXFPS = 60
GRAVITYVALUE = 3

# Obstacle data;
OBSTACLEWIDTH    					= 20
OBSTACLEHEIGHT 	 					= 40
MAXOBSTACLESPEED 					= 10
OBJECTSPEEDINCREMENTATIONSPEEDPOINT                     = 15
DEFAULTOBSTACLESPEED		                        = 3

# Text data;
GAMETEXTFONT = 32


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Global player data;

# Player Geometry;
PLAYERWIDTH                = 50
PLAYERHEIGHT               = 50

# Player Physics;
PLAYERJUMPHEIGHT		   = 175

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Colors;
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE  = (0, 0, 255)


# The main app class, using oop;
# The parameters taken in the __init__() function are username, age, lastWords which are passed when the game class is called;
# Those values are taken in the pyqt5 entry.
class MainApp():
	def __init__(self, _username):

		# Game state keepers;
		self.gameIsRunning = True 			 	# The state keeper for the games "running" state;
		self.gameStartupAnimationHasRun = False # The state keeper for the start animation, using this to make sure the animation only runs once at start.
		self.fpsTextString				= "FPS: " # The state keeper for the fps text;
		self.playerPointsTextString     = "Points: " # The state keeper for the points text;

		
		# Initialising pygame and related stuff;
		pygame.font.init()
		pygame.mixer.init()

		# Creating the fps cap;
		self.gameClock = pygame.time.Clock()

		# Initialising the class data;
		self.initialiseClassDataF()
		
	    # App window;
		self.WIN = pygame.display.set_mode((WIDTH, HEIGHT))
		
		# Initialising the map;
		self.initialiseMapF()
		
		# Initialising the player;
		# Passing the received widget-entry player data as parameters to be used in the self.playerObject;
		self.initialisePlayerF(_username)

		# Initialising the obstacle;
		self.initialiseObstacleF()

		# Initialising the display texts;
		self.initialiseDisplayTextsF()

		# Window settings;
		pygame.display.set_caption(f"Adaks Dino Game | Goodluck {_username}")


		# __init__() function starts the app loop;
		# The screen rerenders will be made in the constant self.reRenderScreenF();
		while self.gameIsRunning:

			# Calling the game clock;
			self.gameClock.tick(MAXFPS)
			self.fpsTextString = f"FPS: {str(int(self.gameClock.get_fps()))}"

			# Running the start animation if it hasnt run yet;
			if not(self.gameStartupAnimationHasRun):
				# The animation and re-location function;
				self.setPlayerLocationOnStartupWithAnimationF()
				# Setting the self.gameStartupAnimationHasRun to True so it doesnt run again;
				self.gameStartupAnimationHasRun = True
				
				
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
				# Key presses;
				if event.type == pygame.KEYDOWN:
					# Player jump;
					if event.key == pygame.K_SPACE:
						# First checking if the player has already jumped;
						if self.playerIsOnPlatform():
							# The player hasn't jumped so jumping them;
							self.playerObject.playerRect.y -= PLAYERJUMPHEIGHT
						
						
			# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			# Physics;

			# Player drops on jumps;
			self.dropPlayerByGravityF()
			

			# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			# Obstacle Movements;
			if not(self.obstacleObject.hasBeenStopped):
				# Moving the obstacle left by the obstacle speed;
				self.obstacleObject.obstacleRect.x -= self.obstacleObject.movementSpeed

				# Setting the object speed based of the amount of points the player has;
				# The logic is: "For the amount of speed increment point value in points increment speed by 1 unless speed is at the allowed maximum";
				if self.obstacleObject.movementSpeed < MAXOBSTACLESPEED:
					self.obstacleObject.movementSpeed = DEFAULTOBSTACLESPEED 	# Setting the value to 3 (default) pre incrementation;
					for speedValue in range(self.playerObject.playerPoints):
						if speedValue % OBJECTSPEEDINCREMENTATIONSPEEDPOINT == 0:
							self.obstacleObject.movementSpeed += 1
				print(self.obstacleObject.movementSpeed)
				
				
			# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			# Collision Detection;

			# Checking if the player collides with the obstacle;
			if self.obstacleObject.obstacleCollidesWithPlayerF(self.playerObject.playerRect):
				self.gameLostF()

			# Checking if the obstacle has passed the screen y point and if it has,
			# incrementing the player points and putting the obstacle to the right side again;
			if self.obstacleObject.obstacleRect.x <= 0:
				self.playerObject.playerPoints += 1
				self.obstacleObject.obstacleRect.x = WIDTH - OBSTACLEWIDTH

			# Rerendering the screen;
			self.reRenderScreenF()

	# The rerender function;
	def reRenderScreenF(self):

		# Clearing the background;
		self.WIN.fill(BLACK)

		# Re-Initialising the map;
		self.initialiseMapF()

		# Drawing the player;
		pygame.draw.rect(self.WIN, BLUE, self.playerObject.playerRect)

		# Drawing the obstacle;
		pygame.draw.rect(self.WIN, RED, self.obstacleObject.obstacleRect)
        
		# Drawing the fps text;
		self.WIN.blit(self.gameTextsFont.render(self.fpsTextString, False, WHITE), (15, 15))

		# Drawing the current game speed text;
		self.WIN.blit(self.gameTextsFont.render(f"Speed: {str(self.obstacleObject.movementSpeed)}", False, WHITE), (15, 60))

		# Drawing the points text;
		self.WIN.blit(self.gameTextsFont.render(f"Points: {str(self.playerObject.playerPoints)}", False, WHITE), (15, 105))

		# Updating the display / Displaying the changes / Re-Rendering the screen;
		pygame.display.update()


    # The function for initialising the map;
	def initialiseMapF(self):
        
		# Creating the floor;
		self.floorFrame = pygame.Rect(0, (HEIGHT - self.floorPlatformMarginFromBottom), WIDTH, self.floorPlatformHeight)
		pygame.draw.rect(self.WIN, GREEN, self.floorFrame)


	# The function for initialising the class/state data that will be changed throught the app run;
	def initialiseClassDataF(self):

		# Map Related;
		self.floorPlatformMarginFromBottom = 30  # The margin of the platform from the bottom (This will be used for bottom collision-detection of the player);
		self.floorPlatformHeight           = 10  # The height of the platform (this is just a visual data);

        
	# The function for initialising the player / creating the player object;
	# Username, age and lastwords are taken as params; 
	def initialisePlayerF(self, username):
		# First, creating the player rect data;
		playerMarginFromTopOnStart = HEIGHT - (PLAYERHEIGHT + self.floorPlatformMarginFromBottom) # The starting height of the player, perfectly on the floor platform;
		playerColor  = RED
		
		playerRect = pygame.Rect(0, playerMarginFromTopOnStart, PLAYERWIDTH, PLAYERHEIGHT) # The player rect;
		
		# Creating the player's general data object via a player class call (this approach allows adding other player data except of just a rect playing around);
		self.playerObject = PlayerClass(playerRect, username)


	# The function for checking if the player has jumped based of the players current (Y) coordinate;
	# This function works with the same logic as the player start height location finding;
	# It just checks if the players (y) coordinate is the same as (HEIGHT - (PLAYERHEIGHT + self.floorPlatformMarginFromBottom)),
	# and if it is, it returns True;
	def playerIsOnPlatform(self):
		if self.playerObject.playerRect.y == (HEIGHT - (PLAYERHEIGHT + self.floorPlatformMarginFromBottom)):
			return True


	# The function for setting the start location of the player on the map horizontally with an animation;
	# Getting the placement location by using the PERCENTAGEPLAYERSTARTLOCATIONONMAP and running a simple player centering calculation to make sure its at that width point of the screen;
	def setPlayerLocationOnStartupWithAnimationF(self):
		for movementTick in range( ((WIDTH // 100) * PERCENTAGEPLAYERSTARTLOCATIONONMAP) - (PLAYERWIDTH // 2) ):
			# Ticking the game-clock to make the animation slower;
			# self.gameClock.tick(180)
			
			# Moving the player by 1 pixel;
			self.playerObject.playerRect.x += 1
			# Re-Rendering the screen;
			self.reRenderScreenF()


	# The function for dropping the player by the gravity amount if the player isn't on the platform (aka: Falling Physics);
	def dropPlayerByGravityF(self):
		# Checking if the player is on platform;
		# If the player is on the platform doing nothing, otherwise, dropping the player by the gravity amount;
		# Doing everything in a for loop and going through the drop 1 tick by 1 tick for the range of gravity;
		# This approach is used for making sure the player doesn't get below the border no matter what the gravity drop or the player (Y) coordinate is;
		for dropTick in range(GRAVITYVALUE):
			if not(self.playerIsOnPlatform()):
				self.playerObject.playerRect.y += dropTick


	# The function for initialising the obstacle;
	def initialiseObstacleF(self):
		# Using this method to create just a single obstacle as there will always be just a single obstace displayed on the screen;
		# The obstacle logic will work as "when obstacle.x < 0 set obstacle x to width and player_points += 1";
		# And also collision detections with the obstacle will work by "if obstacle.x <= (player.x + player.width) and obstacle.y > (player.y + player.height)";
		
		# Creating the obstacle rect; 
		obstacleRect = pygame.Rect((WIDTH - OBSTACLEWIDTH), (HEIGHT - (OBSTACLEHEIGHT + self.floorPlatformMarginFromBottom)), OBSTACLEWIDTH, OBSTACLEHEIGHT)

		# Creating the obstacle object;
		# Using object based approach for using class functions to do stuff such as collision detection; 
		self.obstacleObject = ObstacleClass(obstacleRect, DEFAULTOBSTACLESPEED)

	
	# The function for starting the texts on the screen;
	# Their values will be changed via text strings stateholders and rerenders will be done via self.reRenderScreenF()
	def initialiseDisplayTextsF(self):
		# Creating the font;
		self.gameTextsFont = pygame.font.SysFont('Comic Sans MS', GAMETEXTFONT)


	# The loss function, its to be called wwhen the player collides with the obstacle;
	def gameLostF(self):
		# Stopping the pygame;
		self.obstacleObject.obstacleRect.x = WIDTH
		self.obstacleObject.hasBeenStopped = True

		# Showing people their score/etc in a pyqt window;
		self.infoWindow = qtw.QDialog()

		# Window Settings;
		self.infoWindow.setFixedSize(200, 250)
		self.infoWindow.setWindowFlags(qtc.Qt.FramelessWindowHint | qtc.Qt.WindowStaysOnTopHint)

		# Information labels;

		# Username;
		usernameLabel = qtw.QLabel(f"Player: {self.playerObject.playerName}", self.infoWindow)
		usernameLabel.setFont(qtg.QFont("Arial", 16))
		usernameLabel.move(10, 10)

		# Points;
		pointsLabel = qtw.QLabel(f"Points: {self.playerObject.playerPoints}", self.infoWindow)
		pointsLabel.setFont(qtg.QFont("Arial", 16))
		pointsLabel.move(10, 40)

		# Restart Button;
		restartButton = qtw.QPushButton("Restart", self.infoWindow)
		restartButton.setFixedSize(100, 40)
		restartButton.clicked.connect(self.restartGameF)
		restartButton.move(50, 100)
		restartButton.setObjectName("restartButton")

		# Quit Button;
		quitButton = qtw.QPushButton("Quit", self.infoWindow)
		quitButton.setFixedSize(100, 40)
		quitButton.clicked.connect(self.quitAppF)
		quitButton.move(50, 150)
		quitButton.setObjectName("quitButton")


		self.infoWindow.setStyleSheet("""
			QPushButton#restartButton {
			    border: 2px solid white;
			    color: white;
			    background-color: #29b51f;
			    border-radius: 12%;
			}
			QPushButton:hover#restartButton {
			    background-color: #60d171;
			    border: 2px solid gray;
			}

			QPushButton#quitButton {
			    border: 2px solid white;
			    color: white;
			    background-color: #f1565e;
			    border-radius: 12%;
			}
			QPushButton:hover#quitButton {
			    background-color: #cf8488;
			    border: 2px solid gray;
			}
		""")


		self.infoWindow.show()


	def quitAppF(self):
		sysExit()

	# This function defaults all the values in the game and restarts the game;
	def restartGameF(self):
		# Destroying the info-window;
		self.infoWindow.deleteLater()

		# Setting game values to default;
		# Player;
		self.playerObject.playerPoints = 0

		# Object;
		self.obstacleObject.movementSpeed  = DEFAULTOBSTACLESPEED
		self.obstacleObject.hasBeenStopped = False 
		
	
# The popup window asking for user information at the start of the game;
class AskUserInfoPopup(qtw.QWidget):
	def __init__(self):
		super(AskUserInfoPopup, self).__init__()

		# Widget data;
		widgetWidth, widgetHeight = 400, 210

        # Setting widget settings
		self.setFixedSize(widgetWidth, widgetHeight)
		self.setWindowTitle("Adaks Dino Game!")

		# Background color frame;
		backgroundFrame = qtw.QFrame(self)
		backgroundFrame.setObjectName("backgroundFrame")
		backgroundFrame.setFixedSize(widgetWidth, widgetHeight)
		backgroundFrame.move(0, 0)

		# Register Label;
		registerLabel = qtw.QLabel("Adaks Dino Game", self)
		registerLabel.setObjectName("registerLabel")
		registerLabel.setFont(qtg.QFont("Arial", 28))
		registerLabel.move(50, 10)

		# Input Name's Label;
		inputNamesLabel = qtw.QLabel("Username:", self)
		inputNamesLabel.setObjectName("inputNamesLabel")
		inputNamesLabel.setFont(qtg.QFont("Arial", 15))
		inputNamesLabel.move(10, 75)

		# Entries;
		# Username Entry;
		self.usernameEntry = qtw.QLineEdit(self)
		self.usernameEntry.setFont(qtg.QFont("Arial", 15))
		self.usernameEntry.setFixedSize(240, 30)
		self.usernameEntry.setMaxLength(8)
		self.usernameEntry.move(125, 72)
		self.usernameEntry.setPlaceholderText("username")
		
		# Register Button;
		registerButton = qtw.QPushButton("Start", self)
		registerButton.setObjectName("registerButton")
		registerButton.setFixedSize(120, 50)
		registerButton.clicked.connect(self.playGameF)
		registerButton.setFont(qtg.QFont("Arial", 16))
		registerButton.move(140, 145)

		
		# Loading stylesheet;
		self.setStyleSheet("""
			QFrame#backgroundFrame {
			background: qlineargradient( x1:0 y1:0, x2:1 y2:0, stop:0 #4f446d, stop:1 #166af0);
			border-top: 3px solid white;
			}
			QLabel#registerLabel {
				color: white;
			}
			QLabel#inputNamesLabel {
				color: white;
			}
			QPushButton#registerButton {
			    border: 2px solid white;
			    color: white;
			    background-color: #f1565e;
			    border-radius: 12%;
			}
			QPushButton:hover#registerButton {
			    background-color: #cf8488;
			    border: 2px solid gray;
			}
		""")

		# Showing the widget;
		self.show()


    # The function for running required validations and then basedd of starting the game (or not);
	def playGameF(self):
		# First, assigning the values to variables for easier access;
		username  = self.usernameEntry.text()

		# Validating the data;
		if len(username) > 0:
			# Data validation succesfull, starting the game now;
			self.startGameF()
		else:
			qtw.QMessageBox.warning(self, "Error", "Please enter a username!")

	
	# The function for clearing the entry window and starting the game;
	def startGameF(self):
		# Clearing the entry window;
		self.close()

		# Starting the game;
		gameWindow = MainApp(
			self.usernameEntry.text(),
		)


if __name__ == "__main__":
    # Getting some player information before starting the game;
    # The game is started by the AskUserInfoPopup class when required player data is given;
    app = qtw.QApplication([])
    appVar = AskUserInfoPopup()
    app.exec_()
