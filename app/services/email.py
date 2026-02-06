"""
Email service for sending notifications about inquiries and contacts.
"""
from flask import current_app
from flask_mail import Message
from app import mail


def send_inquiry_email(inquiry):
    """
    Send email notification for a new room booking inquiry.
    
    Args:
        inquiry: Inquiry object
    """
    # Email to business owner
    subject = f"New Booking Inquiry - {inquiry.name}"
    
    room_info = ""
    if inquiry.room:
        room_info = f"""
Room Details:
- Room: {inquiry.room.name}
- Type: {inquiry.room.type}
- Price: KSh {inquiry.room.price_per_night:,}/night
"""
    
    dates_info = ""
    if inquiry.check_in and inquiry.check_out:
        dates_info = f"""
Dates:
- Check-in: {inquiry.check_in.strftime('%B %d, %Y')}
- Check-out: {inquiry.check_out.strftime('%B %d, %Y')}
- Guests: {inquiry.guests or 'Not specified'}
"""
    
    body = f"""
You have received a new booking inquiry from WIMA Serenity Gardens website.

Guest Information:
- Name: {inquiry.name}
- Email: {inquiry.email}
- Phone: {inquiry.phone}
- Inquiry Type: {inquiry.inquiry_type}
{room_info}{dates_info}
Message:
{inquiry.message}

---
This is an automated message from WIMA Serenity Gardens booking system.
Reply directly to this email to respond to the guest.
"""
    
    msg = Message(
        subject=subject,
        recipients=[current_app.config['BUSINESS_EMAIL']],
        reply_to=inquiry.email,
        body=body
    )
    
    mail.send(msg)
    
    # Confirmation email to guest
    guest_subject = "Thank you for your inquiry - WIMA Serenity Gardens"
    guest_body = f"""
Dear {inquiry.name},

Thank you for your interest in WIMA Serenity Gardens!

We have received your inquiry and will get back to you within 24 hours.

Your Inquiry Details:
- Inquiry Type: {inquiry.inquiry_type}
{room_info if room_info else ""}
{dates_info if dates_info else ""}
In the meantime, if you have any urgent questions, feel free to reach us at:
- Phone: {current_app.config['BUSINESS_PHONE']}
- WhatsApp: {current_app.config['BUSINESS_WHATSAPP']}
- Email: {current_app.config['BUSINESS_EMAIL']}

We look forward to hosting you!

Warm regards,
The WIMA Serenity Gardens Team

---
WIMA Serenity Gardens
Guest House | Leisure Gardens | Event Venue
Kericho, Kenya
"""
    
    guest_msg = Message(
        subject=guest_subject,
        recipients=[inquiry.email],
        body=guest_body
    )
    
    mail.send(guest_msg)


def send_event_inquiry_email(event_inquiry):
    """
    Send email notification for a new event venue inquiry.
    
    Args:
        event_inquiry: EventInquiry object
    """
    # Email to business owner
    subject = f"New Event Inquiry - {event_inquiry.event_type.title()}"
    
    venue_info = ""
    if event_inquiry.venue_preference:
        venue_info = f"- Venue Preference: {event_inquiry.venue_preference}\n"
    
    body = f"""
You have received a new event venue inquiry from WIMA Serenity Gardens website.

Client Information:
- Name: {event_inquiry.name}
- Email: {event_inquiry.email}
- Phone: {event_inquiry.phone}

Event Details:
- Event Type: {event_inquiry.event_type}
- Event Date: {event_inquiry.event_date.strftime('%B %d, %Y')}
- Expected Guests: {event_inquiry.guest_count}
{venue_info}
Message:
{event_inquiry.message}

---
This is an automated message from WIMA Serenity Gardens booking system.
Reply directly to this email to respond to the client.
"""
    
    msg = Message(
        subject=subject,
        recipients=[current_app.config['BUSINESS_EMAIL']],
        reply_to=event_inquiry.email,
        body=body
    )
    
    mail.send(msg)
    
    # Confirmation email to client
    client_subject = "Thank you for your event inquiry - WIMA Serenity Gardens"
    client_body = f"""
Dear {event_inquiry.name},

Thank you for considering WIMA Serenity Gardens for your {event_inquiry.event_type}!

We have received your event inquiry and will get back to you within 24 hours to discuss:
- Venue availability for {event_inquiry.event_date.strftime('%B %d, %Y')}
- Event setup options
- Catering arrangements
- Pricing and packages

Your Event Details:
- Event Type: {event_inquiry.event_type}
- Date: {event_inquiry.event_date.strftime('%B %d, %Y')}
- Guest Count: {event_inquiry.guest_count}

For immediate assistance, please contact us at:
- Phone: {current_app.config['BUSINESS_PHONE']}
- WhatsApp: {current_app.config['BUSINESS_WHATSAPP']}
- Email: {current_app.config['BUSINESS_EMAIL']}

We look forward to making your event memorable!

Warm regards,
The WIMA Serenity Gardens Team

---
WIMA Serenity Gardens
Guest House | Leisure Gardens | Event Venue
Kericho, Kenya
"""
    
    client_msg = Message(
        subject=client_subject,
        recipients=[event_inquiry.email],
        body=client_body
    )
    
    mail.send(client_msg)


def send_contact_email(name, email, phone, subject, message):
    """
    Send email notification for a general contact form submission.
    
    Args:
        name: Contact's name
        email: Contact's email
        phone: Contact's phone
        subject: Contact subject
        message: Contact message
    """
    # Email to business owner
    email_subject = f"New Contact Form Message - {subject}"
    
    body = f"""
You have received a new message from the WIMA Serenity Gardens contact form.

Contact Information:
- Name: {name}
- Email: {email}
- Phone: {phone}
- Subject: {subject}

Message:
{message}

---
This is an automated message from WIMA Serenity Gardens website.
Reply directly to this email to respond to the sender.
"""
    
    msg = Message(
        subject=email_subject,
        recipients=[current_app.config['BUSINESS_EMAIL']],
        reply_to=email,
        body=body
    )
    
    mail.send(msg)
    
    # Confirmation email to sender
    confirmation_subject = "Thank you for contacting WIMA Serenity Gardens"
    confirmation_body = f"""
Dear {name},

Thank you for reaching out to WIMA Serenity Gardens!

We have received your message and will respond shortly

Your Message:
{message}

If you need immediate assistance, please contact us at:
- Phone: {current_app.config['BUSINESS_PHONE']}
- WhatsApp: {current_app.config['BUSINESS_WHATSAPP']}
- Email: {current_app.config['BUSINESS_EMAIL']}

Warm regards,
The WIMA Serenity Gardens Team

---
WIMA Serenity Gardens
Guest House | Leisure Gardens | Event Venue
Kericho, Kenya
"""
    
    confirmation_msg = Message(
        subject=confirmation_subject,
        recipients=[email],
        body=confirmation_body
    )
    
    mail.send(confirmation_msg)