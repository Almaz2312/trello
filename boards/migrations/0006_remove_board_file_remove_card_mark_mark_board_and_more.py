# Generated by Django 4.1.3 on 2022-11-30 12:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('boards', '0005_board_file'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='board',
            name='file',
        ),
        migrations.RemoveField(
            model_name='card',
            name='mark',
        ),
        migrations.AddField(
            model_name='mark',
            name='board',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='boards.board'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='comment',
            name='card',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment', to='boards.card'),
        ),
        migrations.CreateModel(
            name='MarkCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attached_to_card', to='boards.card')),
                ('mark', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attached_mark', to='boards.mark')),
            ],
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.FileField(upload_to='board_files')),
                ('card', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='file', to='boards.card')),
            ],
        ),
    ]