__author__ = 'Riley Dawson'
import serial
import time
from time import strftime
from twython import Twython
from collections import namedtuple

# Python driver for Twasker project. This program fetches a list of tasks assigned on twitter.\
# Tasks are passed throuhg to an arduino attached to an LCD display, to show the next task to be completed.
# Once completed, the user presses a physical button on the arduino, notifying the python program over serial
# connection. The arduino is then sent the next task to be completed, if available.

# Define task object for storing tweets and their users
Task = namedtuple('Task', ['tweet', 'user'])
# Define
taskQueue = []
# ID of last task completed, needs to be manually updated each time the program is run (no stored memory).
lastID = 000000000000000000

# Twitter API keys (input your own)
CONKEY = '*************************************'
CONSECRET = '*************************************'

ACCTOKEN = '*************************************'
ACCSECRET = '*************************************'

# Load twitter object, set global defaults
twitter = Twython(CONKEY, CONSECRET, ACCTOKEN, ACCSECRET)
runningTask = False
currentTask = Task("", "")
# There are 900 seconds in 15 minutes, which is when twitter's api limits get requests, this just tracks to make sure
# new tasks are only fetched once every 15 minutes
fetch_timer = 91

# Set's up connection to Arduino
def twasker_setup():
    # Establish connection with Arduino
    ser = serial.Serial(2, 9600)
    ser.flush()
    # Wait until arduino is ready to receive
    while ser.readline() != b"Arduino Ready\r\n":
        time.sleep(0.01)
    return ser


# Fetches 10 most recent tasks and stores them in a stack (newest tasks are pushed onto stack first)
def task_fetch():
    global taskQueue, lastID, twitter
    # Get dictionary of most recent mentions
    messages = twitter.get_mentions_timeline(since_id=lastID, count=10)
    # Store each task
    for message in messages:
        task = Task(message['text'].replace("@GnarlyTwasker ", ""), message['user']['screen_name'])
        # Notify task giver their message has been received.
        tweet = "@" + ((message['user']['screen_name'])) + " your task sent at " + message[
            'created_at'] + ", has been received and will (probably) be completed (eventually)."
        twitter.update_status(status=tweet)
        # Quick sleep to not ddos twitter :s
        time.sleep(4)
        # Make sure most recent task isn't a duplicate of last task pushed
        if task != taskQueue[-1:]:
            taskQueue.append(task)
        # Update tweet tracker to not fetch the same tweets next time
        lastID = message['id_str']
        print(message['text'])

    return


# Send tasks out to the Arduino
def task_send(ser):
    global runningTask, currentTask
    ser.write(str(currentTask.tweet).encode())
    # Update flag to show a task is currently running
    runningTask = True


# Send tweet notifying task assignee their task has been completed.
def complete_tweet():
    global twitter, currentTask
    twitter.update_status(status='@' + currentTask.user + ' your assigned task ' + '"' + currentTask.tweet[:15] +
                                 '..." was completed at: ' + strftime("%Y-%m-%d %H:%M:%S"))


# Main execution loop
def twasker_run(ser):
    # Begin main running process
    global taskQueue, runningTask, currentTask, fetch_timer
    while 1:
        # Check to see if the most recent task has been completed.
        arduino_message = ser.readline()
        if arduino_message != "":
            # Task has been completed, notify task assignee
            runningTask = False
            complete_tweet()
            arduino_message = ""

        # Fetch newly assigned tasks if there are none currently being completed, and it has been at least 15 min since
        #  the last fetch.
        if not taskQueue and fetch_timer > 90:
            print("Fetching tasks")
            # Restart Fetch timer
            fetch_timer = 0
            # Fetch tasks
            task_fetch()
            print("task fetch complete")
        # Update arduino with a new task.
        if not runningTask and taskQueue:
            currentTask = taskQueue.pop()
            task_send(ser)
        # Sleep and update the timer
        time.sleep(10)
        fetch_timer += 1

# Run program
print("running setup")
ser = twasker_setup()
print("setup complete!")
print("Running!")
twasker_run(ser)
ser.close()