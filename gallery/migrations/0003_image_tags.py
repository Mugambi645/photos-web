# Generated by Django 5.2.1 on 2025-05-17 14:12

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("gallery", "0002_alter_image_submitter"),
    ]

    operations = [
        migrations.AddField(
            model_name="image",
            name="tags",
            field=models.ManyToManyField(to="gallery.tag"),
        ),
    ]
