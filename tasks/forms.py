from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Task, Habit, Note, Event

class TaskForm(forms.ModelForm):
    due_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        label="Due Date"
    )
    class Meta:
        model = Task
        fields = [
            'title', 'completed', 'due_date', 'priority', 'tags', 
            'recurring', 'notes'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'What needs to be done?'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Add details or notes...', 'class': 'form-control'}),
            'tags': forms.TextInput(attrs={'placeholder': 'Comma-separated, e.g. Work, Personal', 'class': 'form-control'}),
        }
        help_texts = {
            'tags': "You can add multiple tags separated by commas.",
        }

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "phone", "password1", "password2")



class HabitForm(forms.ModelForm):
    last_done = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Last Done"
    )
    class Meta:
        model = Habit
        fields = [
            'name', 'frequency', 'last_done', 'streak', 'notes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name your habit'}),
            'frequency': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Habit notes or motivation...', 'class': 'form-control'}),
            'streak': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'streak': "How many days/weeks/months in a row you've done this habit.",
        }

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'content', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title of note'}),
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your note here...', 'class': 'form-control'}),
            'tags': forms.TextInput(attrs={'placeholder': 'Ideas, Work, Study...', 'class': 'form-control'}),
        }

class EventForm(forms.ModelForm):
    event_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        label="Event Date"
    )
    reminder = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        label="Reminder Time"
    )
    class Meta:
        model = Event
        fields = [
            'title', 'event_date', 'location', 'description', 'reminder', 'tags'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Event name'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Where?'}),
            'description': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Event details...', 'class': 'form-control'}),
            'tags': forms.TextInput(attrs={'placeholder': 'Meeting, Work, Birthday...', 'class': 'form-control'}),
        }
