# Generated by Django 4.1.7 on 2023-06-06 20:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_alter_contact_is_business'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user_info',
            name='profile_picture',
        ),
    ]
