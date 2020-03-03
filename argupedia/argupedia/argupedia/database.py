
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render
from django.contrib import auth
import pyrebase
import pandas as pd 
import time

config = {
    'apiKey': "AIzaSyDTNvuZOGHUuuG1PTkBZOW64xdb9Ry5TWE",
    'authDomain': "argupedia-d2e12.firebaseapp.com",
    'databaseURL': "https://argupedia-d2e12.firebaseio.com",
    'projectId': "argupedia-d2e12",
    'storageBucket': "argupedia-d2e12.appspot.com",
    'messagingSenderId': "356627337302",
    'appId': "1:356627337302:web:db1808484ddac94be2ebf7",
    'measurementId': "G-8JS80GCSHV"
}

firebase = pyrebase.initialize_app(config)
authF = firebase.auth()
db = firebase.database()
storage = firebase.storage()


class Database:
    def __init__(self):
        self.registerInitialState()

    def registerInitialState(self):
        self.userID = None
    
    def set_uid(self, currentUid):
        print("user ID has been set to ", currentUid)
        self.userID = currentUid

    def return_uid(self):
        return self.userID
    
    def log_out(self):
        self.userID = None
    
    def check_logged_in(self):
        if (self.userID is None):
            return False
        else:
            return True

    def return_username(self):
        #return self.userID
        print(self.userID)
        if self.check_logged_in():
            #https://argupedia-d2e12.firebaseio.com/users/n3mWvrmhtehe7oC2FEQbh7q9dlpg2
            try:
                username = db.child('users').child(self.userID).child('username').get().val()
                return (username)
            except:
                print("error fetching username")
                return None
        else: 
            return None
    
    def add_argument(self, data, fileRef, image):
        if self.check_logged_in():
            try:
                print("tried to add")
                print(self.userID) 
                data["title"].title()
                data["topic"].title()
                argumentKey = db.child("users").child(self.userID).child("arguments").push(data)
                print("argument added")
                key = argumentKey['name']
                topic = data["topic"]
                topicKey = db.child("topics").child(topic).push(key)
                print("topic added", topicKey['name'])
                author = {'uidAuthor': self.userID}
                db.child("topics").child(topic).child(topicKey['name']).set(author)
                #maybe should be this:       db.child("topics").child("Coronavirus").push(author)

                # print ("ARGUMENT KEY", argumentKey['name'])
                # test = storage.child("images").child(key).put(image)
                # print("test", test)
                # print ("image ok")
                # storage.child("files").child(key).child(self.userID).put(fileRef)
            except:
                pass
        else:
            return None
    
    def return_arguments(self):
        print ("called me")
        if self.check_logged_in():
            print(self.userID) 
            username = db.child('users').child(self.userID).child('username').get().val()
            print (username)
            argument = db.child('users').child(self.userID).child('arguments').get()
            data = pd.DataFrame(argument.val())
            print("dictionary", data.to_dict())
            #dictionary {'-M1GrB2f4w35ZwQVMYUR': {'content': 'have ALL the babies. ALL OF THEM.', 'fileReference': '', 'title': 'abortion sucks bitched', 'topic': 'abortion', 'urlReference': ''}, '-M1Gzr2YVAaF9dmuzF_7': {'content': 'computer says no', 'fileReference': nan, 'title': 'No Brexit for Britain', 'topic': 'Brexit', 'urlReference': ''}}
            return data.to_dict()
            #print (argument)
            # data                             -M1GrB2f4w35ZwQVMYUR   -M1Gzr2YVAaF9dmuzF_7
            # content        have ALL the babies. ALL OF THEM.       computer says no
            # fileReference                                                       NaN
            # title                     abortion sucks bitched  No Brexit for Britain
            # topic                                   abortion                 Brexit
            #image = storage.child("images").child('-M1Gzr2YVAaF9dmuzF_7').get('argupediaBrexit.jpg')
            #print ("image?")
            #return self.userID
        else: 
            return None
    
    def haha(self, topic):
        try:
            print ("topic", topic.title())
        except:
            print("no title")
        try:
            print ("topic", str(topic).title() )
        except:
            print("no string title")
        try:
            print ("topic", str(topic).capwords() )
        except:
            print("no string capwords")
    def search_arguments(self, topic):
        #print ("topic", topic)
        topic = topic.title()
        #data = db.child("topics").child(topic).get()
        data = db.child("topics").child(topic).get().val()
        if data is not None:
            try:
                dataInDict = {}
                for key, value in data.items():
                    print("key", key) #-M1GrB2f4w35ZwQVMYUR
                    print("value", value) #value {'uidAuthor': 'OjTpCCeALlcGCluPNoWWSj6bS532'}
                    print("value[uidAuthor]", value["uidAuthor"]) #value[uidAuthor] OjTpCCeALlcGCluPNoWWSj6bS532
                    authorID = value["uidAuthor"]
                    test = db.child("users").child(authorID).child("arguments").child(key).get().val()
                    print(test)
                    print(db.child("users").child(authorID).child("arguments").child(key).get())
                    dataInDict[key] = test
                    return dataInDict
            except:
                return None
        else:
            return None



