# Generated by Django 2.0.6 on 2019-09-11 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fbCrawler', '0018_session_deliver_rule'),
    ]

    operations = [
        migrations.AlterField(
            model_name='members',
            name='user_profile_url',
            field=models.URLField(blank=True, null=True, verbose_name='FB url'),
        ),
    ]
