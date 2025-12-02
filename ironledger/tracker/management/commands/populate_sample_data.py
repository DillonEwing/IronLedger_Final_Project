from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tracker.models import GlobalExercise, WorkoutPlan, PlannedExercise


class Command(BaseCommand):
    help = 'Populate database with sample exercises and Push Day workout plan'

    def handle(self, *args, **options):
        self.stdout.write('Creating global exercises...')
        
        # Create exercises for all PPL days
        exercises = [
            # Push Day Exercises
            {
                'name': 'Shoulder Press',
                'description': 'Overhead barbell or dumbbell shoulder press',
                'equipment_type': 'barbell',
                'primary_muscle_group': 'shoulders',
                'secondary_muscle_groups': 'arms',
                'weight_increment_type': 'plate',
            },
            {
                'name': 'Cable Lateral Raises',
                'description': 'Cable lateral raises for side delts',
                'equipment_type': 'cable',
                'primary_muscle_group': 'shoulders',
                'secondary_muscle_groups': '',
                'weight_increment_type': 'pin',
            },
            {
                'name': 'Incline Dumbbell Press',
                'description': 'Incline dumbbell bench press',
                'equipment_type': 'dumbbell',
                'primary_muscle_group': 'chest',
                'secondary_muscle_groups': 'shoulders,arms',
                'weight_increment_type': 'plate',
            },
            {
                'name': 'Chest Fly',
                'description': 'Cable or machine chest fly',
                'equipment_type': 'cable',
                'primary_muscle_group': 'chest',
                'secondary_muscle_groups': '',
                'weight_increment_type': 'pin',
            },
            {
                'name': 'Tricep Pushdown',
                'description': 'Cable tricep pushdown',
                'equipment_type': 'cable',
                'primary_muscle_group': 'arms',
                'secondary_muscle_groups': '',
                'weight_increment_type': 'pin',
            },
            {
                'name': 'Tricep Extension',
                'description': 'Overhead or cable tricep extension',
                'equipment_type': 'cable',
                'primary_muscle_group': 'arms',
                'secondary_muscle_groups': '',
                'weight_increment_type': 'pin',
            },
            # Pull Day Exercises
            {
                'name': 'Iso Lat Pull',
                'description': 'Isolated lateral pull machine',
                'equipment_type': 'machine',
                'primary_muscle_group': 'back',
                'secondary_muscle_groups': 'arms',
                'weight_increment_type': 'pin',
            },
            {
                'name': 'Cable Face Pull',
                'description': 'Cable face pulls for rear delts',
                'equipment_type': 'cable',
                'primary_muscle_group': 'shoulders',
                'secondary_muscle_groups': 'back',
                'weight_increment_type': 'pin',
            },
            {
                'name': 'Front Cable Row',
                'description': 'Seated cable row',
                'equipment_type': 'cable',
                'primary_muscle_group': 'back',
                'secondary_muscle_groups': 'arms',
                'weight_increment_type': 'pin',
            },
            {
                'name': 'Lat Pulldown',
                'description': 'Wide grip lat pulldown',
                'equipment_type': 'cable',
                'primary_muscle_group': 'back',
                'secondary_muscle_groups': 'arms',
                'weight_increment_type': 'pin',
            },
            {
                'name': 'Preacher Curl',
                'description': 'Preacher curl machine or barbell',
                'equipment_type': 'machine',
                'primary_muscle_group': 'arms',
                'secondary_muscle_groups': '',
                'weight_increment_type': 'pin',
            },
            {
                'name': 'Cable Hammer Curl',
                'description': 'Cable hammer curls with rope attachment',
                'equipment_type': 'cable',
                'primary_muscle_group': 'arms',
                'secondary_muscle_groups': '',
                'weight_increment_type': 'pin',
            },
            {
                'name': 'Hanging Dumbbell Curl',
                'description': 'Standing dumbbell curls',
                'equipment_type': 'dumbbell',
                'primary_muscle_group': 'arms',
                'secondary_muscle_groups': '',
                'weight_increment_type': 'plate',
            },
            # Leg Day Exercises
            {
                'name': 'Leg Press',
                'description': 'Machine leg press',
                'equipment_type': 'machine',
                'primary_muscle_group': 'legs',
                'secondary_muscle_groups': '',
                'weight_increment_type': 'plate',
            },
            {
                'name': 'Bulgarian Split Squat',
                'description': 'Single leg squat with rear foot elevated',
                'equipment_type': 'dumbbell',
                'primary_muscle_group': 'legs',
                'secondary_muscle_groups': '',
                'weight_increment_type': 'plate',
            },
            {
                'name': 'Leg Extension',
                'description': 'Seated leg extension machine',
                'equipment_type': 'machine',
                'primary_muscle_group': 'legs',
                'secondary_muscle_groups': '',
                'weight_increment_type': 'pin',
            },
            {
                'name': 'Leg Curl',
                'description': 'Lying or seated leg curl machine',
                'equipment_type': 'machine',
                'primary_muscle_group': 'legs',
                'secondary_muscle_groups': '',
                'weight_increment_type': 'pin',
            },
        ]
        
        created_exercises = {}
        for ex_data in exercises:
            exercise, created = GlobalExercise.objects.get_or_create(
                name=ex_data['name'],
                defaults=ex_data
            )
            created_exercises[ex_data['name']] = exercise
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created: {exercise.name}'))
            else:
                self.stdout.write(f'  Already exists: {exercise.name}')
        
        # Create a sample admin user for the global workout plan (if doesn't exist)
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@ironledger.com',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin')  # Change this in production
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('✓ Created admin user'))
        
        # Create Push Day workout plan
        self.stdout.write('\nCreating workout plans...')
        
        # PUSH DAY
        push_plan, created = WorkoutPlan.objects.get_or_create(
            user=admin_user,
            name='Push Day - Sample',
            defaults={
                'description': 'Sample Push Day workout focusing on shoulders, chest, and triceps',
                'privacy': 'shared',
                'tags': 'Push,PPL,Strength,Hypertrophy',
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created workout plan: {push_plan.name}'))
            
            push_exercises = [
                {
                    'exercise': 'Shoulder Press',
                    'order': 1,
                    'target_sets': 4,
                    'target_reps': None,
                    'target_weight': 65.00,
                    'notes': 'Warmup: 1x40 lbs, Working sets: 3x65 lbs',
                },
                {
                    'exercise': 'Cable Lateral Raises',
                    'order': 2,
                    'target_sets': 3,
                    'target_reps': 15,
                    'target_weight': 15.00,
                    'notes': '3 sets of 15 reps',
                },
                {
                    'exercise': 'Incline Dumbbell Press',
                    'order': 3,
                    'target_sets': 3,
                    'target_reps': None,
                    'target_weight': 35.00,
                    'notes': '3 sets with 35 lb dumbbells',
                },
                {
                    'exercise': 'Chest Fly',
                    'order': 4,
                    'target_sets': 3,
                    'target_reps': None,
                    'target_weight': 85.00,
                    'notes': '3 sets at 85 lbs',
                },
                {
                    'exercise': 'Tricep Pushdown',
                    'order': 5,
                    'target_sets': 3,
                    'target_reps': None,
                    'target_weight': 50.00,
                    'notes': '3 sets at 50 lbs',
                },
                {
                    'exercise': 'Tricep Extension',
                    'order': 6,
                    'target_sets': 3,
                    'target_reps': None,
                    'target_weight': 80.00,
                    'notes': '3 sets at 80 lbs',
                },
            ]
            
            for ex_data in push_exercises:
                PlannedExercise.objects.create(
                    workout_plan=push_plan,
                    global_exercise=created_exercises[ex_data['exercise']],
                    order=ex_data['order'],
                    target_sets=ex_data['target_sets'],
                    target_reps=ex_data['target_reps'],
                    target_weight=ex_data['target_weight'],
                    notes=ex_data['notes'],
                )
                self.stdout.write(f'  ✓ Added: {ex_data["exercise"]}')
        else:
            self.stdout.write('  Push Day plan already exists')
        
        # PULL DAY
        pull_plan, created = WorkoutPlan.objects.get_or_create(
            user=admin_user,
            name='Pull Day - Sample',
            defaults={
                'description': 'Sample Pull Day workout focusing on back and biceps',
                'privacy': 'shared',
                'tags': 'Pull,PPL,Strength,Hypertrophy',
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created workout plan: {pull_plan.name}'))
            
            pull_exercises = [
                {
                    'exercise': 'Iso Lat Pull',
                    'order': 1,
                    'target_sets': 4,
                    'target_reps': None,
                    'target_weight': 80.00,
                    'notes': 'Warmup: 1x40 lbs, Working sets: 3x80 lbs',
                },
                {
                    'exercise': 'Cable Face Pull',
                    'order': 2,
                    'target_sets': 3,
                    'target_reps': None,
                    'target_weight': 57.00,
                    'notes': '3 sets at 57 lbs',
                },
                {
                    'exercise': 'Front Cable Row',
                    'order': 3,
                    'target_sets': 3,
                    'target_reps': None,
                    'target_weight': 120.00,
                    'notes': '3 sets at 120 lbs',
                },
                {
                    'exercise': 'Lat Pulldown',
                    'order': 4,
                    'target_sets': 3,
                    'target_reps': None,
                    'target_weight': 120.00,
                    'notes': '3 sets at 120 lbs',
                },
                {
                    'exercise': 'Preacher Curl',
                    'order': 5,
                    'target_sets': 3,
                    'target_reps': None,
                    'target_weight': 95.00,
                    'notes': '3 sets at 95 lbs',
                },
                {
                    'exercise': 'Cable Hammer Curl',
                    'order': 6,
                    'target_sets': 3,
                    'target_reps': None,
                    'target_weight': 30.00,
                    'notes': '3 sets at 30 lbs',
                },
                {
                    'exercise': 'Hanging Dumbbell Curl',
                    'order': 7,
                    'target_sets': 3,
                    'target_reps': None,
                    'target_weight': 20.00,
                    'notes': '3 sets with 20 lb dumbbells',
                },
            ]
            
            for ex_data in pull_exercises:
                PlannedExercise.objects.create(
                    workout_plan=pull_plan,
                    global_exercise=created_exercises[ex_data['exercise']],
                    order=ex_data['order'],
                    target_sets=ex_data['target_sets'],
                    target_reps=ex_data['target_reps'],
                    target_weight=ex_data['target_weight'],
                    notes=ex_data['notes'],
                )
                self.stdout.write(f'  ✓ Added: {ex_data["exercise"]}')
        else:
            self.stdout.write('  Pull Day plan already exists')
        
        # LEG DAY
        leg_plan, created = WorkoutPlan.objects.get_or_create(
            user=admin_user,
            name='Leg Day - Sample',
            defaults={
                'description': 'Sample Leg Day workout focusing on quads, hamstrings, and glutes',
                'privacy': 'shared',
                'tags': 'Legs,PPL,Strength,Hypertrophy',
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created workout plan: {leg_plan.name}'))
            
            leg_exercises = [
                {
                    'exercise': 'Leg Press',
                    'order': 1,
                    'target_sets': 4,
                    'target_reps': None,
                    'target_weight': 270.00,
                    'notes': 'Warmup: 1x150 lbs, Working sets: 3x270 lbs',
                },
                {
                    'exercise': 'Bulgarian Split Squat',
                    'order': 2,
                    'target_sets': 3,
                    'target_reps': None,
                    'target_weight': 45.00,
                    'notes': '3 sets with 45 lb dumbbells',
                },
                {
                    'exercise': 'Leg Extension',
                    'order': 3,
                    'target_sets': 3,
                    'target_reps': None,
                    'target_weight': 175.00,
                    'notes': '3 sets at 175 lbs',
                },
                {
                    'exercise': 'Leg Curl',
                    'order': 4,
                    'target_sets': 3,
                    'target_reps': None,
                    'target_weight': 175.00,
                    'notes': '3 sets at 175 lbs',
                },
            ]
            
            for ex_data in leg_exercises:
                PlannedExercise.objects.create(
                    workout_plan=leg_plan,
                    global_exercise=created_exercises[ex_data['exercise']],
                    order=ex_data['order'],
                    target_sets=ex_data['target_sets'],
                    target_reps=ex_data['target_reps'],
                    target_weight=ex_data['target_weight'],
                    notes=ex_data['notes'],
                )
                self.stdout.write(f'  ✓ Added: {ex_data["exercise"]}')
        else:
            self.stdout.write('  Leg Day plan already exists')
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'✅ Successfully created {len([push_plan, pull_plan, leg_plan])} PPL workout plans!'))
        self.stdout.write('='*60)
