# Generated by Django 3.2.8 on 2022-09-20 17:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jenkins', '0005_auto_20220917_1803'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pushnotification',
            name='developer',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
