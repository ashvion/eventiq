from django.contrib import admin
from .models import Event, Booking

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'location')
    search_fields = ('title', 'location')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'event', 'short_code', 'ticket_id', 'date')
    search_fields = ('name', 'email', 'event__title', 'short_code', 'ticket_id')
    readonly_fields = ('ticket_id', 'short_code', 'date')
    list_filter = ('event', 'date')