# Threading is used for creating a second process that only listens to hotkeys
import threading
# As we are working with multiple threads, we need to be able to communicate between them, it seemed to me that a Pipe was the most easy way of doing so
from multiprocessing import Pipe, Process
# socket is used for external communication
import socket
# Select is used to check if there has been a response, if not, it keeps going on.
# This is used to check if there are messages send from Twitch without pausing the script until there is a reply.
# If we just use socket, it waits until a message is received, this will pause the script, so the next action only happens after a message is received.
import select
# re = regex
import re
# Used for time related things ;) and generating a "random" number
import time
# os is used to check for filenames/paths
import os
# sys is used to write things to console
import sys
#an import nice_updating is imported later on, but this is only when it is going to check for an update, saves some precious RAM ;P
#I know that it's better to only import at the top of the script, but it just isn't always needed.
#I tried to make all the functions in my script as diverse as possible, so you can use them in your own scripts too.


# hotkeys is the script that listens for hotkeys (system wide, this means that it listens even if the script has lost focus)
import hotkeys as listen_for_hotkeys
	
#function to update a line in the config file
def update_config_value(file,option,value):
	with open(file,"r") as config:
		config_content = config.read()
	new_config = re.sub("(.*){option}[ 	]*=.*(#.*)\n".format(option=option),"\g<1>{option} = {value} \g<2>\n".format(option=option,value=value),config_content)
	with open(file,"w") as config:
		config.write(new_config)

# Self made kind of pseudorandom generator, as it doesn't do anything with security, it doesn't matter how truely random it is.
def random():
	i = int(str(time.time())[-1:])
	while i <= 4:
		i = int(str(time.time())[-1:])
	randomm = ""
	for i in range(i):
		randomm = str(randomm) + str(time.time())[-2:]
		time.sleep(0.001)
	return(randomm[:7])

# Function to read a config and return a dictionary of the values stored in the config file
def parse_config(file):
	options = {}
	with open(file,"r") as config:
		for line in config:
			# Stripping the lines of newline characters and such, so empty lines will by length 0, this makes them fals when passed to bool()
			line = line.strip()
			# Excluding lines that start with a #, or are 0 characters long (empty lines)
			if (line.startswith("#")) or (not bool(line)):
				pass
			else:
				# Separating the value from the option
				option, value = line.split("=", 1)
				option = option.strip()
				value = value.strip()
				if (value.lower() == "true"):
					value = True
				elif (value.lower() == "false"):
					value = False
				elif (value.isdigit()):
					value = int(value)
				elif (value.count("#")):
					#not -1, because we already made sure that the first character shouldn't be a #
					#This should be done better, as you don't want to use a break, please make a pull request if you have a good idea!
					last_place = 0
					for i in range(value.count("#")):
						last_place = value.find("#",last_place+1)
						if value[last_place-1] != "\\":
							value = value[:last_place]
							break
				# Remove unessesary characters
				options[option] = value
	return(options)

def start():
	# Asking the user for the answers/options to display
	valid_votes = [input("option 1: ")]
	# I = 2 because we already asked for the first vote (this variable will be used as a human friendly readable number)
	i=2
	# This while statement will run until s or S is received
	while (valid_votes[-1].lower() != "s"):
		# Appending each new vote to the list
		valid_votes.append(input("option {i} (s to stop): ".format(i=i)))
		i+=1
	# Because the last option in the list is always s or S, we need to remove that, as we do not want that as an option... ;)
	valid_votes = valid_votes[:-1]
	# Creating the actual result list
	list_of_votes = []
	# For each option that has been given, we append a 0 (as it shouldn't have any votes at this moment)
	# This will create a list like this: [0,0,0]
	# List[0] will be the total number of votes for the first option, 0 at this moment
	for vote in valid_votes:
		list_of_votes.append(0)

	#if the current voting system is voting with time, set the maximum time, else no time :)
	if current_vote == vote_with_time:
		timer = int(time.time() + default_timer)
	else:
		timer = None
	# Calling the write_vote_file function to create that result file, this is done at this point, so users can import it, and don't have to wait for the first vote.
	write_vote_file(valid_votes,list_of_votes,timer=timer)
	# Calling the write_to_console function so it instantly shows the results and you don't have to wait for the first user to vote.
	write_to_console(valid_votes,list_of_votes,timer=timer)
	# This dictionary will contain every username with their last vote. why the username? That makes it easy to check if they have voted already ;)
	users_voted = {}
	# Returning the variables 
	return(valid_votes,list_of_votes,users_voted,timer)



