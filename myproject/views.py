from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
import json
from django.views.decorators.csrf import csrf_exempt

def home(request):
    """Render a simple home page (no calculator)."""
    return render(request, 'home.html')


from app1.models import Event

def events(request):
    """Show a simple list of events from the database."""
    # Fetch events from Database
    all_events = Event.objects.all().order_by('date')
    
    return render(request, 'events.html', {'events': all_events})

def event_details(request, event_id):
    """Show detailed page for a single event."""
    event = get_object_or_404(Event, pk=event_id)
    return render(request, 'event_details.html', {'event': event})



@user_passes_test(lambda u: u.is_superuser)
def create_event(request):
    """Create a new event and log data to terminal. Only accessible by admins."""
    if request.method == 'POST':
        title = request.POST.get('title')
        date = request.POST.get('date')
        location = request.POST.get('location')
        description = request.POST.get('description')
        seats = request.POST.get('seats', 0)
        event_type = request.POST.get('event_type', 'Tech')
        price = request.POST.get('price', 0.00)
        image = request.FILES.get('image')
        
        # LOGGING TO TERMINAL AS REQUESTED
        print("\n" + "="*40)
        print(" NEW EVENT CREATED ")
        print("="*40)
        print(f"Title:       {title}")
        print(f"Date:        {date}")
        print(f"Location:    {location}")
        print(f"Seats:       {seats}")
        print(f"Type:        {event_type}")
        print(f"Price:       {price}")
        print(f"Description: {description}")
        print(f"Image:       {image}")
        print("="*40 + "\n")
        
        # Save to Database
        if title and date and location:
             Event.objects.create(
                title=title,
                date=date,
                location=location,
                description=description,
                seats=seats,
                event_type=event_type,
                price=price,
                image=image
            )
        
        return redirect('events')

    return render(request, 'create_event.html')


from app1.models import Event, Booking

def booking(request):
    """Display booking form and process bookings saving them to database."""
    message = None
    # Fetch events from Database
    events_list = Event.objects.all().order_by('date')

    # prefill event if passed as query param
    event_id = request.GET.get('event_id')
    event_name = request.GET.get('event_name')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        event_id_post = request.POST.get('event', '').strip()
        seats = request.POST.get('seats', '1').strip()

        if not name or not email or not event_id_post:
            message = {'type': 'error', 'text': 'Please fill name, email and select an event.'}
        else:
            try:
                # Validate seats
                seats_int = int(seats)
                if seats_int < 1 or seats_int > 2:
                    message = {'type': 'error', 'text': 'Please select 1 or 2 seats only.'}
                else:
                    selected_event = Event.objects.get(id=event_id_post)
                    
                    if selected_event.seats < seats_int:
                        message = {'type': 'error', 'text': f'Sorry, only {selected_event.seats} seats left.'}
                    else:
                        # Decrement seats
                        selected_event.seats -= seats_int
                        selected_event.save()

                        # Create Booking in DB with pending payment status
                        booking = Booking.objects.create(
                            event=selected_event,
                            user=request.user if request.user.is_authenticated else None,
                            name=name,
                            email=email,
                            seats=seats_int,
                            payment_status='pending'
                        )
                        return redirect('payment_page', booking_id=booking.ticket_id)
            except ValueError:
                message = {'type': 'error', 'text': 'Invalid number of seats.'}
            except Event.DoesNotExist:
                message = {'type': 'error', 'text': 'Selected event does not exist.'}
            except Exception as e:
                message = {'type': 'error', 'text': f'Error saving booking: {e}'}

    return render(request, 'booking.html', {
        'message': message,
        'events': events_list,
        'event_id': event_id,
        'event_name': event_name,
    })


import qrcode
from io import BytesIO
import base64
from app1.models import Booking

