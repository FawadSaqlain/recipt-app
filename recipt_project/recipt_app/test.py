from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def send_whatsapp_message(phone_number, message):
    # Set up Chrome WebDriver
    driver = webdriver.Chrome()  # Ensure ChromeDriver is in PATH
    driver.get(f'https://web.whatsapp.com/send?phone={phone_number}&text={message}')
    
    try:
        # Wait for the page to load and for the user to scan the QR code if not already logged in
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//div[@role="textbox"]')))
        
        # Wait until the send button is clickable and click it
        send_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]'))
        )
        send_button.click()

        print("Message sent successfully!")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the browser
        time.sleep(5)
        driver.quit()

# Test the function
while True:
    number = input('Enter number: ')
    message = input('Enter message: ')
    send_whatsapp_message(number, message)