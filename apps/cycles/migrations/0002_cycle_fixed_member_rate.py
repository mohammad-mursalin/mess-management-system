from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cycles', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cycle',
            name='fixed_member_rate',
            field=models.DecimalField(decimal_places=2, default=30, max_digits=10),
        ),
    ]
