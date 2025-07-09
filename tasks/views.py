from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render,redirect
from .models import Task, Habit, Note, Event
from .forms import TaskForm, HabitForm, NoteForm, EventForm 
from .serializers import TaskSerializer, HabitSerializer, NoteSerializer, EventSerializer
from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer
from rest_framework import permissions, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

#APIS Display
@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'tasks': reverse('tasks:api_task_list', request=request, format=format),
        'habits': reverse('tasks:api_habit_list', request=request, format=format),
        'notes': reverse('tasks:api_note_list', request=request, format=format),
        'events': reverse('tasks:api_event_list', request=request, format=format),
        'register': reverse('tasks:api_register', request=request, format=format),
    })




#User Authentication
class UserRegisterSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(username=validated_data['username'])
        user.set_password(validated_data['password'])
        user.save()
        return user

class UserRegisterAPI(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer

#PERMISSIONS
class IsSuperUserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow all users to view (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        # Only allow superusers to modify (POST, PUT, DELETE, etc.)
        return request.user and request.user.is_superuser

# TASKS API
class TaskListCreateAPI(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class TaskDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsSuperUserOrReadOnly]

# HABITS API
class HabitListCreateAPI(generics.ListCreateAPIView):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class HabitDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = [IsSuperUserOrReadOnly]

# NOTES API

class NoteListCreateAPI(generics.ListCreateAPIView):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class NoteDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [IsSuperUserOrReadOnly]

# EVENTS API

class EventListCreateAPI(generics.ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class EventDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsSuperUserOrReadOnly]

@login_required
@user_passes_test(lambda u: u.is_superuser)
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tasks:task_list')
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def habit_create(request):
    if request.method == 'POST':
        form = HabitForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tasks:habit_list')
    else:
        form = HabitForm()
    return render(request, 'tasks/habit_form.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def note_create(request):
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tasks:note_list')
    else:
        form = NoteForm()
    return render(request, 'tasks/note_form.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tasks:event_list')
    else:
        form = EventForm()
    return render(request, 'tasks/event_form.html', {'form': form})

@login_required
def task_list(request):
    tasks = Task.objects.all()
    return render(request, 'tasks/task_list.html', {'tasks': tasks})

@login_required
def habit_list(request):
    habits = Habit.objects.all()
    return render(request, 'tasks/habit_list.html', {'habits': habits})

@login_required
def note_list(request):
    notes = Note.objects.all()
    return render(request, 'tasks/note_list.html', {'notes': notes})

@login_required
def event_list(request):
    events = Event.objects.all()
    return render(request, 'tasks/event_list.html', {'events': events})

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  
            return redirect('login')  
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
