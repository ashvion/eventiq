from django.db import models

# Create your models here.


class Event(models.Model):
    EVENT_TYPES = [
        ('Tech', 'Tech'),
        ('Concert', 'Concert'),
        ('Conference', 'Conference'),
        ('Workshop', 'Workshop'),
    ]

    title = models.CharField(max_length=200)
    date = models.DateField()
    location = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    seats = models.PositiveIntegerField(default=0)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES, default='Tech')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.date}) - {self.event_type}"


import uuid

import random
import string

class Booking(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    ticket_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    short_code = models.CharField(max_length=8, unique=True, blank=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='bookings', null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    seats = models.PositiveIntegerField(default=1)
    date = models.DateField(auto_now_add=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.short_code:
            # Generate a random 6-character alphanumeric code
            chars = string.ascii_uppercase + string.digits
            while True:
                code = ''.join(random.choices(chars, k=6))
                if not Booking.objects.filter(short_code=code).exists():
                    self.short_code = code
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.event.title} ({self.short_code})"


class Expense(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='expenses')
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - ${self.amount}"