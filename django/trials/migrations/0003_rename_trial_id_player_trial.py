# Generated by Django 4.2.16 on 2024-10-23 12:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trials', '0002_alter_player_role_alter_trial_defendant_claim_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='player',
            old_name='trial_id',
            new_name='trial',
        ),
    ]
