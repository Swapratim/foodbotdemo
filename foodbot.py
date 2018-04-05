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
    elif reqContext.get("result").get("action") == "openinghoursandlocation":
       return openinghours(reqContext)
    elif reqContext.get("result").get("action") == "menu":
       return mainMenu(reqContext)
    elif reqContext.get("result").get("action") == "menuitems":
       return menuitems(reqContext)
    elif reqContext.get("result").get("action") == "howareyou":
       return howareyou(reqContext)
    elif reqContext.get("result").get("action") == "forsalebottemplate":
       return forsale(reqContext)
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

    # Insert Data into MongoDB table:
    USER_DATA = [
    {
        'id': data.get('id'),
        'first_name': data.get('first_name'),
        'last_name': data.get('last_name'),
        'locale': data.get('locale'),
        'timezone': data.get('timezone'),
        'gender': data.get('gender')
    }]
    client = MongoClient("mongodb://heroku_stgdzdbp:heroku_stgdzdbp@ds235169.mlab.com:35169/heroku_jnq3vlhz")
    db = client.get_default_database()
    user_table = db['foodbot_user_details']
    user_table.insert_many(USER_DATA)

    # Check if already the user is present in database
    if user_table.find( { "id" : id } ):
       print ("Data is already PRESENT in the Database")
       #user_table.delete_many({"first_name": "Swapratim"})
    else: 
       print ("IT LANDED IN THE ELSE LOOP")
       user_table.insert_many(USER_DATA)
       print ("Data has been INSERTED")

    speech = "I'm FoodBot. How can I help you?"
    res = {
          "speech": speech,
          "displayText": speech,
           "data" : {
              "facebook" : [
              {
                    "sender_action": "typing_on"
              },
              {
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
       "sender_action": "typing_on"
    },
    {
      "text": "This is a DEMO to showcase the power of automated customer service in restaurants"
    },
    {
       "sender_action": "typing_on"
    },
    {
      "text": "I'm Restaurant Chatbot - the virtual assistant at your service"
    },
    {
      "text": "Let me guide you to the virtual tour. Below are the most frequent topics of search",
      "quick_replies": [
        {
          "content_type": "text",
          "title": "Menu",
          "payload": "Menu",
          "image_url": "https://cdn1.iconfinder.com/data/icons/hotel-restaurant/512/16-512.png"
        },
        {
          "content_type": "text",
          "title": "Opening Hours",
          "payload": "openinghoursandlocation",
          "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcREBeHDCh_So0LEhyWapjjilpDFiRLXMaeuwUfc1rrxu3qShTCUqQ"
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
          "title": "For Sale",
          "payload": "For Sale",
          "image_url": "http://p.lnwfile.com/_/p/_raw/pg/vn/cm.png"
        },
        {
          "content_type": "text",
          "title": "Contact",
          "payload": "contact",
          "image_url": "https://cdn3.iconfinder.com/data/icons/communication-mass-media-news/512/phone_marketing-128.png"
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
#                       OPENING HOURS                                                #
#                                                                                    #
#************************************************************************************#
def openinghours(reqContext):
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
                      "template_type" : "generic",
                       "elements" : [ 
                                 {
                                   "title" : "Coco & Butter - Copenhagen",
                                   "image_url" : "https://richardkenworthy.files.wordpress.com/2012/06/img_3877-edit.jpg",
                                   "subtitle" : "Best Food in Town",
                                   "buttons": [{
                                        "type": "postback",
                                        "title": "View Opening Hours",
                                        "payload":"View Opening Hours"
                                    }]
                                 },
                                 {
                                   "title" : "Coco & Butter - Aarhus",
                                   "image_url" : "https://previews.123rf.com/images/duha127/duha1271112/duha127111200074/11708665-Fine-restaurant-dinner-table-place-setting-Stock-Photo-dining.jpg",
                                   "subtitle" : "Best Food in Town",
                                   "buttons": [{
                                        "type": "postback",
                                        "title": "View Opening Hours",
                                        "payload":"View Opening Hours"
                                    }]
                                 }
                           ]
                       } 
                   }
                },
        {
      "text": "Can I help you more information:",
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
          "title": "For Sale",
          "payload": "For Sale",
          "image_url": "http://p.lnwfile.com/_/p/_raw/pg/vn/cm.png"
        },
        {
          "content_type": "text",
          "title": "Contact",
          "payload": "contact",
          "image_url": "https://cdn3.iconfinder.com/data/icons/communication-mass-media-news/512/phone_marketing-128.png"
        }
       ]
     }]
   } 
 };
    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r
