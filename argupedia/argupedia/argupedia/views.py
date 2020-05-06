
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render
from django.contrib import auth
from .database import Database
import pyrebase

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
dbF = firebase.database()
db = Database()





#Load Home Page:
def home_page(request):
    images = db.return_images()
    uid = db.return_uid()
    context = {"title": "Home", "uid": uid, "schema" : True, "images" : images, "uid": uid}
    template_name = 'argupedia/index.html'
    return render(request, template_name, context)


#check if user is logged in
def logged_in(request):
    try: 
        uID = firebase.auth().currentUser().getIdToken()
        return authF.getInstance().getCurrentUser()
    except:
        print("Error logging user in")
        return False


#Load register user page
def register_page(request):
    uid = db.return_uid()
    context = {"title": "Register", "uid": uid}
    template_name = 'argupedia/register.html'
    return render(request, template_name, context)

#Register user's details
def post_register(request): 
    data = {
            "fName": request.POST.get('fName'),
            "lName" : request.POST.get('lName'),
            "username": request.POST.get('username'), 
            "email": request.POST.get('email')
    }
    email = request.POST.get('email')
    password = request.POST.get('password')
    try:
        user = authF.create_user_with_email_and_password(email, password)
        userID = user['localId']
        dbF.child("users").child(userID).set(data)
        post_login(request)
    except:
        context = {"message": "There was an error creating your account", "uid": None}
        template_name = 'argupedia/register.html'
        return render(request, template_name, context)
    uid = db.return_uid()
    context = {"e": "Welcome {}".format(email), "uid": uid}
    template_name = 'argupedia/login_success.html'
    return render(request, template_name, context)


def login_page(request):
    uid = db.return_uid()
    context = {"title": "Log In", "uid": uid}
    template_name = 'argupedia/login.html'
    return render(request, template_name, context)

def post_login(request):
    email = request.POST.get('email')
    password = request.POST.get('password')
    try:
        user = authF.sign_in_with_email_and_password(email, password)
        session_id = user['localId']
        request.session['uid'] = str(session_id)
        db.set_uid(session_id, user['idToken'])
    except:
        context = {"message":"invalid credentials", "uid": None}
        template_name = 'argupedia/login.html'
        return render(request, template_name, context )
    uid = db.return_uid()
    context = {"e": "Welcome {}".format(email), "uid": uid}
    template_name = 'argupedia/login_success.html'
    return render(request, template_name, context)


def log_out(request):
    try:
        auth.logout(request)
        db.log_out()
        context = {"message": "You have successfully logged out", "uid": None}
    except:
        print("Error Logging the user out")
        uid = db.return_uid()
        context = {"message": "There was an error logging you out", "uid": uid}
    template_name = 'argupedia/login_success.html'
    return render(request, template_name, context)

#function does not currently work - could be implemented in the future
def delete_user(request):
    uid = db.return_uid()
    token = db.return_firebaseID()
    try:
        auth.delete_user(uid)
        db.delete_user()
        context = {"message": "You have successfully deleted your account", "uid": None}
    except:
        uid = db.return_uid()
        context = {"message": "There was an error deleting your account", "uid": uid}
    template_name = 'argupedia/login_success.html'
    return render(request, template_name, context)

def about_page(request):
    uid = db.return_uid()
    context = {"title": "About", "uid": uid}
    template_name = 'argupedia/about.html'
    return render(request, template_name, context)

#add an argument 
def add_argument(request):
    if request.POST.get('selfAttack') is None:
        selfAttack = False
    else: 
        selfAttack = True
    contentString = str(request.POST.get('content-1')) + " \n "  + str(request.POST.get('content-2'))  + " \n "  + str(request.POST.get('content-3')) + " \n "  + str(request.POST.get('content-4')) 
    data = {
        "argumentType": request.POST.get('argumentType'),
        "topic": request.POST.get('topic'),
        "title" : request.POST.get('title'),
        "urlReference": request.POST.get('urlReference'),
        "fileReference": request.POST.get('fileReference'),
        "image": request.POST.get('image'),
        "argumentType" : request.POST.get('argumentType'), 
        "selfAttack" : selfAttack,
        "content": contentString,
        'votes': 0,
    }
    fileRef =  request.POST.get('fileReference')
    image = request.POST.get('image')
    passCheck = db.add_argument(data, fileRef, image)
    uid = db.return_uid()
    if passCheck is None: 
        context = {"message": "Error", "uid": uid}
        template_name = 'argupedia/create_argument.html'
        return render(request, template_name, context)
    else:
        context = {"e": "Your argument {} has been successfully submitted".format(passCheck), "uid": uid}
        template_name = 'argupedia/login_success.html'
        return render(request, template_name, context)

def search_argument_page(request):
    argumentTypes = db.return_argumentTypes()
    template_name = 'argupedia/search_argument.html'
    uid = db.return_username()
    return render(request, template_name, {"uid" : uid, "types": argumentTypes})

def create_argument_page(request):
    template_name = 'argupedia/create_argument.html'
    argumentType = request.POST.get('argumentType')
    argumentFormat = db.return_argumentFormats(argumentType)
    uid = db.return_uid()
    return render(request, template_name, {"argumentType": argumentType, "format" : argumentFormat, "uid": uid})

def turn_content_to_list(contentString):
    contentList = contentString.strip('][').split(',')
    content = []
    for item in contentList:
        content.append(item.replace("'", ""))
    return content


