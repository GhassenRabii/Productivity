from rest_framework import serializers
from .models import Task, Habit, Note, Event

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'completed', 'user']
        read_only_fields = ['user']

class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = ['id', 'name', 'frequency', 'last_done', 'user']
        read_only_fields = ['user']

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['id', 'title', 'content', 'created', 'user']
        read_only_fields = ['user', 'created']

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'title', 'event_date', 'description', 'user']
        read_only_fields = ['user']
