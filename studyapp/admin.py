from django.contrib import admin
from django.urls import reverse
from django.urls import path
from django.shortcuts import render, redirect
from django.utils.html import format_html
from .models import StudySpot, Review


class StudySpotSubmissionAdmin(admin.ModelAdmin):
    list_display = ('building', 'room_number', 'lat', 'lng','submitted_by', 'is_approved','submission_date',)
    list_editable = ('building', 'room_number', 'is_approved',)
    list_display_links = ('lat',)  
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('approve-submission/<int:id>/', self.admin_approve_submission, name='admin-approve-submission'),
        ]
        return custom_urls + urls
    
    def admin_approve_submission(self, request, id):
        study_spot = StudySpot.objects.get(id=id)
        if study_spot:
            study_spot.is_approved = True
            study_spot.save()
            return redirect('admin:studyapp_studyspot_change', study_spot.id)
        else:
            return redirect('admin:studyapp_studyspot_changelist')
admin.site.register(StudySpot, StudySpotSubmissionAdmin)

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('building', 'room_number','rating', 'noise_level', 'crowdedness', 'comfort', 'location', 'parking', 'hours', 'occupancy', 'description','is_approved')
    list_editable = ('building', 'room_number', 'is_approved',)
    list_display_links = ('rating',)  
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('approve-review/<int:id>/', self.admin_approve_review, name='admin-approve-review'),
        ]
        return custom_urls + urls
    
    def admin_approve_review(self, request, id):
        review = Review.objects.get(id=id)
        if review:
            review.is_approved = True
            review.save()
            return redirect('admin:studyapp_review_change', review.id)
        else:
            return redirect('admin:studyapp_review_changelist')

admin.site.register(Review, ReviewAdmin)