#************************************************************************************#
#                                                                                    #
#                       MAIN MENU  DISPLAY                                           #
#                                                                                    #
#************************************************************************************#
def mainMenu(reqContext):
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
                      "template_type" : "generic",
                       "elements" : [ 
                                 {
                                   "title" : "Coco & Butter Menu",
                                   "image_url" : "http://mediad.publicbroadcasting.net/p/michigan/files/201703/32621859132_25f783b550_o.jpg",
                                   "subtitle" : "Best in town dishes, only for you.",
                                   "buttons": [{
                                        "type": "postback",
                                        "title": "Menu Items",
                                        "payload":"Menu Items"
                                    },
                                    {
                                        "type": "postback",
                                        "title": "Drinks",
                                        "payload": "Drinks"
                                    },
                                    {
                                        "type": "postback",
                                        "title": "Seasonal Offers",
                                        "payload": "Seasonal Offers"
                                    }]
                                 }
                           ]
                       } 
                   }
                },
        {
      "text": "Please select any of the menu from above. \nTo view other options, please click below options:",
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
          "title": "For Sale",
          "payload": "For Sale",
          "image_url": "http://p.lnwfile.com/_/p/_raw/pg/vn/cm.png"
        },
        {
          "content_type": "text",
          "title": "Contact",
          "payload": "contact",
          "image_url": "https://cdn3.iconfinder.com/data/icons/communication-mass-media-news/512/phone_marketing-128.png"
        }
       ]
     }]
   } 
 };
    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r
#************************************************************************************#
#                                                                                    #
#                       MENU ITEMS DISPLAY                                           #
#                                                                                    #
#************************************************************************************#
def menuitems(reqContext):
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
                      "template_type" : "generic",
                       "elements" : [ 
                                 {
                                   "title" : "Chef's Special",
                                   "image_url" : "https://img.grouponcdn.com/deal/fqWyQpQoCk7Kzq51nszzcE/fuads_restaurant-2048x1229/v1/c700x420.jpg",
                                   "subtitle" : "60% Discount on Menu",
                                 },
                                 {
                                   "title" : "Chicken Mamma Miya",
                                   "image_url" : "https://www.bu.edu/today/files/2011/10/t_11-4183-INHOUSE-006.jpg",
                                   "subtitle" : "Buy One, Get one Coke Free",
                                 },
                                 {
                                   "title" : "Mexican Roll",
                                   "image_url" : "http://img.taste.com.au/_k6sa3dZ/w720-h480-cfill-q80/taste/2016/11/chicken-and-prosciutto-parmigiana-79468-1.jpeg",
                                   "subtitle" : "20% Offer on Take Away Orders",
                                 },
                                 {
                                   "title" : "Steak Style",
                                   "image_url" : "http://www.quivertreeapartments.com/wp-content/uploads/Picture30-300x233.png",
                                   "subtitle" : "Early Bird Promo Offer",
                                 }
                           ]
                       } 
                   }
                },
        {
      "text": "Taste our Chef's special excuisite dishes at reasonable price. \nTo view other options, please click below options:",
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
          "title": "For Sale",
          "payload": "For Sale",
          "image_url": "http://p.lnwfile.com/_/p/_raw/pg/vn/cm.png"
        },
        {
          "content_type": "text",
          "title": "Contact",
          "payload": "contact",
          "image_url": "https://cdn3.iconfinder.com/data/icons/communication-mass-media-news/512/phone_marketing-128.png"
        }
       ]
     }]
   } 
 };
    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r
