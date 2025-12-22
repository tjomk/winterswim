"""
Management command to generate random test locations in Estonia.
"""

import random
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from apps.locations.models import Location, LocationType, Facility


class Command(BaseCommand):
    help = 'Generate 50 random winter swimming locations in Estonia for testing'

    # Estonia bounds: roughly 57.5-59.7°N, 21.5-28.2°E
    ESTONIA_LAT_MIN = 57.5
    ESTONIA_LAT_MAX = 59.7
    ESTONIA_LON_MIN = 21.5
    ESTONIA_LON_MAX = 28.2

    # Estonian place names and features for realistic names
    ESTONIAN_PLACES = [
        'Tallinn', 'Tartu', 'Pärnu', 'Narva', 'Kohtla-Järve',
        'Viljandi', 'Rakvere', 'Maardu', 'Sillamäe', 'Kuressaare',
        'Võru', 'Valga', 'Haapsalu', 'Jõhvi', 'Paide',
        'Keila', 'Kiviõli', 'Tapa', 'Põlva', 'Türi',
        'Elva', 'Saue', 'Sindi', 'Kärdla', 'Võhma',
        'Kallaste', 'Tamsalu', 'Otepää', 'Kehra', 'Rapla',
        'Paldiski', 'Kunda', 'Põltsamaa', 'Mustvee', 'Võsu',
    ]

    WATER_FEATURES = [
        'Beach', 'Bay', 'Lake', 'River', 'Harbor',
        'Shore', 'Coast', 'Pier', 'Marina', 'Port',
        'Strand', 'Inlet', 'Cove', 'Waterfront', 'Dock',
    ]

    FACILITY_TYPES = [
        'Avanto', 'Ice Hole', 'Winter Swimming Spot', 'Swimming Club',
        'Sauna Complex', 'Public Beach', 'Wild Spot', 'Swimming Point',
        'Wellness Center', 'Recreation Area', 'Natural Pool', 'Swimming Facility',
    ]

    DESCRIPTIONS = [
        'A beautiful spot perfect for winter swimming enthusiasts.',
        'Popular location with excellent facilities and easy access.',
        'Scenic natural location ideal for cold water swimming.',
        'Well-maintained facility with regular winter swimmers.',
        'Hidden gem known to local swimming community.',
        'Traditional winter swimming spot with great atmosphere.',
        'Modern facility with all necessary amenities.',
        'Peaceful location surrounded by nature.',
        'Active swimming community meets here regularly.',
        'Beginner-friendly location with gentle access.',
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing locations before generating new ones',
        )
        parser.add_argument(
            '--count',
            type=int,
            default=50,
            help='Number of locations to generate (default: 50)',
        )

    def handle(self, *args, **options):
        count = options['count']

        if options['clear']:
            deleted_count = Location.objects.all().count()
            Location.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(f'Deleted {deleted_count} existing locations')
            )

        self.stdout.write(f'Generating {count} random locations in Estonia...')

        locations_created = 0

        for i in range(count):
            location = self.create_random_location()
            locations_created += 1

            if (i + 1) % 10 == 0:
                self.stdout.write(f'Created {i + 1}/{count} locations...')

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully created {locations_created} random locations!'
            )
        )

    def create_random_location(self):
        """Create a single random location."""

        # Generate random coordinates within Estonia
        lat = random.uniform(self.ESTONIA_LAT_MIN, self.ESTONIA_LAT_MAX)
        lon = random.uniform(self.ESTONIA_LON_MIN, self.ESTONIA_LON_MAX)
        point = Point(lon, lat, srid=4326)

        # Generate a name
        place = random.choice(self.ESTONIAN_PLACES)
        feature = random.choice(self.WATER_FEATURES)
        facility_type = random.choice(self.FACILITY_TYPES)

        name_patterns = [
            f'{place} {feature}',
            f'{place} {facility_type}',
            f'{feature} at {place}',
            f'{place} Winter Swimming',
            f'{facility_type} {place}',
        ]
        name = random.choice(name_patterns)

        # Random location type
        location_type = random.choice(list(LocationType.values))

        # Random facilities
        all_facilities = list(Facility.values)
        num_facilities = random.randint(0, 5)
        facilities = random.sample(all_facilities, num_facilities) if num_facilities > 0 else []

        # Random pricing
        is_free = random.choice([True, True, True, False])  # 75% free
        pricing_details = '' if is_free else f'{random.randint(3, 15)} EUR per visit'

        # Random approval status (80% approved for testing)
        is_approved = random.choice([True, True, True, True, False])

        # Create the location
        location_obj = Location.objects.create(
            name=name,
            description=random.choice(self.DESCRIPTIONS),
            location=point,
            address=f'{place}, Estonia' if random.random() > 0.3 else '',
            location_type=location_type,
            facilities=facilities,
            access_instructions=random.choice([
                'Follow the signs from the parking area.',
                'Access from the main road, 5 minutes walk.',
                'Enter through the main gate.',
                'Located near the town center.',
                '',
            ]),
            website=f'https://example.com/{place.lower()}' if random.random() > 0.6 else '',
            email=f'info@{place.lower()}.ee' if random.random() > 0.7 else '',
            phone=f'+372 {random.randint(5000000, 5999999)}' if random.random() > 0.7 else '',
            is_free=is_free,
            pricing_details=pricing_details,
            is_approved=is_approved,
            submitted_by_name=random.choice(['', 'Test User', 'Admin', 'Community Member']),
        )

        return location_obj
