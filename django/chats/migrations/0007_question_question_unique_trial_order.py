# Generated by Django 4.2.16 on 2024-10-26 06:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trials', '0005_alter_gamestate_state'),
        ('chats', '0006_good_unique_good'),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('order', models.PositiveIntegerField()),
                ('trial', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='trials.trial')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.AddConstraint(
            model_name='question',
            constraint=models.UniqueConstraint(fields=('trial', 'order'), name='unique_trial_order'),
        ),
    ]
