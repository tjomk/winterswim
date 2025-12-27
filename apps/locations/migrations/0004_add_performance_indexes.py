"""
Add performance indexes for common query patterns.

This migration adds:
- Spatial GiST index on location field for efficient distance queries
- Index on updated_at for sitemap queries
- Composite index for location type grouping
- Partial index for approved locations (reduces index size)
- Trigram indexes on translated name fields for admin search
"""

from django.db import migrations, models
import django.contrib.postgres.indexes as pg_indexes
import django.contrib.gis.db.models.indexes as gis_indexes


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0003_add_search_indexes'),
    ]

    operations = [
        # Add spatial index on location field for PostGIS distance queries
        # Used by: get_nearby_locations(), get_locations_with_proximity()
        migrations.AddIndex(
            model_name='location',
            index=gis_indexes.GistIndex(
                fields=['location'],
                name='location_spatial_gist_idx'
            ),
        ),

        # Add index on updated_at for sitemap generation
        # Used by: get_locations_for_sitemap()
        migrations.AddIndex(
            model_name='location',
            index=models.Index(
                fields=['-updated_at'],
                name='location_updated_idx'
            ),
        ),

        # Add composite index for location type grouping queries
        # Used by: get_locations_grouped_by_type()
        migrations.AddIndex(
            model_name='location',
            index=models.Index(
                fields=['is_approved', 'location_type', 'name'],
                name='location_type_name_idx'
            ),
        ),

        # Add partial index for approved locations
        # This reduces index size by only indexing approved locations
        # Used by: Most queries filter by is_approved=True
        migrations.AddIndex(
            model_name='location',
            index=models.Index(
                fields=['-created_at'],
                name='location_approved_created_idx',
                condition=models.Q(is_approved=True)
            ),
        ),

        # Add trigram indexes on translated name fields for fuzzy admin search
        # Used by: Admin search_fields
        # Note: Requires pg_trgm extension (already enabled in 0003)
        migrations.AddIndex(
            model_name='location',
            index=pg_indexes.GinIndex(
                fields=['name_en'],
                name='location_name_en_trgm_idx',
                opclasses=['gin_trgm_ops'],
            ),
        ),
        migrations.AddIndex(
            model_name='location',
            index=pg_indexes.GinIndex(
                fields=['name_fi'],
                name='location_name_fi_trgm_idx',
                opclasses=['gin_trgm_ops'],
            ),
        ),
        migrations.AddIndex(
            model_name='location',
            index=pg_indexes.GinIndex(
                fields=['name_et'],
                name='location_name_et_trgm_idx',
                opclasses=['gin_trgm_ops'],
            ),
        ),
    ]
