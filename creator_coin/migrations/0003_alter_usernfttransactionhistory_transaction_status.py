# Generated by Django 3.2.16 on 2022-11-06 01:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('creator_coin', '0002_auto_20221105_2117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usernfttransactionhistory',
            name='transaction_status',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]