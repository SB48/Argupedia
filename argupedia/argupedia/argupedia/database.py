
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
        pass
        #function to delete to be implemented
    
    #This returns the username of the current user that is logged in 
    def return_username(self):
        #return self.userID
        if self.check_logged_in():
            #reference https://argupedia-d2e12.firebaseio.com/users/n3mWvrmhtehe7oC2FEQbh7q9dlpg2
            try:
                username = db.child('users').child(self.userID).child('username').get().val()
                return (username)
            except:
                print("Error fetching username")
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
                if type(topicInformation['arguments']) is dict :
                    argumentsDict = topicInformation['arguments']
                    # This ensures that an image only links to one argument. Even if the topic has many arguments.
                    # Currently the choice of argument to show is random but this could be changed by altering this line
                    argument = random.choice(list(argumentsDict.keys()))

                    toReturn[argument] = topicInformation['image']
        return toReturn

    # loop through argument schema under original key, altering labellings via which ones are being attacked
    # originalKey is the key to the schema
    # key is the new argument that has just been created
    # attackingKeys are all the arguments that the new argument, that has just been created, attacks (could be one or multiple)
    # alternate and selfAttacking are booleans
    def change_labellings(self, originalKey, key, attackingKeys, alternate, selfAttacking):
        # in order to understand the code in this function the following names / keys will be used
        # argument being attacked = B  - this could be the original argument for the schema but not necessarily
        # new argument attacking = A  - this is the argument that has just been added by the user
        # arguments being attacked by B = C
        # A --> B --> C or A <--> B --> C
        
        #returns the argument(s) that the current argument is attacking
        for attacking in attackingKeys:
            # information to updates argument B with to say it is now being attacked by A
            updateAttackedBy = {key : "attackedBy"} 
            
            #if the first argument / originalKey is the one being attacked - original argument is argument B
            if originalKey == attacking: 

                # updates originalKey to say it is being attacked by the new argument
                db.child('arguments').child(originalKey).child('attackedBy').update(updateAttackedBy)
                
                #if the new attacking argument is not an "alternate"
                if alternate == False:
                    #if the new attacking argument is attacking itself then the argument it attacks does not need to change
                    if selfAttacking == False:
                        # as long as the new argument A is not self attacking or alternate then the arguments B which A attacks will always be out
                        # as they now have an attacker which is in
                        labellings = {'in': False, 'out': True, 'undec': False}
                        db.child('arguments').child(originalKey).child('labellings').set(labellings)

                #if A is an alternate to B
                else:
                    #argument B is still the originalKey
                    updateAttackedBy = {attacking : "attackedBy"}

                    #this sets the new argument as attacked by original
                    db.child('arguments').child(originalKey).child('argumentSchema').child(key).child('attackedBy').update(updateAttackedBy)

                    #this sets the original argument as attacking the new argument
                    updateAttacking = {key : "attacking"}
                    db.child('arguments').child(originalKey).child('attacking').update(updateAttacking)

                    #now change the labellings for argument B as undecided as long as the new argument does not attack itself
                    if selfAttacking == False:
                        labellings = {'in': False, 'out': False, 'undec': True}
                        db.child('arguments').child(originalKey).child('labellings').set(labellings)

                #returns the next arguments whose labels need to be edited
                argument = db.child('arguments').child(originalKey).child('argumentSchema').child(attacking).get()

            else: #if argument being attacked is not the original

                # updates argument B to say it is now being attacked by A
                db.child('arguments').child(originalKey).child('argumentSchema').child(attacking).child('attackedBy').update(updateAttackedBy)

                if alternate == False:
                    #if the new attacking argument is attacking itself then the argument it attacks does not need to change
                    if selfAttacking == False:
                        # as long as the new argument A is not self attacking or alternate then the arguments B which A attacks will always be out
                        # as they now have an attacker which is in
                        labellings = {'in': False, 'out': True, 'undec': False}
                        db.child('arguments').child(originalKey).child('argumentSchema').child(attacking).child('labellings').set(labellings)

                #originalKey is not being attacked and alternate is true
                else: 

                    #this sets the new argument A as also attacked by B which it attacks
                    updateAttackedBy = {attacking : "attackedBy"}
                    db.child('arguments').child(originalKey).child('argumentSchema').child(key).child('attackedBy').update(updateAttackedBy)
                    
                    #this sets the argument B as also attacking the new argument A
                    updateAttacking = {key : "attacking"}
                    db.child('arguments').child(originalKey).child('argumentSchema').child(attacking).child('attacking').update(updateAttacking)
                    
                    #updates argument B as undecided
                    if selfAttacking == False:
                        labellings = {'in': False, 'out': False, 'undec': True}
                        db.child('arguments').child(originalKey).child('argumentSchema').child(attacking).child('labellings').set(labellings)
            
                
            try: #this could be empty if the argument (B) which is now being attacked is itself not attacking any arguments
                #this should be a data frame of the information about argument B
            
                #returns the next arguments whose labels need to be edited
                if originalKey == attacking:
                    argument = db.child('arguments').child(originalKey).child('attacking').get().val()
                else: 
                    argument = db.child('arguments').child(originalKey).child('argumentSchema').child(attacking).child('attacking').get().val()

                try:
                    newAttacking =  argument.keys()
                except:
                    multipleKeys = pd.DataFrame(argument).to_dict()
                    newAttacking = multipleKeys.keys()

                if newAttacking is not None:
                    #send through recursively running through the rest of the schema checking which arguments are now in or out
                    self.change_labellings_recursive(originalKey, list(newAttacking), {})
            except:
                print("Error returning list of new arguments being attacked")
                pass
                
    # This function will check the rest of the arguments in the schema with the new information and 
    # recursively check if they have an attacker that is in
    # so if there are two arguments which are being attacked by new argument A then this will run twice for both of them
    def change_labellings_recursive(self, originalKey, attackingKeys, alternate):
        #dictionary of the next arguments to check
        nextRecursionKeys = {}
        #ensure that looking at alternate arguemnts does not lead to infinite recursion
        alternateCheck = False
        #key is the argument that has just newly been attacked and been made either undecided or out
        #new attacking - this will be named C -  are the arguments attacked by key
        for attacking in attackingKeys:
            # the next step when check C's labellings is to look at its attackers
            if attacking == originalKey: 
                #below is potential improvement for code - currently had bugs but could be implemented to impove code
                #path = "db.child('arguments')"
                #These are the arguments that need to be checked to determine C's labellings - they are C's attackers
                attackedKeys = db.child('arguments').child(originalKey).child('attackedBy').get().val()
                #These are the arguments that C attacks which will be checked in the next iteration of this function
                nextRecursion = db.child('arguments').child(originalKey).child('attacking').get().val()
                #in order to prevent infinite recursion, there must be a check to ensure the alternates are not repeated
                try:
                    alternateCheck = db.child('arguments').child(originalKey).child('alternate').get().val()
                except:
                    pass
            else:
                #path = "db.child('arguments').child(originalKey).child('argumentSchema')"
                #These are the arguments that need to be checked to determine C's labellings - they are C's attackers
                attackedKeys = db.child('arguments').child(originalKey).child("argumentSchema").child(attacking).child('attackedBy').get().val()
                #These are the arguments that C attacks which will be checked in the next iteration of this function
                nextRecursion = db.child('arguments').child(originalKey).child('argumentSchema').child(attacking).child('attacking').get().val()
                #in order to prevent infinite recursion, there must be a check to ensure the alternates are not repeated
                try:
                    alternateCheck = db.child('arguments').child(originalKey).child("argumentSchema").child(attacking).child('alternate').get().val()
                except:
                    pass
            #add to list of new arguments to check the labellings of
            try:
                for item, value in nextRecursion.items():
                    nextRecursionKeys[item] = 'checkLabel'
            except:
                pass

            newAttacked = list(attackedKeys.keys())

            in_argument_found = False
            labellings = {'in': True, 'out': False, 'undec': False}
            count = 0
            count_out_arguments = 0
            count_undec_arguments = 0
            selfAttack = False
            for element in newAttacked:
                count += 1
                #run through all arguments attacking the arguments in attacking Keys (B) and check if they are in or out
                #finding an in argument is the deciding factor for when the algorithm should stop running
                #even if an undecided attacker is found
                if in_argument_found == False and selfAttack == False: 
                    if element == originalKey:
                        check = db.child('arguments').child(originalKey).child('labellings').get().val()
                    else:
                        check = db.child('arguments').child(originalKey).child('argumentSchema').child(element).child('labellings').get().val()
                    if check['in'] == True:
                        labellings = {'in': False, 'out': True, 'undec': False}
                        in_argument_found = True
                    if check['out'] == True:
                        count_out_arguments += 1
                    if check['undec'] == True:
                        count_undec_arguments += 1

            #if the argument is self attacking then it should not have its labellings changed as it will always be out
            try:
                for key, value in nextRecursionKeys.items():
                    if key == originalKey:
                        selfAttack = db.child('arguments').child(originalKey).child('selfAttack').get().val()
                    else:
                        selfAttack = db.child('arguments').child(originalKey).child('argumentSchema').child(key).child('selfAttack').get().val()
                if selfAttack == True:
                    nextRecursionKeys.pop(key)
            except:
                print('Error in checking if the argument is self attacking in the recursive change labellings algorithm')
                pass
            
            #if all arguments that attack this one are out or there is no in argument found then change this argument to 'in'
            #this allows the possibility of it remaining as 'undecided'
            if in_argument_found == False and selfAttack == False:
                #all arguments attacking this argument (C) are out therefore this one is in
                if count_out_arguments == count:
                    labellings = {'in': True, 'out': False, 'undec': False}
                #if every argument attacking this one (C) is undecided then this argument is undecided
                elif count_undec_arguments == count:
                    labellings = {'in': False, 'out': False, 'undec': True}
            elif in_argument_found == True: #if an in attacker is found then this argument is out
                labellings = {'in': False, 'out': True, 'undec': False}

            if attacking == originalKey: 
                db.child('arguments').child(originalKey).child('labellings').set(labellings)
            else:
                db.child('arguments').child(originalKey).child('argumentSchema').child(attacking).child('labellings').set(labellings)
            
        try:
            for key, value in alternate.items():
                # needs to be checked more than once as otherwise the labellings
                # will be dependent on which alternate argument is found first
                if value < 2:
                    value +=1
                else:
                    nextRecursionKeys.pop(element)
        except:
            pass

        if bool(nextRecursionKeys): 
            recursiveNewAttacking = list(nextRecursionKeys.keys())
            try:
                if alternateCheck == True:
                    #add to list of alternate arguments to limit checking
                    alternate[attacking] = 0
            except:
                self.change_labellings_recursive(originalKey, recursiveNewAttacking, alternate)
                    

    # When a user adds an attacking argument, the algorithm begins here.
    def add_attack(self, data, originalKey, fileRef, image, attacking):
        try:
            data["title"].title()
            data["uidAuthor"] = self.userID
            
            if data["alternate"] is False:
                #the current argument just added is the starting point for the algorithm which is now "in"
                labellings = {"in": True, "out": False, "undec": False}
            else:
                #if the argument is an alternate then it is undecided, not in
                labellings = {"in": False, "out": False, "undec": True}
            
            data["labellings"] = labellings
            #push the new argument's data into the database
            argumentKey = db.child("arguments").child(originalKey).child("argumentSchema").push(data)
            #store the id of this argument
            key = argumentKey['name']
            #updates the  user table with the argument they now have created
            userData = {key : originalKey}
            db.child("users").child(self.userID).child("attacks").update(userData)
            alternate = data["alternate"]
            selfAttacking = data["selfAttack"]

            if selfAttacking == True:
                self.add_self_attack(originalKey, False, key)
            elif alternate == True: #selfAttacking is false but alternate is true
                self.alternate_update(originalKey, key, attacking)

            self.change_labellings(originalKey, key, attacking, alternate, selfAttacking)

            return (data["title"])
        except:
            pass


    # In the case of adding an attacking argument which is an alternate to the argument it attacks, this function is called
    # This stores information in each argument a link to its alternate.
    # This will assist in the comparing of the votes
    def alternate_update(self, originalKey, key, attackingKeys):
        alternateCheck = {'alternate': True}
        for attacking in attackingKeys:
            if originalKey == attacking:
                try:   
                    alternateArgument = {'alternateArgument' : originalKey}
                    alternateArgumentNew = {'alternateArgument' : key}
                    db.child('arguments').child(originalKey).update(alternateArgumentNew)
                    db.child('arguments').child(originalKey).update(alternateCheck)
                except:
                    print('Error alternate original argument')
                    pass
            else: 
                try:
                    alternateArgument = {'alternateArgument' : attacking}
                    alternateArgumentNew = {'alternateArgument' : key}
                    db.child('arguments').child(originalKey).child('argumentSchema').child(attacking).update(alternateArgumentNew)
                    db.child('arguments').child(originalKey).child('argumentSchema').child(attacking).update(alternateCheck)
                except:
                    print('Error alternate secondary argument')
            db.child('arguments').child(originalKey).child('argumentSchema').child(key).update(alternateArgument)
            db.child('arguments').child(originalKey).child('argumentSchema').child(key).update(alternateCheck)

    #argument attacks itself and is attacked by itself
    #original key relates to the original argument premise, original is a boolean to see if the 
    #argument which is being updated is itself an original argument (not an attacker)
    def add_self_attack(self, originalKey, original, key):
        attacking = {key : "attacking"}
        attacked = {key : "attackedBy"}
        labellings = {"in": False, "out": True, "undec": False}
        #if the new argument is not an attack
        if original:
            db.child('arguments').child(originalKey).child('attacking').update(attacking)
            db.child('arguments').child(originalKey).child('attackedBy').update(attacked)
            db.child('arguments').child(originalKey).child('labellings').set(labellings)
        #if the new argument is an attack on another
        else:
            db.child('arguments').child(originalKey).child('argumentSchema').child(key).child('attacking').update(attacking)
            db.child('arguments').child(originalKey).child('argumentSchema').child(key).child('attackedBy').update(attacked)
            db.child('arguments').child(originalKey).child('argumentSchema').child(key).child('labellings').set(labellings)

    # This function adds an argument to the database - this is different to when a user adds an attacking argument
    def add_argument(self, data, fileRef, image):
        if self.check_logged_in():
            try: 
                data["title"].title()
                data["topic"].title()
                data["uidAuthor"] = self.userID
                labellings = {"in": True, "out": False, "undec": False}
                data["labellings"] = labellings

                # Adds the argument to the 'arguments' section of the database
                argumentKey = db.child("arguments").push(data)

                if data['selfAttack'] == True:
                    self.add_self_attack(argumentKey, True, argumentKey)

                key = argumentKey['name']

                # Adds the argument to the 'users' section of the database 
                userData = {key : "author"}
                db.child("users").child(self.userID).child("arguments").update(userData)

                # Adds a new topic to the database making the arguments searchable
                topic = data["topic"]
                authorInfo = {key : self.userID}
                topicKey = db.child("topics").child(topic).child("arguments").update(authorInfo)
                return (data["title"])
            except:
                pass
        else:
            return None
    
    #returns the list of critical questions that can be used to attack an argument
    def return_criticalQuestions(self, argumentKey, originalKey):
        try:
            if originalKey == argumentKey:
                argumentType = db.child("arguments").child(argumentKey).child("argumentType").get().val()
            else:
                argumentType = db.child("arguments").child(originalKey).child('argumentSchema').child(argumentKey).child("argumentType").get().val()
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


    #returns the current user's arguments
    def return_arguments(self):
        if self.check_logged_in():
            argumentKey = db.child('users').child(self.userID).child('arguments').get().val()
            toReturn = {}
            if argumentKey != None:
                for key, value in argumentKey.items():
                    toReturn[key] = db.child('arguments').child(key).get().val()
                    toReturn[key]["originalKey"] = key

            argumentKey = db.child('users').child(self.userID).child('attacks').get().val()
            if argumentKey != None:
                for key, value in argumentKey.items():
                    #key is the key of the attacking argument
                    #value is the key of the original argument
                    toReturn[key] = db.child('arguments').child(value).child('argumentSchema').child(key).get().val()
                    toReturn[key]["originalKey"] = value
            
            return toReturn
        else: 
            return None
         
    # Return the entire schema of an argument i.e. all attacking arguments within one debate
    def return_schema(self, originalKey):
        originalArgument = db.child('arguments').child(originalKey).get().val()
        try:
            originalArgument.pop('argumentSchema', None)
        except:
            print("Error in returning the schema")
            pass

        argument = db.child('arguments').child(originalKey).child('argumentSchema').get()
        data = pd.DataFrame(argument.val())
        inclOriginal = data.to_dict()
        inclOriginal[originalKey] = originalArgument
        return inclOriginal
        
    # Search through the arguments in the database by a kew word / topic
    def search_arguments(self, topic):
        topic = topic.title()
        data = db.child("topics").child(topic).child("arguments").get().val()
        if data is not None:
            try:
                dataInDict = {}
                for key, value in data.items():
                    argumentInfo = db.child("arguments").child(key).get().val()
                    dataInDict[key] = argumentInfo
                    return dataInDict
            except:
                return None
        else:
            return None

    # Return the number of votes for an undecided argument
    def returnVotes(self, originalKey, argumentKey):
        try:
            if originalKey == argumentKey:
                # Check that the argument is not self attacking
                selfAttackCheck = db.child('arguments').child(originalKey).child('selfAttack').get().val()
                if selfAttackCheck == None:
                    selfAttackCheck = False
                try:
                    
                    votes = db.child('arguments').child(originalKey).child('votes').get().val()
                    return [selfAttackCheck, votes]
                except:
                    return[False, 0]
            else:
                selfAttackCheck = db.child('arguments').child(originalKey).child('argumentSchema').child(argumentKey).child('selfAttack').get().val()
                if selfAttackCheck == None:
                    selfAttackCheck = False
                try:
                    votes = db.child('arguments').child(originalKey).child('argumentSchema').child(argumentKey).child('votes').get().val()
                    return [selfAttackCheck, votes]
                except:
                    return[selfAttackCheck, 0]
        except:
            return [True, 0]
    
    # Allow the user to vote on an argument
    def vote(self, originalKey, argumentKey): 
        votes = self.returnVotes(originalKey, argumentKey)
        if votes[0] == False:
            try:
                votes[1] += 1
            except:
                pass
            vote = votes[1]
            increaseVotes = {"votes": vote}
            if originalKey == argumentKey:
                votes = db.child('arguments').child(originalKey).update(increaseVotes)
            else:
                votes = db.child('arguments').child(originalKey).child('argumentSchema').child(argumentKey).update(increaseVotes)
            return ("Your vote has been logged")
        else:
            return('Sorry you cannot vote on a self attacking argument')

    # Return the directed graph of attacks of an argument schema
    def return_graph_data(self, originalKey):
        schema = self.return_schema(originalKey)

        nodes = {}
        edges = []
        edgesNames = {}
        name = 1
        try:
            for key, value in schema.items():
                if value["labellings"]["in"] == True: 
                    labelling = "in"
                elif value["labellings"]["out"] == True: 
                    labelling = "out"
                else: 
                    labelling = "undecided"
                nodes[key] = [value["title"], labelling]
                try:
                    attacking = value["attacking"]
                    for aKey, aValue in attacking.items():
                        if key not in edgesNames and aKey not in edgesNames:
                            edgesNames[key] = name
                            name += 1
                            edgesNames[aKey] = name
                            name += 1
                        elif key not in edgesNames:
                            edgesNames[key] = name
                            name += 1
                        elif aKey not in edgesNames:
                            edgesNames[aKey] = name
                            name += 1
                        edges.append((edgesNames[key], edgesNames[aKey]))
                except:
                    pass
            for key, value in nodes.items():
                nodes[key] = {"title": value[0], "number": edgesNames[key], "labelling": value[1]}
        except:
            print("Error returning graph schema data")
            pass
        return [nodes, edges]
        








