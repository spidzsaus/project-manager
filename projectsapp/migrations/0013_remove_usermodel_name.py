# Generated by Django 5.1.3 on 2025-05-29 15:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projectsapp', '0012_alter_usermodel_options_alter_usermodel_managers_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usermodel',
            name='name',
        ),
    ]
