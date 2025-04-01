from tkinter import ttk
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import time
import traceback

def scrape_headway_book(email, password, book_url):
    """Scrape a book from Headway using provided credentials"""
    # Constants
    SUMMARY_CONTENT_SELECTOR = ".MuiStack-root.mui-style-mhauuz"
    NEXT_PAGE_BUTTON_SELECTOR = "button[aria-label='Next page']"
    
    # Initialize variables for collecting text
    all_summary_text = []
    driver = None
    
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
        # Use JS for more reliable input
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

        # Navigate to book URL
        print("Navigating to book...")
        driver.get(book_url)
        time.sleep(3)  # Wait for book page to load
        
        # Initialize page counter
        page_count = 1

        # Loop through pages
        while True:
            print(f"Processing page {page_count}...")
            try:
                # Wait for content
                content_element = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, SUMMARY_CONTENT_SELECTOR))
                )
                
                # Get text from page
                page_text = content_element.text
                if page_text:
                    all_summary_text.append(page_text)
                    print(f"Added content from page {page_count}")

                # Look for next button with increased wait time
                print("Looking for next page button...")
                next_button = WebDriverWait(driver, 25).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, NEXT_PAGE_BUTTON_SELECTOR))
                )

                # Check if button is enabled
                is_button_enabled = driver.execute_script(
                    "return !arguments[0].hasAttribute('disabled')",
                    next_button
                )
                is_mui_disabled = driver.execute_script(
                    "return arguments[0].classList.contains('Mui-disabled')",
                    next_button
                )

                if not is_button_enabled or is_mui_disabled:
                    print("Next button is disabled. Reached last page.")
                    break

                # Click next button with delay
                time.sleep(1)
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(2)
                page_count += 1

            except TimeoutException:
                print("No more pages found.")
                break
            except Exception as e:
                print(f"Error processing page: {str(e)}")
                traceback.print_exc()
                break

        # Combine all text
        print("Finishing up...")
        if not all_summary_text:
            raise Exception("No content was scraped")
        return "\n\n".join(all_summary_text)

    except Exception as e:
        print(f"Error during scraping: {str(e)}")
        traceback.print_exc()
        raise Exception(f"Failed to scrape book: {str(e)}")

    finally:
        if driver:
            try:
                driver.quit()
                print("Browser closed successfully.")
            except Exception as e:
                print(f"Error closing browser: {str(e)}")

class SpeedReaderApp:

    def update_display(self, word):
        self.display_label.config(text=word)
        self.root.update()

    def start_reading(self):
        text = self.text_input.get("1.0", tk.END)
        self.text_processor.set_text(text)
        try:
            speed_wpm = int(self.speed_var.get())
            speed_ms = int(60000 / speed_wpm)
            self.speed_controller.set_speed(speed_ms)
            self.speed_controller.start_reading()
            self.start_button['state'] = 'disabled'
            self.pause_button['state'] = 'normal'
        except ValueError:
            self.display_label.config(text="Please enter a valid speed")

    def pause_reading(self):
        self.speed_controller.stop_reading()
        self.start_button['state'] = 'normal'
        self.pause_button['state'] = 'disabled'
        self.paused = True

    def toggle_text(self):
        if hasattr(self.text_container, '_is_hidden') and not self.text_container._is_hidden:
            self.text_container.pack_forget()
            self.text_container._is_hidden = True
        else:
            self.text_container.pack(after=self.title_label)
            self.text_container._is_hidden = False

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def show_headway_inputs(self):
        if not hasattr(self, 'headway_frame'):
            # Create headway input frame
            self.headway_frame = ttk.Frame(self.root)
            
            # Email input
            ttk.Label(self.headway_frame, text="Email:").pack(pady=5)
            self.email_var = tk.StringVar()
            ttk.Entry(self.headway_frame, textvariable=self.email_var, width=40).pack()
            
            # Password input
            ttk.Label(self.headway_frame, text="Password:").pack(pady=5)
            self.password_var = tk.StringVar()
            password_entry = ttk.Entry(self.headway_frame, textvariable=self.password_var, show="*", width=40)
            password_entry.pack()
            
            # Book URL input
            ttk.Label(self.headway_frame, text="Book URL:").pack(pady=5)
            self.book_url_var = tk.StringVar()
            ttk.Entry(self.headway_frame, textvariable=self.book_url_var, width=40).pack()
            
            # Send button
            ttk.Button(self.headway_frame, text="Send",
                       command=self.scrape_and_load_book,
                       style='Controls.TButton').pack(pady=20)
        
        if hasattr(self.headway_frame, '_is_hidden') and not self.headway_frame._is_hidden:
            self.headway_frame.pack_forget()
            self.headway_frame._is_hidden = True
        else:
            self.headway_frame.pack(after=self.title_label, pady=20)
            self.headway_frame._is_hidden = False

    def scrape_and_load_book(self):
        self.display_label.config(text="Scraping book... Please wait...")
        
        # Disable inputs while scraping
        for child in self.headway_frame.winfo_children():
            if isinstance(child, ttk.Entry) or isinstance(child, ttk.Button):
                child['state'] = 'disabled'
        
        # Show loading message
        self.display_label.config(text="Scraping book...")
        
        # Start scraping in a separate thread
        def scrape_thread():
            try:
                # Get the scraped text
                scraped_text = scrape_headway_book(
                    self.email_var.get(),
                    self.password_var.get(),
                    self.book_url_var.get()
                )
                
                # Update the text input with scraped content
                self.text_input.delete('1.0', tk.END)
                self.text_input.insert('1.0', scraped_text)
                
                # Hide the headway frame
                self.headway_frame.pack_forget()
                self.headway_frame._is_hidden = True
                
                # Show success message
                self.display_label.config(text="Book loaded successfully!")
            
            except Exception as e:
                self.display_label.config(text=f"Error: {str(e)}")
            
            finally:
                # Re-enable inputs
                for child in self.headway_frame.winfo_children():
                    if isinstance(child, ttk.Entry) or isinstance(child, ttk.Button):
                        child['state'] = 'normal'
        
        threading.Thread(target=scrape_thread, daemon=True).start()

def main():
    root = tk.Tk()
    app = SpeedReaderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()