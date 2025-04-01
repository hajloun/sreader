from selenium.common import NoSuchElementException, TimeoutException # Import necessary exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import time
import traceback # Added for better error reporting

# --- Selectors (Using Option 2 as requested) ---
# If issues persist, double-check these selectors are correct *for all pages*
SUMMARY_CONTENT_SELECTOR = ".MuiStack-root.mui-style-mhauuz"
NEXT_PAGE_BUTTON_SELECTOR = 'button:has(svg path[d^="M16.6141 11L"])'# ------------------------------------------------

# --- Credentials ---
USER_EMAIL = "hhh.honzula@gmail.com" # Replace if needed
USER_PASSWORD = "pw."         # Replace if needed
# -----------------

# --- Target URL ---
BOOK_SUMMARY_START_URL = "https://app.makeheadway.com/books/the-willpower-instinct/summary?mode=reading"
# ------------------

driver = None # Initialize driver to None for finally block
try:
    # Spuštění prohlížeče
    print("Starting browser...")
    driver = uc.Chrome()
    driver.maximize_window() # Maximize window can sometimes help with element visibility
    print("Browser started.")

    # Otevření stránky přihlášení
    print("Navigating to login page...")
    driver.get("https://app.makeheadway.com/login")

    # --- Login Logic ---
    print("Attempting login...")
    # Increased initial wait slightly
    time.sleep(4)

    # Wait for email input
    print("Waiting for email input field...")
    email_input = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.NAME, "email"))
    )
    print("Email field found. Entering email.")
    email_input.click()
    email_input.clear()
    time.sleep(0.5)
    # Use JS for potentially more reliable input
    driver.execute_script(f"arguments[0].value = '{USER_EMAIL}'", email_input)
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
    # Send keys should be fine for password, but JS could be used if needed
    password_input.send_keys(USER_PASSWORD)
    time.sleep(0.5)

    # Wait for login button to be clickable
    print("Waiting for login button to be clickable...")
    login_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
    )
    print("Login button found and clickable.")

    # Check if button is *actually* enabled (sometimes clickable doesn't mean enabled)
    is_login_enabled = driver.execute_script("return !arguments[0].disabled", login_button)
    is_login_mui_disabled = driver.execute_script("return arguments[0].classList.contains('Mui-disabled')", login_button)
    print(f"Is login button enabled (attr)? {is_login_enabled}, Has Mui-disabled class? {is_login_mui_disabled}")

    if not is_login_enabled or is_login_mui_disabled:
        print("⚠ Login button is not enabled. Trying JS activation...")
        try:
            driver.execute_script("arguments[0].disabled = false;", login_button)
            driver.execute_script("arguments[0].classList.remove('Mui-disabled');", login_button) # Try removing class too
            time.sleep(0.5)
            print("Attempting JS click on login button...")
            driver.execute_script("arguments[0].click();", login_button)
        except Exception as js_click_err:
            print(f"⚠ JS click failed: {js_click_err}. Trying Selenium click again...")
            login_button.click() # Try normal click anyway
    else:
        print("Clicking login button...")
        login_button.click()

    # Wait for login process - check for URL change away from login page
    print("Waiting for page change after login attempt...")
    try:
        WebDriverWait(driver, 25).until( # Increased wait
            EC.url_changes("https://app.makeheadway.com/login")
        )
        print("✅ URL changed, likely logged in.")
    except TimeoutException:
        print("⚠ Warning: URL did not change from login page after timeout.")
        # Check current URL again
        current_url = driver.current_url
        print(f"Current URL is still: {current_url}")
        if "login" in current_url:
             # Attempt to grab error message if stuck on login
             try:
                 error_msg_element = WebDriverWait(driver, 3).until(
                     EC.visibility_of_element_located((By.CSS_SELECTOR, ".MuiFormHelperText-root.Mui-error")) # Common selector for MUI errors
                 )
                 print(f"⚠ Login Error Message Found: {error_msg_element.text}")
             except TimeoutException:
                 print("⚠ No specific error message found on login page.")
             raise Exception("Login failed: Stuck on login page.") # Stop the script
        else:
            print("URL did change eventually or was not login page to begin with. Proceeding cautiously.")

    time.sleep(3) # Extra pause for dashboard/redirects to settle
    current_url = driver.current_url
    print(f"Current URL after login sequence: {current_url}")

    if "login" in current_url:
        print("⚠ Login failed, still on login page after checks. Exiting.")
        # Exit or handle error appropriately
        raise Exception("Login failed verification.")
    else:
        print("✅ Successfully logged in or navigated away from login.")
        # --- Navigate to the START of the book summary ---
        print(f"Navigating to summary start: {BOOK_SUMMARY_START_URL}")
        driver.get(BOOK_SUMMARY_START_URL)
        time.sleep(2) # Pause for initial summary page load

        all_summary_text = []
        page_count = 1
        max_pages = 15 # Safety break to prevent infinite loops

        # --- Loop through pages ---
        while page_count <= max_pages:
            print(f"\n--- Attempting to scrape page {page_count} ---")
            try:
                # Wait for the main content area of the current page to be visible
                print(f"Waiting for content element ({SUMMARY_CONTENT_SELECTOR})...")
                # Increased wait time for content on potentially slower subsequent pages
                content_element = WebDriverWait(driver, 25).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, SUMMARY_CONTENT_SELECTOR))
                )
                print("Content element found.")

                # Get text and add to list
                page_text = content_element.text
                if not page_text:
                    print("⚠ Warning: Content element found but text is empty.")
                    # Optionally add a small retry wait here
                    time.sleep(2)
                    page_text = content_element.text
                    if not page_text:
                         print("⚠ Still no text after retry. Skipping page text.")

                all_summary_text.append(page_text)
                print(f"Content scraped (first 100 chars): {page_text[:100]}...")

                # --- Find and click the 'Next Page' button ---
                print(f"Looking for 'Next Page' button ({NEXT_PAGE_BUTTON_SELECTOR})...")
                try:
                    # INCREASED Wait for the next button to be clickable - try 25 seconds
                    print(f"Waiting up to 25 seconds for button to be clickable...")
                    next_button = WebDriverWait(driver, 25).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, NEXT_PAGE_BUTTON_SELECTOR))
                    )
                    print("Next button element found and deemed clickable by Selenium.")

                    # Explicitly check button state
                    is_button_enabled = driver.execute_script(
                        "return !arguments[0].hasAttribute('disabled') || arguments[0].getAttribute('disabled') === 'false'", 
                        next_button
                    )
                    is_mui_disabled = driver.execute_script(
                        "return arguments[0].classList.contains('Mui-disabled')", 
                        next_button
                    )
                    print(f"Is Next button enabled (attr)? {is_button_enabled}, Has Mui-disabled class? {is_mui_disabled}")

                    # Only break if we're sure the button is disabled
                    if not is_button_enabled or is_mui_disabled:
                        print("\n--------------------------------------------------------------------")
                        print("⚠ Next button found but appears disabled. Verifying if this is the last page...")
                        button_html = driver.execute_script("return arguments[0].outerHTML;", next_button)
                        print(f"Button HTML: {button_html}")
                        
                        # Additional check to verify we're really on the last page
                        try:
                            # Try to find any alternate navigation elements
                            alt_nav = driver.find_elements(By.CSS_SELECTOR, "[aria-label*='page']")
                            if alt_nav:
                                print("Found alternative navigation elements, attempting to continue...")
                                continue
                        except:
                            print("No alternative navigation found. This appears to be the last page.")
                            print("--------------------------------------------------------------------\n")
                            break

                    # If we get here, the button seems active
                    print("Attempting to click 'Next Page' button...")
                    time.sleep(1)  # Increased pause BEFORE click
                    driver.execute_script("arguments[0].click();", next_button)
                    print("JS Click executed.")
                    time.sleep(2)  # Increased pause AFTER click

                    page_count += 1
                    print(f"Advanced to page {page_count}. Current URL: {driver.current_url}")

                except TimeoutException:
                    # This is the expected way to finish if the button disappears OR REMAINS UNCLICKABLE
                    print("\n--------------------------------------------------------------------")
                    print("DEBUG: Timed out after waiting for button clickability.")
                    print(f"✅ 'Next Page' button ('{NEXT_PAGE_BUTTON_SELECTOR}') did not become clickable within timeout.")
                    print("Verifying if this is truly the last page...")
                    
                    # Final verification
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, NEXT_PAGE_BUTTON_SELECTOR)
                        if not elements:
                            print("Confirmed: No 'Next' button found. This is likely the last page.")
                        else:
                            print(f"Warning: Found {len(elements)} potential 'Next' buttons, but none were clickable.")
                    except:
                        print("Unable to perform final verification check.")
                    
                    print("--------------------------------------------------------------------\n")
                    break  # Exit the loop, we are likely on the last page

                except NoSuchElementException:
                    print("\n--------------------------------------------------------------------")
                    print("DEBUG: Button element not found in DOM.")
                    print(f"✅ 'Next Page' button selector did not find any element.")
                    print("This is likely the last page.")
                    print("--------------------------------------------------------------------\n")
                    break

            except TimeoutException:
                # (This block handles waiting for CONTENT at the start of the loop - keep it)
                print(f"⚠ Timed out waiting for page {page_count} content ({SUMMARY_CONTENT_SELECTOR}). Stopping scrape loop.")
                break # Exit loop if content takes too long
            except Exception as page_err:
                # (Keep this error handling)
                print(f"⚠ An unexpected error occurred while processing page {page_count}: {page_err}")
                traceback.print_exc() # Print full error details
                break # Stop if any other error occurs

        # Check if loop exited due to max_pages
        if page_count > max_pages:
            print(f"\n⚠ Warning: Reached maximum page limit ({max_pages}). Stopping.")


        # --- Combine and Print Results ---
        print("\n" + "="*30)
        print(f"Scraping complete. Total pages processed: {len(all_summary_text)}")
        print("="*30 + "\n")

        if all_summary_text:
            full_text = "\n\n--- PAGE BREAK ---\n\n".join(all_summary_text)
            print("--- Full Scraped Summary ---")
            print(full_text)
            print("--- End of Summary ---")
        else:
            print("⚠ No summary text was scraped.")


except Exception as e:
    print(f"\n⚠ An OVERALL error occurred during the process: {e}")
    traceback.print_exc() # Print detailed traceback for debugging

finally:
    # Bezpečné zavření prohlížeče
    print("\nScript finished or errored out. Closing browser...")
    try:
        if driver:
            time.sleep(5) # Keep browser open for a few seconds to see final state
            driver.close() # Closes the current window
            driver.quit() # Closes the browser instance and cleans up processes
            print("Browser closed successfully.")
        else:
            print("Driver was not initialized.")
    except Exception as e:
        print(f"⚠ Error closing browser: {e}")