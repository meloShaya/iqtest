from django.shortcuts import render
import random
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
import json
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from io import BytesIO
from reportlab.lib.utils import ImageReader
from django.http import FileResponse
from django.conf import settings
import os
from .forms import ReviewForm
from .models import Review


# Create your views here.

from django.shortcuts import render
from .models import Question, TestSession, UserAnswer
from .forms import LoginForm, UserRegistrationForm

def index(request):
    reviews = Review.objects.filter(approved=True).order_by("-created_at")[:5]  # Show the 5 most recent approved reviews
    return render(request, "quiz/index.html", {"reviews": reviews})

def question_list(request):
    questions = Question.objects.all().order_by("id")
    
    return render(request, "quiz/question_list.html", {"questions": questions})

def start(request):
    return render(request, "quiz/start.html")


@login_required
def dashboard(request):
    # Fetch the user"s completed test sessions, ordered by most recent first
    # test_sessions = TestSession.objects.filter(user=request.user, is_completed=True, payment_status="paid").order_by("-end_time")
    

    # Filter sessions that are completed and either paid or shared
    test_sessions = TestSession.objects.filter(
        user=request.user,
        is_completed=True
    ).filter(
        Q(payment_status="paid") | Q(payment_status="shared")
    ).order_by("-end_time")


    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.test_session = test_sessions.first()  # Link to the latest completed session
            review.save()
            # Add success message
            messages.success(request, "Thank you! Your review has been submitted and will be visible shortly.")
            return redirect("dashboard")
    else:
        form = ReviewForm()

    # Prepare the results data with IQ scores
    results = []
    for session in test_sessions:
        correct_answers = UserAnswer.objects.filter(test_session=session, is_correct=True).count()
        total_questions = session.questions.count()
        score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        # Calculate IQ: 40 (min) + (fraction correct) * 120 (range from 40 to 160)
        iq = 40 + (correct_answers / total_questions) * 120 if total_questions > 0 else 40
        results.append({
            "session": session,
            "correct_answers": correct_answers,
            "total_questions": total_questions,
            "score": score,
            "iq": iq
        })

    # Prepare data for graphs
    dates = [result["session"].end_time.strftime("%Y-%m-%d %H:%M") for result in results]
    iq_scores = [result["iq"] for result in results]
    percentages = [result["score"] for result in results]

    # Data for pie chart of the latest session
    if results:
        latest_correct = results[0]["correct_answers"]
        latest_total = results[0]["total_questions"]
        latest_incorrect = latest_total - latest_correct
    else:
        latest_correct = 0
        latest_incorrect = 0

    # Pass data to the template
    return render(request, "quiz/dashboard.html", {
        "section": "dashboard",
        "results": results,
        "dates": json.dumps(dates),  # Serialize for JavaScript
        "iq_scores": json.dumps(iq_scores),
        "percentages": json.dumps(percentages),
        "latest_correct": latest_correct,
        "latest_incorrect": latest_incorrect,
        "test_sessions": test_sessions,
        "review_form": form,
    })

@login_required
def take_test(request):
    """
    Start a new test session and render the test template, ending any active sessions.
    """

    # fix the bug with sessions not being marked as completed immidiately 
    # End all active sessions for the user
    TestSession.objects.filter(user=request.user, is_completed=False).update(
        # is_completed=True,
        end_time=timezone.now()
    )

    # Create a new session
    session = TestSession.objects.create(user=request.user, start_time=timezone.now())
    questions = select_random_questions()
    session.questions.set(questions)
    session.save()

    context = {"session_id": session.id, "total_questions": 5}
    return render(request, "quiz/take_test.html", context)

def select_random_questions(num_questions=5):
    """
    Select 25 random questions, prioritizing diversity across categories.
    """
    categories = Question.objects.values_list("category", flat=True).distinct()
    selected_questions = []

    for category in categories:
        questions_in_category = list(Question.objects.filter(category=category))
        if questions_in_category:
            selected_questions.extend(random.sample(questions_in_category, min(2, len(questions_in_category))))

    while len(selected_questions) < num_questions:
        remaining_questions = Question.objects.exclude(id__in=[q.id for q in selected_questions])
        if remaining_questions.exists():
            selected_questions.append(random.choice(remaining_questions))

    random.shuffle(selected_questions)
    return selected_questions[:num_questions]


