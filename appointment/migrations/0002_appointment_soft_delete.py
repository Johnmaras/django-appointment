from django.db import migrations, models


class Migration(migrations.Migration):
    """Add soft-delete support to the Appointment model.

    Existing deployments (tables created via syncdb without migrations) should run:
        python manage.py migrate appointment --fake 0001_initial
        python manage.py migrate appointment
    This skips table creation (0001) and only applies the two new columns (0002).

    New deployments: python manage.py migrate
    """

    dependencies = [
        ('appointment', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='appointment',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
