import tkinter as tk
from tkinter import ttk
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import time
import traceback
import threading

def scrape_headway_book(email, password, book_url):
    """Scrape a book from Headway using provided credentials"""
    # Constants
    SUMMARY_CONTENT_SELECTOR = ".MuiStack-root.mui-style-mhauuz"
    NEXT_PAGE_BUTTON_SELECTOR = """
        button.MuiButtonBase-root.MuiButton-root:has(svg path[d^="M16.6141 11"]),
        button[class*="MuiButton-root"]:has(svg path[d^="M16.6141"])
    """
    
    # Initialize variables for collecting text
    all_summary_text = []
    driver = None
    page_count = 1
    
    try:
        # Configure Chrome options for headless mode
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')

        # Initialize Chrome with headless options
        print("Starting Chrome in headless mode...")
        driver = uc.Chrome(options=chrome_options)
        driver.maximize_window()

        # Navigate to login page
        print("Navigating to login page...")
        driver.get("https://app.makeheadway.com/login")
        time.sleep(4)  # Increased initial wait

        # Wait for and fill email
        print("Waiting for email input field...")
        email_input = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.NAME, "email"))
        )
        print("Email field found. Entering email.")
        email_input.click()
        email_input.clear()
        time.sleep(0.5)
        driver.execute_script(f"arguments[0].value = '{email}'", email_input)
        driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }))", email_input)
        driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }))", email_input)
        time.sleep(0.5)

        # Wait for password input
        print("Waiting for password input field...")
        password_input = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.NAME, "password"))
        )
        print("Password field found. Entering password.")
        password_input.click()
        password_input.clear()
        time.sleep(0.5)
        password_input.send_keys(password)
        time.sleep(0.5)

        # Wait for login button
        print("Waiting for login button...")
        login_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        print("Login button found and clickable.")

        # Check if button is enabled
        is_login_enabled = driver.execute_script("return !arguments[0].disabled", login_button)
        is_login_mui_disabled = driver.execute_script("return arguments[0].classList.contains('Mui-disabled')", login_button)
        print(f"Is login button enabled? {is_login_enabled}, Has Mui-disabled class? {is_login_mui_disabled}")

        if not is_login_enabled or is_login_mui_disabled:
            print("Login button not enabled. Trying JS click...")
            driver.execute_script("arguments[0].click();", login_button)
        else:
            print("Clicking login button...")
            login_button.click()

        # Wait for login completion
        print("Waiting for login completion...")
        WebDriverWait(driver, 25).until(
            EC.url_changes("https://app.makeheadway.com/login")
        )
        time.sleep(3)  # Wait for any redirects

        # Navigate to book URL with retry mechanism
        print("Loading book...")
        max_retries = 3
        for attempt in range(max_retries):
            try:
                driver.get(book_url)
                time.sleep(5)  # Increased wait time for book loading
                
                # Verify we're on the correct page
                current_url = driver.current_url
                if "/summary" not in current_url:
                    print(f"Unexpected URL: {current_url}, retrying...")
                    continue
                
                # Wait for initial content
                content = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, SUMMARY_CONTENT_SELECTOR))
                )
                if content.is_displayed() and content.text.strip():
                    print("Book content loaded successfully")
                    break
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise Exception("Failed to load book content")
                time.sleep(2)

        # Scraping loop with improved navigation
        while True:
            print(f"Processing page {page_count}...")
            try:
                # Try multiple selectors for content
                content_found = False
                for selector in [SUMMARY_CONTENT_SELECTOR, 
                               ".MuiStack-root", 
                               "div[class*='book-content']"]:
                    try:
                        content_element = WebDriverWait(driver, 15).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        if content_element.is_displayed():
                            page_text = content_element.text.strip()
                            if page_text:
                                all_summary_text.append(page_text)
                                print(f"Content found on page {page_count}")
                                content_found = True
                                break
                    except:
                        continue

                if not content_found:
                    raise Exception("No content found on current page")

                # Look for next button with improved detection
                next_buttons = driver.find_elements(By.CSS_SELECTOR, NEXT_PAGE_BUTTON_SELECTOR)
                next_button = None
                
                for btn in next_buttons:
                    if btn.is_displayed():
                        is_disabled = driver.execute_script("""
                            return arguments[0].disabled || 
                                   arguments[0].classList.contains('Mui-disabled') ||
                                   !arguments[0].offsetParent;
                        """, btn)
                        if not is_disabled:
                            next_button = btn
                            break

                if not next_button:
                    print("No active next button found - reached last page")
                    break

                # Click next button with verification
                print("Moving to next page...")
                current_url = driver.current_url
                
                try:
                    driver.execute_script("arguments[0].click();", next_button)
                    # Wait for URL or content change
                    WebDriverWait(driver, 10).until(lambda d: (
                        d.current_url != current_url or
                        d.find_element(By.CSS_SELECTOR, SUMMARY_CONTENT_SELECTOR).text != page_text
                    ))
                    time.sleep(2)  # Additional wait for content load
                    page_count += 1
                except:
                    print("Page transition failed - reached last page")
                    break

            except Exception as e:
                print(f"Error on page {page_count}: {str(e)}")
                if page_count == 1:
                    raise
                break

        if not all_summary_text:
            raise Exception("No content was scraped")

        print(f"Successfully scraped {page_count} pages")
        return "\n\n".join(all_summary_text)  # Simplified join without page break markers

    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()
        raise

    finally:
        if driver:
            driver.quit()