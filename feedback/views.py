import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Avg, Count
from .models import User, Course, Feedback, Suggestion
from .forms import CustomUserCreationForm, CourseForm, FeedbackForm
import google.generativeai as genai
from django.conf import settings
from django.http import HttpResponse
from .pdf_generator import generate_feedback_report_pdf
from .email_utils import send_feedback_notification, send_suggestion_generated_notification

# Gemini API config
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')


# Role checking
def is_lecturer(user):
    return user.is_authenticated and user.role == 'lecturer'


def is_student(user):
    return user.is_authenticated and user.role == 'student'


# Public views
def index(request):
    """Homepage"""
    return render(request, 'index.html')


def register(request):
    """User registration"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome {user.username}! Your account has been created.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


# Dashboard views
@login_required
def dashboard(request):
    """Role-based dashboard"""
    if request.user.role == 'student':
        return student_dashboard(request)
    else:
        return lecturer_dashboard(request)


def student_dashboard(request):
    """Student dashboard - view courses and rate lecturers"""
    courses = Course.objects.select_related('lecturer').all()
    return render(request, 'feedback/student_dashboard.html', {'courses': courses})


def lecturer_dashboard(request):
    """Lecturer dashboard - view feedback and statistics"""
    lecturer = request.user
    feedback_qs = Feedback.objects.filter(lecturer=lecturer).select_related('course', 'student')
    courses = Course.objects.filter(lecturer=lecturer)
    
    # Calculate statistics
    stats = feedback_qs.aggregate(
        avg_rating=Avg('rating'),
        avg_teaching=Avg('teaching_rating'),
        avg_communication=Avg('communication_rating'),
        avg_engagement=Avg('engagement_rating'),
        total_feedback=Count('id')
    )
    
    # Chart data (average ratings by category)

    chart_labels = ["Overall", "Teaching", "Communication", "Engagement"]
    chart_data = [
        round(stats['avg_rating'] or 0, 2),
        round(stats['avg_teaching'] or 0, 2),
        round(stats['avg_communication'] or 0, 2),
        round(stats['avg_engagement'] or 0, 2),
    ]

    
    # Get latest suggestion
    latest_suggestion = Suggestion.objects.filter(lecturer=lecturer).order_by('-generated_at').first()
    
    context = {
        'feedback': feedback_qs[:10],  # Latest 10 feedback items
        'courses': courses,
        'avg_rating': round(stats['avg_rating'] or 0, 2),
        'avg_teaching': round(stats['avg_teaching'] or 0, 2),
        'avg_communication': round(stats['avg_communication'] or 0, 2),
        'avg_engagement': round(stats['avg_engagement'] or 0, 2),
        'total_feedback': stats['total_feedback'],
        'latest_suggestion': latest_suggestion,
        
        #Pass chart data
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    }
    return render(request, 'feedback/lecturer_dashboard.html', context)


# Course management
@login_required
@user_passes_test(is_lecturer)
def add_course(request):
    """Add new course (lecturers only)"""
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.lecturer = request.user
            course.save()
            messages.success(request, f'Course {course.code} added successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CourseForm()
    return render(request, 'feedback/add_course.html', {'form': form})

#PDF export 
@login_required
@user_passes_test(is_lecturer)
def export_feedback_pdf(request):
    """Export feedback as PDF"""
    lecturer = request.user
    feedback_list = Feedback.objects.filter(lecturer=lecturer).select_related('course', 'student').order_by('-created_at')
    
    if not feedback_list.exists():
        messages.warning(request, 'No feedback available to export.')
        return redirect('dashboard')
    
    # Calculate stats
    stats = feedback_list.aggregate(
        avg_rating=Avg('rating'),
        avg_teaching=Avg('teaching_rating'),
        avg_communication=Avg('communication_rating'),
        avg_engagement=Avg('engagement_rating'),
    )
    
    # Generate PDF
    pdf_buffer = generate_feedback_report_pdf(lecturer, feedback_list, stats)
    
    # Create response
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    filename = f"feedback_report_{lecturer.username}_{datetime.now().strftime('%Y%m%d')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


# Lecturer views
@login_required
@user_passes_test(is_student)
def lecturers_list(request):
    """List all lecturers (students only)"""
    lecturers = User.objects.filter(role='lecturer').prefetch_related('courses')
    return render(request, 'feedback/lecturers.html', {'lecturers': lecturers})


@login_required
@user_passes_test(is_student)
def rate_lecturer(request, lecturer_id):
    """Rate a specific lecturer (students only)"""
    lecturer = get_object_or_404(User, id=lecturer_id, role='lecturer')
    courses = Course.objects.filter(lecturer=lecturer)
    
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            # Check if feedback already exists
            course = form.cleaned_data['course']
            existing = Feedback.objects.filter(
                student=request.user,
                lecturer=lecturer,
                course=course
            ).exists()
            
            if existing:
                messages.error(request, 'You have already submitted feedback for this course.')
                return redirect('rate_lecturer', lecturer_id=lecturer_id)
            
            # Save feedback
            feedback = form.save(commit=False)
            feedback.student = request.user
            feedback.lecturer = lecturer
            feedback.save()
            
            #Send feedback notification
            send_feedback_notification(feedback)
            
            messages.success(request, 'Thank you! Your feedback has been submitted.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = FeedbackForm()
        form.fields['course'].queryset = courses
    
    context = {
        'lecturer': lecturer,
        'courses': courses,
        'form': form
    }
    return render(request, 'feedback/rate_lecturer.html', context)

    
        


# AI Suggestions
def generate_suggestions_with_gemini(feedback_list, lecturer_name):
    """Generate AI suggestions using Gemini API"""
    try:
        # Prepare feedback data
        feedback_text = ""
        for fb in feedback_list:
            feedback_text += f"Course: {fb.course.code}\n"
            feedback_text += f"Overall Rating: {fb.rating}/5\n"
            
            if fb.teaching_rating:
                feedback_text += f"Teaching: {fb.teaching_rating}/5 | "
            if fb.communication_rating:
                feedback_text += f"Communication: {fb.communication_rating}/5 | "
            if fb.engagement_rating:
                feedback_text += f"Engagement: {fb.engagement_rating}/5\n"
            
            if fb.comment:
                feedback_text += f"Comment: {fb.comment}\n"
            feedback_text += "---\n"
        
        # Create prompt for Gemini
        prompt = f"""
