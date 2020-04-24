
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render
from django.contrib import auth
import pyrebase
import math
import random
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

    #when the file is created it is initiated with an empty userID
    def registerInitialState(self):
        self.userID = None
        self.idToken = None
    
    #when a user logs in or registers the userID is set
    def set_uid(self, currentUid, userIDToken):
        print("user ID has been set to ", currentUid)
        self.idToken = userIDToken
        self.userID = currentUid

    #returns the stored userID to the views to check if the user is logged in
    def return_uid(self):
        return self.userID
    
    def log_out(self):
        self.idToken = None
        self.userID = None
    
    def return_firebaseID(self):
        return self.idToken
    
    def check_logged_in(self):
        if (self.userID is None):
            return False
        else:
            return True
    
    def delete_user(self):
        print("need to delete")
    
    #This returns the username of the current user that is logged in 
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
    
    # This function returns all arguments in the topic section of the database that have an image listed.
    # These arguments are sent to the home page along with their related image so they can be 
    # displayed and link to the relevant argument
    def return_images(self):
        allTopics = db.child("topics").get()
        topicsDF = pd.DataFrame(allTopics.val())
        topics = topicsDF.to_dict()
        toReturn = {}
        for topic, topicInformation in topics.items():
            if (str(topicInformation['image']) != "nan") :
                print(topicInformation['image'])
                if type(topicInformation['arguments']) is dict :
                    argumentsDict = topicInformation['arguments']
                    argument = random.choice(list(argumentsDict.keys()))
                    toReturn[argument] = topicInformation['image']
        return toReturn

    # loop through argument schema under original key, altering labellings via which ones are being attacked
    def change_labellings(self, originalKey, key, attackingKeys, alternate, selfAttacking):
        print("change labellings called")
        print("attackingKeys ", attackingKeys)
        print("originalKey ", originalKey)
        print("newKey ", key)
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
                #original key is the one being attacked
                print("original key is the one being attacked")

                # updates originalKey to say it is being attacked by the new argument
                db.child('arguments').child(originalKey).child('attackedBy').update(updateAttackedBy)
                #if the new attacking argument is not an "alternate"
                if alternate == False:
                    print("alternate is false")
                    #update original argument as out
                    print("we in the right place tho")
                    #if the new attacking argument is attacking itself then the argument it attacks does not need to change
                    if selfAttacking == True:
                        labellings = {'in': False, 'out': True, 'undec': False}
                        db.child('arguments').child(originalKey).child('labellings').set(labellings)
                #if it is an alternate; alternate == true
                else:
                    print("alternate is true")
                    #here attacking is the originalKey
                    updateAttackedBy = {attacking : "attackedBy"}

                    labellings = {"in": False, "out": False, "undec": True}
                    db.child('arguments').child(originalKey).child('labellings').set(labellings)

                    #this sets the new argument as attacked by original
                    db.child('arguments').child(originalKey).child('argumentSchema').child(key).child('attackedBy').update(updateAttackedBy)

                    updateAttacking = {key : "attacking"}
                    #this sets the original argument as attacking the new argument
                    db.child('arguments').child(originalKey).child('attacking').update(updateAttacking)

                    #now change the labellings for argument B as undecided as long as the new argument does not attack itself
                    if selfAttacking == True:
                        labellings = {'in': False, 'out': False, 'undec': True}
                        db.child('arguments').child(originalKey).child('labellings').set(labellings)

                #returns the next arguments whose labels need to be edited
                argument = db.child('arguments').child(originalKey).child('argumentSchema').child(attacking).get()

            else: #if argument being attacked is not the original
                print("original key is not being attacked")
                # updates argument B to say it is now being attacked by A
                db.child('arguments').child(originalKey).child('argumentSchema').child(attacking).child('attackedBy').update(updateAttackedBy)
                if alternate == False:
                    print("alternate is false")
                    #the current argument just added is the starting point for the algorithm which is now "in"
                    #update argument B as out
                    if selfAttacking == True:
                        labellings = {'in': False, 'out': True, 'undec': False}
                        db.child('arguments').child(originalKey).child('argumentSchema').child(attacking).child('labellings').set(labellings)
                else:
                    #originalKey is not being attacked and alternate is true
                    print("alternate is true")
                    print("original Key", originalKey)
                    print("attacking", attacking)
                    
                    labellings = {"in": False, "out": False, "undec": True}
                    db.child('arguments').child(originalKey).child('argumentSchema').child(attacking).child('labellings').set(labellings)
                    

                    #this sets the new argument A as also attacked by B which it attacks
                    updateAttackedBy = {attacking : "attackedBy"}
                    db.child('arguments').child(originalKey).child('argumentSchema').child(key).child('attackedBy').update(updateAttackedBy)
                    #this sets the argument B as also attacking the new argument A
                    updateAttacking = {attacking : "attacking"}
                    db.child('arguments').child(originalKey).child('argumentSchema').child(attacking).child('attacking').update(updateAttacking)
                    #now change the labellings for argument B as undecised
                    if selfAttacking == True:
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
                    #send through recursively running through the rest of the schema checking which arguments are now in or out
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

            #     #now change the labellings for argument B as undecised
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
        #key is the argument that has just newly been attacked and been made either undecided or out
        #new attacking are the arguments attacked by key
        print ("recursive check")
        for attacking in attackingKeys:
            if attacking == originalKey: 
                path = "db.child('arguments')"
                argument = db.child('arguments').child(originalKey).get()
            else:
                path = "db.child('arguments').child(originalKey).child('argumentSchema')"
                argument = db.child('arguments').child(originalKey).child("argumentSchema").child(attacking).get()
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
                    if element == originalKey:
                        check = db.child('arguments').child(originalKey).child('labellings').get().val()
                    else:
                        check = db.child('arguments').child(originalKey).child('argumentSchema').child(element).child('labellings').get().val()
                    #check = db.child('arguments').child(originalKey).child(element).child(labellings).get().val()
                    print("check", check)
                    #if they are in
                    if check['in'] == True:
                        labellings = {'in': False, 'out': True, 'undec': True}
                        in_argument_not_Found = False
                    #if they are undecided
                    # elif check['undec'] == True:
                    #     labellings = {'in': False, 'out': False, 'undec': True}

            #update the labellings for argument B based on whether a new argument is found
            if attacking == originalKey: 
                db.child('arguments').child(originalKey).child('labellings').set(labellings)
            else:
                db.child('arguments').child(originalKey).child('argumentSchema').child(argument).child('labellings').set(labellings)

            #then recursively run through again
            print("new attacking list before recursive call", newAttacking)
            
            #remove current argument which will not need to be updated
            newAttacking.pop(key, None)
            if newAttacking is not None:
                #recursively runs through from 
                print("after attempt to delete", newAttacking)
                self.change_labellings_recursive(originalKey, attacking, newAttacking, alternate)
                    


    def add_attack(self, data, originalKey, fileRef, image):
        #if self.check_logged_in():
        print("")
        try:
            print("in database add attack", self.userID) 
            data["title"].title()
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
            selfAttacking = data["selfAttack"]
            print("self attack now", selfAttacking)
            print("alternate now", alternate)
            print("end of add attack call")
            print("")
            if selfAttacking == True:
                self.add_self_attack(originalKey, False, key)
            elif alternate == True: #selfAttacking is false but alternate is true
                alternateArgument = {'alternateArgument' : originalArgument}
                db.child('arguments').child(originalKey).child('argumentSchema').child(key).update(alternateArgument)
                alternateArgument = {'alternateArgument' : key}
                db.child('arguments').child(originalKey).update(alternateArgument)

            self.change_labellings(originalKey, key, attacking, alternate, selfAttacking)

            print("OUT OF RECURSION!")
            print(key)
            print (labellings)
            return (data["title"])
        except:
            pass
        #else:
            #return None

    #argument attacks itself and is attacked by itself
    #original key relates to the original argument premise, original is a boolean to see if the 
    #argument which is being updated is itself an original argument (not an attacker)
    def add_self_attack(self, originalKey, original, key):
        attacking = {key : "attacking"}
        attacked = {key : "attackedBy"}
        labellings = {"in": False, "out": True, "undec": False}
        if original:
            db.child('arguments').child(originalKey).child('attacking').update(attacking)
            db.child('arguments').child(originalKey).child('attackedBy').update(attacked)
            db.child('arguments').child(originalKey).child('labellings').set(labellings)
        else:
            db.child('arguments').child(originalKey).child('argumentSchema').child(key).child('attacking').update(attacking)
            db.child('arguments').child(originalKey).child('argumentSchema').child(key).child('attackedBy').update(attacked)
            db.child('arguments').child(originalKey).child('argumentSchema').child(key).child('labellings').set(labellings)


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
                if data['selfAttack'] == True:
                    self.add_self_attack(argumentKey, True, argumentKey)

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
                topicKey = db.child("topics").child(topic).child("arguments").update(authorInfo)
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
            return None
    
    #return a list of the argument types the user can choose from
    def return_argumentTypes(self):
        argumentTypeTitle = db.child("argumentType").get().val()
        data = pd.DataFrame(argumentTypeTitle).to_dict()
        listTypes = {}
        for argumentType in argumentTypeTitle:
            description = data[argumentType]["description"]
            description.pop(0)
            listTypes[argumentType] = description[0]
        return listTypes
    
    #returns the formatting of the argument that can be used to attack an argument
    def return_argumentFormats(self, argumentType):
        try:
            argumentFormat = db.child("argumentType").child(argumentType).child("format").get().val()
            argumentFormat.pop(0)
            return argumentFormat
        except:
            return None



    # def return_argument_content(self, originalKey, key):
    #     if key == originalKey:
    #         argumentContent = db.child("arguments").child(originalKey).get().val()
    #         argumentContent.pop('argumentSchema', None)
    #         content = pd.DataFrame(argumentContent)
    #         return content.to_dict()
    #     else:
    #         argumentContent = db.child("arguments").child(originalKey).child("argumentSchema").child(key).get().val()
    #         content = pd.DataFrame(argumentContent)
    #         return content.to_dict()

    #returns the current user's arguments
    def return_arguments(self):
        print ("called return arguments")
        if self.check_logged_in():
            #print(self.userID) 
            #username = db.child('users').child(self.userID).child('username').get().val()
            #print (username)
            argumentKey = db.child('users').child(self.userID).child('arguments').get().val()
            #print(argumentKey) #OrderedDict([('-M1axBKlwoxMjN_qJnb1', 'author'), ('-M1ayqYaaeJ3zKlSQYrK', 'author')])
            toReturn = {}
            if argumentKey != None:
                for key, value in argumentKey.items():
                    toReturn[key] = db.child('arguments').child(key).get().val()
                    toReturn[key]["originalKey"] = key
                    #print(db.child('arguments').child(key).get().val())
                    #print(db.child('arguments').child(key).get())

            argumentKey = db.child('users').child(self.userID).child('attacks').get().val()
            print(argumentKey) #OrderedDict([('-M1axBKlwoxMjN_qJnb1', 'author'), ('-M1ayqYaaeJ3zKlSQYrK', 'author')])
            if argumentKey != None:
                for key, value in argumentKey.items():
                    print(key, "key is the key of the attacking argument")
                    print(value, "value is the key of the original argument")
                    #key is the key of the attacking argument
                    #value is the key of the original argument
                    toReturn[key] = db.child('arguments').child(value).child('argumentSchema').child(key).get().val()
                    toReturn[key]["originalKey"] = value
                    print(toReturn[key])
            
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
         

    def return_schema2(self, originalKey):
        originalArgument = db.child('arguments').child(originalKey).get().val()
        toReturn = {}
        for (key, value) in originalArgument.items():
            try:
                print("adding children")
                for (newKey, newValue) in value['argumentSchema'].items():
                    data = pd.DataFrame(newValue)
                    valueDict = data.to_dict()
                    print("new key", newKey)
                    toReturn[newKey] = newValue
            except:
                print("no addy childreny")
                pass
            try: 
                value.pop('argumentSchema', None)

            except:
                print("no poppidy")
                pass
            
            toReturn[key] = value
            
            print(type(key)) #string
            print(type(value)) #dict

        
        print("toReturn", toReturn)
        return toReturn

    def return_schema(self, originalKey):
        print("")
        print(originalKey)
        print("")
        originalArgument = db.child('arguments').child(originalKey).get().val()
        try:
            originalArgument.pop('argumentSchema', None)
        except:
            print("Error in returning the schema")

        argument = db.child('arguments').child(originalKey).child('argumentSchema').get()
        data = pd.DataFrame(argument.val())
        inclOriginal = data.to_dict()
        inclOriginal[originalKey] = originalArgument
        print("final", inclOriginal)
        print("")
        return inclOriginal
        