def reset_votes(list_of_votes):
	#This was a request (just as the whole program, sort of ;P)
	#The streamers wanted to be able to reset the votes back to 0, so users that have left, don't keep their last vote

	# Storing the old list 
	length_of_vote_list = len(list_of_votes)
	list_of_votes = []
	for i in range(length_of_vote_list):
		list_of_votes.append(0)
	# Also resetting the list with usernames, so everyone can vote again ;)
	users_voted = {}
	write_vote_file(valid_votes,list_of_votes)
	write_to_console(valid_votes,list_of_votes)
	return(list_of_votes,users_voted)

def connect():
	# Function to connect to the Twitch IRC channel that has been given
	irc = socket.socket()
	irc.connect(("irc.twitch.tv", 443))
	irc.send(bytes("PASS {passw}\r\n".format(passw=Twitch_pass),'utf-8'))
	irc.send(bytes("NICK {user}\r\n".format(user = Twitch_user),'utf-8'))
	irc.send(bytes("USER {user} 199.9.253.199 bla :{user}\r\n".format(user=Twitch_user),'utf-8'))
	# This isn't used in this script, but this allowed me to join more channels, which I used for another script
	for channel in Twitch_channel:
		irc.send(bytes("JOIN #{channel}\r\n".format(channel=channel.lower()),'utf-8'))
	# Returning the socket object
	return(irc)

def split_message(buf):
	# Use as follows split_message(":rikels!rikels@rikels.tmi.twitch.tv PRIVMSG #rikels :Sample")
	# This function will extract the username and the actual message they sent
	# In this case {"username":"rikels","message":"Sample"} will be returned
	extracted_info = re.match(":(\w+)!\w+@\w+.tmi.twitch.tv PRIVMSG #(\w+) :(.*)",str(buf))
	username = extracted_info.group(1)
	message = extracted_info.group(3)
	return({"username":username , "message":message})

def extract_vote_info(message):
	# It will return a dictionary as follows: {"username":"rikels", "vote":1}
	# If people try to !vote A (instead of a number) it would trow an error. Therfore a Try except is used
	# !vote A will be discarded as an invalid vote, users just have to enter a valid vote if they want to vote...
	try:
		# A Regular Expression, so users can put some garbage in and it'll be still used as a valid vote... 
		vote = re.match("!(?:[vV]|\\\/)(?:[oO0]|\(\))(?:[tT7])(?:[eE3])(?:[ 	])*(\d+)",message["message"]).group(1)
		# Returning the username with the number of the option they want to vote for
		return({"username":message["username"],"vote":int(vote)})
	except:
		pass

def write_vote_file(valid_votes,list_of_votes,timer=None):
	# Write_vote_file(["Option 1","Option 2"],[0,2])
	# Writing the results to a file
	with open(vote_file_path,"w") as vote_file:
			i=0
			for vote in valid_votes:
				vote_file.write("{i}. {option} (!vote {i}) {votes}\r\n".format(i=i+1,option=vote,votes=list_of_votes[i]))
				i += 1
			if timer is not None:
				vote_file.write("time remaining:	{time}".format(time=(timer-int(time.time()))))

