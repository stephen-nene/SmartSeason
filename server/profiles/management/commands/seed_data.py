# seeds.py
import os
import sys
import django
from datetime import date, timedelta
from django.utils import timezone
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from profiles.models import Field, FieldAssignment, UserRole, UserStatus
from seasons.models import CropType, CropSeason, FieldUpdate, FieldUpdateStage, SeasonStatus

User = get_user_model()


def seed_users():
    """Create all user types - admin, coordinators, and field agents"""
    users = {}

    # Admin user
    admin, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@agritech.com',
            'role': UserRole.ADMIN,
            'status': UserStatus.ACTIVE,
            'is_staff': True,
            'is_superuser': True,
            'email_verified': True,
        }
    )
    if created:
        admin.set_password('admin123!')
        admin.save()
    users['admin'] = admin
    print(f"Admin created: {admin.username}")

    # Coordinator users
    coordinators_data = [
        {
            'username': 'coordinator_north',
            'email': 'coordinator.north@agritech.com',
            'first_name': 'Jane',
            'last_name': 'Smith',
        },
        {
            'username': 'coordinator_south',
            'email': 'coordinator.south@agritech.com',
            'first_name': 'Robert',
            'last_name': 'Johnson',
        },
    ]

    for coord_data in coordinators_data:
        coordinator, created = User.objects.get_or_create(
            username=coord_data['username'],
            defaults={
                **coord_data,
                'role': UserRole.COORDINATOR,
                'status': UserStatus.ACTIVE,
                'email_verified': True,
            }
        )
        if created:
            coordinator.set_password('coord123!')
            coordinator.save()
        users[coordinator.username] = coordinator
        print(f"Coordinator created: {coordinator.username}")

    # Field Agent users
    field_agents_data = [
        {
            'username': 'agent_mwangi',
            'email': 'mwangi.field@agritech.com',
            'first_name': 'James',
            'last_name': 'Mwangi',
            'phone_number': '+254712345678',
        },
        {
            'username': 'agent_akinyi',
            'email': 'akinyi.field@agritech.com',
            'first_name': 'Grace',
            'last_name': 'Akinyi',
            'phone_number': '+254723456789',
        },
        {
            'username': 'agent_kiprop',
            'email': 'kiprop.field@agritech.com',
            'first_name': 'Daniel',
            'last_name': 'Kiprop',
            'phone_number': '+254734567890',
        },
        {
            'username': 'agent_wanjiku',
            'email': 'wanjiku.field@agritech.com',
            'first_name': 'Alice',
            'last_name': 'Wanjiku',
            'phone_number': '+254745678901',
        },
        {
            'username': 'agent_otieno',
            'email': 'otieno.field@agritech.com',
            'first_name': 'Peter',
            'last_name': 'Otieno',
            'phone_number': '+254756789012',
        },
    ]

    for agent_data in field_agents_data:
        agent, created = User.objects.get_or_create(
            username=agent_data['username'],
            defaults={
                **agent_data,
                'role': UserRole.FIELD_AGENT,
                'status': UserStatus.ACTIVE,
                'email_verified': True,
            }
        )
        if created:
            agent.set_password('agent123!')
            agent.save()
        users[agent.username] = agent
        print(f"Field Agent created: {agent.username}")

    return users


