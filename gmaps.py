import json, urllib.request
from urllib.parse import urlencode
import googlemaps
import re
from flask import Flask, request
from twilio.rest import Client
from twilio import twiml

account_sid = #removed for security
auth_token  = #removed for security
client = Client(account_sid,auth_token)

def cleanhtml(raw_html):
	cleanr=re.compile('<.*?>')
	cleantext = re.sub(cleanr,'',raw_html)
	return cleantext

def splitMessage(message):
	messages=[]
	for i in range(0,len(message),1500):
		spacer=0
		while len(message) > i+1500+spacer and message[i+1500+spacer] != '\n':
			spacer+=1
		messages.append(message[i:i+1500+spacer])
		i+=spacer
	return messages


def sendDirections(number,origin,destination,mode,sendText=False):
	

	origin = origin.replace(" ","+")
	destination =  destination.replace(" ","+")
	url = 'http://maps.googleapis.com/maps/api/directions/json?%s' % urlencode((('origin', origin),('destination', destination),('mode',mode)))
	urlOpen = urllib.request.urlopen(url)
	directions = json.load(urlOpen)
	message=mode.title()+" from "+origin.replace("+"," ")+" to "+destination.replace("+"," ")+"\n"
	print(directions)
	print(len (directions['routes'][0]['legs'][0]['steps']))
	for i in range (0, len (directions['routes'][0]['legs'][0]['steps'])):
		j = directions['routes'][0]['legs'][0]['steps'][i]['html_instructions'] 
		message+=cleanhtml(j)+"\n"
	if len(message) <= 1550:
		if sendText:
			client.api.account.messages.create(to=number,from_="+12019928470",body=message)
		else:
			print(message)
	else:
		messages = splitMessage(message)
		for message in messages:
			if sendText:
				client.api.account.messages.create(to=number,from_="+12019928470",body=message)
			else:
				print(message)

app = Flask(__name__)

@app.route('/sms',methods=['POST'])
def sms():
	number = request.form['From']
	message_body = request.form['Body'].split("__")
	sendDirections(number,message_body[0],message_body[1],message_body[2])




if __name__ == "__main__":
	#app.run()

	number = input("Enter phone number: ")
	if len(number)==0:
		number="+15558675309"
	origin = input("Starting Location: ")
	if len(origin)==0:
		origin="Boston, MA"
	destination = input("End Location: ")
	if len(destination)==0:
		destination="Cambridge MA"
	mode = input("Mode of transportation (driving,walking,bicycling,transit): ")
	if len(mode)==0:
		mode="driving"
	sendText = input("Send text message? ")
	if sendText=="y":
		sendText=True
	else:
		sendText=False
	try:
	#+13608885843
		sendDirections(number,origin,destination,mode,sendText)
	except:
		print("Could not find a path "+mode+" from "+origin+" to "+ destination)