def view_argument_info_page(request):
    uid = db.return_uid()
    template_name = 'argupedia/view_argument_info.html'

    originalKey = request.POST.get('originalKey')
    argumentKey = request.POST.get('argumentKey')
    votes = db.returnVotes(originalKey, argumentKey)
    selfAttack = votes[0] 
    data = {
        "selfAttack" : selfAttack,
        "votes": votes[1],
        "originalKey" : originalKey,
        "argumentKey" : argumentKey,
        "content": request.POST.get('content'),
        "title" : request.POST.get('title'), 
        "urlReference": request.POST.get('urlReference'),
        "fileReference": request.POST.get('fileReference'),
        "labellings": request.POST.get('labellings'),
    }
    return render(request, template_name, {"value": data,"uid": uid})


def view_arguments_page(request):
    uid = db.return_uid()
    template_name = 'argupedia/view_arguments.html'
    if uid is not None:
        argumentTypes = db.return_argumentTypes()
        argument = db.return_arguments()
        toReturn = {"uid" : uid, "arguments" : argument, "types": argumentTypes}
        if (argument):
            toReturn = {"uid" : uid, "arguments" : argument}
            return render(request, template_name, toReturn)
        else:
            return render(request, template_name, {"uid" : uid, "arguments": None, "types": argumentTypes})
    else:
        return render(request, template_name, {"uid" : uid, "arguments": None, "types": None})


#reference : https://stackoverflow.com/questions/298772/django-template-variables-and-javascript Daniel Munoz
# this function recieves the necessary information from the database in the appropriate form
# this information then has to be converted to javascript before being run in the views
def view_argument_schema_page(request):
    uid = db.return_uid()
    originalKey = request.POST.get('originalKey')
    arguments = db.return_schema(originalKey)
    argumentTypes = db.return_argumentTypes()
    template_name = 'argupedia/view_schema.html'
    if arguments is not None: 
        graphFile = db.return_graph_data(originalKey)
        if len(graphFile[1]) >= 1:
            dot = "var dot = \"dinetwork {node[shape=circle];"
            for tuple in graphFile[1]:
                toAdd = " " + str(tuple[0]) + " -> " + str(tuple[1]) + ";"
                dot = dot + "" + toAdd + ""
            dot = dot[:-1]
            dot = dot + " }\";"
            context = {"originalKey": originalKey, "arguments": arguments, "schema" : True, "dot": dot, "names" : graphFile[0], "uid": uid, "types": argumentTypes}
        else: 
            context = {"originalKey": originalKey, "arguments": arguments, "schema" : True, "dot": None, "names" : None, "uid": uid, "types" : argumentTypes}
    else: 
        context = {"originalKey": originalKey, "arguments": None, "schema" : True, "uid": uid}
    return render(request, template_name, context)

def view_graph_page(request):
    uid = db.return_uid()
    originalKey = request.POST.get("originalKey")
    originalKey = request.POST.get("key")
    graphFile = db.return_graph_data(originalKey)
    template_name = 'argupedia/view_graph.html'
    context = {"graph": graphFile, "uid": uid}
    return render(request, template_name, context)

def search_argument_nav_page(request):
    uid = db.return_uid()
    search = request.POST.get('searchTerm')
    argumentTypes = db.return_argumentTypes()
    template_name = 'argupedia/search_results.html'
    results = db.search_arguments(search)
    context = {"arguments": results, "uid": uid, "types" : argumentTypes}
    return render(request, template_name, context)

def critical_questions_page(request):
    uid = db.return_uid()
    topic = request.POST.get('topic')
    argumentType = request.POST.get('argumentType')
    argumentFormat = db.return_argumentFormats(argumentType)
    key = request.POST.get('key')
    originalKey = request.POST.get('originalKey')
    uid = db.return_uid()
    criticalQuestions = db.return_criticalQuestions(key, originalKey)
    context = {"uid": uid, "topic": topic, "key": key, "originalKey": originalKey, "criticalQuestions": criticalQuestions, "argumentType": argumentType, "format" : argumentFormat}
    template_name = 'argupedia/critical_questions.html'
    return render(request, template_name, context)
    


#adds an attacking argument 
def add_attack(request):
    uid = db.return_uid()
    originalKey = request.POST.get('originalKey')
    if request.POST.get('alternate') is None:
        alternate = False
    else: 
        alternate = True
    
    if request.POST.get('selfAttack') is None:
        selfAttack = False
    else: 
        selfAttack = True
    contentString = contentString = str(request.POST.get('content-1')) + " \n "  + str(request.POST.get('content-2'))  + " \n "  + str(request.POST.get('content-3')) + " \n "  + str(request.POST.get('content-4')) 
    data = {
        "title" : request.POST.get('title'),
        "content": contentString,
        "urlReference": request.POST.get('urlReference'),
        "fileReference": request.POST.get('fileReference'),
        "image": request.POST.get('image'),
        "argumentType" : request.POST.get('argumentType'),
        "criticalQuestion": request.POST.get('criticalQuestion'),
        "attacking" : {request.POST.get('attackingKey') : "attacking"},
        "originalKey": originalKey,
        "attackedBy": "",
        "alternate" : alternate,
        "selfAttack": selfAttack, 
        "votes": 0,
    }

    fileRef =  request.POST.get('fileReference')
    image = request.POST.get('image')
    passCheck = db.add_attack(data, originalKey, fileRef, image, [request.POST.get('attackingKey')] )
    if passCheck is None: 
        context = {"message": "Error", "uid": uid}
        template_name = 'argupedia/create_argument.html'
        return render(request, template_name, context)
    else:
        context = {"e": "Your argument {} has been successfully submitted".format(passCheck), "uid": uid}
        template_name = 'argupedia/login_success.html'
        return render(request, template_name, context)

def vote_argument(request):
    uid = db.return_uid()
    vote = db.vote(request.POST.get('originalKey'), request.POST.get('argumentKey'))
    context = {"e": vote, "uid": uid}
    template_name = 'argupedia/login_success.html'
    return render(request, template_name, context)






