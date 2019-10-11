# Generated by Django 2.0.6 on 2019-09-19 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fbCrawler', '0022_checkout_transfer_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='status',
            field=models.CharField(choices=[('open', '進行中'), ('update_orders', '更新數量'), ('system_updating', '系統計算中'), ('checkout', '結帳'), ('cloced', '已結團')], default='open', max_length=20, verbose_name='團次狀態'),
        ),
    ]
