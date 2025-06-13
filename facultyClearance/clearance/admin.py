from django.contrib import admin
from .models import (
    Department,
    FacultyMember,
    DepartmentChair,
    CollegeDean,
    ClearanceDocument
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(FacultyMember)
class FacultyMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'department')
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


@admin.register(ClearanceDocument)
class ClearanceDocumentAdmin(admin.ModelAdmin):
    list_display = ('document_type', 'uploader', 'role', 'department', 'status', 'uploaded_at')
    list_filter = ('role', 'department', 'status', 'uploaded_at')
    search_fields = ('uploader__username', 'document_type', 'comments')
    readonly_fields = ('uploaded_at',)