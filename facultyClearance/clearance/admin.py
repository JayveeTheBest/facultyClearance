from django.contrib import admin
from .models import (
    Department,
    FacultyMember,
    DepartmentChair,
    CollegeDean,
    Requirement,
    Upload
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(FacultyMember)
class FacultyMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'is_part_time')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    list_filter = ('department',)


@admin.register(DepartmentChair)
class DepartmentChairAdmin(admin.ModelAdmin):
    list_display = ('user', 'department')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    list_filter = ('department',)


@admin.register(CollegeDean)
class CollegeDeanAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')


@admin.register(Requirement)
class RequirementAdmin(admin.ModelAdmin):
    list_display = ('title', 'applicable_to', 'created_at')
    search_fields = ('title',)
    ordering = ('-created_at',)


@admin.register(Upload)
class UploadAdmin(admin.ModelAdmin):
    list_display = ('requirement', 'uploaded_by', 'get_department', 'status', 'uploaded_at')
    list_filter = ('status',)
    search_fields = ('requirement__name', 'uploaded_by__username')  # ✅ corrected field

    def get_department(self, obj):
        user = obj.uploaded_by
        if hasattr(user, 'facultymember'):
            return user.facultymember.department.name
        elif hasattr(user, 'departmentchair'):
            return user.departmentchair.department.name
        return 'N/A'

    get_department.short_description = 'Department'
