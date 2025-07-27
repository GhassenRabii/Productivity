# tasks/migrations/0002_add_groups_to_models.py
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='groups',
            field=models.ManyToManyField(
                blank=True,
                to='auth.Group',
                related_name='tasks'
            ),
        ),
        migrations.AddField(
            model_name='habit',
            name='groups',
            field=models.ManyToManyField(
                blank=True,
                to='auth.Group',
                related_name='habits'
            ),
        ),
        migrations.AddField(
            model_name='note',
            name='groups',
            field=models.ManyToManyField(
                blank=True,
                to='auth.Group',
                related_name='notes'
            ),
        ),
        migrations.AddField(
            model_name='event',
            name='groups',
            field=models.ManyToManyField(
                blank=True,
                to='auth.Group',
                related_name='events'
            ),
        ),
    ]
