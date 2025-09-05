from rest_framework import serializers
from .models import Task, Habit, Note, Event

class TaskSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # Shows username in API
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'completed', 'due_date', 'priority', 'created',
            'last_modified', 'tags', 'recurring', 'notes', 'user'
        ]
        read_only_fields = ['user', 'created', 'last_modified']

class HabitSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Habit
        fields = [
            'id', 'name', 'frequency', 'last_done', 'streak',
            'created', 'last_modified', 'notes', 'user'
        ]
        read_only_fields = ['user', 'created', 'last_modified', 'streak']

class NoteSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Note
        fields = [
            'id', 'title', 'content', 'created',
            'last_modified', 'tags', 'user'
        ]
        read_only_fields = ['user', 'created', 'last_modified']

class EventSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'event_date', 'location', 'description',
            'reminder', 'created', 'last_modified', 'tags', 'user'
        ]
        read_only_fields = ['user', 'created', 'last_modified']
