# Generated by Django 5.0.6 on 2024-06-13 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0030_subcategory_report_subcategory'),
    ]

    operations = [
        migrations.AddField(
            model_name='profession',
            name='subCategory',
            field=models.ManyToManyField(blank=True, to='main.subcategory'),
        ),
    ]
