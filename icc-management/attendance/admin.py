from django.contrib import admin
from .models import ServiceEvent, Attendance

@admin.register(ServiceEvent)
class ServiceEventAdmin(admin.ModelAdmin):
    list_display = ('name', 'event_type', 'date')
    list_filter = ('event_type', 'date')
    search_fields = ('name',)
    ordering = ('-date',)

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('servant', 'event', 'department', 'status', 'marked_by', 'timestamp')
    list_filter = ('status', 'department', 'event', 'marked_by')
    search_fields = ('servant__nom', 'servant__prenom', 'event__name')
    ordering = ('-timestamp',)
    
    # Pour rendre la lecture plus facile dans l'admin
    def servant(self, obj):
        return f"{obj.servant.prenom} {obj.servant.nom}"
    servant.short_description = 'Serviteur'