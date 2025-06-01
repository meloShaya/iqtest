from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views
from . import views

# app_name = 'quiz'

urlpatterns = [
    # path('api/questions/', QuestionList.as_view(), name='api-question-list'),
    path('', views.index, name='index'),
    path('question_list/', views.question_list, name='question_list'),
    path('take_test/', views.take_test, name='take_test'),
    path('start/', views.start, name='start'),
    path('get-question/', views.get_question, name='get_question'),
    path('certificate/<int:session_id>/', views.certificate_form, name='certificate_form'),
    path('generate-certificate/<int:session_id>/', views.generate_certificate, name='generate_certificate'),
    path('certificate_generated/', views.certificate_generated, name='certificate_generated'),
    # path('test-summary/', views.test_summary, name='test_summary'),
    path('logout/', views.logout_view, name='logout'),
    path('', include('django.contrib.auth.urls')),
    path('share-to-view/<int:session_id>/', views.share_to_view, name='share_to_view'),
    path('confirm-share/<int:session_id>/', views.confirm_share, name='confirm_share'),
    path('share-success/<int:session_id>/', views.share_success, name='share_success'),
    # path('login/', auth_views.LoginView.as_view(), name='login'),
    # # change password urls
    # path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    # path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    # # reset password urls
    # path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    # path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    # path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    # path('register_done/', views.register_done, name='register_done'),

    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # Admin URLs
    path('staff/manage-reviews/', views.manage_reviews, name='manage_reviews'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)