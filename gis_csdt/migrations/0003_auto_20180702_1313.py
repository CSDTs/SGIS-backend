# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-07-02 17:13
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('gis_csdt', '0002_phonenumber'),
    ]

    operations = [
        migrations.CreateModel(
            name='DatasetNameField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field1_en', models.CharField(blank=True, max_length=150)),
                ('field1_name', models.CharField(blank=True, max_length=50)),
                ('field2_en', models.CharField(blank=True, max_length=150)),
                ('field2_name', models.CharField(blank=True, max_length=50)),
                ('field3_en', models.CharField(blank=True, max_length=150)),
                ('field3_name', models.CharField(blank=True, max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='GeoCoordinates',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lat_field', models.CharField(blank=True, default=b'latitude', max_length=50)),
                ('lon_field', models.CharField(blank=True, default=b'longitude', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('street_field', models.CharField(blank=True, default=b'street', max_length=50)),
                ('city_field', models.CharField(blank=True, default=b'city', max_length=50)),
                ('state_field', models.CharField(blank=True, default=b'state', max_length=50)),
                ('zipcode_field', models.CharField(blank=True, default=b'zip', max_length=50)),
                ('county_field', models.CharField(blank=True, default=b'county', max_length=50)),
            ],
        ),
        migrations.RemoveField(
            model_name='observation',
            name='mapelement',
        ),
        migrations.RemoveField(
            model_name='observation',
            name='sensor',
        ),
        migrations.AlterUniqueTogether(
            name='observationvalue',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='observationvalue',
            name='observation',
        ),
        migrations.RemoveField(
            model_name='datapoint',
            name='point',
        ),
        migrations.RemoveField(
            model_name='datapoint',
            name='sensor',
        ),
        migrations.RemoveField(
            model_name='datapoint',
            name='user',
        ),
        migrations.RemoveField(
            model_name='dataset',
            name='city_field',
        ),
        migrations.RemoveField(
            model_name='dataset',
            name='county_field',
        ),
        migrations.RemoveField(
            model_name='dataset',
            name='field1_en',
        ),
        migrations.RemoveField(
            model_name='dataset',
            name='field1_name',
        ),
        migrations.RemoveField(
            model_name='dataset',
            name='field2_en',
        ),
        migrations.RemoveField(
            model_name='dataset',
            name='field2_name',
        ),
        migrations.RemoveField(
            model_name='dataset',
            name='field3_en',
        ),
        migrations.RemoveField(
            model_name='dataset',
            name='field3_name',
        ),
        migrations.RemoveField(
            model_name='dataset',
            name='lat_field',
        ),
        migrations.RemoveField(
            model_name='dataset',
            name='lon_field',
        ),
        migrations.RemoveField(
            model_name='dataset',
            name='state_field',
        ),
        migrations.RemoveField(
            model_name='dataset',
            name='street_field',
        ),
        migrations.RemoveField(
            model_name='dataset',
            name='zipcode_field',
        ),
        migrations.AddField(
            model_name='datapoint',
            name='time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='sensor',
            name='datapoints',
            field=models.ManyToManyField(blank=True, to='gis_csdt.DataPoint'),
        ),
        migrations.AddField(
            model_name='sensor',
            name='mappoint',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='points', to='gis_csdt.MapPoint'),
        ),
        migrations.AddField(
            model_name='sensor',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='Observation',
        ),
        migrations.DeleteModel(
            name='ObservationValue',
        ),
        migrations.AddField(
            model_name='dataset',
            name='coordinates',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='gis_csdt.GeoCoordinates'),
        ),
        migrations.AddField(
            model_name='dataset',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='gis_csdt.Location'),
        ),
        migrations.AddField(
            model_name='dataset',
            name='names',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='gis_csdt.DatasetNameField'),
        ),
    ]