def write_to_console(valid_votes,list_of_votes,timer=None):
	# Write_to_console(["Option 1","Option 2"],[0,2])
	# Writing the results to the console (easy for the streamer to view)
	i=0
	# "cls" isn't the best option, but with multiline text it is impossible to use the sys.out option
	os.system('cls')
	# Printing the votes as they show up in the text file to the terminal
	for vote in valid_votes:
		print("{i}. {option}		{votes}\r".format(i=i+1,option=vote,votes=list_of_votes[i]))
		i += 1
	if timer is not None:
				print("time remaining:	{time}".format(time=(timer-int(time.time()))))
#############hmm.. not sure if this can be deleted?
	sys.stdout.flush()

def set_vote(users_voted,list_of_votes,vote):
	# Function to set a new vote
	list_of_votes[vote["vote"]-1] += 1
	users_voted.update({vote["username"]:vote["vote"]})
	return(users_voted,list_of_votes)

def change_vote(users_voted,list_of_votes,vote):
	# Function to change the vote, in the future there will come a checkbox in webpage to enable/disable changing of votes
	# If left unchecked, this function just will not be used :D
	try:
		# Lowering the option they vreviously voted for by 1
		list_of_votes[users_voted[vote["username"]]-1] -= 1
		# Adding 1 vote to the new option they voted for
		list_of_votes[vote["vote"]-1] += 1
		users_voted.update({vote["username"]:vote["vote"]})
		return(users_voted,list_of_votes)
	except:
		pass

def vote_without_time(users_voted,list_of_votes,valid_votes,vote,timer=None):
	try:
		if vote["username"] not in users_voted:
		# Checking if the user has already voted
			if vote["vote"] <= len(valid_votes):
			# Checking if the vote is valid (less or equal to the length of all votes)
				users_voted,list_of_votes = set_vote(users_voted,list_of_votes,vote)
				write_vote_file(valid_votes,list_of_votes,timer=timer)
				write_to_console(valid_votes,list_of_votes,timer=timer)
		#allow_vote_changing is a boolean, if the username is already in the list (which means that he/she voted)
		#they will be able to change their vote, if the allow_vote_chaning is set to True
		elif allow_vote_changing:
		# If they have already voted...
			if vote["vote"] <= len(valid_votes):
				# Checking if the vote isn't the same as their last vote, so we don't use valuable harddisk writes if not needed
				if vote["vote"] != users_voted[vote["username"]]:
					users_voted,list_of_votes = change_vote(users_voted,list_of_votes,vote)
					write_vote_file(valid_votes,list_of_votes,timer=timer)
					write_to_console(valid_votes,list_of_votes,timer=timer)
	except exception as error:
		print(error)
	return(users_voted,list_of_votes,valid_votes,vote,timer)

def vote_with_time(users_voted,list_of_votes,valid_votes,vote,timer):
	if timer-int(time.time()) >= 0:
		try:
			# Checking if the user has already voted
			if vote["username"] not in users_voted:
				# Checking if the vote is valid (less or equal to the length of all votes)
				if vote["vote"] <= len(valid_votes):
					users_voted,list_of_votes = set_vote(users_voted,list_of_votes,vote)
					write_vote_file(valid_votes,list_of_votes,timer=timer)
					write_to_console(valid_votes,list_of_votes,timer=timer)
			#allow_vote_changing is a boolean, if the username is already in the list (which means that he/she voted)
			#they will be able to change their vote, if the allow_vote_chaning is set to True
			elif allow_vote_changing:
			# If they have already voted...
				if vote["vote"] <= len(valid_votes):
					# Checking if the vote isn't the same as their last vote, so we don't use valuable harddisk writes if not needed
					if vote["vote"] != users_voted[vote["username"]]:
						users_voted,list_of_votes = change_vote(users_voted,list_of_votes,vote)
						write_vote_file(valid_votes,list_of_votes,timer=timer)
						write_to_console(valid_votes,list_of_votes,timer=timer)
		except exception as error:
			print(error)
	return(users_voted,list_of_votes,valid_votes,vote,timer)



if os.path.exists(os.path.dirname(os.path.abspath("__file__"))+"\\config.txt"):
	config = parse_config(os.path.dirname(os.path.abspath("__file__"))+"\\config.txt")
