from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Workout Plans
    path('plans/', views.workout_plans_list, name='workout_plans_list'),
    
    # Workout Session
    path('workout/start/', views.start_workout, name='start_workout'),
    path('workout/start/<int:plan_id>/', views.start_workout, name='start_workout_from_plan'),
    path('workout/<int:workout_id>/', views.active_workout, name='active_workout'),
    path('workout/<int:workout_id>/end/', views.end_workout, name='end_workout'),
    path('workout/<int:workout_id>/detail/', views.workout_detail, name='workout_detail'),
    
    # AJAX Endpoints
    path('api/set/add/<int:session_exercise_id>/', views.add_set, name='add_set'),
    path('api/set/<int:set_id>/update/', views.update_set, name='update_set'),
    path('api/set/<int:set_id>/delete/', views.delete_set, name='delete_set'),
    path('api/plates/calculate/', views.calculate_plates, name='calculate_plates'),
]
