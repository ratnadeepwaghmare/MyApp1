import webbrowser
from urllib.parse import quote
import time
import os


class WhatsAppService:
    def __init__(self):
        self.whatsapp_delay = 10
        self.send_delay = 3

    def send_message(self, phone_number, message):
        try:
            # Format phone number
            cleaned_number = ''.join(filter(str.isdigit, phone_number))

            # Android version - open WhatsApp with pre-filled message
            url = f"https://api.whatsapp.com/send?phone={cleaned_number}&text={quote(message)}"
            webbrowser.open(url)

            return True
        except Exception as e:
            print(f"Error sending WhatsApp message: {e}")
            return False

    def send_payment_notification(self, user_data, payment_data):
        amount_paid = payment_data.get('amount_paid', 0)
        month = payment_data.get('month', 'Unknown')
        year = payment_data.get('year', 'Unknown')
        balance_amount = payment_data.get('balance_amount', 0)
        receipt_number = payment_data.get('receipt_number', 'Unknown')
        payment_date = payment_data.get('payment_date', 'Unknown')

        message = f"""💰 Payment Receipt 💰

Name: {user_data['name']}
Amount Paid: ₹{amount_paid}
Month: {month} {year}
Balance: ₹{balance_amount}
Receipt No: {receipt_number}
Date: {payment_date}

Sunil Raut,\nMittal Reading,\nThank you for your payment! 💪"""

        return self.send_message(user_data['mobile_number'], message)

    def send_defaulter_reminder(self, user_data, defaulter_data, message_type="reminder"):
        if message_type == "first_reminder":
            message = f"""🔔 Payment Reminder

Dear {user_data['name']},

Your payment for {defaulter_data['month']} {defaulter_data['year']} is due.
Amount: ₹{defaulter_data['balance_amount']}

Please make the payment at the earliest.

Sunil Raut,\nMittal Reading,\nThank you"""
        elif message_type == "second_reminder":
            message = f"""⚠️ Second Reminder

Dear {user_data['name']},

Your payment for {defaulter_data['month']} {defaulter_data['year']} is still pending.
Due Amount: ₹{defaulter_data['balance_amount']}

Please clear the dues to avoid inconvenience.

Sunil Raut,\nMittal Reading,\nThank you"""
        elif message_type == "third_reminder":
            message = f"""🚨 Urgent Reminder

Dear {user_data['name']},

Your payment for {defaulter_data['month']} {defaulter_data['year']} is overdue.
Due Amount: ₹{defaulter_data['balance_amount']}

Please make immediate payment.

Sunil Raut,\nMittal Reading,\nThank you"""
        else:
            message = f"""⏰ Final Reminder

Dear {user_data['name']},

Your payment for {defaulter_data['month']} {defaulter_data['year']} is critically overdue.
Due Amount: ₹{defaulter_data['balance_amount']}

Please clear the dues immediately to avoid service disruption.

Sunil Raut,\nMittal Reading,\nThank you"""

        return self.send_message(user_data['mobile_number'], message)