def booking_confirmation(request, booking_id):
    """Generate QR code and show ticket."""
    try:
        booking = Booking.objects.get(ticket_id=booking_id)
        
        # Create QR Code
        qr_data = booking.ticket_id
        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=5
        )
        qr.add_data(str(qr_data))
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        
        # Save to buffer
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        qr_image = base64.b64encode(buffer.getvalue()).decode()
        
        return render(request, 'ticket.html', {'booking': booking, 'qr_image': qr_image})
    except Booking.DoesNotExist:
        return HttpResponse("Ticket not found", status=404)

from django.http import JsonResponse 

def scanner(request):
    """Admin page to scan tickets."""
    return render(request, 'scanner.html')

def verify_ticket(request, ticket_id):
    """API to verify if a ticket is valid."""
    try:
        # Try to find by UUID first, then by short_code
        if len(ticket_id) <= 10:  # Likely a short code
            booking = Booking.objects.get(short_code=ticket_id.upper())
        else:  # Likely a UUID
            booking = Booking.objects.get(ticket_id=ticket_id)
        
        return JsonResponse({
            'valid': True,
            'attendee': booking.name,
            'event': booking.event.title,
            'code': booking.short_code
        })
    except Booking.DoesNotExist:
        return JsonResponse({'valid': False})


# ============================================
# AUTHENTICATION VIEWS
# ============================================

