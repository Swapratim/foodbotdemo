#!/usr/bin/env python

from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
import urllib.request, urllib.parse, urllib.error
import json
import os
import sys
import psycopg2
import urlparse
import pymongo

from flask import Flask
from flask import request, render_template
from flask import make_response
from pymongo import MongoClient


# Flask should start in global layout
context = Flask(__name__)
# Facbook Access Token (For FoodBot Facebook Page)
ACCESS_TOKEN = "EAALflMNd24sBAB7pQyVOtc6nzzl8IwGQ3u7ZAqwc5DoqDhiwsxwPPIcqFwgFvZAazzLS415ZChO6ZBUpIi6RLeSA7ZBi2ZCFAhChDx1SQSDjMzmSHAu1PQ2P6tnEHM3Ko1cULn4XJt31ZBXs6IfXVC8xFXxZBf2La8fq4VdfgPuMTAZDZD"
# Google Access Token
Google_Acces_Token = "key=AIzaSyDNYsLn4JGIR4UaZMFTAgDB9gKN3rty2aM&cx=003066316917117435589%3Avcms6hy5lxs&q="
# NewsAPI Access Token
newspai_access_token = "505c1506aeb94ba69b72a4dbdce31996"
# Weather Update API KeyError
weather_update_key = "747d84ccfe063ba9"

#************************************************************************************#
#                                                                                    #
#    All Webhook requests lands within the method --webhook                          #
#                                                                                    #
#************************************************************************************#
@context.route('/webhook', methods=['POST'])
def webhook():
    reqContext = request.get_json(silent=True, force=True)
    if reqContext.get("result").get("action") == "input.welcome":
       return welcome()
    elif reqContext.get("result").get("action") == "Help":
       return help(reqContext)
    else:
       print("Good Bye")

#************************************************************************************#
#                                                                                    #
#   This method is to get the Facebook User Deatails via graph.facebook.com/v2.6     #
#                                                                                    #
#************************************************************************************#
def welcome():
    print ("within welcome method")
    data = request.json
    print (data)
    if data is None:
        return {}
    entry = data.get('originalRequest')
    dataall = entry.get('data')
    sender = dataall.get('sender')
    id = sender.get('id')
    print ("id :" + id)
    fb_info = "https://graph.facebook.com/v2.6/" + id + "?fields=first_name,last_name,profile_pic,locale,timezone,gender&access_token=" + ACCESS_TOKEN
    print (fb_info)
    result = urllib.request.urlopen(fb_info).read()
    print (result)
    data = json.loads(result)
    first_name = data.get('first_name')
    print (first_name)
    speech = "I'm FoodBot. How can I help you?"
    res = {
          "speech": speech,
          "displayText": speech,
           "data" : {
              "facebook" : [{
      "attachment": {
        "type": "template",
        "payload": {
          "template_type": "generic",
          "elements": [
            {
              "title": "Hi " + first_name + ", Welcome to The South Indian!",
              "image_url": "http://s.dinnerbooking.eu/uploads/restaurant_pictures/530x250/1493285301_505-1348-the-south-indian-herning.jpg"
            }
          ]
        }
      }
    },
    {
      "text": "South Indian is dedicated to showcase the finest South Indian cuisine in Denmark."
    },
    {
      "text": "I'm FoodBot. How can I help you?",
      "quick_replies": [
        {
          "content_type": "text",
          "title": "Opening Hours",
          "payload": "openinghoursandlocation",
          "image_url": "http://s3.amazonaws.com/libapps/accounts/26094/images/open-icon.jpg"
        },
        {
          "content_type": "text",
          "title": "Discover Menu",
          "payload": "Menu",
          "image_url": "http://malaysiapca.com/wp-content/uploads/2016/09/pca-malaysia-chefs-table-food-menu-icon.jpg"
        },
        {
          "content_type": "text",
          "title": "Take Away",
          "payload": "Take Away",
          "image_url": "http://discoverybayuk.com/wp-content/uploads/2015/09/takeaway-icon.gif"
        },
        {
          "content_type": "text",
          "title": "Event",
          "payload": "Event",
          "image_url": "http://banburytown.com/wp-content/uploads/2015/08/icon_event.png"
        },
        {
          "content_type": "text",
          "title": "Help",
          "payload": "Help",
          "image_url": "https://cdn1.iconfinder.com/data/icons/logotypes/32/youtube-512.png"
        }
       ]
      }
     ]
    }
   };
    print (res)
    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    print (r)
    return r

def reply(user_id, msg):
    data = {
        "recipient": {"id": user_id},
        "message": {"text": msg}
    }
    print ("Data.........")
    print (data)
    resp = requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=" + ACCESS_TOKEN, json=data)
    print(resp.content)
 

#************************************************************************************#
#                                                                                    #
#   Help Information Providing                                                       #
#                                                                                    #
#************************************************************************************#
def help(resolvedQuery):
    speech = "I'm sorry if I make you confused. Please select Quick Reply or Menu to chat with me. \n\n 1. Click on 'News' to read latest news from 33 globally leading newspapers \n 2. Click on 'Weather' and write a city name to get weather forecast \n 3. Click on 'Wikipedia' and write a topic you want to know about. No need to ask a full question. \n 4. Click on 'YouTube' and search for your favourite videos. \n 5. You can still chat directly with Marvin without the quick replies like before for - Weather, Wikipedia & Small Talk."
    res = {
        "speech": speech,
        "displayText": speech,
        "data" : {
        "facebook" : [
               {
                "text": speech
               }
             ]
           } 
         };
    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting APPLICATION on port %d" % port)
    context.run(debug=True, port=port, host='0.0.0.0')