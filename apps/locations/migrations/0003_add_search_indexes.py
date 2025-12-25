"""
Add full-text search indexes and geolocation support.

This migration adds:
- Search vector fields for each language (en, fi, et)
- GIN indexes for full-text search
- Trigram index for fuzzy address matching
- Composite index for common query patterns
"""

from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.db import migrations, models
import django.contrib.postgres.indexes as pg_indexes
from django.contrib.postgres.operations import TrigramExtension


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0002_location_slug'),
    ]

    operations = [
        # Enable PostgreSQL trigram extension for fuzzy matching
        TrigramExtension(),

        # Add search vector columns for each language
        # These are generated fields that automatically maintain search indexes
        migrations.AddField(
            model_name='location',
            name='search_vector_en',
            field=models.GeneratedField(
                expression=SearchVector('name_en', 'description_en', 'address', config='english'),
                output_field=SearchVectorField(),
                db_persist=True,
            ),
        ),
        migrations.AddField(
            model_name='location',
            name='search_vector_fi',
            field=models.GeneratedField(
                expression=SearchVector('name_fi', 'description_fi', 'address', config='finnish'),
                output_field=SearchVectorField(),
                db_persist=True,
            ),
        ),
        migrations.AddField(
            model_name='location',
            name='search_vector_et',
            field=models.GeneratedField(
                expression=SearchVector('name_et', 'description_et', 'address', config='simple'),
                output_field=SearchVectorField(),
                db_persist=True,
            ),
        ),

        # Add GIN indexes for full-text search (one per language)
        migrations.AddIndex(
            model_name='location',
            index=pg_indexes.GinIndex(fields=['search_vector_en'], name='location_search_en_idx'),
        ),
        migrations.AddIndex(
            model_name='location',
            index=pg_indexes.GinIndex(fields=['search_vector_fi'], name='location_search_fi_idx'),
        ),
        migrations.AddIndex(
            model_name='location',
            index=pg_indexes.GinIndex(fields=['search_vector_et'], name='location_search_et_idx'),
        ),

        # Add trigram index on address for fuzzy matching
        migrations.AddIndex(
            model_name='location',
            index=pg_indexes.GinIndex(
                name='location_address_trgm_idx',
                fields=['address'],
                opclasses=['gin_trgm_ops'],
            ),
        ),

        # Add composite index for common query pattern
        migrations.AddIndex(
            model_name='location',
            index=models.Index(
                fields=['is_approved', 'location_type', '-created_at'],
                name='location_list_query_idx'
            ),
        ),
    ]
