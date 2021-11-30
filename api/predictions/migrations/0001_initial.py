# Generated by Django 3.2.9 on 2021-11-29 19:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cleanevent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_ori', models.PositiveIntegerField(db_column='CaseID', unique=True)),
                ('date_time', models.DateTimeField(db_column='StartTime')),
                ('event_type', models.CharField(db_column='CaseTypeName', max_length=50)),
                ('latitude', models.FloatField(db_column='Location_Lat')),
                ('longitude', models.FloatField(db_column='Location_Lng')),
                ('name_poly', models.CharField(blank=True, db_column='poly_name', max_length=50)),
                ('date_hour', models.DateTimeField(db_column='Date_Hour')),
                ('date', models.DateField(db_column='DATE')),
                ('time', models.TimeField(db_column='Time')),
                ('year', models.PositiveIntegerField(db_column='Year')),
                ('month', models.CharField(db_column='Month', max_length=20)),
                ('day_week', models.CharField(db_column='Day_week', max_length=50)),
                ('hour_number', models.PositiveIntegerField(db_column='Hour')),
            ],
        ),
        migrations.CreateModel(
            name='Prediction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parameters', models.JSONField(db_column='parameters')),
                ('predict_json', models.JSONField(db_column='predict_json')),
            ],
        ),
        migrations.CreateModel(
            name='Aditionalevent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_column', models.CharField(choices=[('CloseTime', 'CloseTime'), ('NumLogs', 'NumLogs'), ('CaseTypeId', 'CaseTypeId'), ('ShipType', 'ShipType')], max_length=50)),
                ('values_column', models.CharField(blank=True, max_length=50)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='predictions.cleanevent')),
            ],
        ),
    ]
