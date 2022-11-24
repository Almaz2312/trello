# Generated by Django 4.1.3 on 2022-11-24 10:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('boards', '0002_lastseen'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='board',
            name='members',
        ),
        migrations.AlterField(
            model_name='board',
            name='background',
            field=models.ImageField(blank=True, null=True, upload_to='board_background'),
        ),
        migrations.CreateModel(
            name='Members',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('board', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='boards.board')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
