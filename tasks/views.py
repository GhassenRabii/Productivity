from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Group
from django.core.paginator import Paginator
from .models import Task, Habit, Note, Event
from .forms import TaskForm, HabitForm, NoteForm, EventForm 
from .serializers import TaskSerializer, HabitSerializer, NoteSerializer, EventSerializer
from rest_framework.serializers import ModelSerializer
from rest_framework import permissions, generics, pagination
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

# Decorators for group-based access

def in_group(group_name, login_url='no-access'):
    return user_passes_test(
        lambda u: u.is_authenticated and u.groups.filter(name=group_name).exists(),
        login_url=login_url
    )

def in_groups(group_names, login_url='no-access'):
    return user_passes_test(
        lambda u: u.is_authenticated and u.groups.filter(name__in=group_names).exists(),
        login_url=login_url
    )

# --- API PAGINATION ---
class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

# --- API ROOT ---
@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'tasks': reverse('tasks:api_task_list', request=request, format=format),
        'habits': reverse('tasks:api_habit_list', request=request, format=format),
        'notes': reverse('tasks:api_note_list', request=request, format=format),
        'events': reverse('tasks:api_event_list', request=request, format=format),
        'register': reverse('tasks:api_register', request=request, format=format),
    })

# --- USER REGISTRATION API ---
class UserRegisterSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(username=validated_data['username'])
        user.set_password(validated_data['password'])
        user.save()
        # assign default group
        default_group, _ = Group.objects.get_or_create(name='users')
        user.groups.add(default_group)
        return user

class UserRegisterAPI(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer

# --- PERMISSIONS ---
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user or request.user.is_superuser

# --- TASKS API ---
class TaskListCreateAPI(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Task.objects.filter(user=self.request.user)
        return Task.objects.none()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TaskDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Task.objects.filter(user=self.request.user)
        return Task.objects.none()

# --- HABITS API ---
class HabitListCreateAPI(generics.ListCreateAPIView):
    serializer_class = HabitSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Habit.objects.filter(user=self.request.user)
        return Habit.objects.none()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class HabitDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = HabitSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Habit.objects.filter(user=self.request.user)
        return Habit.objects.none()

# --- NOTES API ---
class NoteListCreateAPI(generics.ListCreateAPIView):
    serializer_class = NoteSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Note.objects.filter(user=self.request.user)
        return Note.objects.none()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class NoteDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = NoteSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Note.objects.filter(user=self.request.user)
        return Note.objects.none()

# --- EVENTS API ---
class EventListCreateAPI(generics.ListCreateAPIView):
    serializer_class = EventSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Event.objects.filter(user=self.request.user)
        return Event.objects.none()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class EventDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Event.objects.filter(user=self.request.user)
        return Event.objects.none()

# --- WEB VIEWS WITH FEEDBACK, USER DATA, AND DELETE ACTIONS ---
@login_required
def task_list(request):
    user = request.user
    own    = Task.objects.filter(user=user)
    shared = Task.objects.filter(groups__in=user.groups.all())
    tasks  = (own | shared).distinct()
    paginator    = Paginator(tasks, 10)
    page         = request.GET.get('page')
    tasks_page   = paginator.get_page(page)
    return render(request, 'tasks/task_list.html', {'tasks': tasks_page})

@login_required
def habit_list(request):
    user    = request.user
    own      = Habit.objects.filter(user=user)
    shared   = Habit.objects.filter(groups__in=user.groups.all())
    habits   = (own | shared).distinct()
    paginator  = Paginator(habits, 10)
    page       = request.GET.get('page')
    habits_page= paginator.get_page(page)
    return render(request, 'tasks/habit_list.html', {'habits': habits_page})

@login_required
def note_list(request):
    user    = request.user
    own      = Note.objects.filter(user=user)
    shared   = Note.objects.filter(groups__in=user.groups.all())
    notes    = (own | shared).distinct()
    paginator  = Paginator(notes, 10)
    page       = request.GET.get('page')
    notes_page = paginator.get_page(page)
    return render(request, 'tasks/note_list.html', {'notes': notes_page})

@login_required
def event_list(request):
    user     = request.user
    own       = Event.objects.filter(user=user)
    shared    = Event.objects.filter(groups__in=user.groups.all())
    events    = (own | shared).distinct()
    paginator   = Paginator(events, 10)
    page        = request.GET.get('page')
    events_page = paginator.get_page(page)
    return render(request, 'tasks/event_list.html', {'events': events_page})

@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            form.save_m2m()
            messages.success(request, 'Task created!')
            return redirect('tasks:task_list')
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form})

@login_required
@in_groups(['Admins', 'dev'])
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted!')
        return redirect('tasks:task_list')
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})

@login_required
def habit_create(request):
    if request.method == 'POST':
        form = HabitForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            form.save_m2m()
            messages.success(request, 'Habit created!')
            return redirect('tasks:habit_list')
    else:
        form = HabitForm()
    return render(request, 'tasks/habit_form.html', {'form': form})

@login_required
@in_groups(['Admins', 'dev'])
def habit_delete(request, pk):
    habit = get_object_or_404(Habit, pk=pk)
    if request.method == 'POST':
        habit.delete()
        messages.success(request, 'Habit deleted!')
        return redirect('tasks:habit_list')
    return render(request, 'tasks/habit_confirm_delete.html', {'habit': habit})

@login_required
def note_create(request):
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            form.save_m2m()
            messages.success(request, 'Note created!')
            return redirect('tasks:note_list')
    else:
        form = NoteForm()
    return render(request, 'tasks/note_form.html', {'form': form})

@login_required
@in_groups(['Admins', 'dev'])
def note_delete(request, pk):
    note = get_object_or_404(Note, pk=pk)
    if request.method == 'POST':
        note.delete()
        messages.success(request, 'Note deleted!')
        return redirect('tasks:note_list')
    return render(request, 'tasks/note_confirm_delete.html', {'note': note})

@login_required
def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            form.save_m2m()
            messages.success(request, 'Event created!')
            return redirect('tasks:event_list')
    else:
        form = EventForm()
    return render(request, 'tasks/event_form.html', {'form': form})

@login_required
@in_groups(['Admins', 'dev'])
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted!')
        return redirect('tasks:event_list')
    return render(request, 'tasks/event_confirm_delete.html', {'event': event})

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            default_group, _ = Group.objects.get_or_create(name='users')
            user.groups.add(default_group)
            login(request, user)
            messages.success(request, "Registration successful! Welcome!")
            return redirect('tasks:task_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
