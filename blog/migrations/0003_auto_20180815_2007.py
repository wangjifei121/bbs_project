# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-08-15 12:07
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_auto_20180815_1414'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='tag',
            unique_together=set([('title', 'blog')]),
        ),
    ]