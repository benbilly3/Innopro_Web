# Generated by Django 2.0.6 on 2019-09-29 16:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fbCrawler', '0030_auto_20190929_2233'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='checkout',
            name='amount_payable',
        ),
        migrations.AddField(
            model_name='checkout',
            name='transfer_amount',
            field=models.IntegerField(blank=True, null=True, verbose_name='已匯款金額'),
        ),
        migrations.AlterField(
            model_name='orders',
            name='amount',
            field=models.IntegerField(verbose_name='下單數量'),
        ),
    ]
