# Generated by Django 2.0.6 on 2019-09-21 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fbCrawler', '0026_members_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='status',
            field=models.CharField(choices=[('open', '進行中'), ('update_orders', '用戶更新訂單'), ('system_updating', '系統計算中'), ('checkout', '用戶匯款'), ('closed', '已結團')], default='open', max_length=20, verbose_name='團次狀態'),
        ),
    ]
