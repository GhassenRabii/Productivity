from django.db import models

# -------------- TASK MODEL --------------
class Task(models.Model):
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]
    title = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)
    due_date = models.DateTimeField(null=True, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Medium')
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    tags = models.CharField(max_length=100, blank=True, help_text="Comma-separated tags, e.g. Work, Personal")
    recurring = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.title

# -------------- HABIT MODEL --------------
class Habit(models.Model):
    FREQUENCY_CHOICES = [
        ('Daily', 'Daily'),
        ('Weekly', 'Weekly'),
        ('Monthly', 'Monthly'),
    ]
    name = models.CharField(max_length=200)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default='Daily')
    last_done = models.DateField(null=True, blank=True)
    streak = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.name

# -------------- NOTE MODEL --------------
class Note(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    tags = models.CharField(max_length=100, blank=True, help_text="Comma-separated tags, e.g. Ideas, Work")

    def __str__(self):
        return self.title

# -------------- EVENT MODEL --------------
class Event(models.Model):
    title = models.CharField(max_length=200)
    event_date = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    reminder = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    tags = models.CharField(max_length=100, blank=True, help_text="Comma-separated tags, e.g. Meeting, Personal")

    def __str__(self):
        return f"{self.title} ({self.event_date.strftime('%Y-%m-%d %H:%M')})"

