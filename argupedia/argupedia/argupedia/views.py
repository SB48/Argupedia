
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





#Load Pages:
def home_page(request):
    images = db.return_images()
    uid = db.return_uid()
    context = {"title": "Home", "uid": uid, "schema" : True, "images" : images, "uid": uid}
    template_name = 'argupedia/index.html'
    return render(request, template_name, context)


#check if logged in
def logged_in(request):
    try: 
        uID = firebase.auth().currentUser().getIdToken()
        print(uID)
        return authF.getInstance().getCurrentUser()
    except:
        print("no")
        return False


#Register
def register_page(request):
    uid = db.return_uid()
    context = {"title": "Register", "uid": uid}
    template_name = 'argupedia/register.html'
    return render(request, template_name, context)

def post_register(request): 
    print("register called")
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
        print("create user")
        userID = user['localId']
        dbF.child("users").child(userID).set(data)
        print("register completed")
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
    print("log in attempt")
    email = request.POST.get('email')
    password = request.POST.get('password')
    try:
        user = authF.sign_in_with_email_and_password(email, password)
        print(user)
        session_id = user['localId']
        request.session['uid'] = str(session_id)
        db.set_uid(session_id, user['idToken'])
    except:
        print("we tried")
        context = {"message":"invalid credentials", "uid": None}
        template_name = 'argupedia/login.html'
        return render(request, template_name, context )
    uid = db.return_uid()
    context = {"e": "Welcome {}".format(email), "uid": uid}
    template_name = 'argupedia/login_success.html'
    return render(request, template_name, context)


def log_out(request):
    print("user has logged out")
    try:
        auth.logout(request)
        db.log_out()
        context = {"message": "You have successfully logged out", "uid": None}
    except:
        print("log out error")
        uid = db.return_uid()
        context = {"message": "There was an error logging you out", "uid": uid}
    template_name = 'argupedia/login_success.html'
    return render(request, template_name, context)

def delete_user(request):
    print("user has been deleted")
    uid = db.return_uid()
    print("uid", uid)
    token = db.return_firebaseID()
    try:
        auth.delete_user(uid)
        auth.delete_user(uid)
        print("yeh")
        db.delete_user()
        context = {"message": "You have successfully deleted your account", "uid": None}
    except:
        print("deletion error")
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
    data = {
        "topic": request.POST.get('topic'),
        "title" : request.POST.get('title'),
        "urlReference": request.POST.get('urlReference'),
        "fileReference": request.POST.get('fileReference'),
        "image": request.POST.get('image'),
        "argumentType" : request.POST.get('argumentType'), 
        "selfAttack" : selfAttack,
        "content": [str(request.POST.get('content-1')),str(request.POST.get('content-2')),str(request.POST.get('content-3')),str(request.POST.get('content-4'))],
    }
    fileRef =  request.POST.get('fileReference')
    image = request.POST.get('image')
    passCheck = db.add_argument(data, fileRef, image)
    uid = db.return_uid()
    if passCheck is None: 
        context = {"message": "Error", "uid": uid}
        template_name = 'argupedia/create_argument.html'
        return render(request, template_name, context)
        #userID = authF.currentUser().getIdToken()
        # userID = db.return_uid()
        # print(userID)
        # dbF.child("users").child(userID).child("arguments").push(data)
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
    return render(request, template_name, {"format" : argumentFormat, "uid": uid})

def turn_content_to_list(contentString):
    contentList = contentString.strip('][').split(',')
    content = []
    for item in contentList:
        content.append(item.replace("'", ""))
    # contentListFixed = contentList.replace("'", "")
    # "var dot = \"dinetwork {node[shape=circle];"   " }\";"
    return content


def view_argument_info_page(request):
    uid = db.return_uid()
    template_name = 'argupedia/view_argument_info.html'
    contentString = request.POST.get('content')
    content = turn_content_to_list(contentString)
    print("contentList", content)
    originalKey = request.POST.get('originalKey')
    argumentKey = request.POST.get('argumentKey')
    votes = db.returnVotes(originalKey, argumentKey)
    selfAttack = votes[0] 
    data = {
        "selfAttack" : selfAttack,
        "votes": votes[1],
        "originalKey" : originalKey,
        "argumentKey" : argumentKey,
        "content": content,
        "title" : request.POST.get('title'), 
        "urlReference": request.POST.get('urlReference'),
        "fileReference": request.POST.get('fileReference'),
        "labellings": request.POST.get('labellings'),
    }
    return render(request, template_name, {"value": data,"uid": uid})


