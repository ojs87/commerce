# Generated by Django 3.1.3 on 2020-11-30 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_auction_auctionauthor'),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='minimumbid',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=7),
            preserve_default=False,
        ),
    ]