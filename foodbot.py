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
    elif reqContext.get("result").get("action") == "input.event":
       return eventlist(reqContext)
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
              "title": "Hi " + first_name + ", Welcome to The Coco & Butter Restaurant!",
              "image_url": "http://www.pdcdc.org/wp-content/uploads/2016/03/restaurant-939435_960_720.jpg"
            }
          ]
        }
      }
    },
    {
      "text": "Coco & Butter is dedicated to showcase the finest local cuisine in Denmark."
    },
    {
      "text": "I'm FoodBot. How can I help you?",
      "quick_replies": [
        {
          "content_type": "text",
          "title": "Opening Hours",
          "payload": "openinghoursandlocation",
          "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcREBeHDCh_So0LEhyWapjjilpDFiRLXMaeuwUfc1rrxu3qShTCUqQ"
        },
        {
          "content_type": "text",
          "title": "Menu",
          "payload": "Menu",
          "image_url": "https://cdn1.iconfinder.com/data/icons/hotel-restaurant/512/16-512.png"
        },
        {
          "content_type": "text",
          "title": "Take Away",
          "payload": "Take Away",
          "image_url": "https://d30y9cdsu7xlg0.cloudfront.net/png/66559-200.png"
        },
        {
          "content_type": "text",
          "title": "Event",
          "payload": "Event",
          "image_url": "http://icons.iconarchive.com/icons/icons8/windows-8/512/Time-Today-icon.png"
        },
        {
          "content_type": "text",
          "title": "Contact Us",
          "payload": "contact",
          "image_url": "http://www.logoeps.com/wp-content/uploads/2013/04/whatsapp-logo-symbol-vector.png"
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
#   Below method is to get the Event Details as List Template                        #
#                                                                                    #
#************************************************************************************#
newspaper_url = ''
data = ''
def eventlist(reqContext):
    resolvedQuery = reqContext.get("result").get("resolvedQuery")
    res = {
            "speech": "Events",
            "displayText": "Events",
            "data" : {
            "facebook" : [
                 {
                    "sender_action": "typing_on"
                  },
                 {
                "attachment" : {
                  "type" : "template",
                    "payload" : {
                     "template_type" : "list",
                     "elements" : [ 
                        {
                            "title": "Aarhus - The Grand Opening",
                            "image_url": "https://media-cdn.tripadvisor.com/media/photo-o/0d/b3/3a/55/the-south-indian-xpress.jpg",
                            "default_action": {
                               "type": "web_url",
                               "url": "http://southindian.dk/calendar/the-south-indian-xpress-takeaway-arhus-the-grand-opening/",
                                "webview_height_ratio": "tall",
                                },
                            "buttons": [
                            {
                               "title": "Read More",
                               "type": "web_url",
                               "url": "http://southindian.dk/calendar/the-south-indian-xpress-takeaway-arhus-the-grand-opening/",
                               "webview_height_ratio": "tall",
                            }
                          ]
                        },
                        {
                            "title": "Solrød: Frokost Tilbud",
                            "image_url": "http://southindian.dk/wp-content/uploads/2017/03/Forkost-Tilbud2.png",
                            "subtitle": "Enjoy the Food Festival",
                            "default_action": 
                                {
                                    "type": "web_url",
                                    "url": "http://southindian.dk/calendar/solrod-frokost-tilbud/",
                                    "webview_height_ratio": "tall"
                                },
                                "buttons": [
                                {
                                     "title": "Read More",
                                     "type": "web_url",
                                     "url": "http://southindian.dk/calendar/solrod-frokost-tilbud/",
                                     "webview_height_ratio": "tall"
                                }
                               ]
                        },
                        {
                            "title": "Tamil Nytår",
                            "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQBd2nw84IbiTM1L3yy7yKTv6uCf7gJfv8cuIZrXog_G1YRsNweeQ",
                            "subtitle": "4. November 2016 12:00",
                            "default_action": 
                               {
                                   "type": "web_url",
                                   "url": "http://southindian.dk/calendar/tamil-nytar-og-ny-frokostmenu/",
                                   "webview_height_ratio": "tall"
                                },
                                "buttons": [
                                {
                                   "title": "Read More",
                                   "type": "web_url",
                                   "url": "http://southindian.dk/calendar/tamil-nytar-og-ny-frokostmenu/",
                                   "webview_height_ratio": "tall"
                                }
                              ]
                       },
                       {
                            "title": "Prøvespisning",
                            "image_url": "http://southindian.dk/wp-content/uploads/2014/10/Up-close-clay-horse-of-Aiyanar-Temple-Chettinad-Tamil-Nadu-India.jpg",
                            "subtitle": "1. November 2014 18:00, The Coco & Butter Godthåbsvej 12, 2000 Frederiksberg",
                            "default_action": 
                            {
                                "type": "web_url",
                                "url": "http://southindian.dk/calendar/provespisning/",
                                "webview_height_ratio": "tall"
                            },
                            "buttons": [
                            {
                                "title": "Read More",
                                "type": "web_url",
                                "url": "http://southindian.dk/calendar/provespisning/",
                                "webview_height_ratio": "tall"
                            }
                           ]
                        }
                        ],
                        "buttons": [
                         {
                            "title": "View Site",
                            "type": "web_url",
                            "url": newspaper_url
                        }
                       ]  
                     } 
                   }
                 }
               ]
             } 
           };
    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

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