# Generated by Django 4.1.1 on 2022-11-14 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scaan", "0002_originalfile_savedfile_delete_file"),
    ]

    operations = [
        migrations.AlterField(
            model_name="originalfile",
            name="filepath",
            field=models.FileField(null=True, upload_to="files/"),
        ),
        migrations.AlterField(
            model_name="originalfile",
            name="name",
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name="savedfile",
            name="filepath",
            field=models.FileField(null=True, upload_to="saved/"),
        ),
        migrations.AlterField(
            model_name="savedfile",
            name="name",
            field=models.CharField(max_length=500),
        ),
    ]
