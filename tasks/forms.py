from django import forms
from .models import Task, Habit, Note, Event

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'completed']

class HabitForm(forms.ModelForm):
    class Meta:
        model = Habit
        fields = ['name', 'frequency', 'last_done']

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'content']

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'event_date', 'description']
