from django import forms
from .models import Task, Habit, Note, Event

class TaskForm(forms.ModelForm):
    due_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label="Due Date"
    )
    class Meta:
        model = Task
        fields = [
            'title', 'completed', 'due_date', 'priority', 'tags', 
            'recurring', 'notes'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Add details or notes...'}),
            'tags': forms.TextInput(attrs={'placeholder': 'Comma-separated, e.g. Work, Personal'}),
        }
        help_texts = {
            'tags': "You can add multiple tags separated by commas.",
        }

class HabitForm(forms.ModelForm):
    last_done = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Last Done"
    )
    class Meta:
        model = Habit
        fields = [
            'name', 'frequency', 'last_done', 'streak', 'notes'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Habit notes or motivation...'}),
        }
        help_texts = {
            'streak': "How many days/weeks/months in a row you've done this habit.",
        }

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'content', 'tags']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your note here...'}),
            'tags': forms.TextInput(attrs={'placeholder': 'Ideas, Work, Study...'}),
        }

class EventForm(forms.ModelForm):
    event_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label="Event Date"
    )
    reminder = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label="Reminder Time"
    )
    class Meta:
        model = Event
        fields = [
            'title', 'event_date', 'location', 'description', 'reminder', 'tags'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Event details...'}),
            'tags': forms.TextInput(attrs={'placeholder': 'Meeting, Work, Birthday...'}),
        }