@login_required
def get_question(request):
    """AJAX endpoint to fetch a question and handle answer submission."""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method"})

    session = TestSession.objects.get(id=request.POST.get("session_id"), user=request.user)
    questions = list(session.questions.all())

    time_elapsed = (timezone.now() - session.start_time).total_seconds()
    if time_elapsed > 60:
        session.is_completed = True
        session.end_time = timezone.now()
        session.save()
        return JsonResponse({"status": "completed"})

    current_index = int(request.POST.get("current_index", 0))

    # Check completion first
    if current_index >= len(questions):
        session.is_completed = True
        session.end_time = timezone.now()
        session.save()
        return JsonResponse({"status": "completed"})

    # Handle answer submission only if within bounds
    if "answer" in request.POST:
        question_id = request.POST.get("question_id")
        selected_answer = request.POST.get("answer", "").strip()
        question = questions[current_index]  # Safe now
        is_correct = selected_answer == question.correct_answer if selected_answer else False
        UserAnswer.objects.update_or_create(
            test_session=session,
            question=question,
            defaults={"selected_answer": selected_answer if selected_answer else None, "is_correct": is_correct}
        )
        session.score = session.answers.filter(is_correct=True).count()
        session.save()

    # Fetch the current question
    question = questions[current_index]
    options = question.options if question.options else {}
    option_images = {img.key: img.image.url for img in question.option_images.all()}

    return JsonResponse({
        "status": "success",
        "question_id": question.id,
        "text": question.text,
        "has_image": question.has_image,
        "image_url": question.image.url if question.has_image else None,
        "options": options,
        "option_images": option_images,
        "current_index": current_index,
        "total_questions": len(questions),
        "time_remaining": max(0, 60 - int(time_elapsed))
    })


@login_required
def certificate_form(request, session_id):
    """Render a form for the user to input their name for the certificate."""      
    test_session = get_object_or_404(TestSession, id=session_id, user=request.user, payment_status__in=["paid", "shared"])
    return render(request, "quiz/certificate_form.html", {"test_session": test_session})

