from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='CTFFlag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('challenge_id', models.CharField(max_length=50, unique=True)),
                ('flag', models.CharField(max_length=200)),
                ('category', models.CharField(default='SQLi', max_length=50)),
                ('difficulty', models.CharField(default='Intermediate', max_length=20)),
            ],
            options={
                'verbose_name': 'CTF Flag',
                'verbose_name_plural': 'CTF Flags',
            },
        ),
    ]
