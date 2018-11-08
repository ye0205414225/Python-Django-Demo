# Generated by Django 2.1.1 on 2018-09-26 00:32

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='demo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('crated_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]
