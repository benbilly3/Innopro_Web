# Generated by Django 2.0.6 on 2019-08-26 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fbCrawler', '0012_auto_20190826_1741'),
    ]

    operations = [
        migrations.AddField(
            model_name='members',
            name='is_self_take',
            field=models.BooleanField(default=False, verbose_name='是否自取'),
        ),
    ]