def seed_crop_types():
    """Create common crop types with growth cycles"""
    crop_types = {}

    crops_data = [
        {
            'name': 'Maize',
            'description': 'Corn/maize - staple grain crop. Requires moderate rainfall and well-drained soil.',
            'growth_cycle_days': 120,
        },
        {
            'name': 'Wheat',
            'description': 'Winter wheat variety. Suitable for cooler climates with good soil preparation.',
            'growth_cycle_days': 150,
        },
        {
            'name': 'Rice',
            'description': 'Paddy rice - requires flooded conditions during growing period.',
            'growth_cycle_days': 130,
        },
        {
            'name': 'Tomatoes',
            'description': 'Fresh market tomatoes. Requires staking and regular pest management.',
            'growth_cycle_days': 80,
        },
        {
            'name': 'Potatoes',
            'description': 'Irish potatoes - requires well-drained sandy loam soil.',
            'growth_cycle_days': 100,
        },
        {
            'name': 'Beans',
            'description': 'Common beans - nitrogen-fixing legume, good for crop rotation.',
            'growth_cycle_days': 75,
        },
        {
            'name': 'Coffee',
            'description': 'Arabica coffee - long-term perennial crop requiring shade management.',
            'growth_cycle_days': 270,
        },
        {
            'name': 'Tea',
            'description': 'Tea bushes - perennial crop for high altitude areas with acidic soils.',
            'growth_cycle_days': 300,
        },
        {
            'name': 'Avocado',
            'description': 'Hass avocado variety - requires grafting and proper orchard management.',
            'growth_cycle_days': 365,
        },
        {
            'name': 'Onions',
            'description': 'Bulb onions - requires short day varieties for tropical regions.',
            'growth_cycle_days': 100,
        },
    ]

    for crop_data in crops_data:
        crop, created = CropType.objects.get_or_create(
            name=crop_data['name'],
            defaults=crop_data
        )
        crop_types[crop.name.lower()] = crop
        print(f"Crop Type {'created' if created else 'exists'}: {crop.name}")

    return crop_types


def seed_fields():
    """Create field/farm locations"""
    fields = {}

    fields_data = [
        {
            'name': 'North Field - Plot A',
            'description': '5-acre plot in northern sector. Well-drained loamy soil with irrigation access.',
            'max_active_seasons': 1,
        },
        {
            'name': 'North Field - Plot B',
            'description': '3-acre plot adjacent to river. Silty soil, good for rice cultivation.',
            'max_active_seasons': 1,
        },
        {
            'name': 'South Field - Block 1',
            'description': '10-acre main block with drip irrigation system installed.',
            'max_active_seasons': 2,
        },
        {
            'name': 'South Field - Block 2',
            'description': '7-acre block with greenhouse facilities for vegetables.',
            'max_active_seasons': 2,
        },
        {
            'name': 'East Valley Orchard',
            'description': '15-acre orchard for fruit trees and coffee plantation.',
            'max_active_seasons': 3,
        },
        {
            'name': 'West Highland Garden',
            'description': '2-acre highland garden suitable for tea and cool-season crops.',
            'max_active_seasons': 1,
        },
        {
            'name': 'Central Greenhouse Complex',
            'description': 'Climate-controlled greenhouse for tomatoes and specialty crops.',
            'max_active_seasons': 2,
        },
        {
            'name': 'Riverbank Rice Paddies',
            'description': '8-acre flood-irrigated paddies specifically for rice cultivation.',
            'max_active_seasons': 1,
        },
    ]

    for field_data in fields_data:
        field, created = Field.objects.get_or_create(
            name=field_data['name'],
            defaults=field_data
        )
        fields[field.name] = field
        print(f"Field {'created' if created else 'exists'}: {field.name}")

    return fields


def seed_field_assignments(users, fields):
    """Assign field agents to specific fields"""
    assignments = []

    assignment_map = {
        'agent_mwangi': ['North Field - Plot A', 'North Field - Plot B'],
        'agent_akinyi': ['South Field - Block 1', 'South Field - Block 2'],
        'agent_kiprop': ['East Valley Orchard'],
        'agent_wanjiku': ['West Highland Garden', 'Central Greenhouse Complex'],
        'agent_otieno': ['Riverbank Rice Paddies'],
    }

    for agent_username, field_names in assignment_map.items():
        agent = users.get(agent_username)
        admin = users.get('admin')

        if not agent:
            print(f"Warning: Agent {agent_username} not found")
            continue

        for field_name in field_names:
            field = fields.get(field_name)
            if not field:
                print(f"Warning: Field {field_name} not found")
                continue

            assignment, created = FieldAssignment.objects.get_or_create(
                field=field,
                agent=agent,
                defaults={'assigned_by': admin}
            )
            assignments.append(assignment)
            print(f"Assignment {'created' if created else 'exists'}: {agent.username} -> {field.name}")

    return assignments


