# Generated by Django 3.1.3 on 2020-12-01 11:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0009_auto_20201130_1638'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.CharField(max_length=1000)),
                ('auction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment', to='auctions.auction')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='commentowner', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]