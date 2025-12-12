# Generated manually for adding Favorite model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('biblio', '0005_remove_book_cover_url_book_cover_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorited_by', to='biblio.book')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Favori',
                'verbose_name_plural': 'Favoris',
                'ordering': ['-added_at'],
                'unique_together': {('user', 'book')},
            },
        ),
    ]
