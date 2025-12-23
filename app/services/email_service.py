from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from jinja2 import Environment, FileSystemLoader
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Optional

# Config từ environment variables
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "noreply@yourapp.com")
SENDER_NAME = os.getenv("SENDER_NAME", "Resort Booking")

executor = ThreadPoolExecutor(max_workers=3)


def _send_email_sync(to_email: str, subject: str, html_content: str):
    """Gửi email đồng bộ qua SendGrid (chạy trong thread pool)"""
    print(f"[EMAIL] Sending email to: {to_email}, subject: {subject}")
    
    message = Mail(
        from_email=Email(SENDER_EMAIL, SENDER_NAME),
        to_emails=To(to_email),
        subject=subject,
        html_content=Content("text/html", html_content)
    )
    
    sg = SendGridAPIClient(SENDGRID_API_KEY)
    response = sg.send(message)
    
    print(f"[EMAIL] SendGrid response: {response.status_code}")
    
    if response.status_code not in [200, 201, 202]:
        raise Exception(f"SendGrid error: {response.status_code} - {response.body}")
    
    return response


async def send_email(to_email: str, subject: str, html_content: str):
    """Gửi email bất đồng bộ qua SendGrid"""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        executor, 
        _send_email_sync, 
        to_email, subject, html_content
    )


async def send_booking_confirmation_email(
    customer_email: str,
    customer_name: str,
    customer_phone: Optional[str],
    booking_id: int,
    booking_details: list,
    invoices: list,
    total_cost: float,
    payment_method: str = "ZALOPAY",
    payment_time: Optional[datetime] = None
):
    """
    Gửi email xác nhận đặt phòng thành công kèm hóa đơn
    """
    template_dir = os.path.join(os.path.dirname(__file__), "..", "templates", "emails")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("booking_invoice.html")
    
    # Chuẩn bị data chi tiết đặt phòng
    details_data = []
    for detail in booking_details:
        nights = (detail.finished_at - detail.started_at).days
        if nights < 1:
            nights = 1
        
        details_data.append({
            "resort_name": detail.offer.room_type.resort.name,
            "resort_address": detail.offer.room_type.resort.address or "",
            "room_type": detail.offer.room_type.name,
            "number_of_rooms": detail.number_of_rooms,
            "nights": nights,
            "check_in": detail.started_at.strftime("%d/%m/%Y %H:%M"),
            "check_out": detail.finished_at.strftime("%d/%m/%Y %H:%M"),
            "unit_price": float(detail.offer.cost or 0),
            "cost": float(detail.cost or 0)
        })
    
    # Chuẩn bị data hóa đơn
    invoices_data = []
    for inv in invoices:
        invoices_data.append({
            "invoice_id": inv.id,
            "cost": float(inv.cost or 0),
            "payment_method": inv.payment_method,
            "finished_time": inv.finished_time.strftime("%d/%m/%Y %H:%M") if inv.finished_time else ""
        })
    
    html_content = template.render(
        customer_name=customer_name or "Quý khách",
        customer_email=customer_email,
        customer_phone=customer_phone or "",
        booking_id=booking_id,
        booking_details=details_data,
        invoices=invoices_data,
        total_cost=total_cost,
        payment_method=payment_method,
        payment_time=payment_time.strftime("%d/%m/%Y %H:%M") if payment_time else datetime.now().strftime("%d/%m/%Y %H:%M"),
        current_year=datetime.now().year
    )
    
    await send_email(
        to_email=customer_email,
        subject=f"[Hóa đơn] Xác nhận đặt phòng #{booking_id} thành công",
        html_content=html_content
    )
