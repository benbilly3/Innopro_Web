# Generated by Django 2.0.6 on 2019-10-01 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fbCrawler', '0033_bankstatement'),
    ]

    operations = [
        migrations.AddField(
            model_name='checkout',
            name='amount_payable',
            field=models.IntegerField(blank=True, null=True, verbose_name='應付款項'),
        ),
        migrations.AddField(
            model_name='checkout',
            name='quantity_sum',
            field=models.IntegerField(blank=True, null=True, verbose_name='本期確認購買瓶數'),
        ),
        migrations.AddField(
            model_name='product',
            name='deliver_free',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='sale',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='style',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
