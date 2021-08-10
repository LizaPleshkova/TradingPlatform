from django.contrib import admin
from work_shift.models import WorkShift, Position, Plan


class PlanAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'start', 'end')
    search_fields = ['name']


class PositionAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name',)
    list_filter = ['first_name']


class WorkShiftAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'plan', 'start_date', 'end_date')
    search_fields = ['name']
    list_filter = ['plan']


admin.site.register(WorkShift, WorkShiftAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.register(Plan, PlanAdmin)