# original OrderedDict([('-M1v_Wu7l6mpOYEha1fU', 
#                                 {'argumentSchema': 
#                                 {'-M2TztWLfZde4ymGK3-B': 
#                                     {'alternate': False, 
#                                     'attackedBy': 
#                                         {'-M2TztWLfZde4ymGK3-B': 'attackedBy'}, 
#                                     'attacking': 
#                                         {'0': '-M1v_Wu7l6mpOYEha1fU', 
#                                         '-M2TztWLfZde4ymGK3-B': 'attacking'}, 
#                                     'content': 'cgfvhjbnk', 
#                                     'fileReference': '', 
#                                     'image': '', 
#                                     'labellings': 
#                                         {'in': False, 'out': True, 'undec': False}, 
#                                     'selfAttack': True, 
#                                     'title': 'testing self attacking', 
#                                     'uidAuthor': 'IdZbjSY6RmeUDhgsLZaPA1bv9OI2', 
#                                     'urlReference': ''}}, 
#                             'argumentType': 'expertOpinion', 
#                             'attackedBy': {'-M2TztWLfZde4ymGK3-B': 'attackedBy'}, 
#                             'content': 'Expert says X and Y which means that this is what I believe and we should all believe.', 
#                             'fileReference': '', 
#                             'image': 'https://www.michiganreview.com/wp-content/uploads/2016/11/75384602.jpg', 
#                             'labellings': {'in': True, 'out': False, 'undec': False}, 
#                             'title': 'Abortion is wrong because expert says so', 
#                             'topic': 'Abortion', 
#                             'uidAuthor': 'IdZbjSY6RmeUDhgsLZaPA1bv9OI2',
#                              'urlReference': 'https://www.michiganreview.com/wp-content/uploads/2016/11/75384602.jpg'}), 
#                              ('-M251jahlPO93-9B4TwS', {'argumentType': 'positionToKnow', 'content': 'cfgvhjbkn;lm;,', 'fileReference': '', 'image': '', 'labellings': {'in': True, 'out': False, 'undec': False}, 'title': 'Dont do it pls and thanks', 'topic': 'Brexit', 'uidAuthor': 'IdZbjSY6RmeUDhgsLZaPA1bv9OI2', 'urlReference': ''})])


    
    def search_arguments(self, topic):
        topic = topic.title()
        data = db.child("topics").child(topic).child("arguments").get().val()
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
        data = db.child("topics").child("arguments").child(topic).get().val()
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

    def returnVotes(self, originalKey, argumentKey):
        try:
            if originalKey == argumentKey:
                print("hi")
                selfAttackCheck = db.child('arguments').child(originalKey).child('selfAttack').get().val()
                print("check1", selfAttackCheck)
                votes = db.child('arguments').child(originalKey).child('votes').get.val()
                print("votes", votes)
            else:
                print("hi2")
                print(originalKey)
                print(argumentKey)
                selfAttackCheck = db.child('arguments').child(originalKey).child('argumentSchema').child(argumentKey).child('selfAttack').get().val()
                print("check2", selfAttackCheck)
                votes = db.child('arguments').child(originalKey).child('argumentSchema').child(argumentKey).child('votes').get().val()
                print("votes", votes)
            return [selfAttackCheck, votes]
        except:
            print ("error")
            return [True, 0]
    
    def vote(self, originalKey, argumentKey):
        print("called")
        votes = self.returnVotes(originalKey, argumentKey)
        try:
            votes += 1
        except:
            votes = 1
        increaseVotes = {"votes": votes}
        if originalKey == argumentKey:
            votes = db.child('arguments').child(originalKey).update(increaseVotes)
        else:
            votes = db.child('arguments').child(originalKey).child('argumentSchema').child(argumentKey).update(increaseVotes)
        self.checkVoting(originalKey, argumentKey, votes)
        return ("Your vote has been logged")

    def checkVoting(self, originalKey, argumentKey, votes):
        print ("check voting")

        #returns the key of the argument which attacks and is attacked by the current argument
        if originalKey == argumentKey:
            alternateArgument = db.child('arguments').child(originalKey).child('argumentSchema').child(argumentKey).child('alternateArgument').get().val()
        else:
            alternateArgument = db.child('arguments').child(originalKey).child('argumentSchema').child(argumentKey).child('alternateArgument').get().val()
        

    
    def return_graph_data(self, originalKey):
        schema = self.return_schema(originalKey)

        nodes = {}
        edges = []
        edgesNames = {}
        try:
            for key, value in schema.items():
                print("HEREEEEEEEEEEEEEEEEEEEEEE", value["labellings"])
                print("HEREEEEEEEEEEEEEEEEEEEEEE", value["labellings"]["in"])
                if value["labellings"]["in"] == True: 
                    labelling = "in"
                elif value["labellings"]["out"] == True: 
                    labelling = "out"
                else: 
                    labelling = "undecided"
                nodes[key] = [value["title"], labelling]
                print("")
                print("current key", key)
                print("")
                try:
                    attacking = value["attacking"]
                    print("attacking", attacking) #attacking {'-M1v_Wu7l6mpOYEha1fU': 'attacking', '-M2TztWLfZde4ymGK3-B': 'attacking'}
                    name = 1
                    for aKey, aValue in attacking.items():
                        print("attacking from (", key, "to ,", aKey, ")")
                        if key not in edgesNames and aKey not in edgesNames:
                            edgesNames[key] = name
                            name += 1
                            edgesNames[aKey] = name
                            name+=1
                        elif (edgesNames[key]) == None:
                            edgesNames[key] = name
                            name += 1
                        elif (edgesNames[aKey]) == None:
                            edgesNames[aKey] = name
                            name += 1
                        edges.append((edgesNames[key], edgesNames[aKey]))
                    print("edges", edges)
                    print("edgesNames", edgesNames.items())
                except:
                    pass
            for key, value in nodes.items():
                nodes[key] = {"title": value[0], "number": edgesNames[key], "labelling": value[1]}
        except:
            pass
        return [nodes, edges]
        








