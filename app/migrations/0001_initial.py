# Generated by Django 5.1.7 on 2025-03-23 04:13

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Lead',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, validators=[django.core.validators.MinLengthValidator(2)])),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(blank=True, max_length=15, null=True, validators=[django.core.validators.RegexValidator('^\\+?\\d{9,15}$', 'Enter a valid phone number with 9 to 15 digits.')])),
                ('service', models.CharField(choices=[('window_replacement', 'Window Replacement'), ('door_installation', 'Door Installation'), ('roof_repair', 'Roof Repair')], default='window_replacement', max_length=100)),
                ('status', models.CharField(choices=[('new', 'New'), ('contacted', 'Contacted'), ('converted', 'Converted')], default='new', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Lead',
                'verbose_name_plural': 'Leads',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender', models.CharField(max_length=100, verbose_name='Sender Name')),
                ('receiver', models.CharField(max_length=100, verbose_name='Receiver Name')),
                ('subject', models.CharField(max_length=200, verbose_name='Message Subject')),
                ('content', models.TextField(verbose_name='Message Content')),
                ('is_read', models.BooleanField(default=False, verbose_name='Read Status')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
            ],
            options={
                'verbose_name': 'Message',
                'verbose_name_plural': 'Messages',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_name', models.CharField(default='Unknown', max_length=255)),
                ('date', models.DateField()),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('in-progress', 'In Progress'), ('completed', 'Completed')], max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('window_style', models.CharField(max_length=100)),
                ('status', models.CharField(choices=[('completed', 'Completed'), ('in-progress', 'In Progress')], max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Quote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=30)),
                ('service', models.CharField(max_length=100)),
                ('windowType', models.CharField(choices=[('double_hung', 'Double Hung'), ('casement', 'Casement'), ('sliding', 'Sliding'), ('bay_bow', 'Picture'), ('custom', 'Custom')], max_length=50)),
                ('details', models.TextField(blank=True)),
                ('city', models.CharField(blank=True, max_length=100)),
                ('state', models.CharField(blank=True, max_length=100)),
                ('zipcode', models.CharField(blank=True, max_length=10)),
                ('property_address', models.CharField(blank=True, max_length=255)),
                ('financing', models.BooleanField(blank=True, null=True)),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_picture', models.ImageField(default='profile_pics/default-profile.png', upload_to='profile_pics/')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
