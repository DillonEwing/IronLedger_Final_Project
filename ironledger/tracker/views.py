from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from .forms import SignUpForm, LoginForm
from .models import (
    WorkoutPlan, PlannedExercise, LoggedWorkout, SessionExercise, 
    LoggedSet, GlobalExercise, CustomExercise, UserSettings
)
import json
from decimal import Decimal


def home(request):
    """Home page view"""
    return render(request, 'tracker/home.html')


def signup_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to IronLedger, {user.username}!')
            return redirect('dashboard')
    else:
        form = SignUpForm()
    
    return render(request, 'tracker/signup.html', {'form': form})


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('dashboard')
    else:
        form = LoginForm()
    
    return render(request, 'tracker/login.html', {'form': form})


def logout_view(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required
def dashboard(request):
    """User dashboard - main page after login"""
    # Get user's recent workouts
    recent_workouts = LoggedWorkout.objects.filter(
        user=request.user,
        is_active=True
    ).order_by('-started_at')[:5]
    
    # Check if there's an active workout
    active_workout = LoggedWorkout.objects.filter(
        user=request.user,
        ended_at__isnull=True,
        is_active=True
    ).first()
    
    # Get available workout plans (user's own and shared plans)
    user_plans = WorkoutPlan.objects.filter(
        user=request.user,
        is_active=True
    ).prefetch_related('planned_exercises').order_by('-updated_at')[:5]
    
    shared_plans = WorkoutPlan.objects.filter(
        privacy='shared',
        is_active=True
    ).exclude(user=request.user).prefetch_related('planned_exercises').order_by('-times_used')[:5]
    
    # Combine for display
    workout_plans = list(user_plans) + list(shared_plans)
    
    context = {
        'recent_workouts': recent_workouts,
        'active_workout': active_workout,
        'workout_plans': workout_plans,
    }
    return render(request, 'tracker/dashboard.html', context)


@login_required
def workout_plans_list(request):
    """List all available workout plans"""
    user_plans = WorkoutPlan.objects.filter(
        user=request.user,
        is_active=True
    ).order_by('-updated_at')
    
    shared_plans = WorkoutPlan.objects.filter(
        privacy='shared',
        is_active=True
    ).exclude(user=request.user).order_by('-times_used')
    
    context = {
        'user_plans': user_plans,
        'shared_plans': shared_plans,
    }
    return render(request, 'tracker/workout_plans_list.html', context)


@login_required
def start_workout(request, plan_id=None):
    """Start a new workout from a plan or from scratch"""
    plan = None
    if plan_id:
        plan = get_object_or_404(WorkoutPlan, id=plan_id, is_active=True)
        # Check if user can access this plan
        if plan.user != request.user and plan.privacy != 'shared':
            messages.error(request, 'You do not have access to this workout plan.')
            return redirect('dashboard')
    
    if request.method == 'POST':
        workout_name = request.POST.get('workout_name', '')
        
        # Create the logged workout
        workout = LoggedWorkout.objects.create(
            user=request.user,
            workout_plan=plan,
            name=workout_name or (plan.name if plan else 'Quick Workout'),
            started_at=timezone.now()
        )
        
        # If starting from a plan, copy exercises
        if plan:
            planned_exercises = plan.planned_exercises.all().order_by('order')
            for planned_ex in planned_exercises:
                SessionExercise.objects.create(
                    logged_workout=workout,
                    global_exercise=planned_ex.global_exercise,
                    custom_exercise=planned_ex.custom_exercise,
                    order=planned_ex.order,
                    notes=planned_ex.notes
                )
            # Increment plan usage
            plan.increment_usage()
        
        messages.success(request, f'Workout started: {workout.name}')
        return redirect('active_workout', workout_id=workout.id)
    
    context = {
        'plan': plan,
    }
    return render(request, 'tracker/start_workout.html', context)


@login_required
def active_workout(request, workout_id):
    """Active workout session - main logging interface"""
    workout = get_object_or_404(LoggedWorkout, id=workout_id, user=request.user)
    
    # Get user settings for plate calculator
    settings, created = UserSettings.objects.get_or_create(user=request.user)
    
    # Get all exercises in this workout
    session_exercises = workout.session_exercises.all().order_by('order')
    
    # Build exercise data with sets
    exercises_data = []
    for session_ex in session_exercises:
        sets = session_ex.logged_sets.all().order_by('set_number')
        exercise_name = session_ex.get_exercise_name()
        
        # Get exercise details for weight increment type
        exercise_obj = session_ex.global_exercise or session_ex.custom_exercise
        
        exercises_data.append({
            'session_exercise': session_ex,
            'exercise_name': exercise_name,
            'exercise_obj': exercise_obj,
            'sets': sets,
            'set_count': sets.count(),
        })
    
    context = {
        'workout': workout,
        'exercises_data': exercises_data,
        'settings': settings,
    }
    return render(request, 'tracker/active_workout.html', context)


@login_required
def add_set(request, session_exercise_id):
    """Add a set to a session exercise (AJAX endpoint)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    
    session_exercise = get_object_or_404(SessionExercise, id=session_exercise_id)
    
    # Verify ownership
    if session_exercise.logged_workout.user != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    # Verify workout is still active
    if session_exercise.logged_workout.ended_at is not None:
        return JsonResponse({'error': 'Workout already ended'}, status=400)
    
    try:
        data = json.loads(request.body)
        weight = Decimal(str(data.get('weight', 0)))
        reps = int(data.get('reps', 0))
        is_warmup = data.get('is_warmup', False)
        is_dropset = data.get('is_dropset', False)
        notes = data.get('notes', '')
        
        # Get the next set number
        last_set = session_exercise.logged_sets.order_by('-set_number').first()
        set_number = (last_set.set_number + 1) if last_set else 1
        
        # Calculate rest duration if there was a previous set
        if last_set and last_set.completed_at:
            rest_duration = int((timezone.now() - last_set.completed_at).total_seconds())
        else:
            rest_duration = None
        
        # Create the set
        logged_set = LoggedSet.objects.create(
            session_exercise=session_exercise,
            set_number=set_number,
            weight=weight,
            reps=reps,
            is_warmup=is_warmup,
            is_dropset=is_dropset,
            notes=notes,
            started_at=timezone.now(),
            completed_at=timezone.now(),
            rest_duration=rest_duration
        )
        
        return JsonResponse({
            'success': True,
            'set_id': logged_set.id,
            'set_number': set_number,
            'rest_duration': rest_duration,
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def update_set(request, set_id):
    """Update an existing set (AJAX endpoint)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    
    logged_set = get_object_or_404(LoggedSet, id=set_id)
    
    # Verify ownership
    if logged_set.session_exercise.logged_workout.user != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        data = json.loads(request.body)
        
        if 'weight' in data:
            logged_set.weight = Decimal(str(data['weight']))
        if 'reps' in data:
            logged_set.reps = int(data['reps'])
        if 'is_warmup' in data:
            logged_set.is_warmup = data['is_warmup']
        if 'is_dropset' in data:
            logged_set.is_dropset = data['is_dropset']
        if 'notes' in data:
            logged_set.notes = data['notes']
        
        logged_set.save()
        
        return JsonResponse({'success': True})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def delete_set(request, set_id):
    """Delete a set (AJAX endpoint)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    
    logged_set = get_object_or_404(LoggedSet, id=set_id)
    
    # Verify ownership
    if logged_set.session_exercise.logged_workout.user != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    logged_set.delete()
    return JsonResponse({'success': True})


@login_required
def end_workout(request, workout_id):
    """End an active workout"""
    workout = get_object_or_404(LoggedWorkout, id=workout_id, user=request.user)
    
    if workout.ended_at:
        messages.warning(request, 'This workout has already ended.')
        return redirect('workout_detail', workout_id=workout.id)
    
    if request.method == 'POST':
        workout.ended_at = timezone.now()
        workout.notes = request.POST.get('workout_notes', workout.notes)
        workout.save()
        
        messages.success(request, f'Workout completed! Duration: {workout.duration}')
        return redirect('workout_detail', workout_id=workout.id)
    
    context = {'workout': workout}
    return render(request, 'tracker/end_workout.html', context)


@login_required
def workout_detail(request, workout_id):
    """View a completed workout"""
    workout = get_object_or_404(LoggedWorkout, id=workout_id, user=request.user)
    
    session_exercises = workout.session_exercises.all().order_by('order')
    
    exercises_data = []
    for session_ex in session_exercises:
        sets = session_ex.logged_sets.all().order_by('set_number')
        exercises_data.append({
            'session_exercise': session_ex,
            'exercise_name': session_ex.get_exercise_name(),
            'sets': sets,
        })
    
    context = {
        'workout': workout,
        'exercises_data': exercises_data,
    }
    return render(request, 'tracker/workout_detail.html', context)


@login_required
def calculate_plates(request):
    """Calculate plate distribution for a target weight (AJAX endpoint)"""
    if request.method != 'GET':
        return JsonResponse({'error': 'GET required'}, status=400)
    
    try:
        target_weight = Decimal(request.GET.get('weight', 0))
        settings = UserSettings.objects.get(user=request.user)
        bar_weight = settings.default_bar_weight
        
        # Calculate weight per side
        weight_per_side = (target_weight - bar_weight) / 2
        
        if weight_per_side < 0:
            return JsonResponse({
                'error': 'Target weight is less than bar weight',
                'plates': []
            })
        
        # Available plate weights (in lbs)
        available_plates = [45, 35, 25, 10, 5, 2.5]
        plates_needed = []
        remaining = float(weight_per_side)
        
        for plate in available_plates:
            count = int(remaining / plate)
            if count > 0:
                plates_needed.append({'weight': plate, 'count': count})
                remaining -= plate * count
        
        return JsonResponse({
            'success': True,
            'target_weight': float(target_weight),
            'bar_weight': float(bar_weight),
            'weight_per_side': float(weight_per_side),
            'plates': plates_needed,
            'remainder': round(remaining, 2)
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
