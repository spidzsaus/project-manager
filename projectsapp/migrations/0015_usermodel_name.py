# Generated by Django 5.1.3 on 2025-05-29 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projectsapp', '0014_alter_usermodel_managers'),
    ]

    operations = [
        migrations.AddField(
            model_name='usermodel',
            name='name',
            field=models.CharField(default='aboba', max_length=128, unique=True),
            preserve_default=False,
        ),
    ]