def view_arguments_page(request):
    print("")
    print("view arguments page called")
    print("")
    template_name = 'argupedia/view_arguments.html'
    argumentTypes = db.return_argumentTypes()
    uid = db.return_uid()
    argument = db.return_arguments()
    #temporary for testing! delete up until next comment then uncomment the rest
    # data = {'-M1GrB2f4w35ZwQVMYUR': {'content': 'have ALL the babies. ALL OF THEM.', 'fileReference': '', 'title': 'abortion sucks bitched', 'topic': 'abortion', 'urlReference': '', 'image': 'https://images.dailykos.com/images/598155/large/abortion-debate.jpg?1539112132' }, '-M1Gzr2YVAaF9dmuzF_7': {'content': 'computer says no', 'fileReference': '', 'title': 'No Brexit for Britain', 'topic': 'Brexit', 'urlReference': '', 'image': 'https://1gb82h2px4rr3s7tp94g0nt1-wpengine.netdna-ssl.com/wp-content/uploads/2019/01/brexitborder.jpg'}}
    # toReturn = {"uid" : "OjTpCCeALlcGCluPNoWWSj6bS532", "arguments" : data}
    # return render(request, template_name, toReturn)
    #end of testing segment!!
    toReturn = {"uid" : uid, "arguments" : argument, "types": argumentTypes}
    if (argument):
        toReturn = {"uid" : uid, "arguments" : argument}
        print("")
        print ("views print statement", toReturn)
        print("")
        return render(request, template_name, toReturn)
    else:
        return render(request, template_name, {"uid" : uid, "arguments": None, "types": argumentTypes})

# def view_argument_content(request):
#     originalKey = request.POSt.get("originalKey")
#     key = request.POSt.get("key")
#     argument = db.return_argument_content(originalKey, key)
#     template_name = "argupedia/view_argument_content.html"
#     context = {"argument": argument}
#     return render(request, template_name, context)

#reference : https://stackoverflow.com/questions/298772/django-template-variables-and-javascript Daniel Munoz
def view_argument_schema_page(request):
    uid = db.return_uid()
    print("viewing schema")
    originalKey = request.POST.get('originalKey')
    print("originalKey", originalKey)
    arguments = db.return_schema(originalKey)
    argumentTypes = db.return_argumentTypes()
    template_name = 'argupedia/view_schema.html'
    if arguments is not None: 
        graphFile = db.return_graph_data(originalKey)
        print ("graphFile", graphFile)
        print ("graphFile", len(graphFile))
        print ("graphFile", len(graphFile[1]))
        if len(graphFile[1]) >= 1:
            dot = "var dot = \"dinetwork {node[shape=circle];"
            for tuple in graphFile[1]:
                print("tuple", tuple)
                toAdd = " " + str(tuple[0]) + " -> " + str(tuple[1]) + ";"
                #toAdd = str("(",key,",",value,")")
                dot = dot + "" + toAdd + ""
            dot = dot[:-1]
            dot = dot + " }\";"
            print("")
            print(dot)
            print("")
            context = {"originalKey": originalKey, "arguments": arguments, "schema" : True, "dot": dot, "names" : graphFile[0], "uid": uid, "types": argumentTypes}
        else: 
            context = {"originalKey": originalKey, "arguments": arguments, "schema" : True, "dot": None, "names" : None, "uid": uid, "types" : argumentTypes}
        #dot = "var dot = \"dinetwork {node[shape=circle]; 1 -> 2; 1 -> 1; 2 -> 1}\";"
        #print(dot)
        # var dot = "dinetwork {node[shape=circle]; 1 -> 1 -> 2; 2 -> 3; 2 -- 4; 2 -> 1 }";
    # if arguments is not None:
    #     graphFile = db.return_graph_data(originalKey)
    #     nodes = "var importNodes = ["
    #     for key, value in graphFile[0].items():
    #         toAdd = "'" + str(key) + "','" + str(value) + "'"
    #         #toAdd = str("(",key,",",value,")")
    #         nodes = nodes + "" + toAdd + ","
    #     nodes = nodes[:-1]
    #     nodes = nodes + "];"
    #     print("")
    #     print(nodes)
    #     print("")
    #     edges = "var importEdges =["
    #     for tuple in graphFile[1]:
    #         toAdd = "'" + str(tuple[0]) + "','" + str(tuple[1]) + "'"
    #         edges = edges + "" + toAdd + ","
    #     edges = edges[:-1]
    #     edges = edges + "];"
    #     print("")
    #     print(edges)
    #     print("")
    #     context = {"originalKey": originalKey, "arguments": arguments, "schema" : True, "nodes": nodes, "edges" : edges}
    else: 
        context = {"originalKey": originalKey, "arguments": None, "schema" : True, "uid": uid}
    return render(request, template_name, context)

