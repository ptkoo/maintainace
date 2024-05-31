from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile
from .models import Profile, Report, Image, OperationLine, Profession
from django import forms
# Register your models here.

from .models import Report, Image

class ImageInline(admin.TabularInline):
    model = Image
    extra = 0

class ReportAdmin(admin.ModelAdmin):
    inlines = [ImageInline]

admin.site.register(Report, ReportAdmin)

# Adding more options for Operation Line No and profession
class ProfileAdminForm(forms.ModelForm):
    operation_line_no = forms.ModelMultipleChoiceField(
        queryset=OperationLine.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    profession = forms.ModelMultipleChoiceField(
        queryset=Profession.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Profile
        fields = '__all__'

class OperationLineInline(admin.TabularInline):
    model = Profile.operation_line_no.through
    extra = 1

class ProfessionInline(admin.TabularInline):
    model = Profile.profession.through
    extra = 1

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    form = ProfileAdminForm
    inlines = [OperationLineInline, ProfessionInline]

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(OperationLine)
admin.site.register(Profession)



