# Generated by Django 5.1.6 on 2025-03-02 08:50

import quiz.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0010_testsession_questions'),
    ]

    operations = [
        migrations.AddField(
            model_name='useranswer',
            name='hint',
            field=models.TextField(blank=True, default='', max_length=255, verbose_name=quiz.models.Question),
        ),
    ]
