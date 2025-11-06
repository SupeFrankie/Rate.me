from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Public pages
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    
    # Authentication
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Course management (lecturers)
    path('add-course/', views.add_course, name='add_course'),
    
    # Rating system (students)
    path('lecturers/', views.lecturers_list, name='lecturers'),
    path('rate-lecturer/<int:lecturer_id>/', views.rate_lecturer, name='rate_lecturer'),
    
    # AI Suggestions (lecturers)
    path('generate-suggestions/', views.generate_suggestions, name='generate_suggestions'),
]