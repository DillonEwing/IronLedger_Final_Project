# 🏋️ IronLedger - Workout Tracking Application

**CIDM 6325 - Advanced Web Development Final Project**  
Student: Dillon Ewing  
Semester: Fall 2025

---

## 📋 Project Overview

IronLedger is a comprehensive workout tracking web application built with Django 5.2. It allows users to create workout plans, log exercises, track sets and reps, monitor rest times, and view their workout history.

**Live Demo**: [https://ironledger-final-project.onrender.com](https://ironledger-final-project.onrender.com)

---

## ✨ Key Features

### Core Functionality
- ✅ **User Authentication** - Secure signup, login, and logout
- ✅ **Workout Plans** - Create reusable workout templates with custom exercises
- ✅ **Exercise Library** - Global exercise database + user custom exercises
- ✅ **Live Workout Tracking** - Real-time set/rep logging with rest timer
- ✅ **Workout History** - View past workouts with detailed statistics
- ✅ **Privacy Controls** - Share workout plans or keep them private
- ✅ **Personal Records** - Automatic PR tracking and display
- ✅ **Rest Timer** - Built-in timer with accurate duration tracking
- ✅ **Responsive Design** - Mobile-friendly Bootstrap 5 interface

### Technical Highlights
- 🔥 **9 Django Models** with complex relationships
- 🔥 **31 Comprehensive Tests** (models, views, forms, URLs, integration)
- 🔥 **Custom Admin Interface** with branded theming (dark/light modes)
- 🔥 **AJAX Functionality** for seamless set logging
- 🔥 **Session Storage** for active workout state management
- 🔥 **Custom Template Filters** and tags
- 🔥 **Signal Handlers** for automated user settings creation
- 🔥 **PostgreSQL Database** on production

---

## 🛠️ Technology Stack

- **Backend**: Django 5.2.8, Python 3.13
- **Database**: SQLite (development), PostgreSQL (production)
- **Frontend**: Bootstrap 5.3, JavaScript (Vanilla)
- **Deployment**: Render.com with Gunicorn
- **Version Control**: Git/GitHub

---

## 📦 Installation & Setup

### Prerequisites
- Python 3.11+
- pip package manager
- Git

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/DillonEwing/IronLedger_Final_Project.git
   cd IronLedger_Final_Project/ironledger
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Mac/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser (for admin access)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Load sample data (optional)**
   ```bash
   python manage.py loaddata global_exercises.json
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Main app: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

---

## 🗄️ Database Schema

### Core Models
- **GlobalExercise** - Shared exercise library (e.g., Bench Press, Squat)
- **CustomExercise** - User-created exercises
- **WorkoutPlan** - Reusable workout templates
- **PlannedExercise** - Exercises within a workout plan
- **LoggedWorkout** - Actual workout sessions
- **SessionExercise** - Exercises performed in a session
- **LoggedSet** - Individual sets with weight/reps/rest data
- **UserSettings** - User preferences
- **PersonalRecord** - PR tracking per exercise

### Key Relationships
- User → WorkoutPlans (1:M)
- User → LoggedWorkouts (1:M)
- WorkoutPlan → PlannedExercises (1:M)
- LoggedWorkout → SessionExercises (1:M)
- SessionExercise → LoggedSets (1:M)

---

## 🧪 Testing

Run the test suite:
```bash
python manage.py test tracker
```

**Test Coverage**: 31 tests covering:
- Model creation and relationships
- View rendering and authentication
- Form validation
- URL routing
- Integration workflows

---

## 🎨 Custom Admin Interface

Custom Django admin with IronLedger branding:
- **Custom login page** - Branded with gradient background
- **Custom dashboard** - Welcome cards and feature overview
- **Dark/Light mode support** - Professional color schemes
- **Enhanced model admin** - List displays, filters, search, inlines

---

## 📱 User Workflows

### Creating a Workout Plan
1. Navigate to "Workout Plans"
2. Click "Create New Plan"
3. Add exercises from global library or create custom
4. Set target sets/reps (optional)
5. Save and share (optional)

### Logging a Workout
1. Start from a plan or create quick workout
2. Select exercises
3. Begin workout session
4. Log sets with weight/reps
5. Use built-in rest timer between sets
6. Complete and save workout

### Viewing History
1. Navigate to "Workout History"
2. View past workouts by date
3. See detailed set/rep data
4. Track progress over time

---

## 🚀 Deployment

Deployed on **Render.com** with:
- PostgreSQL database
- Gunicorn WSGI server
- Static files served via WhiteNoise
- Environment variables for secrets
- Automatic deploys from main branch

**Production URL**: https://ironledger-final-project.onrender.com

---

## 📊 Course Requirements Met

### Baseline (70%)
✅ Multiple models with relationships  
✅ Forms and validation  
✅ User authentication  
✅ Admin interface customization  
✅ Templates with inheritance  
✅ Comprehensive tests (31 tests)  

### Good Tier (5%) - 15+ features implemented
✅ Custom template filters  
✅ Signals  
✅ Model properties  
✅ Query optimization  
✅ AJAX functionality  
✅ Session storage  
✅ And more...

### Better Tier (5%) - 16+ features implemented
✅ Complex queries  
✅ Bootstrap integration  
✅ Responsive design  
✅ JavaScript interactivity  
✅ Dynamic forms  
✅ Permission checks  
✅ And more...

### Best Tier (5%)
✅ **Custom Django Admin Templates** (Chapter 7)  
- Custom login page with branding  
- Custom dashboard layout  
- Dark/light mode theming  

### Project Fit (10%)
✅ Real-world workout tracking application  
✅ Clear user workflows  
✅ Professional UI/UX  
✅ Practical and usable  

---

## 👤 Author

**Dillon Ewing**  
CIDM 6325 - Advanced Web Development  
West Texas A&M University  
Fall 2025

---

## 📄 License

This project is for educational purposes as part of CIDM 6325 coursework.

---

## 🙏 Acknowledgments

- Django Documentation
- Bootstrap Documentation
- Course materials from CIDM 6325
- Render.com for hosting

