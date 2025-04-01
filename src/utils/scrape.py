from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import time

# Spuštění prohlížeče
driver = uc.Chrome()
# Otevření stránky přihlášení
driver.get("https://app.makeheadway.com/login")

try:
    # Počkáme na načtení stránky
    time.sleep(3)
    
    # Počkáme na pole pro e-mail a ověříme, že je viditelné
    email_input = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.NAME, "email"))
    )
    
    # Explicitní kliknutí a vyčištění
    email_input.click()
    email_input.clear()
    time.sleep(1)
    # Zadáme e-mail pomocí JavaScript
    driver.execute_script("arguments[0].value = 'hhh.honzula@gmail.com'", email_input)
    driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }))", email_input)
    driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }))", email_input)
    time.sleep(1)
    
    # Tab pro přechod na další pole (někdy pomáhá s validací)
    email_input.send_keys("\t")
    time.sleep(1)
    
    # Počkáme na pole pro heslo a ověříme, že je viditelné
    password_input = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.NAME, "password"))
    )
    
    # Explicitní kliknutí a vyčištění
    password_input.click()
    password_input.clear()
    time.sleep(1)
    
    # Zadáme heslo
    password_input.send_keys("password.")
    time.sleep(1)
    
    # Přidání posunu stránky a dalšího kliknutí pro aktivaci formuláře
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)
    
    # Kontrola stavu tlačítka
    login_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='submit']"))
    )
    
    # Ověření, zda je tlačítko aktivní
    is_enabled = driver.execute_script("return !arguments[0].disabled", login_button)
    if not is_enabled:
        print("⚠ Tlačítko přihlášení je neaktivní!")
        
        # Zkusíme aktivovat tlačítko pomocí JavaScriptu
        driver.execute_script("arguments[0].disabled = false", login_button)
        
        # Zkusíme kliknout pomocí JavaScriptu
        print("Pokus o kliknutí pomocí JavaScriptu...")
        driver.execute_script("arguments[0].click()", login_button)
    else:
        # Normální kliknutí
        login_button.click()
    
    # Delší čekání na přihlášení
    WebDriverWait(driver, 20).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    print("✅ Přihlášení bylo úspěšné nebo se o něj alespoň pokusilo.")
    
    # Zkontrolujeme, zda jsme skutečně přihlášeni
    time.sleep(5)
    current_url = driver.current_url
    print(f"Aktuální URL: {current_url}")
    
    # Pokud jsme stále na přihlašovací stránce, něco je špatně
    if "login" in current_url:
        print("⚠ Přihlášení selhalo, stále jsme na přihlašovací stránce.")
        
        # Získání možné chybové zprávy
        try:
            error_msg = driver.find_element(By.CSS_SELECTOR, "div.error-message")
            print(f"Chybová zpráva: {error_msg.text}")
        except:
            print("Žádná chybová zpráva nenalezena.")
    else:
        # Pokračování k cílové stránce
        driver.get("https://app.makeheadway.com/books/fluent-forever-how-to-learn-any-language-fast-and-never-forget-it/summary?mode=reading&page=1")
        
        element = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".MuiStack-root.mui-style-mhauuz"))
        )
        
        text = element.text
        print(text)
except Exception as e:
    print(f"⚠ Chyba: {e}")
finally:
    # Bezpečné zavření prohlížeče - přidaná pauza před ukončením
    try:
        time.sleep(3)
        driver.close()
        driver.quit()
    except Exception as e:
        print(f"⚠ Chyba při zavírání prohlížeče: {e}")