def seed_crop_seasons(users, fields, crop_types):
    """Create active and completed crop seasons"""
    seasons = []
    today = timezone.now().date()

    # Active seasons for field agents to update
    active_seasons_data = [
        {
            'name': 'Maize - North A - 2024',
            'field_name': 'North Field - Plot A',
            'crop_type_name': 'Maize',
            'planting_date': today - timedelta(days=30),
            'expected_harvest_date': today + timedelta(days=90),
            'status': SeasonStatus.ACTIVE,
            'current_stage': FieldUpdateStage.GROWING,
            'created_by_username': 'agent_mwangi',
        },
        {
            'name': 'Rice - North B - 2024',
            'field_name': 'North Field - Plot B',
            'crop_type_name': 'Rice',
            'planting_date': today - timedelta(days=15),
            'expected_harvest_date': today + timedelta(days=115),
            'status': SeasonStatus.ACTIVE,
            'current_stage': FieldUpdateStage.PLANTED,
            'created_by_username': 'agent_mwangi',
        },
        {
            'name': 'Tomatoes - South 1 - 2024',
            'field_name': 'South Field - Block 1',
            'crop_type_name': 'Tomatoes',
            'planting_date': today - timedelta(days=50),
            'expected_harvest_date': today + timedelta(days=30),
            'status': SeasonStatus.ACTIVE,
            'current_stage': FieldUpdateStage.GROWING,
            'created_by_username': 'agent_akinyi',
        },
        {
            'name': 'Coffee - East Orchard - 2024',
            'field_name': 'East Valley Orchard',
            'crop_type_name': 'Coffee',
            'planting_date': today - timedelta(days=180),
            'expected_harvest_date': today + timedelta(days=90),
            'status': SeasonStatus.ACTIVE,
            'current_stage': FieldUpdateStage.GROWING,
            'created_by_username': 'agent_kiprop',
        },
        {
            'name': 'Tea - West Highland - 2024',
            'field_name': 'West Highland Garden',
            'crop_type_name': 'Tea',
            'planting_date': today - timedelta(days=200),
            'expected_harvest_date': today + timedelta(days=100),
            'status': SeasonStatus.ACTIVE,
            'current_stage': FieldUpdateStage.GROWING,
            'created_by_username': 'agent_wanjiku',
        },
        {
            'name': 'Onions - South 2 - 2024',
            'field_name': 'South Field - Block 2',
            'crop_type_name': 'Onions',
            'planting_date': today - timedelta(days=60),
            'expected_harvest_date': today + timedelta(days=40),
            'status': SeasonStatus.ACTIVE,
            'current_stage': FieldUpdateStage.GROWING,
            'created_by_username': 'agent_akinyi',
        },
        # At-risk season (past expected harvest)
        {
            'name': 'Beans - Riverbank - 2024 Late',
            'field_name': 'Riverbank Rice Paddies',
            'crop_type_name': 'Beans',
            'planting_date': today - timedelta(days=90),
            'expected_harvest_date': today - timedelta(days=5),  # Overdue
            'status': SeasonStatus.AT_RISK,
            'current_stage': FieldUpdateStage.GROWING,
            'created_by_username': 'agent_otieno',
        },
        # Completed season
        {
            'name': 'Potatoes - Central GH - 2024 Q1',
            'field_name': 'Central Greenhouse Complex',
            'crop_type_name': 'Potatoes',
            'planting_date': today - timedelta(days=120),
            'expected_harvest_date': today - timedelta(days=20),
            'actual_harvest_date': today - timedelta(days=18),
            'status': SeasonStatus.COMPLETED,
            'current_stage': FieldUpdateStage.HARVESTED,
            'created_by_username': 'agent_wanjiku',
        },
    ]

    for season_data in active_seasons_data:
        field = fields.get(season_data['field_name'])
        crop_type = crop_types.get(season_data['crop_type_name'].lower())
        created_by = users.get(season_data['created_by_username'])

        if not all([field, crop_type, created_by]):
            print(f"Warning: Missing data for season {season_data['name']}")
            continue

        season_defaults = {
            'field': field,
            'crop_type': crop_type,
            'planting_date': season_data['planting_date'],
            'expected_harvest_date': season_data['expected_harvest_date'],
            'status': season_data['status'],
            'current_stage': season_data['current_stage'],
            'created_by': created_by,
        }

        if 'actual_harvest_date' in season_data:
            season_defaults['actual_harvest_date'] = season_data['actual_harvest_date']

        season, created = CropSeason.objects.get_or_create(
            name=season_data['name'],
            defaults=season_defaults
        )
        seasons.append(season)
        print(f"Crop Season {'created' if created else 'exists'}: {season.name} [{season.status}]")

    return seasons


