from django.urls import path
from . import views
from django.views.generic import TemplateView
from .views import root_redirect
from .views import SignUpView



# Import the API views
from .views import (
    TaskListCreateAPI, TaskDetailAPI,
    HabitListCreateAPI, HabitDetailAPI,
    NoteListCreateAPI, NoteDetailAPI,
    EventListCreateAPI, EventDetailAPI,
    UserRegisterAPI, register,
)

app_name = "tasks"

urlpatterns = [
    # HTML views
    path('no-access/', TemplateView.as_view(template_name='tasks/no_access.html'), name='no-access'),
    path('', views.task_list, name='task_list'),
    path('new/', views.task_create, name='task_create'),
    path('habits/', views.habit_list, name='habit_list'),
    path('habits/new/', views.habit_create, name='habit_create'),
    path('notes/', views.note_list, name='note_list'),
    path('notes/new/', views.note_create, name='note_create'),
    path('events/', views.event_list, name='event_list'),
    path('events/new/', views.event_create, name='event_create'),
    path('tasks/<int:pk>/delete/', views.task_delete, name='task_delete'),
    path('habits/<int:pk>/delete/', views.habit_delete, name='habit_delete'),
    path('notes/<int:pk>/delete/', views.note_delete, name='note_delete'),
    path('events/<int:pk>/delete/', views.event_delete, name='event_delete'),
    
    # API endpoints
    path('api/tasks/', TaskListCreateAPI.as_view(), name='api_task_list'),
    path('api/tasks/<int:pk>/', TaskDetailAPI.as_view(), name='api_task_detail'),

    path('api/habits/', HabitListCreateAPI.as_view(), name='api_habit_list'),
    path('api/habits/<int:pk>/', HabitDetailAPI.as_view(), name='api_habit_detail'),

    path('api/notes/', NoteListCreateAPI.as_view(), name='api_note_list'),
    path('api/notes/<int:pk>/', NoteDetailAPI.as_view(), name='api_note_detail'),

    path('api/events/', EventListCreateAPI.as_view(), name='api_event_list'),
    path('api/events/<int:pk>/', EventDetailAPI.as_view(), name='api_event_detail'),
    
    #User registration
    path("register/", SignUpView.as_view(), name="register"),
    path('register/', register, name='register'),

    #Api links
    path('api/', views.api_root, name='api_root'),

]
