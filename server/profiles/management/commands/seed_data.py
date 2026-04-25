# profiles/management/commands/seed_data.py
import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model

from profiles.models import Field, FieldAssignment
from seasons.models import CropType, CropSeason, FieldUpdate

# Import your seed data
from .data import (
    USERS, CROP_TYPES, FIELDS, CROP_SEASONS,
    FIELD_ASSIGNMENTS, FIELD_UPDATES, resolve_seed_data
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed database with sample users, fields, crops, seasons, assignments, and updates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )
        parser.add_argument(
            '--skip-users',
            action='store_true',
            help='Skip user creation (use if users already exist)',
        )

    def handle(self, *args, **options):
        today = timezone.now().date()

        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            FieldUpdate.objects.all().delete()
            CropSeason.objects.all().delete()
            FieldAssignment.objects.all().delete()
            Field.objects.all().delete()
            CropType.objects.all().delete()
            if not options['skip_users']:
                User.objects.filter(is_superuser=False).delete()

        # Create users
        created_users = []
        if not options['skip_users']:
            self.stdout.write('Creating users...')
            for user_data in USERS:
                user, created = User.objects.get_or_create(
                    username=user_data['username'],
                    defaults={
                        'email': user_data['email'],
                        'phone_number': user_data.get('phone_number'),
                        'role': user_data['role'],
                        'status': user_data['status'],
                        'is_staff': user_data.get('is_staff', False),
                        'is_superuser': user_data.get('is_superuser', False),
                    }
                )
                if created:
                    user.set_password(user_data['password'])
                    user.save()
                    self.stdout.write(f'  Created user: {user.username} ({user.role})')
                else:
                    self.stdout.write(f'  User exists: {user.username}')
                created_users.append(user)
        else:
            created_users = list(User.objects.all().order_by('date_joined'))
            self.stdout.write(f'Using {len(created_users)} existing users')

        # Create crop types
        self.stdout.write('\nCreating crop types...')
        created_crop_types = []
        for crop_data in CROP_TYPES:
            crop, created = CropType.objects.get_or_create(
                name=crop_data['name'],
                defaults={
                    'description': crop_data['description'],
                    'growth_cycle_days': crop_data['growth_cycle_days'],
                }
            )
            status = 'Created' if created else 'Exists'
            self.stdout.write(f'  {status}: {crop.name} ({crop.growth_cycle_days} days)')
            created_crop_types.append(crop)

        # Create fields
        self.stdout.write('\nCreating fields...')
        created_fields = []
        for field_data in FIELDS:
            field, created = Field.objects.get_or_create(
                name=field_data['name'],
                defaults={'description': field_data['description']}
            )
            status = 'Created' if created else 'Exists'
            self.stdout.write(f'  {status}: {field.name}')
            created_fields.append(field)

        # Create crop seasons
        self.stdout.write('\nCreating crop seasons...')
        created_seasons = []
        admin_user = created_users[0]

        for season_data in CROP_SEASONS:
            season, created = CropSeason.objects.get_or_create(
                name=season_data['name'],
                defaults={
                    'field': created_fields[season_data['field_index']],
                    'crop_type': created_crop_types[season_data['crop_type_index']],
                    'planting_date': season_data['planting_date'],
                    'expected_harvest_date': season_data['expected_harvest_date'],
                    'actual_harvest_date': season_data.get('actual_harvest_date'),
                    'status': season_data['status'],
                    'current_stage': season_data['current_stage'],
                    'active': season_data.get('active', True),
                    'created_by': admin_user,
                }
            )
            status = 'Created' if created else 'Exists'
            active_marker = ' [ACTIVE]' if season.active else ''
            self.stdout.write(f'  {status}: {season.name} - {season.current_stage}{active_marker}')
            created_seasons.append(season)

        # Create field assignments
        self.stdout.write('\nCreating field assignments...')
        resolved_assignments, resolved_updates = resolve_seed_data(
            created_users, created_crop_types, created_fields, created_seasons
        )

        assignment_count = 0
        for assignment_data in resolved_assignments:
            _, created = FieldAssignment.objects.get_or_create(
                field=assignment_data['field'],
                agent=assignment_data['agent'],
                defaults={'assigned_by': assignment_data['assigned_by']}
            )
            if created:
                self.stdout.write(
                    f'  Assigned: {assignment_data["agent"].username} -> '
                    f'{assignment_data["field"].name}'
                )
                assignment_count += 1

        # Create field updates with custom timestamps
        self.stdout.write('\nCreating field updates...')
        update_count = 0
        for update_data in resolved_updates:
            update = FieldUpdate(
                crop_season=update_data['crop_season'],
                agent=update_data['agent'],
                stage=update_data['stage'],
                notes=update_data['notes'],
            )
            # Save with skip_validation for historical/completed seasons
            update.save(skip_validation=True)

            # Override created_at with timezone-aware datetime
            naive_datetime = update_data['created_at_override']
            aware_datetime = timezone.make_aware(
                timezone.datetime.combine(naive_datetime, timezone.datetime.min.time())
            )
            FieldUpdate.objects.filter(pk=update.pk).update(
                created_at=aware_datetime,
                updated_at=aware_datetime,
            )
            self.stdout.write(
                f'  Update: {update.crop_season.name} -> {update.get_stage_display()} '
                f'by {update.agent.username}'
            )
            update_count += 1

        # Summary
        self.stdout.write(self.style.SUCCESS(f'\n{"="*50}'))
        self.stdout.write(self.style.SUCCESS('SEEDING COMPLETE'))
        self.stdout.write(self.style.SUCCESS(f'{"="*50}'))
        self.stdout.write(f'  Users:           {len(created_users)}')
        self.stdout.write(f'  Crop Types:      {len(created_crop_types)}')
        self.stdout.write(f'  Fields:          {len(created_fields)}')
        self.stdout.write(f'  Crop Seasons:    {len(created_seasons)}')
        self.stdout.write(f'  Active Seasons:  {sum(1 for s in created_seasons if s.active)}')
        self.stdout.write(f'  Assignments:     {assignment_count}')
        self.stdout.write(f'  Field Updates:   {update_count}')




# # Basic seeding
# python manage.py seed_data

# # Clear existing data first
# python manage.py seed_data --clear

# # Skip user creation (use existing users)
# python manage.py seed_data --skip-users

# # Clear everything including users and re-seed
# python manage.py seed_data --clear
