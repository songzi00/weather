from django.urls import path
from myapp import views

app_name = '[myapp]'

urlpatterns = [
    path('',views.index,name='index'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    path('area/(?p<id>)$',views.area,name='area'),
    path('national/(?p<level>)$',views.national,name='national')
]






