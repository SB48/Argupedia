
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import render
from django.contrib import auth
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
db = firebase.database()

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
        db.child("users").child(userID).set(data)
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
    email = request.POST.get('email')
    password = request.POST.get('password')
    try:
        user = authF.sign_in_with_email_and_password(email, password)
        print(user)
        print()
        session_id = user['idToken']
        request.session['uid'] = str(session_id)
        print(request.session['uid'])
    except:
        context = {"message":"invalid credentials"}
        template_name = 'argupedia/login.html'
        return render(request, template_name, context )
    context = {"e": email}
    template_name = 'argupedia/login_success.html'
    return render(request, template_name, context)


def log_out(request):
    try:
        auth.logout(request)
        context = {"message": "You have successfully logged out"}
    except:
        context = {"message": "There was an error logging you out"}
    template_name = 'argupedia/index.html'
    return render(request, template_name, context)

#add an argument 
def add_argument(request):
    title = request.POST.get('titleArgument')
    print("called me!!!")
    try:
        #test = authF.get_user(uid)
        userID = authF.currentUser().getIdToken()
        print(userID)
        db.child("users").child(userID).child("arguments").push(title)
    except:
        context = {"message": "Error"}
        template_name = 'argupedia/create_argument.html'
        return render(request, template_name, context)
    context = {"e": "YES SUBMITTED"}
    template_name = 'argupedia/login_success.html'
    return render(request, template_name, context)

def create_argument_page(request):
    context = {"title": "Create Argument"}
    template_name = 'argupedia/create_argument.html'
    if request.session.has_key('uid'):
      uid = request.session['uid']
      username = db.child("users").child(uid).child("username")
      return render(request, template_name, {"uid" : username})
    else:
      return render(request, template_name, {"uid" : None})