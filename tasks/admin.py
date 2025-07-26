from django.contrib import admin
from .models import Task, Habit, Note, Event

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'completed', 'priority', 'due_date', 'recurring', 'created', 'updated')
    list_filter = ('completed', 'priority', 'due_date', 'recurring', 'tags')
    search_fields = ('title', 'notes', 'tags')
    ordering = ('-created',)
    date_hierarchy = 'due_date'
    readonly_fields = ('created', 'updated')
    fieldsets = (
        (None, {
            'fields': ('title', 'completed', 'priority', 'due_date', 'recurring', 'tags')
        }),
        ('Details', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created', 'updated')
        }),
    )

@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ('name', 'frequency', 'last_done', 'streak', 'created', 'updated')
    list_filter = ('frequency', 'streak')
    search_fields = ('name', 'notes', 'tags')
    ordering = ('-streak',)
    readonly_fields = ('created', 'updated')
    fieldsets = (
        (None, {
            'fields': ('name', 'frequency', 'last_done', 'streak', 'tags')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created', 'updated')
        }),
    )

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'created', 'updated', 'tags')
    list_filter = ('tags',)
    search_fields = ('title', 'content', 'tags')
    ordering = ('-created',)
    readonly_fields = ('created', 'updated')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date', 'location', 'reminder', 'created', 'updated')
    list_filter = ('event_date', 'tags')
    search_fields = ('title', 'description', 'tags')
    ordering = ('event_date',)
    readonly_fields = ('created', 'updated')
    fieldsets = (
        (None, {
            'fields': ('title', 'event_date', 'location', 'reminder', 'tags')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Timestamps', {
            'fields': ('created', 'updated')
        }),
    )
