# Generated by Django 3.2.16 on 2022-11-13 02:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('creator_coin', '0004_userbetaemails_creator_obj'),
    ]

    operations = [
        migrations.AlterField(
            model_name='githubprofile',
            name='user_obj',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