def signup(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect('profile')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        password2 = request.POST.get('password2', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        
        # Validation
        if not username or not email or not password:
            messages.error(request, 'Please fill in all required fields.')
        elif password != password2:
            messages.error(request, 'Passwords do not match.')
        elif len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
        else:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            # Auto login after registration
            login(request, user)
            messages.success(request, f'Welcome to EventIQ, {user.first_name or user.username}!')
            return redirect('profile')
    
    return render(request, 'signup.html')


def signin(request):
    """User login view."""
    if request.user.is_authenticated:
        return redirect('profile')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        
        if not username or not password:
            messages.error(request, 'Please enter both username and password.')
        else:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                next_url = request.GET.get('next', 'profile')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
    
    return render(request, 'signin.html')


def user_logout(request):
    """User logout view."""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required(login_url='signin')
def profile(request):
    """User profile page showing user info and bookings."""
    user_bookings = Booking.objects.filter(user=request.user).select_related('event').order_by('-date')
    
    context = {
        'user': request.user,
        'bookings': user_bookings,
        'total_bookings': user_bookings.count()
    }
    
    return render(request, 'profile.html', context)


def sbc(request):
    return HttpResponse("My First webpage")

def abc(request):
    return HttpResponse("My First response")

def xyz(request):
    return HttpResponse(" response on webpage")


from django.utils import timezone
from django.db.models import Sum
from app1.models import Expense

def ai_agent(request):
    """
    Budget Planner AI Agent & Expense Dashboard.
    """
    today = timezone.now().date()
    current_month_start = today.replace(day=1)
    current_year_start = today.replace(month=1, day=1)
    
    suggested_events = []
    ai_response = None

    # Handle Forms
    if request.method == 'POST':
        if 'add_expense' in request.POST:
            # Handle Expense Addition
            title = request.POST.get('title')
            amount = request.POST.get('amount')
            category = request.POST.get('category')
            if title and amount:
                if request.user.is_authenticated:
                    Expense.objects.create(
                        user=request.user,
                        title=title,
                        amount=amount,
                        category=category
                    )
                messages.success(request, "Expense added successfully!")
                return redirect('ai_agent')
                
        elif 'ask_agent' in request.POST:
            # Handle AI Planning (Event Suggestions)
            interests = request.POST.get('interests', '').lower()
            budget = request.POST.get('budget', 0)
            
            try:
                budget = float(budget)
            except ValueError:
                budget = 0
            
            # Simple keyword matching logic
            all_events = Event.objects.all().order_by('date')
            for event in all_events:
                # Mock price checking would happen here
                lower_title = event.title.lower() if event.title else ""
                lower_desc = event.description.lower() if event.description else ""
                
                if interests in lower_title or interests in lower_desc:
                    suggested_events.append(event)
            
            if not suggested_events:
                ai_response = f"I couldn't find any events matching '{interests}' this month. Maybe try 'Tech' or 'Music'?"
            else:
                ai_response = f"Based on your interest in '{interests}', here are some events I found:"

        elif 'chat_message' in request.POST:
             # Handle Chat Intent
             user_message = request.POST.get('chat_message')
             mode = request.POST.get('mode', 'general')
             
             try:
                 import google.generativeai as genai
                 from django.conf import settings
                 import os
                 from app1.models import Event, Booking
                 
                 api_key = getattr(settings, 'GEMINI_API_KEY', '') or os.environ.get('GEMINI_API_KEY', '')
                 
                 if not api_key:
                      return JsonResponse({'reply': "I'm not configured yet! Please set the GEMINI_API_KEY."})
                 
                 genai.configure(api_key=api_key)

                 # Use isolated history based on mode (same as chat_api for consistency)
                 history_key = f'chug_history_ai_agent_{mode}'
                 session_history = request.session.get(history_key, [])
                 
                 # Reconstruct history for Gemini
                 history = []
                 for msg in session_history:
                     history.append({
                         "role": msg["role"],
                         "parts": [{"text": msg["parts"][0]["text"]}]
                     })

                 # Use the same system instruction as chat_api for consistency
                 system_instruction = f"""
                 You are Chug, the AI assistant for EventIQ.
                 You help users explore events, understand platform features, and book tickets.
                 
                 VISIBLE AUTOMATION (YOUR REAL POWER):
                 You HAVE the power to redirect the user to the booking tab. 
                 When you call 'book_event', the user's browser WILL be redirected automatically.
                 They will see the form being automatically filled and confirmed for them.
                 NEVER say you cannot redirect or open a tab. You DO THIS via the tool.
                 
                 TOOLS:
                 - Use 'list_events' to show upcoming events.
                 - Use 'book_event' ONLY when you have: Event ID, Name, Email, and Seats (1 or 2).
                 
                 RULES:
                 1. Be helpful and informative.
                 2. You MUST ask for the number of seats (1 or 2) if not specified.
                 3. Once you call 'book_event', tell the user: "I'm taking you to the booking tab now. You'll see the form being filled and confirmed automatically for you!"
                 
                 USER CONTEXT:
                 - Auth User: {request.user.username if request.user.is_authenticated else "Guest"}
                 """
                 
                 # Setup model with tools
                 model = genai.GenerativeModel(
                     model_name='gemini-2.5-flash', 
                     system_instruction=system_instruction,
                     tools=[list_events, book_event]
                 )
                 
                 # Chat session for history and automatic tool calling
                 chat = model.start_chat(history=history, enable_automatic_function_calling=True)
                 response = chat.send_message(user_message)
                 
                 # Safe extraction of text parts to avoid "response.text" error
                 bot_reply = "".join([p.text for p in response.candidates[0].content.parts if hasattr(p, 'text') and p.text]) or "I've initiated the action for you!"
                 
                 # Save history back to session
                 updated_history = []
                 for content in chat.history:
                     text_parts = [p.text for p in content.parts if hasattr(p, 'text') and p.text]
                     if text_parts:
                         updated_history.append({
                             "role": content.role,
                             "parts": [{"text": " ".join(text_parts)}]
                         })
                 request.session[history_key] = updated_history
                 
                 # Search for redirect URL in tool calls
                 redirect_url = None
                 for history_item in chat.history[-2:]:
                     for part in history_item.parts:
                         if part.function_response:
                             resp_data = part.function_response.response
                             if resp_data and hasattr(resp_data, 'get'):
                                 if resp_data.get('status') == 'success' and 'redirect_url' in resp_data:
                                     redirect_url = resp_data['redirect_url']

                 return JsonResponse({
                     'reply': bot_reply,
                     'redirect': redirect_url
                 })
             except Exception as e:
                 return JsonResponse({'reply': f"I encountered an error: {str(e)}"}, status=500)

    # Dashboard Stats - only for authenticated users
    if request.user.is_authenticated:
        expenses = Expense.objects.filter(user=request.user).order_by('-date')
        monthly_expenses = expenses.filter(date__gte=current_month_start).aggregate(Sum('amount'))['amount__sum'] or 0
        yearly_expenses = expenses.filter(date__gte=current_year_start).aggregate(Sum('amount'))['amount__sum'] or 0
    else:
        expenses = []
        monthly_expenses = 0
        yearly_expenses = 0

    context = {
        'expenses': expenses[:5] if expenses else [], # Show recent 5
        'monthly_total': monthly_expenses,
        'yearly_total': yearly_expenses,
        'suggested_events': suggested_events,
        'ai_response': ai_response
    }
    return render(request, 'ai_agent.html', context)


# --- AI AGENCY TOOLS ---
def list_events():
    """Lists all upcoming events available for booking in the system."""
    from app1.models import Event
    events = Event.objects.all().order_by('date')
    return [{
        "id": e.id,
        "title": e.title,
        "date": str(e.date),
        "price": float(e.price),
        "location": e.location,
        "seats_available": e.seats
    } for e in events]

def book_event(event_id: int, seats: int, name: str, email: str):
    """
    Triggers the booking process. 
    Required parameters:
    - event_id: The unique ID of the event.
    - seats: Number of seats (must be 1 or 2).
    - name: Full name of the attendee.
    - email: Email address for confirmation.
    
    Returns a redirect URL that triggers client-side auto-fill and automatic submission.
    """
    from urllib.parse import urlencode
    from app1.models import Event
    
    event_title = ""
    try:
        event = Event.objects.get(id=event_id)
        event_title = event.title
    except:
        pass

    params = {
        'auto_fill': 'true',
        'event_id': event_id,
        'event_title': event_title,
        'name': name,
        'email': email,
        'seats': seats
    }
    
    redirect_url = f"/booking/?{urlencode(params)}"
    
    return {
        "status": "success",
        "redirect_url": redirect_url
    }

@csrf_exempt
def chat_api(request):
    """
    Dedicated API endpoint for the Global Chat Widget and Voice Assistant.
    Supports modes: 'general', 'booking'.
    """
    if request.method == 'POST':
        try:
            print("--- Chat API Request Received ---")
            
            # Handle both JSON and Form data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                user_message = data.get('message', '')
                mode = data.get('mode', 'general') # Default to general
            else:
                user_message = request.POST.get('chat_message', '')
                mode = request.POST.get('mode', 'general')
            
            print(f"Mode: {mode} | Message: {user_message}")
            
            import google.generativeai as genai
            from django.conf import settings
            import os
            from app1.models import Event, Booking
            
            # Use isolated history based on mode
            history_key = f'chug_history_{mode}'
            session_history = request.session.get(history_key, [])
            
            # Reconstruct history for Gemini
            history = []
            for msg in session_history:
                history.append({
                    "role": msg["role"],
                    "parts": [{"text": msg["parts"][0]["text"]}]
                })
            
            if mode == 'booking':
                system_instruction = f"""
                You are the Booking Specialist for EventIQ.
                Your primary goal is to help the user complete their ticket reservation.
                
                VISIBLE AUTOMATION:
                When you book an event, you will redirect the user to the booking tab. 
                They will see the form being automatically filled and confirmed for them.
                
                TOOLS:
                - Use 'book_event' ONLY when you have: Event ID, Name, Email, and Seats (1 or 2).
                - Use 'list_events' if the user isn't sure which event they want.
                
                STRICT RULES:
                1. You MUST ask for the number of seats (1 or 2).
                2. Once you call 'book_event', tell the user: "I'm taking you to the booking tab now. You'll see the form being filled and confirmed automatically for you!"
                3. If the user says "confirm" or "proceed", and you have the details, book it.
                
                USER CONTEXT:
                - Auth User: {request.user.username if request.user.is_authenticated else "Guest"}
                """
            else: # general mode
                system_instruction = f"""
                You are Chug, the general assistant for EventIQ.
                You help users explore events, understand platform features, and plan their budget.
                
                VISIBLE AUTOMATION:
                If you book an event, you will redirect the user to the booking tab. 
                They will see the form being automatically filled and confirmed for them.
                
                TOOLS:
                - Use 'list_events' to show upcoming events.
                - You CAN use 'book_event' if the user explicitly asks.
                
                RULES:
                1. Be helpful and informative about EventIQ.
                2. You MUST ask for the number of seats (1 or 2) before booking.
                3. Once you call 'book_event', tell the user: "I'm taking you to the booking tab now. You'll see the form being filled and confirmed automatically for you!"
                
                USER CONTEXT:
                - Auth User: {request.user.username if request.user.is_authenticated else "Guest"}
                """
            
            api_key = getattr(settings, 'GEMINI_API_KEY', '') or os.environ.get('GEMINI_API_KEY', '')
            if not api_key:
                return JsonResponse({'reply': "I'm not configured yet! Please set the GEMINI_API_KEY."})
            
            genai.configure(api_key=api_key)
            
            # Initialize model with tools
            model = genai.GenerativeModel(
                model_name='gemini-2.5-flash', 
                system_instruction=system_instruction,
                tools=[list_events, book_event]
            )
            
            # Use chat session for automatic tool execution with history
            chat = model.start_chat(history=history, enable_automatic_function_calling=True)
            response = chat.send_message(user_message)
            
            # Safe extraction of text parts to avoid "response.text" error
            bot_reply = "".join([p.text for p in response.candidates[0].content.parts if hasattr(p, 'text') and p.text]) or "I've initiated the action for you!"
            
            # Save updated history back to session (isolated by mode)
            updated_history = []
            for content in chat.history:
                text_parts = [p.text for p in content.parts if hasattr(p, 'text') and p.text]
                if text_parts:
                    updated_history.append({
                        "role": content.role,
                        "parts": [{"text": " ".join(text_parts)}]
                    })
            request.session[history_key] = updated_history
            
            # Look for redirect in tool output history (current turn)
            redirect_url = None
            for history_item in chat.history[-2:]:
                for part in history_item.parts:
                    if part.function_response:
                        resp_data = part.function_response.response
                        if resp_data and hasattr(resp_data, 'get'):
                            if resp_data.get('status') == 'success' and 'redirect_url' in resp_data:
                                redirect_url = resp_data['redirect_url']

            return JsonResponse({
                'reply': bot_reply,
                'redirect': redirect_url
            })
            
        except Exception as e:
             import traceback
             print(f"Chat API Error: {str(e)}")
             traceback.print_exc()
             return JsonResponse({'reply': f"Error: {str(e)}"}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)


def payment_page(request, booking_id):
    """Display payment page for a booking."""
    try:
        booking = Booking.objects.get(ticket_id=booking_id)
        
        # Check if already paid
        if booking.payment_status == 'completed':
            return redirect('booking_confirmation', booking_id=booking.ticket_id)
        
        return render(request, 'payment.html', {'booking': booking})
    except Booking.DoesNotExist:
        return HttpResponse("Booking not found", status=404)


def process_payment(request, booking_id):
    """Process simulated payment and update booking status."""
    if request.method == 'POST':
        try:
            booking = Booking.objects.get(ticket_id=booking_id)
            
            # Simulate payment processing
            card_number = request.POST.get('card_number', '').replace(' ', '')
            cardholder = request.POST.get('cardholder', '')
            
            # Simple validation - just check if card number has digits
            if len(card_number) >= 13:
                # Update booking status
                booking.payment_status = 'completed'
                booking.payment_method = f"Card ending in {card_number[-4:]}"
                booking.save()
                
                # Redirect to confirmation page
                return redirect('booking_confirmation', booking_id=booking.ticket_id)
            else:
                # Payment failed
                booking.payment_status = 'failed'
                booking.save()
                return HttpResponse("Payment failed. Please try again.", status=400)
                
        except Booking.DoesNotExist:
            return HttpResponse("Booking not found", status=404)
    
    return HttpResponse("Invalid request", status=400)