else:
	print("The config file isn't found, did you rename/move it? (Or haven't I supplied it? contact me ;) )")
	config = {}

#making sure to not check for updates if not wanted (this will prevent that the program will crash if it can't update)
if "allow_automatic_updates" in config:
	allow_automatic_updates = config["allow_automatic_updates"]
else:
	allow_automatic_updates = True

# Firstly checking if there is a newer version available, if the last time checked is more than a week ago and if automatic updates are enabled
if "last_update" in config:
	if config["last_update"] <= (time.time() - 604800) and allow_automatic_updates:
		import nice_update
		try:
			update()
			update_config_value(config,"last_update",time.time())
		except:
			print("something went wrong while updating, please manually download the latest version")

# Generating the path to a file to store the votes, so it can be imported by OBS
if "vote_file_path" in config:
	path ="\\".join(config["vote_file_path"].split("\\")[:-1])
	if os.path.exists(path):
		vote_file_path = config["vote_file_path"]
	else:
		# Sure we could ask them if they want to use an auto generated path, but it's better if they just correct the problem
		print ("The path you entered as vote_file_path in the config doesn't exist, or is invalid.")
		raise SystemExit
else:
	vote_file_path = os.path.dirname(os.path.abspath("__file__"))+"\\votes.txt"

# Checking to see if twitch_username is uncommented in the config, but it could be they didn't uncomment the OAuth option
# That's why we need to check that, and warn them about this.
if "twitch_username" in config:
	try:
		Twitch_user = config["twitch_username"]
		Twitch_pass = config["twitch_oauth"]
	except NameError:
		print("Twitch_username is filled in in config, but you didn't uncomment twitch_oauth.")
else:
	# Creating a justinfan username (this will allow to read the chat without anyone seeing a bot or something of that nature)
	Twitch_user = "justinfan{random}".format(random=int(random()))
	Twitch_pass = "blah"


# Letting the user know the path to the file (just as a backup if it stores it somewhere strange...)
print("open textfile {vote_file_path} in OBS as text file".format(vote_file_path=vote_file_path))


if "Twitch_channel" in config:
	Twitch_channel = [config["Twitch_channel"]]
else:
	# Asking the user which channel to join, if they didn't use the config file to do so
	Twitch_channel = [input("Which Channel to join?: ")]


# Checking if they uncommented the timer option in the config
if "timer" in config:
	default_timer = config["timer"]
else:
	# Default to 40, this means an average of 30 effective seconds (with streaming delay)
	default_timer = 40

# Checking if they uncommented the add_to_timer option
if "add_to_timer" in config:
	add_to_timer = config["add_to_timer"]
else:
	add_to_timer = 10

if "allow_vote_changing" in config:
	allow_vote_changing = config["allow_vote_changing"]
else:
	allow_vote_changing = True

# Checking this after it actually starts
if "timed_voting_default" in config:
	if config["timed_voting_default"] == True:
		current_vote = vote_with_time
	else:
		current_vote = vote_without_time
else:
	current_vote = vote_without_time



# Checking if the key combinations are entered in the config and if they are valid
if "key_combination_reset_votes" in config:
	try:
		key_combination_reset_votes = config["key_combination_reset_votes"].split(",")
	except:
		print("you entered an invalid key combination for key_combination_reset_votes")
else:
	key_combination_reset_votes = ["f2","windows"]

if "key_combination_reset_timed_votes" in config:
	try:
		key_combination_reset_timed_votes = config["key_combination_reset_timed_votes"].split(",")
	except:
		print("you entered an invalid key combination for key_combination_reset_timed_votes")
else:
	key_combination_reset_timed_votes = ["f3", "windows"]

if "key_combination_add_to_timer" in config:
	try:
		key_combination_add_to_timer = config["key_combination_add_to_timer"].split(",")
	except:
		print("you entered an invalid key combination for key_combination_add_to_timer")
else:
	key_combination_add_to_timer = ["f4","windows"]