You are an educational consultant analyzing student feedback for {lecturer_name}, a university lecturer.

STUDENT FEEDBACK DATA:
{feedback_text}

TASK: Analyze this feedback and provide 5 specific, actionable improvement suggestions.

FORMAT YOUR RESPONSE AS:
1. [Category]: [Specific actionable suggestion with details]
2. [Category]: [Specific actionable suggestion with details]
3. [Category]: [Specific actionable suggestion with details]
4. [Category]: [Specific actionable suggestion with details]
5. [Category]: [Specific actionable suggestion with details]

FOCUS AREAS:
- Teaching methodology and delivery
- Communication clarity and effectiveness
- Student engagement and interaction
- Course structure and organization
- Assessment and feedback practices

REQUIREMENTS:
- Be constructive and supportive in tone
- Provide specific, implementable actions
- Base suggestions on patterns in the feedback
- Avoid generic advice
- Include practical examples where relevant
"""
        
        response = model.generate_content(prompt)
        return response.text
    
    except Exception as e:
        return f"Error generating suggestions: {str(e)}\n\nPlease check your Gemini API key configuration."


@login_required
@user_passes_test(is_lecturer)
def generate_suggestions(request):
    """Generate AI suggestions based on feedback (lecturers only)"""
    lecturer = request.user
    feedback_list = Feedback.objects.filter(lecturer=lecturer).select_related('course')
    
    if not feedback_list.exists():
        messages.warning(request, 'No feedback available yet. Suggestions will be generated once students provide feedback.')
        return redirect('dashboard')
    
    if not settings.GEMINI_API_KEY:
        messages.error(request, 'Gemini API is not configured. Please contact administrator.')
        return redirect('dashboard')
    
    # Generate suggestions
    suggestions_text = generate_suggestions_with_gemini(
        feedback_list,
        lecturer.get_full_name() or lecturer.username
    )
    
    # Save to database
    suggestion = Suggestion.objects.create(
        lecturer=lecturer,
        suggestions_text=suggestions_text,
        based_on_feedback_count=feedback_list.count()
    )
    
    #Send email notification
    send_suggestion_generated_notification(lecturer, suggestion)
    
    messages.success(request, f'New AI suggestions generated based on {feedback_list.count()} feedback items!')
    return redirect('dashboard')
