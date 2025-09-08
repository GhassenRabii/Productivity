from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, Group
from django.core.validators import RegexValidator

# -------------- TASK MODEL --------------
class Task(models.Model):
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)
    due_date = models.DateTimeField(null=True, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Medium')
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    tags = models.CharField(max_length=100, blank=True, help_text="Comma-separated tags, e.g. Work, Personal")
    recurring = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    groups = models.ManyToManyField(Group, blank=True, related_name='tasks')

    def __str__(self):
        return self.title

# -------------- HABIT MODEL --------------
class Habit(models.Model):
    FREQUENCY_CHOICES = [
        ('Daily', 'Daily'),
        ('Weekly', 'Weekly'),
        ('Monthly', 'Monthly'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habits')
    name = models.CharField(max_length=200)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default='Daily')
    last_done = models.DateTimeField(null=True, blank=True)
    streak = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)
    tags = models.CharField(max_length=100, blank=True, help_text="Comma-separated tags, e.g. Ideas, Work")
    groups = models.ManyToManyField(Group, blank=True, related_name='habits')

    def __str__(self):
        return self.name

# -------------- NOTE MODEL --------------
class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=200)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    tags = models.CharField(max_length=100, blank=True, help_text="Comma-separated tags, e.g. Ideas, Work")
    groups = models.ManyToManyField(Group, blank=True, related_name='notes')
    
    def __str__(self):
        return self.title

# -------------- EVENT MODEL --------------
class Event(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200)
    event_date = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    reminder = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    tags = models.CharField(max_length=100, blank=True, help_text="Comma-separated tags, e.g. Meeting, Personal")
    groups = models.ManyToManyField(Group, blank=True, related_name='events')
    
    def __str__(self):
        return f"{self.title} ({self.event_date.strftime('%Y-%m-%d %H:%M')})"
phone_validator = RegexValidator(
    regex=r'^\+?[0-9 .\-()]{7,20}$',
    message="Enter a valid phone number."
)


User = get_user_model()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?[0-9 .\-\(\)]{7,20}$',
                message='Enter a valid phone number.',
            )
        ],
    )

    def __str__(self):
        return f"Profile({self.user.username})"


