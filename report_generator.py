from fpdf import FPDF
import os
from datetime import datetime


class ReportGenerator:
    def __init__(self):
        pass

    def generate_user_report(self, user_data, include_image=False):
        pdf = FPDF()
        pdf.add_page()

        # Title
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'User Information Report', 0, 1, 'C')
        pdf.ln(10)

        # User details - Use 'Rs' instead of rupee symbol to avoid encoding issues
        pdf.set_font('Arial', '', 12)
        details = [
            f"User ID: {user_data['user_id']}",
            f"Name: {user_data['name']}",
            f"Aadhar: {user_data['aadhar_number']}",
            f"Mobile: {user_data['mobile_number']}",
            f"Gender: {user_data['gender']}",
            f"Joining Date: {user_data['joining_date']}",
            f"Address: {user_data['address']}",
            f"Seat Number: {user_data['seat_number']}",
            f"Monthly Fees: Rs{user_data['monthly_fees']}",  # Changed from ₹ to Rs
            f"Status: {user_data['status']}"
        ]

        for detail in details:
            pdf.cell(0, 10, detail, 0, 1)

        if include_image and user_data.get('image_path') and os.path.exists(user_data['image_path']):
            try:
                pdf.ln(10)
                pdf.cell(0, 10, 'Profile Image:', 0, 1)
                # Note: Image support in FPDF is limited, this is a placeholder
                pdf.cell(0, 10, f"Image: {user_data['image_path']}", 0, 1)
            except:
                pdf.cell(0, 10, 'Image not available', 0, 1)

        filename = f"user_report_{user_data['user_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf.output(filename)
        return filename

    def generate_all_users_report(self, users_data):
        pdf = FPDF()
        pdf.add_page()

        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'All Users Report', 0, 1, 'C')
        pdf.ln(10)

        pdf.set_font('Arial', 'B', 10)
        headers = ['ID', 'Name', 'Mobile', 'Fees', 'Status', 'Seat', 'Join Date']

        col_widths = [15, 40, 25, 15, 15, 15, 25]
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 10, header, 1, 0, 'C')
        pdf.ln()

        pdf.set_font('Arial', '', 8)
        for user in users_data:
            pdf.cell(col_widths[0], 10, str(user['user_id']), 1, 0, 'C')
            pdf.cell(col_widths[1], 10, user['name'][:20], 1, 0, 'L')
            pdf.cell(col_widths[2], 10, user['mobile_number'], 1, 0, 'C')
            pdf.cell(col_widths[3], 10, str(user['monthly_fees']), 1, 0, 'C')  # No symbol to avoid encoding issues
            pdf.cell(col_widths[4], 10, user['status'], 1, 0, 'C')
            pdf.cell(col_widths[5], 10, str(user.get('seat_number', '')), 1, 0, 'C')
            pdf.cell(col_widths[6], 10, user['joining_date'], 1, 0, 'C')
            pdf.ln()

        filename = f"all_users_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf.output(filename)
        return filename

    def generate_payments_report(self, payments_data):
        pdf = FPDF()
        pdf.add_page()

        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'All Payments Report', 0, 1, 'C')
        pdf.ln(10)

        pdf.set_font('Arial', 'B', 8)
        headers = ['Date', 'User', 'Month', 'Year', 'Amount', 'Balance', 'Receipt']

        col_widths = [25, 40, 15, 15, 20, 20, 35]
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 10, header, 1, 0, 'C')
        pdf.ln()

        pdf.set_font('Arial', '', 7)
        for payment in payments_data:
            pdf.cell(col_widths[0], 10, payment['payment_date'], 1, 0, 'C')
            pdf.cell(col_widths[1], 10, payment.get('user_name', '')[:25], 1, 0, 'L')
            pdf.cell(col_widths[2], 10, payment['month'], 1, 0, 'C')
            pdf.cell(col_widths[3], 10, str(payment['year']), 1, 0, 'C')
            pdf.cell(col_widths[4], 10, f"Rs{payment['amount_paid']}", 1, 0, 'C')  # Changed from ₹ to Rs
            pdf.cell(col_widths[5], 10, f"Rs{payment['balance_amount']}", 1, 0, 'C')  # Changed from ₹ to Rs
            pdf.cell(col_widths[6], 10, payment['receipt_number'], 1, 0, 'C')
            pdf.ln()

        filename = f"payments_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf.output(filename)
        return filename

    def generate_user_payments_report(self, user_data, payments_data):
        pdf = FPDF()
        pdf.add_page()

        # User header
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, f"Payment Report - {user_data['name']}", 0, 1, 'C')
        pdf.ln(5)

        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f"User ID: {user_data['user_id']} | Mobile: {user_data['mobile_number']}", 0, 1)
        pdf.cell(0, 10, f"Monthly Fees: Rs{user_data['monthly_fees']} | Status: {user_data['status']}", 0,
                 1)  # Changed from ₹ to Rs
        pdf.ln(10)

        # Payments table
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Payment History', 0, 1)
        pdf.ln(5)

        if not payments_data:
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 10, 'No payment records found', 0, 1)
        else:
            pdf.set_font('Arial', 'B', 8)
            headers = ['Date', 'Month', 'Year', 'Amount Paid', 'Balance', 'Receipt']

            col_widths = [25, 20, 15, 25, 25, 40]
            for i, header in enumerate(headers):
                pdf.cell(col_widths[i], 10, header, 1, 0, 'C')
            pdf.ln()

            pdf.set_font('Arial', '', 7)
            total_paid = 0
            for payment in payments_data:
                pdf.cell(col_widths[0], 10, payment['payment_date'], 1, 0, 'C')
                pdf.cell(col_widths[1], 10, payment['month'], 1, 0, 'C')
                pdf.cell(col_widths[2], 10, str(payment['year']), 1, 0, 'C')
                pdf.cell(col_widths[3], 10, f"Rs{payment['amount_paid']}", 1, 0, 'C')  # Changed from ₹ to Rs
                pdf.cell(col_widths[4], 10, f"Rs{payment['balance_amount']}", 1, 0, 'C')  # Changed from ₹ to Rs
                pdf.cell(col_widths[5], 10, payment['receipt_number'], 1, 0, 'C')
                pdf.ln()
                total_paid += payment['amount_paid']

            pdf.ln(5)
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, 10, f'Total Amount Paid: Rs{total_paid}', 0, 1)  # Changed from ₹ to Rs

        filename = f"user_payments_{user_data['user_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf.output(filename)
        return filename