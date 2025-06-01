from django.contrib import admin
from .models import Question, TestSession, UserAnswer, Review
from django.utils.safestring import mark_safe


# Add Exporting orders to CSV files


def order_payment(obj):
    url = obj.get_stripe_url()
    if obj.stripe_session_id:
        return mark_safe(f'<a href="{url}" target="_blank">{obj.stripe_session_id}</a>')
    return '-'
order_payment.short_description = 'Stripe Payment'
    

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('source_id', 'category', 'text','correct_answer', 'hint')  # Hint in list view
    list_filter = ('category',)
    search_fields = ('text', 'hint')

@admin.register(TestSession)
class TestSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_time', 'end_time', 'is_completed', 'score', 'payment_status', order_payment)
    list_filter = ('is_completed',)

@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('test_session', 'question', 'selected_answer', 'hint', 'is_correct')
    list_filter = ('is_correct',)
    # search_fields = ('question__text', 'test_session__user__username')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'comment', 'created_at', 'approved')
    list_filter = ('rating', 'approved')
    search_fields = ('user__username', 'comment')
    # date_hierarchy = 'created_at' 
    ordering = ('-created_at',)
    actions = ['approve_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(approved=True)
    approve_reviews.short_description = "Approve selected reviews"