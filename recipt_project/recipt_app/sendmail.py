import smtplib
from email.mime.text import MIMEText

class EmailSupportAgent:
    def __init__(self, smtp_server, smtp_port, smtp_user, smtp_password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password

    def create_receipt_body(self, email_data):
        body = f"""
        -----------------------------------
        E-RECEIPT
        -----------------------------------
        
        Customer Details:
        -------------------
        Name: {email_data['customer_name']}
        Email: {email_data['customer_email']}
        
        Products Purchased:
        -------------------
        """
        
        for product in email_data['products']:
            name, quantity, price, quantity_price = product
            body += f"""
            - Product: {name}
            Quantity: {quantity}
            Price per Unit: ${price:.2f}
            Total: ${quantity_price:.2f}
            """
        
        body += f"""
        -------------------
        Total Price: ${email_data['total_price']:.2f}
        
        User Information:
        -------------------
        
        First Name: {email_data['first_name']}
        Last Name: {email_data['last_name']}
        Username: {email_data['username']}
        
        Date of Purchase: {email_data['now'].strftime('%B %d, %Y at %I:%M %p')}
        
        -----------------------------------
        Thank you for shopping with us!
        -----------------------------------
        """
        return body

    def send_email(self, subject, body, to_email):
        msg = MIMEText(body, _charset='utf-8')
        msg['Subject'] = subject
        msg['From'] = self.smtp_user
        msg['To'] = to_email

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            return "Success"
        except smtplib.SMTPAuthenticationError as e:
            return f"Authentication Error: {str(e)}"
        except smtplib.SMTPConnectError as e:
            return f"Connection Error: {str(e)}"
        except smtplib.SMTPDataError as e:
            return f"Data Error: {str(e)}"
        except smtplib.SMTPException as e:
            return f"SMTP Error: {str(e)}"
        except Exception as e:
            return f"Unexpected Error: {str(e)}"

    def handle_incoming_email(self, email_data):
        subject = f"{email_data['customer_name']}'s Purchase Receipt from BUGS at {email_data['now'].strftime('%B %d, %Y at %I:%M %p')}"
        body = self.create_receipt_body(email_data)
        return self.send_email(subject, body, email_data['customer_email'])

# Global initialization of support_agent
support_agent = EmailSupportAgent(
    'smtp.gmail.com', 587,
    'saqlainfawad@gmail.com', 'jtpqvszrodmcarlt'  # Replace with your actual app password
)

def viewsdata(email_data):
    return support_agent.handle_incoming_email(email_data)
