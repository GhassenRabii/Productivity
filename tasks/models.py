from django.db import models

class Task(models.Model):
    title = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class Note(models.Model):
    title=models.CharField(max_length=200)
    content=models.TextField()
    created=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Habit(models.Model):
    name=models.CharField(max_length=200)
    frequency=models.DateTimeField()
    last_done=models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Event(models.Model):
    title=models.CharField(max_length=200)
    event_date=models.DateTimeField()
    description=models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.title} ({self.event_date})"