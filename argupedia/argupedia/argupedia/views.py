
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
    context = {"title": "Home"}
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
    context = {"title": "Register"}
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
        context = {"message": "There was an error creating your account"}
        template_name = 'argupedia/register.html'
        return render(request, template_name, context)
    context = {"e": email}
    template_name = 'argupedia/login_success.html'
    return render(request, template_name, context)


def login_page(request):
    context = {"title": "Log In"}
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
        db.set_uid(request.session['uid'])
    except:
        print("we tried")
        context = {"message":"invalid credentials"}
        template_name = 'argupedia/login.html'
        return render(request, template_name, context )
    context = {"e": email}
    template_name = 'argupedia/login_success.html'
    return render(request, template_name, context)


def log_out(request):
    print("user has logged out")
    try:
        auth.logout(request)
        db.log_out()
        context = {"message": "You have successfully logged out"}
    except:
        print("log out error")
        context = {"message": "There was an error logging you out"}
    template_name = 'argupedia/index.html'
    return render(request, template_name, context)

#add an argument 
def add_argument(request):
    print("called me!!!")
    data = {
        "topic": request.POST.get('topic'),
        "title" : request.POST.get('title'),
        "content": request.POST.get('content'), 
        "urlReference": request.POST.get('urlReference'),
        "fileReference": request.POST.get('fileReference'),
        "image": request.POST.get('image')
    }
    fileRef =  request.POST.get('fileReference')
    image = request.POST.get('image')
    if db.add_argument(data, fileRef, image) is None: 
        context = {"message": "Error"}
        template_name = 'argupedia/create_argument.html'
        return render(request, template_name, context)
        #userID = authF.currentUser().getIdToken()
        # userID = db.return_uid()
        # print(userID)
        # dbF.child("users").child(userID).child("arguments").push(data)
    else:
        context = {"e": "Your argument has been successfully submitted"}
        template_name = 'argupedia/login_success.html'
        return render(request, template_name, context)

def search_argument_page(request):
    #context = {"title": "Create Argument"}
    template_name = 'argupedia/search_argument.html'
    uid = db.return_username()
    return render(request, template_name, {"uid" : uid})

def create_argument_page(request):
    template_name = 'argupedia/create_argument.html'
    topic = request.POST.get('argumentTopic')
    uid = db.return_uid()
    #db.check_if_argument_exists(topic)
    #LATER IMPLEMENTATION - search and check if argument exists
    return render(request, template_name, {"topic" : topic, "uid": uid})

def view_arguments_page(request):
    template_name = 'argupedia/view_arguments.html'
    uid = db.return_uid()
    argument = db.return_arguments()
    #temporary for testing! delete up until next comment then uncomment the rest
    # data = {'-M1GrB2f4w35ZwQVMYUR': {'content': 'have ALL the babies. ALL OF THEM.', 'fileReference': '', 'title': 'abortion sucks bitched', 'topic': 'abortion', 'urlReference': '', 'image': 'https://images.dailykos.com/images/598155/large/abortion-debate.jpg?1539112132' }, '-M1Gzr2YVAaF9dmuzF_7': {'content': 'computer says no', 'fileReference': '', 'title': 'No Brexit for Britain', 'topic': 'Brexit', 'urlReference': '', 'image': 'https://1gb82h2px4rr3s7tp94g0nt1-wpengine.netdna-ssl.com/wp-content/uploads/2019/01/brexitborder.jpg'}}
    # toReturn = {"uid" : "OjTpCCeALlcGCluPNoWWSj6bS532", "arguments" : data}
    # return render(request, template_name, toReturn)
    #end of testing segment!!

    #uncmment the following after testing:
    toReturn = {"uid" : uid, "arguments" : argument}
    if argument is not None:
        toReturn = {"uid" : uid, "arguments" : argument}
        print("")
        print ("views print statement", toReturn)
        print("")
        return render(request, template_name, toReturn)
    else:
        return render(request, template_name, {"uid" : uid, "arguments": None})

def search_argument_nav_page(request):
    search = request.POST.get('searchTerm')
    template_name = 'argupedia/search_results.html'
    results = db.search_arguments(search)
    context = {"arguments": results}
    return render(request, template_name, context)
    # if bool(context):
    #     return render(request, template_name, {"arguments": ""})
    # else:




