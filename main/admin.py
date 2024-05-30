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


# adding more options in the admin panel

# class ProfileInline(admin.StackedInline):
#     model = Profile
#     can_delete = False
#     verbose_name_plural = 'Profile'

# class CustomUserAdmin(UserAdmin):
#     inlines = (ProfileInline,)
#     list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_operation_line_no', 'get_profession')

#     def get_operation_line_no(self, instance):
#         return instance.profile.operation_line_no if hasattr(instance, 'profile') else None

#     get_operation_line_no.short_description = 'Operation Line No'

#     def get_profession(self, instance):
#         return instance.profile.profession if hasattr(instance, 'profile') else None
    
#     get_profession.short_description = 'Profession'

# admin.site.unregister(User)
# admin.site.register(User, CustomUserAdmin)

# class ProfileInline(admin.StackedInline):
#     model = Profile
#     can_delete = False
#     verbose_name_plural = 'Profile'

# class CustomUserAdmin(UserAdmin):
#     inlines = (ProfileInline,)
#     list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_operation_line_no', 'get_profession')

#     def get_operation_line_no(self, instance):
#         return instance.profile.operation_line_no.line_no if hasattr(instance, 'profile') and instance.profile.operation_line_no else None

#     get_operation_line_no.short_description = 'Operation Line No'

#     def get_profession(self, instance):
#         return instance.profile.profession.profession_name if hasattr(instance, 'profile') and instance.profile.profession else None
    
#     get_profession.short_description = 'Profession'

# admin.site.unregister(User)
# admin.site.register(User, CustomUserAdmin)
# admin.site.register(OperationLine)
# admin.site.register(Profession)



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



