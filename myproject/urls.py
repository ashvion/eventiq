"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from .views import (home, sbc, abc, xyz, events, booking, create_event, 
                    booking_confirmation, scanner, verify_ticket,
                    signup, signin, user_logout, profile, ai_agent, chat_api,
                    event_details, payment_page, process_payment)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/chat/', chat_api, name='chat_api'),
    path('', home, name='home'),
    path('home/', home, name='home'),
    path('sbc/', sbc, name='sbc'),
    path('abc/', abc, name='abc'),
    path('xyz/', xyz, name='xyz'),
    path('events/', events, name='events'),
    path('events/<int:event_id>/', event_details, name='event_details'),
    path('events/create/', create_event, name='create_event'),
    path('booking/', booking, name='booking'),
    path('payment/<uuid:booking_id>/', payment_page, name='payment_page'),
    path('process-payment/<uuid:booking_id>/', process_payment, name='process_payment'),
    path('ticket/<uuid:booking_id>/', booking_confirmation, name='booking_confirmation'),
    path('scanner/', scanner, name='scanner'),
    path('verify-ticket/<str:ticket_id>/', verify_ticket, name='verify_ticket'),
    # Authentication URLs
    path('signup/', signup, name='signup'),
    path('signin/', signin, name='signin'),
    path('logout/', user_logout, name='logout'),
    path('profile/', profile, name='profile'),
    path('ai-agent/', ai_agent, name='ai_agent'),
    # path('karthik/', include('app1.urls')),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
