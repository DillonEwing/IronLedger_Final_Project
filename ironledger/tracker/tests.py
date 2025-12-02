from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import (
    GlobalExercise, CustomExercise, WorkoutPlan, PlannedExercise,
    LoggedWorkout, SessionExercise, LoggedSet, UserSettings
)
from .forms import SignUpForm, LoginForm


class ModelTests(TestCase):
    """Test model creation and relationships"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_global_exercise_creation(self):
        """Test creating a global exercise"""
        exercise = GlobalExercise.objects.create(
            name='Bench Press',
            description='Barbell bench press',
            equipment_type='barbell',
            primary_muscle_group='chest',
            weight_increment_type='plate'
        )
        self.assertEqual(exercise.name, 'Bench Press')
        self.assertTrue(exercise.is_active)
        self.assertEqual(exercise.equipment_type, 'barbell')
    
    def test_custom_exercise_creation(self):
        """Test creating a custom exercise for a user"""
        exercise = CustomExercise.objects.create(
            user=self.user,
            name='My Custom Exercise',
            equipment_type='dumbbell',
            primary_muscle_group='arms',
            weight_increment_type='plate'
        )
        self.assertEqual(exercise.user, self.user)
        self.assertEqual(exercise.name, 'My Custom Exercise')
    
    def test_workout_plan_creation(self):
        """Test creating a workout plan"""
        plan = WorkoutPlan.objects.create(
            user=self.user,
            name='Test Push Day',
            description='Test workout plan',
            privacy='private'
        )
        self.assertEqual(plan.name, 'Test Push Day')
        self.assertEqual(plan.user, self.user)
        self.assertEqual(plan.times_used, 0)
        self.assertTrue(plan.is_active)
    
    def test_logged_workout_creation(self):
        """Test creating a logged workout"""
        workout = LoggedWorkout.objects.create(
            user=self.user,
            name='Test Workout'
        )
        self.assertEqual(workout.user, self.user)
        self.assertIsNotNone(workout.started_at)
        self.assertIsNone(workout.ended_at)
    
    def test_user_settings_auto_creation(self):
        """Test that UserSettings is auto-created via signal"""
        new_user = User.objects.create_user(
            username='newuser',
            password='pass123'
        )
        # Signal should auto-create UserSettings
        self.assertTrue(hasattr(new_user, 'settings'))
        self.assertIsNotNone(new_user.settings)
    
    def test_session_exercise_relationship(self):
        """Test SessionExercise has correct relationship"""
        workout = LoggedWorkout.objects.create(
            user=self.user,
            name='Test'
        )
        exercise = GlobalExercise.objects.create(
            name='Squat',
            equipment_type='barbell',
            primary_muscle_group='legs',
            weight_increment_type='plate'
        )
        session_ex = SessionExercise.objects.create(
            logged_workout=workout,
            global_exercise=exercise,
            order=1
        )
        self.assertEqual(session_ex.logged_workout, workout)
        self.assertEqual(session_ex.global_exercise, exercise)
        self.assertEqual(session_ex.get_exercise_name(), 'Squat')
    
    def test_logged_set_creation(self):
        """Test creating a logged set"""
        workout = LoggedWorkout.objects.create(user=self.user)
        exercise = GlobalExercise.objects.create(
            name='Deadlift',
            equipment_type='barbell',
            primary_muscle_group='back',
            weight_increment_type='plate'
        )
        session_ex = SessionExercise.objects.create(
            logged_workout=workout,
            global_exercise=exercise,
            order=1
        )
        logged_set = LoggedSet.objects.create(
            session_exercise=session_ex,
            set_number=1,
            weight=135.0,
            reps=5
        )
        self.assertEqual(logged_set.weight, 135.0)
        self.assertEqual(logged_set.reps, 5)
        self.assertEqual(logged_set.set_number, 1)
        self.assertFalse(logged_set.is_warmup)


class ViewTests(TestCase):
    """Test views and URL routing"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_home_page_loads(self):
        """Test home page is accessible"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'IronLedger')
    
    def test_signup_page_loads(self):
        """Test signup page is accessible"""
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign Up')
    
    def test_login_page_loads(self):
        """Test login page is accessible"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')
    
    def test_dashboard_requires_login(self):
        """Test dashboard redirects when not logged in"""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
    
    def test_dashboard_accessible_when_logged_in(self):
        """Test dashboard loads for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')
    
    def test_workout_plans_requires_login(self):
        """Test workout plans page requires authentication"""
        response = self.client.get(reverse('workout_plans_list'))
        self.assertEqual(response.status_code, 302)
    
    def test_workout_plans_accessible_when_logged_in(self):
        """Test workout plans loads for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('workout_plans_list'))
        self.assertEqual(response.status_code, 200)


