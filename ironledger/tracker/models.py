from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class GlobalExercise(models.Model):
    """
    Admin-created exercises available to all users (read-only for users).
    Examples: Bench Press, Squat, Deadlift
    """
    EQUIPMENT_CHOICES = [
        ('barbell', 'Barbell'),
        ('dumbbell', 'Dumbbell'),
        ('cable', 'Cable'),
        ('machine', 'Machine'),
        ('bodyweight', 'Bodyweight'),
        ('other', 'Other'),
    ]
    
    MUSCLE_GROUP_CHOICES = [
        ('chest', 'Chest'),
        ('back', 'Back'),
        ('legs', 'Legs'),
        ('shoulders', 'Shoulders'),
        ('arms', 'Arms'),
        ('core', 'Core'),
        ('full_body', 'Full Body'),
    ]
    
    WEIGHT_INCREMENT_CHOICES = [
        ('plate', 'Plate Loading (2.5, 5, 10, 25, 35, 45 lbs)'),
        ('pin', 'Pin/Cable (1 lb increments)'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    equipment_type = models.CharField(max_length=20, choices=EQUIPMENT_CHOICES, default='barbell')
    primary_muscle_group = models.CharField(max_length=20, choices=MUSCLE_GROUP_CHOICES)
    secondary_muscle_groups = models.CharField(max_length=100, blank=True, help_text="Comma-separated muscle groups")
    
    # Weight increment type for UI suggestions
    weight_increment_type = models.CharField(
        max_length=10, 
        choices=WEIGHT_INCREMENT_CHOICES, 
        default='plate',
        help_text="How weight is incremented on this exercise"
    )
    
    # Optional instructional content
    instructions = models.TextField(blank=True, help_text="How to perform the exercise")
    video_url = models.URLField(blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, help_text="Soft delete flag")
    
    class Meta:
        ordering = ['name']
        verbose_name = "Global Exercise"
        verbose_name_plural = "Global Exercises"
    
    def __str__(self):
        return f"{self.name} ({self.get_equipment_type_display()})"


class CustomExercise(models.Model):
    """
    User-created exercises (private to that user).
    Allows users to add exercises not in the global library.
    """
    EQUIPMENT_CHOICES = GlobalExercise.EQUIPMENT_CHOICES
    MUSCLE_GROUP_CHOICES = GlobalExercise.MUSCLE_GROUP_CHOICES
    WEIGHT_INCREMENT_CHOICES = GlobalExercise.WEIGHT_INCREMENT_CHOICES
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='custom_exercises')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    equipment_type = models.CharField(max_length=20, choices=EQUIPMENT_CHOICES, default='barbell')
    primary_muscle_group = models.CharField(max_length=20, choices=MUSCLE_GROUP_CHOICES)
    secondary_muscle_groups = models.CharField(max_length=100, blank=True)
    
    # Weight increment type for UI suggestions
    weight_increment_type = models.CharField(
        max_length=10, 
        choices=WEIGHT_INCREMENT_CHOICES, 
        default='plate',
        help_text="How weight is incremented on this exercise"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, help_text="Soft delete flag")
    
    class Meta:
        ordering = ['name']
        verbose_name = "Custom Exercise"
        verbose_name_plural = "Custom Exercises"
        unique_together = ['user', 'name']  # User can't have duplicate exercise names
    
    def __str__(self):
        return f"{self.name} (Custom - {self.user.username})"


class WorkoutPlan(models.Model):
    """
    Reusable workout blueprint created by users.
    Example: "Push Day A", "Leg Day - Heavy", "Upper Body Hypertrophy"
    """
    PRIVACY_CHOICES = [
        ('private', 'Private'),
        ('shared', 'Shared'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_plans')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Privacy and sharing
    privacy = models.CharField(max_length=10, choices=PRIVACY_CHOICES, default='private')
    
    # Tags for filtering (comma-separated: "Strength,PPL,Advanced")
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags")
    
    # Usage tracking
    times_used = models.PositiveIntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, help_text="Soft delete flag")
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = "Workout Plan"
        verbose_name_plural = "Workout Plans"
    
    def __str__(self):
        return f"{self.name} ({self.user.username})"
    
    def increment_usage(self):
        """Increment usage counter when plan is used to start a workout"""
        self.times_used += 1
        self.save(update_fields=['times_used'])


class PlannedExercise(models.Model):
    """
    An exercise within a WorkoutPlan.
    Defines the order and target sets/reps for exercises in the plan.
    """
    workout_plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE, related_name='planned_exercises')
    
    # Exercise can be either global or custom
    global_exercise = models.ForeignKey(GlobalExercise, on_delete=models.SET_NULL, null=True, blank=True)
    custom_exercise = models.ForeignKey(CustomExercise, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Order in the workout
    order = models.PositiveIntegerField(default=0)
    
    # Target sets and reps (optional guidance)
    target_sets = models.PositiveIntegerField(default=3, validators=[MinValueValidator(1)])
    target_reps = models.PositiveIntegerField(blank=True, null=True)
    target_weight = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    
    # Notes specific to this exercise in the plan
    notes = models.TextField(blank=True, help_text="E.g., 'Superset with tricep extensions'")
    
    class Meta:
        ordering = ['workout_plan', 'order']
        verbose_name = "Planned Exercise"
        verbose_name_plural = "Planned Exercises"
    
    def __str__(self):
        exercise_name = self.global_exercise.name if self.global_exercise else self.custom_exercise.name
        return f"{self.workout_plan.name} - {exercise_name}"
    
    def get_exercise_name(self):
        """Helper to get exercise name regardless of type"""
        return self.global_exercise.name if self.global_exercise else self.custom_exercise.name


class LoggedWorkout(models.Model):
    """
    An actual workout session at the gym.
    Created from a WorkoutPlan (optional) or from scratch.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='logged_workouts')
    workout_plan = models.ForeignKey(WorkoutPlan, on_delete=models.SET_NULL, null=True, blank=True, 
                                     help_text="The plan this workout was based on (if any)")
    
    # Workout metadata
    name = models.CharField(max_length=200, help_text="E.g., 'Push Day A - Dec 2'")
    notes = models.TextField(blank=True, help_text="Overall workout notes")
    
    # Timestamps
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    # Soft delete
    is_active = models.BooleanField(default=True, help_text="Soft delete flag")
    
    class Meta:
        ordering = ['-started_at']
        verbose_name = "Logged Workout"
        verbose_name_plural = "Logged Workouts"
    
    def __str__(self):
        return f"{self.name} - {self.user.username} ({self.started_at.date()})"
    
    @property
    def duration(self):
        """Calculate workout duration if ended"""
        if self.ended_at:
            return self.ended_at - self.started_at
        return None
    
    @property
    def is_in_progress(self):
        """Check if workout is currently active"""
        return self.ended_at is None


class SessionExercise(models.Model):
    """
    An exercise within a LoggedWorkout session.
    Can be reordered during the workout if needed.
    """
    logged_workout = models.ForeignKey(LoggedWorkout, on_delete=models.CASCADE, related_name='session_exercises')
    
    # Exercise reference (global or custom)
    global_exercise = models.ForeignKey(GlobalExercise, on_delete=models.SET_NULL, null=True, blank=True)
    custom_exercise = models.ForeignKey(CustomExercise, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Order in this specific session (can differ from plan order)
    order = models.PositiveIntegerField(default=0)
    
    # Notes for this exercise in this session
    notes = models.TextField(blank=True, help_text="E.g., 'Moved this later - machine was taken'")
    
    # Timestamp when exercise was started
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['logged_workout', 'order']
        verbose_name = "Session Exercise"
        verbose_name_plural = "Session Exercises"
    
    def __str__(self):
        exercise_name = self.global_exercise.name if self.global_exercise else self.custom_exercise.name
        return f"{self.logged_workout.name} - {exercise_name}"
    
    def get_exercise_name(self):
        """Helper to get exercise name regardless of type"""
        return self.global_exercise.name if self.global_exercise else self.custom_exercise.name


class LoggedSet(models.Model):
    """
    An individual set performed during a workout.
    Tracks weight, reps, rest time, and set type (warmup/working/dropset).
    """
    session_exercise = models.ForeignKey(SessionExercise, on_delete=models.CASCADE, related_name='logged_sets')
    
    # Set number in sequence
    set_number = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    
    # Performance data
    weight = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
    reps = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    
    # Set type flags
    is_warmup = models.BooleanField(default=False)
    is_dropset = models.BooleanField(default=False)
    
    # Rest timing (calculated from timestamps)
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    rest_duration = models.PositiveIntegerField(null=True, blank=True, 
                                                help_text="Rest time in seconds before next set")
    
    # Optional notes per set
    notes = models.TextField(blank=True, help_text="E.g., 'Felt great', 'Knee pain on rep 5'")
    
    class Meta:
        ordering = ['session_exercise', 'set_number']
        verbose_name = "Logged Set"
        verbose_name_plural = "Logged Sets"
    
    def __str__(self):
        return f"{self.session_exercise.get_exercise_name()} - Set {self.set_number}: {self.weight}lbs x {self.reps}"
    
    def calculate_rest_duration(self, next_set_start):
        """Calculate rest duration based on when next set started"""
        if self.completed_at and next_set_start:
            delta = next_set_start - self.completed_at
            self.rest_duration = int(delta.total_seconds())
            self.save(update_fields=['rest_duration'])


class UserSettings(models.Model):
    """
    User preferences and settings for the workout tracker.
    """
    UNIT_CHOICES = [
        ('lbs', 'Pounds (lbs)'),
        ('kg', 'Kilograms (kg)'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    
    # Weight preferences
    default_bar_weight = models.DecimalField(max_digits=5, decimal_places=2, default=45.00,
                                            help_text="Standard barbell weight")
    weight_unit = models.CharField(max_length=3, choices=UNIT_CHOICES, default='lbs')
    
    # Rest timer preferences
    default_rest_time = models.PositiveIntegerField(default=90, help_text="Default rest time in seconds")
    
    # Display preferences
    show_plate_calculator = models.BooleanField(default=True)
    show_warmup_sets = models.BooleanField(default=True, help_text="Display warmup sets in history")
    
    # Notification preferences
    rest_timer_sound = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "User Settings"
        verbose_name_plural = "User Settings"
    
    def __str__(self):
        return f"Settings for {self.user.username}"


class PersonalRecord(models.Model):
    """
    Tracks personal records for exercises.
    Auto-created/updated when user logs sets.
    """
    PR_TYPE_CHOICES = [
        ('weight_at_reps', 'Best Weight at X Reps'),
        ('one_rep_max', 'Estimated 1RM'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='personal_records')
    
    # Exercise reference
    global_exercise = models.ForeignKey(GlobalExercise, on_delete=models.CASCADE, null=True, blank=True)
    custom_exercise = models.ForeignKey(CustomExercise, on_delete=models.CASCADE, null=True, blank=True)
    
    # PR details
    pr_type = models.CharField(max_length=20, choices=PR_TYPE_CHOICES)
    weight = models.DecimalField(max_digits=6, decimal_places=2)
    reps = models.PositiveIntegerField()  # For weight_at_reps type
    estimated_1rm = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    
    # When was this PR achieved
    achieved_at = models.DateTimeField(default=timezone.now)
    
    # Reference to the actual set that created this PR
    logged_set = models.ForeignKey(LoggedSet, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-achieved_at']
        verbose_name = "Personal Record"
        verbose_name_plural = "Personal Records"
    
    def __str__(self):
        exercise_name = self.global_exercise.name if self.global_exercise else self.custom_exercise.name
        if self.pr_type == 'one_rep_max':
            return f"{exercise_name} - 1RM: {self.estimated_1rm}lbs"
        return f"{exercise_name} - {self.weight}lbs x {self.reps} reps"
    
    def get_exercise_name(self):
        """Helper to get exercise name regardless of type"""
        return self.global_exercise.name if self.global_exercise else self.custom_exercise.name
    
    @staticmethod
    def calculate_1rm(weight, reps):
        """
        Calculate estimated 1RM using Epley formula: weight × (1 + reps/30)
        """
        if reps == 1:
            return weight
        return weight * (1 + reps / 30)