def view_graph_page(request):
    uid = db.return_uid()
    print("called")
    originalKey = request.POST.get("originalKey")
    originalKey = request.POST.get("key")
    graphFile = db.return_graph_data(originalKey)
    #graphFile = db.return_schema_json()
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
    print("in views page", results)
    return render(request, template_name, context)

def critical_questions_page(request):
    uid = db.return_uid()
    topic = request.POST.get('topic')
    argumentType = request.POST.get('argumentType')
    argumentFormat = db.return_argumentFormats(argumentType)
    key = request.POST.get('key')
    originalKey = request.POST.get('originalKey')
    uid = db.return_uid()
    criticalQuestions = db.return_criticalQuestions(key)
    context = {"uid": uid, "topic": topic, "key": key, "originalKey": originalKey, "criticalQuestions": criticalQuestions, "argumentType": argumentType, "format" : argumentFormat}
    template_name = 'argupedia/critical_questions.html'
    #testing values: @@@@@@@@@@@@
    # topic = "Abortion"
    # key = "-M1v_Wu7l6mpOYEha1fU"
    # uid = "IdZbjSY6RmeUDhgsLZaPA1bv9OI2"
    # criticalQuestions = db.return_criticalQuestions(key)
    # context = {"uid": uid, "topic": topic, "key": key, "criticalQuestions": criticalQuestions}
    #end of testing values @@@@@@@@@@@@@@@
    return render(request, template_name, context)
    


#adds an attacking argument 
def add_attack(request):
    uid = db.return_uid()
    print("called add attack in views")
    originalKey = request.POST.get('originalKey')
    print("original key", originalKey)
    if request.POST.get('alternate') is None:
        alternate = False
    else: 
        alternate = True
    
    if request.POST.get('selfAttack') is None:
        selfAttack = False
    else: 
        selfAttack = True

    # attackingKeys =  {}
    # for element in request.POST.get('attackingKey'):
    #     attackingKeys[element] = "attacking"
    data = {
        "title" : request.POST.get('title'),
        "content": [str(request.POST.get('content-1')),str(request.POST.get('content-2')),str(request.POST.get('content-3')),str(request.POST.get('content-4'))],
        "urlReference": request.POST.get('urlReference'),
        "fileReference": request.POST.get('fileReference'),
        "image": request.POST.get('image'),
        "argumentType" : request.POST.get('argumentType'),
        "criticalQuestion": request.POST.get('criticalQuestion'),
        "attacking" : {request.POST.get('attackingKey') : "attacking"},
        "originalKey": originalKey,
        "attackedBy": "",
        "alternate" : alternate,
        "selfAttack": selfAttack
    }

    print ("checkbox return value, ", data["alternate"])
    fileRef =  request.POST.get('fileReference')
    image = request.POST.get('image')
    passCheck = db.add_attack(data, originalKey, fileRef, image)
    if passCheck is None: 
        context = {"message": "Error", "uid": uid}
        template_name = 'argupedia/create_argument.html'
        return render(request, template_name, context)
        #userID = authF.currentUser().getIdToken()
        # userID = db.return_uid()
        # print(userID)
        # dbF.child("users").child(userID).child("arguments").push(data)
    else:
        context = {"e": "Your argument {} has been successfully submitted".format(passCheck), "uid": uid}
        template_name = 'argupedia/login_success.html'
        return render(request, template_name, context)

def vote_argument(request):
    uid = db.return_uid()
    print("ok")
    vote = db.vote(request.POST.get('originalKey'), request.POST.get('argumentKey'))
    context = {"e": vote, "uid": uid}
    template_name = 'argupedia/login_success.html'
    return render(request, template_name, context)






