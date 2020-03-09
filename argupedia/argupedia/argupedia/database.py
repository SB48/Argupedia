
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render
from django.contrib import auth
import pyrebase
import numpy as np
import pandas as pd 

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
    
    
    # def add_criticalQ(self, data):
    #     if self.check_logged_in():
    #         try:
                
    
    # def add_attack(self, data):
    #     if self.check_logged_in():
    #         try:

    # loop through argument schema under original key, altering labellings via which ones are being attacked
    def change_labellings(self, originalKey, key, attackingKeys, alternate):
        print("change labellings called")
        print("attackingKeys ", attackingKeys)
        print("originalKey ", originalKey)
        #argument being attacked = B
        #new argument attacking = A
        #arguments being attacked by B = C
        # A --> B --> C or A <--> B --> C
        
        #returns the argument(s) that the current argument is attacking
        print("")
        for attacking in attackingKeys:
            print("attacking now", attacking)
            #updates argument B to say it is now being attacked by A
            updateAttackedBy = {key : "attackedBy"} 
            
            #if the first argument is the one being attacked
            if originalKey == attacking: 
                print("original key is the one being attacked")

                # updates argument B to say it is now being attacked by A
                db.child('arguments').child(originalKey).child('attackedBy').update(updateAttackedBy)
                if alternate == False:
                    print("alternate is false")
                    #update original argument as out
                    print("we in the right place tho")
                    labellings = {'in': False, 'out': True, 'undec': False}
                    db.child('arguments').child(originalKey).child('labellings').set(labellings)
                else:
                    print("alternate is true")
                    #this sets the new argument A as also attacked by B which it attacks
                    updateAttackedBy = {attacking : "attackedBy"}
                    db.child('arguments').child(originalKey).child('attackedBy').update(updateAttackedBy)

                    #now change the labellings for argument B as undecised
                    labellings = {'in': False, 'out': False, 'undec': True}
                    db.child('arguments').child(originalKey).child('labellings').set(labellings)

                #returns the next arguments whose labels need to be edited
                argument = db.child('arguments').child(originalKey).child('argumentSchema').child(attacking).get()

            else: #if argument being attacked is not the original
                print("why tho")
                # updates argument B to say it is now being attacked by A
                db.child('arguments').child(originalKey).child('argumentSchema').child(attacking).child('attackedBy').update(updateAttackedBy)
                if alternate == False:
                    #the current argument just added is the starting point for the algorithm which is now "in"
                    #update argument B as out
                    labellings = {'in': False, 'out': True, 'undec': False}
                    db.child('arguments').child(originalKey).child('argumentSchema').child(attacking).child('labellings').set(labellings)
                else:
                    #this sets the new argument A as also attacked by B which it attacks
                    updateAttackedBy = {attacking : "attackedBy"}
                    db.child('arguments').child(originalKey).child(key).child('attackedBy').update(updateAttackedBy)
                    #now change the labellings for argument B as undecises
                    labellings = {'in': False, 'out': False, 'undec': True}
                    db.child('arguments').child(originalKey).child('argumentSchema').child(attacking).child('labellings').set(labellings)
                #returns the next arguments whose labels need to be edited
                argument = db.child('arguments').child(originalKey).child('argumentSchema').child(attacking).get()
                
            try: #this could be empty if the argument (B) which is now being attacked is itself not attacking any arguments
                #this should be a data frame of the information about argument B
                attacked = pd.DataFrame(argument.val())
                attacked.to_dict()
                print("argument B attacks: ",attacked)
                #returns the arguments that the argument B itself attacks
                newAttacking =  attacked['attacking']
                print ("new attacking", newAttacking)
                print("new attacking list before recursive call", newAttacking)
                #remove current argument which will not need to be uodated
                newAttacking.pop(key, None)
                if newAttacking is not None:
                    #recursively runs through from 
                    print("after attempt to delete", newAttacking)
                    self.change_labellings_recursive(originalKey, attacking, newAttacking, alternate)
            except:
                pass

            # if alternate is False:
            #     #the current argument just added is the starting point for the algorithm which is now "in"
            #     #update argument B as out
            #     labellings = {'in': False, 'out': True, 'undec': False}
            #     db.child('arguments').child(originalKey).child(attacking).child('labellings').set(labellings)

            # else:
            #     #this sets the new argument A as also attacked by B which it attacls
            #     updateAttackedBy = {attacking : "attackedBy"}
            #     db.child('arguments').child(originalKey).child(key).child('attackedBy').update(updateAttackedBy)

            #     #now change the labellings for argument B as undecises
            #     labellings = {'in': False, 'out': False, 'undec': True}
            #     db.child('arguments').child(originalKey).child(attacking).child('labellings').set(labellings)
                #check if this argument (B) has any other attackers which are "in", if it does then B is "out" and the current argument (A) is in
                #otherwise if it has not attackers which are in then set it as well as undecided. Any arguments it attacks are
                #no longer out. Every argument that is attacked by an argument from this chain is now no longer out unless they have an attacker that is in
                
            # this will check the rest of the arguments in the schema with the new information and 
            # recursively check if they have an attacker that is in
            #so if there are two arguments which are being attacked by new argument A then this will run twice for both of them

        
    
    #if an argument is an alternate this runs through the schema checking if the arguments have an attacker which is in
    def change_labellings_recursive(self, originalKey, key, attackingKeys, alternate):
        print ("recursive check")
        for attacking in attackingKeys:
            if attacking == originalKey: 
                path = "db.child('arguments')"
                argument = db.child('arguments').child(originalKey).get()
            else:
                path = "db.child('arguments').child(originalKey)"
                argument = db.child('arguments').child(originalKey).child(attacking).get()
            #this should be a data frame of the information about argument B
            attacked = pd.DataFrame(argument.val())
            attacked.to_dict()
            print(attacked)
            #returns the arguments that the argument B itself attacks
            newAttacking =  attacked['attacking']
            #returns the arguments that attack the current argument
            newAttacked = attacked['attackedBy']
            print ("new attacking", newAttacking)
            print ("new attacked", newAttacked)
            in_argument_not_Found = True
            labellings = {'in': True, 'out': False, 'undec': False}
            for element in newAttacked:
                #run through all arguments attacking the arguments in attacking Keys (B) and check if they are in or out
                if in_argument_not_Found == True:
                    checkLabellingsPath = path + ".child(element).child(labellings).get().val()"
                    #check = db.child('arguments').child(originalKey).child(element).child(labellings).get().val()
                    check = exec(checkLabellingsPath)
                    print("check", check)
                    #if they are in
                    if check['in'] == True:
                        labellings = {'in': False, 'out': True, 'undec': True}
                        in_argument_not_Found = False
                    #if they are undecided
                    elif check['undec'] == True:
                        labellings = {'in': False, 'out': False, 'undec': True}
            #update the labellings for argument B based on whether a new argument is found
            db.child('arguments').child(originalKey).child(argument).child('labellings').set(labellings)
            #then recursively run through again
            print("new attacking list before recursive call", newAttacking)
            
            #remove current argument which will not need to be uodated
            newAttacking.pop(key, None)
            if newAttacking is not None:
                #recursively runs through from 
                print("after attempt to delete", newAttacking)
                self.change_labellings_recursive(originalKey, attacking, newAttacking, alternate)
                    


    def add_attack(self, data, originalKey, fileRef, image):
        #if self.check_logged_in():
        print("")
        try:
            print("in databse add attack", self.userID) 
            data["title"].title()
            data["topic"].title()
            attacking = data["attacking"]
            data["uidAuthor"] = self.userID
            
            print("data[alternate] ",data["alternate"])
            if data["alternate"] is False:
                #the current argument just added is the starting point for the algorithm which is now "in"
                labellings = {"in": True, "out": False, "undec": False}
            else:
                #if the argument is an alternate then it is undecided, not in
                labellings = {"in": False, "out": False, "undec": True}
            
            data["labellings"] = labellings
            print ("labellings", labellings)

            print(data)
            print("original Key", originalKey)
            argumentKey = db.child("arguments").child(originalKey).child("argumentSchema").push(data)
            key = argumentKey['name']
            #recursively change the labellings of the arguments this argument attacks
            userData = {key : originalKey}
            db.child("users").child(self.userID).child("attacks").update(userData)
            alternate = data["alternate"]
            print("alternate now", alternate)
            print("end of add attack call")
            print("")
            self.change_labellings(originalKey, key, attacking, alternate)

            print("OUT OF RECURSION!")
            print(key)
            print (labellings)
            return (data["title"])
        except:
            pass
        #else:
            #return None

    def add_argument(self, data, fileRef, image):
        if self.check_logged_in():
            try:
                print("tried to add")
                print(self.userID) 
                data["title"].title()
                data["topic"].title()
                data["uidAuthor"] = self.userID
                labellings = {"in": True, "out": False, "undec": False}
                data["labellings"] = labellings

                print(data)

                argumentKey = db.child("arguments").push(data)
                #db.child('arguments').child(argumentKey['name']).set(data)
                #argumentKey = db.child("users").child(self.userID).child("arguments").push(data)
                key = argumentKey['name']
                print(key)
                print (labellings)
                #db.child("arguments").child(key).update(labellings)
                userData = {key : "author"}
                db.child("users").child(self.userID).child("arguments").update(userData)
                topic = data["topic"]
                authorInfo = {key : self.userID}
                topicKey = db.child("topics").child(topic).update(authorInfo)
                return (data["title"])
            except:
                pass
        else:
            return None
    
    #returns the list of critical questions that can be used to attack an argument
    def return_criticalQuestions(self, argumentKey):
        try:
            print (argumentKey)
            argumentType = db.child("arguments").child(argumentKey).child("argumentType").get().val()
            print (argumentType)
            criticalQuestions = db.child("argumentType").child(argumentType).child("criticalQuestions").get().val()
            criticalQuestions.pop(0)
            return criticalQuestions
        except:
            print("uh oh critical questions")
            return None

    #returns the current user's arguments
    def return_arguments(self):
        print ("called return arguments")
        if self.check_logged_in():
            #print(self.userID) 
            #username = db.child('users').child(self.userID).child('username').get().val()
            #print (username)
            argumentKey = db.child('users').child(self.userID).child('arguments').get().val()
            print(argumentKey) #OrderedDict([('-M1axBKlwoxMjN_qJnb1', 'author'), ('-M1ayqYaaeJ3zKlSQYrK', 'author')])
            toReturn = {}
            for key, value in argumentKey.items():
                toReturn[key] = db.child('arguments').child(key).get().val()
                print(db.child('arguments').child(key).get().val())
                #print(db.child('arguments').child(key).get())
            argumentKey = db.child('users').child(self.userID).child('attacks').get().val()
            print(argumentKey) #OrderedDict([('-M1axBKlwoxMjN_qJnb1', 'author'), ('-M1ayqYaaeJ3zKlSQYrK', 'author')])
            for key, value in argumentKey.items():
                toReturn[key] = db.child('arguments').child(value).get().val()
                print(db.child('arguments').child(key).get().val())
                #print(db.child('arguments').child(key).get())
            return toReturn

            #argument = db.child('arguments').child(argumentKey).get()
            #print("argument", argument)
            #print("argument val", argument.val())
            #return argument.val()
            #data = pd.DataFrame(argument.val())
            #print("dictionary", data.to_dict())
            #dictionary {'-M1GrB2f4w35ZwQVMYUR': {'content': 'have ALL the babies. ALL OF THEM.', 'fileReference': '', 'title': 'abortion sucks bitched', 'topic': 'abortion', 'urlReference': ''}, '-M1Gzr2YVAaF9dmuzF_7': {'content': 'computer says no', 'fileReference': nan, 'title': 'No Brexit for Britain', 'topic': 'Brexit', 'urlReference': ''}}
            #return data.to_dict()
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
    
    def return_argumentsOG(self):
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
         

    def return_schema(self, key):
        argument = db.child('arguments').child(key).child('argumentSchema').get()
        print(argument)
        data = pd.DataFrame(argument.val())
        print("oh my days fuck me seriously????????", data.to_dict())
        data.to_dict()

        return data.to_dict()
    
    def search_arguments(self, topic):
        topic = topic.title()
        data = db.child("topics").child(topic).get().val()
        if data is not None:
            try:
                dataInDict = {}
                for key, value in data.items():
                    print("key", key) #-M1GrB2f4w35ZwQVMYUR
                    print("value", value) #value {'uidAuthor': 'OjTpCCeALlcGCluPNoWWSj6bS532'}
                    argumentInfo = db.child("arguments").child(key).get().val()
                    dataInDict[key] = argumentInfo
                    return dataInDict
            except:
                return None
        else:
            return None


    def search_argumentsOG(self, topic):
        #print ("topic", topic)
        topic = topic.title()
        #data = db.child("topics").child(topic).get()
        data = db.child("topics").child(topic).get().val()
        print ("data", data)
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






