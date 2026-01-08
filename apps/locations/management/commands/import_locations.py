
import json
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from apps.locations.models.location import Location, LocationType, Facility
from django.db import IntegrityError
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Imports locations from a JSON file.'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, nargs='?', help='The path to the JSON file to import.')

    def print_help(self):
        self.stdout.write("Usage: poetry run python manage.py import_locations <file_path>")
        self.stdout.write("The JSON file should be an array of objects with the following structure:")
        self.stdout.write(json.dumps([
            {
                "name": "Example Location",
                "description": "A beautiful place to swim.",
                "location": {
                    "latitude": 59.436962,
                    "longitude": 24.753574
                },
                "address": "Some street 123",
                "city": "Tallinn",
                "country": "Estonia",
                "location_type": f"({', '.join([choice[0] for choice in LocationType.choices])})",
                "facilities": f"({', '.join([choice[0] for choice in Facility.choices])})",
                "access_instructions": "Easy to find.",
                "website": "https://example.com",
                "email": "info@example.com",
                "phone": "123456789",
                "is_free": True,
                "pricing_details": "",
                "is_approved": True,
                "submitted_by_name": "Artjom",
                "submitted_by_email": "artjom@example.com"
            }
        ], indent=2))


    def handle(self, *args, **options):
        file_path = options['file_path']

        if not file_path:
            self.print_help()
            return

        try:
            with open(file_path, 'r') as f:
                locations_data = json.load(f)
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"File not found at: {file_path}"))
            return
        except json.JSONDecodeError:
            self.stderr.write(self.style.ERROR("Could not parse JSON. Please check the file format."))
            return

        for data in locations_data:
            try:
                location_point = data.get('location')
                if not location_point or 'latitude' not in location_point or 'longitude' not in location_point:
                    logger.error(f"Skipping location '{data.get('name', 'N/A')}' due to missing or invalid location data.")
                    continue

                location = Location(
                    name=data.get('name'),
                    description=data.get('description', ''),
                    location=Point(location_point['longitude'], location_point['latitude']),
                    address=data.get('address', ''),
                    city=data.get('city', ''),
                    country=data.get('country', ''),
                    location_type=data.get('location_type', LocationType.WILD),
                    facilities=data.get('facilities', []),
                    access_instructions=data.get('access_instructions', ''),
                    website=data.get('website') or None,
                    email=data.get('email') or None,
                    phone=data.get('phone') or None,
                    is_free=data.get('is_free', True),
                    pricing_details=data.get('pricing_details', ''),
                    is_approved=data.get('is_approved', False),
                    submitted_by_name=data.get('submitted_by_name', ''),
                    submitted_by_email=data.get('submitted_by_email') or None
                )
                location.save()
                self.stdout.write(self.style.SUCCESS(f"Successfully added location: {location.name}"))
            except IntegrityError as e:
                logger.error(f"IntegrityError for location '{data.get('name', 'N/A')}': {e}")
            except Exception as e:
                logger.error(f"Could not add location '{data.get('name', 'N/A')}': {e}")