def seed_field_updates(users, seasons):
    """Create sample field updates from agents"""
    updates = []

    # Find active seasons for each agent
    for season in seasons:
        if season.status == SeasonStatus.COMPLETED:
            continue

        # Get the agent assigned to this season's field
        assignment = FieldAssignment.objects.filter(field=season.field).first()
        if not assignment:
            continue

        agent = assignment.agent
        days_ago = (timezone.now().date() - season.planting_date).days

        # Create planting update
        update1, created1 = FieldUpdate.objects.get_or_create(
            crop_season=season,
            stage=FieldUpdateStage.PLANTED,
            defaults={
                'agent': agent,
                'notes': f'Successfully planted {season.crop_type.name} on {season.planting_date}. Soil was well-prepared with organic compost added.',
            }
        )
        if created1:
            update1.created_at = season.planting_date
            update1.save()
        updates.append(update1)

        # Create growing update for seasons that have been active > 20 days
        if days_ago > 20:
            update2, created2 = FieldUpdate.objects.get_or_create(
                crop_season=season,
                stage=FieldUpdateStage.GROWING,
                defaults={
                    'agent': agent,
                    'notes': f'Crop showing good vegetative growth. No major pest or disease issues observed. Applied top-dressing fertilizer as recommended.',
                }
            )
            if created2:
                update2.created_at = season.planting_date + timedelta(days=20)
                update2.save()
            updates.append(update2)

    print(f"Created {len(updates)} field updates")


def main():
    """Main seed function"""
    print("=" * 60)
    print("STARTING DATABASE SEEDING")
    print("=" * 60)

    # Seed in order of dependencies
    print("\n1. Seeding Users...")
    print("-" * 40)
    users = seed_users()

    print("\n2. Seeding Crop Types...")
    print("-" * 40)
    crop_types = seed_crop_types()

    print("\n3. Seeding Fields...")
    print("-" * 40)
    fields = seed_fields()

    print("\n4. Seeding Field Assignments...")
    print("-" * 40)
    seed_field_assignments(users, fields)

    print("\n5. Seeding Crop Seasons...")
    print("-" * 40)
    seasons = seed_crop_seasons(users, fields, crop_types)

    print("\n6. Seeding Field Updates...")
    print("-" * 40)
    seed_field_updates(users, seasons)

    print("\n" + "=" * 60)
    print("DATABASE SEEDING COMPLETE!")
    print("=" * 60)

    print("\nLogin Credentials:")
    print("-" * 40)
    print("Admin:     admin / admin123!")
    print("Coordinators: coordinator_north / coord123!")
    print("              coordinator_south / coord123!")
    print("Field Agents:  agent_mwangi / agent123!")
    print("               agent_akinyi / agent123!")
    print("               agent_kiprop / agent123!")
    print("               agent_wanjiku / agent123!")
    print("               agent_otieno / agent123!")


if __name__ == '__main__':
    main()
