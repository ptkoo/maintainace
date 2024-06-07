# Generated by Django 5.0.6 on 2024-06-06 02:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0022_alter_image_report_solution_image_solution'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='image',
            name='solution',
        ),
        migrations.CreateModel(
            name='ImageSolution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imageData', models.ImageField(blank=True, null=True, upload_to='solutionImages/')),
                ('solution', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='images', to='main.solution')),
            ],
            options={
                'db_table': 'imageForSolution',
            },
        ),
    ]