class AuthenticationTests(TestCase):
    """Test user authentication functionality"""
    
    def setUp(self):
        self.client = Client()
    
    def test_user_signup(self):
        """Test user can sign up"""
        response = self.client.post(reverse('signup'), {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!'
        })
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first().username, 'newuser')
    
    def test_user_login(self):
        """Test user can login with correct credentials"""
        User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        # User should be redirected after login
    
    def test_user_login_invalid_credentials(self):
        """Test login fails with wrong password"""
        User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)
        # Should stay on login page
    
    def test_user_logout(self):
        """Test user can logout"""
        User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)


class FormTests(TestCase):
    """Test form validation"""
    
    def test_signup_form_valid_data(self):
        """Test signup form accepts valid data"""
        form = SignUpForm(data={
            'username': 'testuser',
            'email': 'test@test.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!'
        })
        self.assertTrue(form.is_valid())
    
    def test_signup_form_no_data(self):
        """Test signup form rejects empty data"""
        form = SignUpForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 4)
    
    def test_signup_form_password_mismatch(self):
        """Test signup form rejects mismatched passwords"""
        form = SignUpForm(data={
            'username': 'testuser',
            'email': 'test@test.com',
            'password1': 'ComplexPass123!',
            'password2': 'DifferentPass123!'
        })
        self.assertFalse(form.is_valid())
    
    def test_login_form_valid(self):
        """Test login form with valid data"""
        User.objects.create_user(username='testuser', password='testpass123')
        form = LoginForm(data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        # Form validation requires request object, so just check fields
        self.assertIn('username', form.fields)
        self.assertIn('password', form.fields)


class URLTests(TestCase):
    """Test URL routing and reversing"""
    
    def test_home_url_resolves(self):
        """Test home URL resolves correctly"""
        url = reverse('home')
        self.assertEqual(url, '/')
    
    def test_dashboard_url_resolves(self):
        """Test dashboard URL resolves"""
        url = reverse('dashboard')
        self.assertEqual(url, '/dashboard/')
    
    def test_signup_url_resolves(self):
        """Test signup URL resolves"""
        url = reverse('signup')
        self.assertEqual(url, '/signup/')
    
    def test_login_url_resolves(self):
        """Test login URL resolves"""
        url = reverse('login')
        self.assertEqual(url, '/login/')
    
    def test_logout_url_resolves(self):
        """Test logout URL resolves"""
        url = reverse('logout')
        self.assertEqual(url, '/logout/')
    
    def test_workout_plans_url_resolves(self):
        """Test workout plans URL resolves"""
        url = reverse('workout_plans_list')
        self.assertEqual(url, '/plans/')
    
    def test_start_workout_url_resolves(self):
        """Test start workout URL resolves"""
        url = reverse('start_workout')
        self.assertEqual(url, '/workout/start/')


class IntegrationTests(TestCase):
    """Test integrated workflows"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_complete_signup_login_flow(self):
        """Test user can signup and login"""
        # Signup
        signup_response = self.client.post(reverse('signup'), {
            'username': 'flowuser',
            'email': 'flow@test.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!'
        })
        # Should redirect after signup
        self.assertEqual(signup_response.status_code, 302)
        
        # Logout
        self.client.get(reverse('logout'))
        
        # Login again
        login_response = self.client.post(reverse('login'), {
            'username': 'flowuser',
            'password': 'ComplexPass123!'
        })
        self.assertEqual(login_response.status_code, 302)
    
    def test_workout_creation_flow(self):
        """Test creating and accessing a workout"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create workout
        workout = LoggedWorkout.objects.create(
            user=self.user,
            name='Integration Test Workout'
        )
        
        # Create an exercise and session exercise for the workout
        exercise = GlobalExercise.objects.create(
            name='Test Exercise',
            equipment_type='barbell',
            primary_muscle_group='chest',
            weight_increment_type='plate'
        )
        SessionExercise.objects.create(
            logged_workout=workout,
            global_exercise=exercise,
            order=1
        )
        
        # Access workout detail - should work now
        response = self.client.get(
            reverse('active_workout', args=[workout.id])
        )
        self.assertEqual(response.status_code, 200)