# Creating the pipe for use between multiple sources
parent_connection,child_connection = Pipe()

# Sending the key combinations before we start the program,
# so the connection is readable before the hotkey starts and throws errors because it doesn't have any keys to listen to
parent_connection.send([key_combination_reset_votes,key_combination_reset_timed_votes,key_combination_add_to_timer])
# Starting thread to listen for system wide hotkeys without having to pause the script
system_wide_hotkey = threading.Thread(target=listen_for_hotkeys.listen, args=([child_connection]))
system_wide_hotkey.daemon = True
system_wide_hotkey.start()



# Calling the start function, which creates the variables (asking for options), and returns the needed lists
valid_votes,list_of_votes,users_voted,timer = start()
# Connecting to IRC
irc = connect()


#Let the script run forever, waiting for new votes!
# Each iteration it handles 1 receive function (can be more than 1 message)
while(True):
# Checking for incomming messages of child, This child is watching you closely, he's going to alert me when you press WIN+F3.
# I trust my child 100%, and if he says you pressed those particular buttons at the same time... I will reset the votes!
# Using a while statement here, because if the user holds the key combination for a longer time, it will send a few messages over the pipe.
# We don't want to handle 1 keypress and multiple messages at a time. It will take a long time before the hotkeys are handled that way..
	while parent_connection.poll():
		action = parent_connection.recv()
		if action["action"] == 1:
			# Action 1 is resetting the votes
			list_of_votes,users_voted = reset_votes(list_of_votes)
			timer=None
			current_vote = vote_without_time
		elif action["action"] == 2:
			# Action 2 is resetting the votes and turning on the timer
			list_of_votes,users_voted = reset_votes(list_of_votes)
			timer = int(time.time() + default_timer)
			current_vote = vote_with_time
		elif action["action"] == 3:
			# Action 3 is adding time to the timer
			timer = timer+add_to_timer
	# Define which objects we want to check with Select (at the moment it's just 1 object, in the future it will be more (hopfully))
	receive_these = [irc]
	send_these = receive_these
	# Using Select to see if there is new information to be received, both, for the Hotkeys as for the Twitch IRC object
	# Something with Windows not being able to use Select on Multiprocessing Pipes... that's why you do not see the Pipe in the select statement
	
	# As this script only needs to receive, checking if the connection is open for sending isn't needed.
	# Timeout of 0.5 seconds, so if there aren't any messages to be retreived, it will continue after 1 second
	readable, writable, exceptional = select.select(receive_these,[], [],0.5)
	if readable:
		# Action to take if any of the input objects is readable

		# Buff as in buffer, but that is a registered python word/function
		buff = irc.recv(1024)
		# Splitting by newline character, so actually splitting all messages
		buff = buff.split(b'\r\n')
		# Because it splits on a newline character, the last entry in the list will be empty, '', [:-1] means everything except the last one in the list
		for buf in buff[:-1]:
			buf = buf.decode('utf-8')
			# To keep the connection alive, we have to reply to the ping
			# Twitch terminates the connection if it doesn't receive a pong reply after 3 pings
			if "PING" in buf:
				buf = "PONG tmi.twitch.tv\r\n"
				irc.send(bytes(buf,'utf-8'))
			try:
				message = split_message(buf)
				if re.match("^!(?:[vV]|\\\/)(?:[oO0]|\(\))(?:[tT7])(?:[eE3])",message["message"]):
					vote = extract_vote_info(message)
					users_voted,list_of_votes,valid_votes,vote,timer = current_vote(users_voted,list_of_votes,valid_votes,vote,timer=timer)
			except:
				pass
	elif (timer is not None) and (timer-int(time.time()) >= 0):
		# If no one voted, we also update it, suckss, because of harddiskwrites :/
		# Not 100% perfect... if there are a lot of messages, no votes.... the timer won't be updated on display, but it will surely still work :)
		write_to_console(valid_votes,list_of_votes,timer=timer)
		write_vote_file(valid_votes,list_of_votes,timer=timer)