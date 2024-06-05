from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .models import Profile, Report, Image, OperationLine, Profession, Solution
from django import forms
from django.contrib.auth.models import Group
# Register your models here.

# custom filters 

class ProfessionFilter(admin.SimpleListFilter):
    title = 'Profession'
    parameter_name = 'profession'

    def lookups(self, request, model_admin):
        professions = Profession.objects.all()
        return [(profession.id, profession.profession_name) for profession in professions]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(profile__profession__id=self.value())
        return queryset

class OperationLineFilter(admin.SimpleListFilter):
    title = 'Operation Line'
    parameter_name = 'operationLineNo'

    def lookups(self, request, model_admin):
        operation_lines = OperationLine.objects.all()
        return [(operation_line_no.id, operation_line_no) for operation_line_no in operation_lines]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(profile__operation_line_no__id=self.value())
        return queryset
    
# End of custom filters

# Images for report
from .models import Report, Image

class ImageInline(admin.TabularInline):
    model = Image
    extra = 0

class ReportAdmin(admin.ModelAdmin):
    inlines = [ImageInline]
    list_filter = ('status',)
    list_display = ('reportID', 'reporterName', 'operationLineNumber', 'problemCategory', 'status', 'datetime')

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
 

# for user diaplay
class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'get_groups', 'get_operation_lines', 'get_profession')
    list_filter = ('groups', OperationLineFilter, ProfessionFilter)
    def get_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
    get_groups.short_description = 'Groups'
    
    def get_operation_lines(self, obj):
        profile = Profile.objects.get(user=obj)
        return ", ".join([operation_line_no.line_no for operation_line_no in profile.operation_line_no.all()])
    get_operation_lines.short_description = 'Operation Lines'
    
    def get_profession(self, obj):
        profile = Profile.objects.get(user=obj)
        return ", ".join([profession.profession_name for profession in profile.profession.all()])
    get_profession.short_description = 'Profession'


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(OperationLine)
admin.site.register(Profession)
admin.site.register(Solution)


