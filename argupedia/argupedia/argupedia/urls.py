"""argupedia URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.urls import path
from .views import home_page, register_page, login_page, post_login, log_out, post_register, log_out, search_argument_page, add_argument, create_argument_page, view_arguments_page, search_argument_nav_page, critical_questions_page, add_attack, view_argument_schema_page, about_page, view_graph_page, view_argument_info_page, delete_user, vote_argument

urlpatterns = [
    path('', home_page, name='home_page'),
    path('register/', register_page, name='register_page'),
    path('login/', login_page, name= 'login_page'),
    path('post_login/', post_login, name = 'post_login'),
    path('post_register/', post_register, name = 'post_register'),
    path('delete_account/', delete_user, name= 'delete_user'),
    path('add_argument/', add_argument, name = 'add_argument'),
    path('add_attack/', add_attack, name = 'add_attack'),
    path('vote_argument/', vote_argument, name = 'vote_argument'),
    path('view_argument/', view_argument_info_page, name = 'view_argument_info_page'),
    path('about/', about_page, name = 'about_page'),
    path('graph/', view_graph_page, name = 'view_graph_page'),
    path('start_a_debate/', search_argument_page, name = 'search_argument_page'),
    path('get_writing/', create_argument_page, name = 'create_argument_page'),
    path('your_contributions/', view_arguments_page, name = 'view_arguments_page'),
    path('search_results/', search_argument_nav_page, name = 'search_argument_nav_page'),
    path('schema_page/', view_argument_schema_page, name = 'view_argument_schema_page'),
    path('critical_questions/', critical_questions_page, name = 'critical_questions_page'),
    path('log_out/', log_out, name = 'log_out'),
    path('admin/', admin.site.urls),
]