#************************************************************************************#
#                                                                                    #
#   Below method is to get the Event Details as List Template                        #
#                                                                                    #
#************************************************************************************#

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
                        },
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
          "title": "For Sale",
          "payload": "For Sale",
          "image_url": "http://p.lnwfile.com/_/p/_raw/pg/vn/cm.png"
        },
        {
          "content_type": "text",
          "title": "Contact",
          "payload": "contact",
          "image_url": "https://cdn3.iconfinder.com/data/icons/communication-mass-media-news/512/phone_marketing-128.png"
        }
       ]
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
#   Below method is to respond "How are you?"				                         #
#                                                                                    #
#************************************************************************************#
def howareyou(reqContext):
    resolvedQuery = reqContext.get("result").get("resolvedQuery")
    res = {
            "speech": "Events",
            "displayText": "Events",
            "data" : {
            "facebook" : [
    {
      "text": "I am better than ever :) \nHope you will enjoy close to heart delicious foods here. \n How can I help you?",
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
          "title": "For Sale",
          "payload": "For Sale",
          "image_url": "http://p.lnwfile.com/_/p/_raw/pg/vn/cm.png"
        },
        {
          "content_type": "text",
          "title": "Contact",
          "payload": "contact",
          "image_url": "https://cdn3.iconfinder.com/data/icons/communication-mass-media-news/512/phone_marketing-128.png"
        }
       ]
      }]
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
    print ("Within CONTACT US method")
    speech = "FoodBot is been created by marvin.ai. \nDo you like it?"
    res = {
        "speech": speech,
        "displayText": speech,
        "data" : {
        "facebook" : [
               {
                    "sender_action": "typing_on"
               },
               {
                 "text": speech
                },
               {
                    "sender_action": "typing_on"
               },
               {
                 "text": "Did You Know: You can get 10X more Customers with Restaurant Chatbot"
                },
                {
                    "sender_action": "typing_on"
               },
               {
                 "text": "Request for a free Demo to see lot more exciting features of Chatbot"
                },
                {
                 "attachment" : {
                   "type" : "template",
                     "payload" : {
                      "template_type" : "generic",
                       "elements" : [ 
                                 {
                                   "title" : "Swapratm Roy",
                                   "image_url" : "https://marvinchatbot.files.wordpress.com/2017/06/swapratim-roy-founder-owner-of-marvin-ai.jpg?w=700&h=&crop=1",
                                   "subtitle" : "Founder of marvin.ai \nCall: +45-7182-5584",
                                   "buttons": [{
                                        "type": "web_url",
                                        "url": "https://www.messenger.com/t/swapratim.roy",
                                        "title": "Connect on Messenger"
                                    },
                                    {
                                        "type": "web_url",
                                        "url": "https://marvinai.live",
                                        "title": "View Website"
                                    },
                                    {
                                        "type":"phone_number",
                                        "title":"Request For Demo",
                                        "payload": "+4571825584"
                                    }]
                                 }
                           ]
                       } 
                   }
                },
               {
      "text": "How can I help you?",
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
          "title": "For Sale",
          "payload": "For Sale",
          "image_url": "http://p.lnwfile.com/_/p/_raw/pg/vn/cm.png"
        },
        {
          "content_type": "text",
          "title": "Contact",
          "payload": "contact",
          "image_url": "https://cdn3.iconfinder.com/data/icons/communication-mass-media-news/512/phone_marketing-128.png"
        }
       ]
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
#   Displaying ALL CHATBOTS - For Sale                                               #
#                                                                                    #
#************************************************************************************#
def forsale(resolvedQuery):
    print ("Within forsale method")
    speech = "FoodBot is been created by marvin.ai. \nDo you like it?"
    res = {
        "speech": speech,
        "displayText": speech,
        "data" : {
        "facebook" : [
               {
                    "sender_action": "typing_on"
               },
                {
                 "attachment" : {
                   "type" : "template",
                     "payload" : {
                      "template_type" : "generic",
                       "elements" : [ 
                                 {
                                   "title" : "You like this Restaurant Bot Template?",
                                   "image_url" : "https://media.sproutsocial.com/uploads/2017/09/Real-Estate-Marketing-Ideas-1.png",
                                   "subtitle" : "Get customized virtual assistant for your Restaurant today",
                                   "buttons": [{
                                        "type": "web_url",
                                        "url": "https://marvinai.live",
                                        "title": "Buy Template"
                                    },
                                    {
                                        "type": "web_url",
                                        "url": "https://www.facebook.com/marvinai.live",
                                        "title": "Facebook Page"
                                    },
                                    {
                                        "type": "element_share"
                                   }]
                                 },
                                 {
                                   "title" : "Travel Agency Bot Template",
                                   "image_url" : "http://www.sunsail.eu/files/Destinations/Mediteranean/Greece/Athens/thira.jpg",
                                   "subtitle" : "Get customized virtual assistant for your Restaurant today",
                                   "buttons": [{
                                        "type": "web_url",
                                        "url": "https://marvinai.live",
                                        "title": "Buy Template"
                                    },
                                    {
                                        "type": "web_url",
                                        "url": "https://m.me/926146750885580",
                                        "title": "Chat"
                                    },
                                    {
                                        "type": "element_share"
                                   }]
                                 },
                                 {
                                   "title" : "Real Estate Bot Template",
                                   "image_url" : "https://husvild-static.s3.eu-central-1.amazonaws.com/images/files/000/280/915/large/3674bd34e6c1bc42b690adeacfe9c778507f261a?1516032863",
                                   "subtitle" : "Get qualified buyer and seller leads automatically delivered to your inbox!",
                                   "buttons": [{
                                        "type": "web_url",
                                        "url": "https://marvinai.live",
                                        "title": "Buy Template"
                                    },
                                    {
                                        "type": "web_url",
                                        "url": "https://m.me/realestatebotai",
                                        "title": "Chat"
                                    },
                                    {
                                        "type": "element_share"
                                   }]
                                 },
                                 {
                                   "title" : "Personal Assistant Bot",
                                   "image_url" : "http://venturesafrica.com/wp-content/uploads/2015/09/RobotTakeOverBS.jpg",
                                   "subtitle" : "Delete your 36 apps and start using it now. Have one for you today",
                                   "buttons": [{
                                        "type": "web_url",
                                        "url": "https://marvinai.live",
                                        "title": "Buy Template"
                                    },
                                    {
                                        "type": "web_url",
                                        "url": "https://m.me/marvinai.live",
                                        "title": "Chat"
                                    },
                                    {
                                        "type": "element_share"
                                   }]
                                 },
                                 {
                                   "title" : "Gym & Fitness Bot Template",
                                   "image_url" : "https://images-production.global.ssl.fastly.net/uploads/posts/image/139096/chest-exercises-for-men.png?auto=compress&crop=faces,top&fit=crop&h=421&q=55&w=750",
                                   "subtitle" : "Designed for Personal trainers and Fitness centers",
                                   "buttons": [{
                                        "type": "web_url",
                                        "url": "https://marvinai.live",
                                        "title": "Buy Template"
                                    },
                                    {
                                        "type": "web_url",
                                        "url": "https://m.me/566837733658925",
                                        "title": "Chat"
                                    },
                                    {
                                        "type": "element_share"
                                   }]
                                 },
                                 {
                                   "title" : "Coffee Shop Bot Template",
                                   "image_url" : "https://images-na.ssl-images-amazon.com/images/I/71Crz9MYPPL._SY355_.jpg",
                                   "subtitle" : "Your bot can deal with online customers, take orders and many more ",
                                   "buttons": [{
                                        "type": "web_url",
                                        "url": "https://marvinai.live",
                                        "title": "Buy Template"
                                    },
                                    {
                                        "type": "web_url",
                                        "url": "https://m.me/200138490717876",
                                        "title": "Chat"
                                    },
                                    {
                                        "type": "element_share"
                                   }]
                                 },
                                 {
                                   "title" : "VISA Check Bot",
                                   "image_url" : "http://famousdestinations.in/wp-content/uploads/2016/03/howtogetthere.png",
                                   "subtitle" : "One stop solution for all your VISA requirements...Coming Soon!",
                                   "buttons": [{
                                        "type": "web_url",
                                        "url": "https://marvinai.live",
                                        "title": "Visit Website"
                                    },
                                    {
                                        "type": "element_share"
                                   }]
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

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting APPLICATION on port %d" % port)
    context.run(debug=True, port=port, host='0.0.0.0')