@login_required
def generate_certificate(request, session_id):
    """Generate a PDF certificate with the user"s name, IQ score, and date."""
    test_session = get_object_or_404(TestSession, id=session_id, user=request.user, payment_status__in=["paid", "shared"])

    if request.method != "POST":
        return redirect("certificate_form", session_id=session_id)

    # Get the user"s name from the form
    certificate_name = request.POST.get("certificate_name", "").strip()
    if not certificate_name:
        return redirect("certificate_form", session_id=session_id)
    

    # Calculate IQ score for this session
    correct_answers = UserAnswer.objects.filter(test_session=test_session, is_correct=True).count()
    total_questions = test_session.questions.count()
    iq = 40 + (correct_answers / total_questions) * 120 if total_questions > 0 else 0

    # Load the certificate template image
    template_path = os.path.join(settings.STATICFILES_DIRS[0], "images", "IQforge certificate.png")
    image = Image.open(template_path)
    draw = ImageDraw.Draw(image)

    # Load a font (use a TTF font available on your system or include one)
    try:
        font_path = os.path.join(settings.STATICFILES_DIRS[0], "fonts", "times.ttf")  # Adjust to your font
        font_size = 60  # Starting font size
        
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()  # Fallback to default font

    # Adjust font size based on name length
    name = certificate_name.upper()
    max_width = 1400  # Adjust based on your template"s name area width
    while font.getbbox(name)[2] > max_width and font_size > 20:
        font_size -= 5
        font = ImageFont.truetype(font_path, font_size)

    # Position the text (adjust coordinates based on your template)
    name_position = (image.width // 2 - font.getbbox(name)[2] // 2, 520)  # Adjust Y-coordinate
    # Draw the name in bold
    draw.text(name_position, name, font=font, fill=(0, 0, 0))  # Black text
    draw.text((name_position[0] + 1, name_position[1]), name, font=font, fill=(0, 0, 0))  # Offset slightly for bold effect

    # Add IQ score
    iq_text = str(int(iq))
    iq_font = ImageFont.truetype(font_path, 80)  # Larger font for IQ score
    iq_position = (image.width // 2 - iq_font.getbbox(iq_text)[2] // 2, 700)  # Adjust Y-coordinate
    draw.text(iq_position, iq_text, font=iq_font, fill=(0, 0, 0))

    # Add date
    date_text = f"Date of Receiving:\n {timezone.now().strftime('%d.%m.%Y')}"
    date_font = ImageFont.truetype(font_path, 30)
    date_position = (470, 1280)  # Adjust based on template
    draw.text(date_position, date_text, font=date_font, fill=(0, 0, 0))

    # Add certificate ID
    cert_id = f"{session_id:03d}-{int(iq):03d}"  # e.g., "001-117"
    cert_id_text = f"Certificate ID:\n {cert_id}"
    cert_id_position = (image.width - 750, 1280)  # Adjust based on template
    draw.text(cert_id_position, cert_id_text, font=date_font, fill=(0, 0, 0))

    # Save the modified image to a buffer
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    # Create a PDF with the image in landscape orientation
    pdf_buffer = BytesIO()
    pdf = canvas.Canvas(pdf_buffer, pagesize=landscape(letter))  # Set to landscape
    pdf.drawImage(ImageReader(buffer), 0, 0, width=landscape(letter)[0], height=landscape(letter)[1])
    pdf.save()
    pdf_buffer.seek(0)

    # Create the media/certificates directory if it doesn't exist
    certificate_dir = os.path.join(settings.MEDIA_ROOT, 'certificates')
    os.makedirs(certificate_dir, exist_ok=True)
    
    # Create a unique filename
    filename = f"iq_certificate_{session_id}_{int(timezone.now().timestamp())}.pdf"
    file_path = os.path.join(certificate_dir, filename)
    
    # Save the PDF to the file
    with open(file_path, 'wb') as f:
        f.write(pdf_buffer.read())
    
    # Create a URL for the certificate file
    certificate_url = f"{settings.MEDIA_URL}certificates/{filename}"
    
    # Store certificate path in session for retrieval by success page
    request.session['certificate_path'] = certificate_url
    
    # Redirect to success page
    return redirect('certificate_generated')

@login_required
def certificate_generated(request):
    """Render a page indicating the certificate has been generated."""
    certificate_path = request.session.get('certificate_path', None)
    
    # Clear the session variable after retrieving it
    if 'certificate_path' in request.session:
        del request.session['certificate_path']
    
    return render(request, "quiz/certificate_generated.html", {
        "certificate_path": certificate_path
    })

def logout_view(request):
    logout(request)
    return render(request, "quiz/index.html", {"message": "Logged out."})


def register(request):
    if request.method == "POST":
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data["password"])
            new_user.save()
            backend = "django.contrib.auth.backends.ModelBackend"
            login(request, new_user, backend=backend)
            return redirect("dashboard")
    else:
        user_form = UserRegistrationForm()
    return render(request, "quiz/register.html", {"user_form": user_form})

# sharing sytems views

@login_required
def share_to_view(request, session_id):
    # Get the session, ensure it's completed and still pending payment
    session = get_object_or_404(
        TestSession,
        id=session_id,
        user=request.user,
        is_completed=True,
        payment_status="pending"
    )
    return render(request, "quiz/share_to_view.html", {"session": session})

@login_required
def confirm_share(request, session_id):
    if request.method == "POST":
        # Update payment_status to "shared" when user confirms sharing
        session = get_object_or_404(
            TestSession,
            id=session_id,
            user=request.user,
            is_completed=True,
            payment_status="pending"
        )
        session.payment_status = "shared"
        session.save()
        return redirect("share_success", session_id=session.id)
    return redirect("share_to_view", session_id=session_id)

@login_required
def share_success(request, session_id):
    # Ensure the session is marked as shared
    session = get_object_or_404(
        TestSession,
        id=session_id,
        user=request.user,
        is_completed=True,
        payment_status="shared"
    )
    return render(request, "quiz/share_success.html", {"session": session})




# def login_view(request):
#     if request.method == "POST":

#       form = LoginForm(request.POST)
#       if form.is_valid():
#         cd = form.cleaned_data
#         user = authenticate(request, username=cd["username"], password=cd["password"])
#         if user is not None:
#             if user.is_active:
#                 login(request, user)
#                 return HttpResponse("Login Successful")
#             else:
#                 return HttpResponse("Disabled account")
#         else:
#             return HttpResponse("Invalid login crediantials")
#     else:
#         form = LoginForm()
#     return render(request, "quiz/login.html", {"form": form})

# Admin views
@login_required
def manage_reviews(request):
    """Admin view to manage review approval"""
    if not request.user.is_staff:
        return redirect('dashboard')
    
    reviews = Review.objects.all().order_by('-created_at')
    
    if request.method == "POST":
        review_id = request.POST.get("review_id")
        action = request.POST.get("action")
        
        if review_id and action:
            review = get_object_or_404(Review, id=review_id)
            
            if action == "approve":
                review.approved = True
                review.save()
                messages.success(request, f"Review by {review.user.username} approved.")
            elif action == "reject":
                review.delete()
                messages.success(request, f"Review by {review.user.username} deleted.")
    
    return render(request, "quiz/admin/manage_reviews.html", {
        "reviews": reviews
    })