from django.contrib import admin
from .models import (
    GlobalExercise, CustomExercise, WorkoutPlan, PlannedExercise,
    LoggedWorkout, SessionExercise, LoggedSet, UserSettings, PersonalRecord
)


# Inline admin classes
class PlannedExerciseInline(admin.TabularInline):
    model = PlannedExercise
    extra = 1
    fields = ['order', 'global_exercise', 'custom_exercise', 'target_sets', 'target_reps', 'target_weight', 'notes']
    autocomplete_fields = ['global_exercise', 'custom_exercise']


class SessionExerciseInline(admin.TabularInline):
    model = SessionExercise
    extra = 0
    fields = ['order', 'global_exercise', 'custom_exercise', 'notes', 'started_at', 'completed_at']
    readonly_fields = ['started_at', 'completed_at']
    autocomplete_fields = ['global_exercise', 'custom_exercise']


class LoggedSetInline(admin.TabularInline):
    model = LoggedSet
    extra = 0
    fields = ['set_number', 'weight', 'reps', 'is_warmup', 'is_dropset', 'rest_duration', 'notes']
    readonly_fields = ['started_at', 'completed_at']


# Main admin classes
@admin.register(GlobalExercise)
class GlobalExerciseAdmin(admin.ModelAdmin):
    list_display = ['name', 'equipment_type', 'primary_muscle_group', 'weight_increment_type', 'is_active', 'created_at']
    list_filter = ['equipment_type', 'primary_muscle_group', 'weight_increment_type', 'is_active']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'equipment_type', 'weight_increment_type')
        }),
        ('Muscle Groups', {
            'fields': ('primary_muscle_group', 'secondary_muscle_groups')
        }),
        ('Instructions', {
            'fields': ('instructions', 'video_url'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CustomExercise)
class CustomExerciseAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'equipment_type', 'primary_muscle_group', 'weight_increment_type', 'is_active']
    list_filter = ['equipment_type', 'primary_muscle_group', 'weight_increment_type', 'is_active', 'user']
    search_fields = ['name', 'user__username', 'description']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['user']


@admin.register(WorkoutPlan)
class WorkoutPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'privacy', 'times_used', 'is_active', 'updated_at']
    list_filter = ['privacy', 'is_active', 'created_at']
    search_fields = ['name', 'user__username', 'tags', 'description']
    readonly_fields = ['times_used', 'created_at', 'updated_at']
    autocomplete_fields = ['user']
    inlines = [PlannedExerciseInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'description')
        }),
        ('Settings', {
            'fields': ('privacy', 'tags')
        }),
        ('Statistics', {
            'fields': ('times_used', 'is_active'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PlannedExercise)
class PlannedExerciseAdmin(admin.ModelAdmin):
    list_display = ['workout_plan', 'get_exercise_name', 'order', 'target_sets', 'target_reps']
    list_filter = ['workout_plan__user', 'workout_plan']
    search_fields = ['workout_plan__name', 'global_exercise__name', 'custom_exercise__name']
    autocomplete_fields = ['workout_plan', 'global_exercise', 'custom_exercise']


@admin.register(LoggedWorkout)
class LoggedWorkoutAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'started_at', 'ended_at', 'is_in_progress', 'is_active']
    list_filter = ['user', 'started_at', 'is_active']
    search_fields = ['name', 'user__username', 'notes']
    readonly_fields = ['started_at', 'duration']
    autocomplete_fields = ['user', 'workout_plan']
    inlines = [SessionExerciseInline]
    date_hierarchy = 'started_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'workout_plan', 'name', 'notes')
        }),
        ('Timing', {
            'fields': ('started_at', 'ended_at', 'duration')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(SessionExercise)
class SessionExerciseAdmin(admin.ModelAdmin):
    list_display = ['logged_workout', 'get_exercise_name', 'order', 'started_at', 'completed_at']
    list_filter = ['logged_workout__user', 'logged_workout__started_at']
    search_fields = ['logged_workout__name', 'global_exercise__name', 'custom_exercise__name']
    autocomplete_fields = ['logged_workout', 'global_exercise', 'custom_exercise']
    inlines = [LoggedSetInline]


@admin.register(LoggedSet)
class LoggedSetAdmin(admin.ModelAdmin):
    list_display = ['session_exercise', 'set_number', 'weight', 'reps', 'is_warmup', 'is_dropset', 'rest_duration']
    list_filter = ['is_warmup', 'is_dropset', 'session_exercise__logged_workout__user']
    search_fields = ['session_exercise__logged_workout__name']
    readonly_fields = ['started_at', 'completed_at']
    
    fieldsets = (
        ('Exercise', {
            'fields': ('session_exercise',)
        }),
        ('Set Details', {
            'fields': ('set_number', 'weight', 'reps', 'is_warmup', 'is_dropset')
        }),
        ('Timing', {
            'fields': ('started_at', 'completed_at', 'rest_duration')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'weight_unit', 'default_bar_weight', 'default_rest_time', 'show_plate_calculator']
    list_filter = ['weight_unit', 'show_plate_calculator']
    search_fields = ['user__username']
    autocomplete_fields = ['user']


@admin.register(PersonalRecord)
class PersonalRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_exercise_name', 'pr_type', 'weight', 'reps', 'estimated_1rm', 'achieved_at']
    list_filter = ['pr_type', 'user', 'achieved_at']
    search_fields = ['user__username', 'global_exercise__name', 'custom_exercise__name']
    readonly_fields = ['achieved_at']
    autocomplete_fields = ['user', 'global_exercise', 'custom_exercise', 'logged_set']
    date_hierarchy = 'achieved_at'
