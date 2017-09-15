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
    elif reqContext.get("result").get("action") == "contact.us":
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
                            "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTj5F6SkRuRaCN5cB3_LanKl_BtgHPtKRsGGtHWabOvDlhPtcLj",
                            "default_action": {
                               "type": "web_url",
                               "url": "https://www.inc.com/jeff-haden/tyson-cole-how-to-start-successful-restaurant-6-tips.html",
                                "webview_height_ratio": "tall",
                                },
                            "buttons": [
                            {
                               "title": "Read More",
                               "type": "web_url",
                               "url": "https://www.inc.com/jeff-haden/tyson-cole-how-to-start-successful-restaurant-6-tips.html",
                               "webview_height_ratio": "tall",
                            }
                          ]
                        },
                        {
                            "title": "Music & Food Festival",
                            "image_url": "http://balithisweek.com/wp-content/uploads/2017/05/20170602-music-and-food-festival.jpg",
                            "subtitle": "Enjoy the Food Festival with Food",
                            "default_action": 
                                {
                                    "type": "web_url",
                                    "url": "http://balithisweek.com/event/music-and-food-festival/",
                                    "webview_height_ratio": "tall"
                                },
                                "buttons": [
                                {
                                     "title": "Read More",
                                     "type": "web_url",
                                     "url": "http://balithisweek.com/event/music-and-food-festival/",
                                     "webview_height_ratio": "tall"
                                }
                               ]
                        },
                        {
                            "title": "Happy New Year Festival",
                            "image_url": "http://www.call-systems.com/blog/wp-content/uploads/2013/12/new-years.jpg",
                            "subtitle": "1st January, 2017",
                            "default_action": 
                               {
                                   "type": "web_url",
                                   "url": "http://www.call-systems.com/blog/2013/12/17/5-tips-for-a-happy-new-years-party-at-your-restaurant/",
                                   "webview_height_ratio": "tall"
                                },
                                "buttons": [
                                {
                                   "title": "Read More",
                                   "type": "web_url",
                                   "url": "http://www.call-systems.com/blog/2013/12/17/5-tips-for-a-happy-new-years-party-at-your-restaurant/",
                                   "webview_height_ratio": "tall"
                                }
                              ]
                       },
                       {
                            "title": "Christmas Offers",
                            "image_url": "http://l.upstc.com/events/29749/119442/original_1417080466.9791.jpg",
                            "subtitle": "25 December, 2017, Copenhagen",
                            "default_action": 
                            {
                                "type": "web_url",
                                "url": "http://www.upout.com/nyc/do/holiday-happy-hour-1",
                                "webview_height_ratio": "tall"
                            },
                            "buttons": [
                            {
                                "title": "Read More",
                                "type": "web_url",
                                "url": "http://www.upout.com/nyc/do/holiday-happy-hour-1",
                                "webview_height_ratio": "tall"
                            }
                           ]
                        }
                        ],
                        "buttons": [
                         {
                            "title": "View Site",
                            "type": "web_url",
                            "url": "https://marvinai.live"
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
    speech = "To reserve a table or order for food delivery, please contact us at: +45-7182-5584"
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