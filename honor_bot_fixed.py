import os
import shutil
import time
import requests
import re
import random
import string
import threading
import sys

try:
    import pyautogui
except Exception:
    pyautogui = None

from selenium.webdriver import Chrome, Firefox
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException

# Ensure current directory is in python path for local packages
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from captcha_solver.capguru_client import CapGuruClient
except ImportError:
    CapGuruClient = None

file_lock = threading.Lock()
CAPGURU_API_KEY = "74dac63ef7ec8244f293b59814abd958"

def get_and_cut_number():
    file_path = r"C:\Users\Rakib\Desktop\Honor\All_numbers.txt"
    with file_lock:
        if not os.path.exists(file_path):
            print(f"Error: {file_path} file ti pawa jayni!")
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if not lines:
            return None
        number = lines[0].strip()
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines[1:])
        return number

def generate_temp_email():
    print("API theke Secure 'mail.tm' Email banano hocche...")
    for attempt in range(3):
        try:
            domains_resp = requests.get("https://api.mail.tm/domains", timeout=10)
            domain = domains_resp.json()['hydra:member'][0]['domain']
            name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
            address = f"{name}@{domain}"
            temp_pass = "Password123!"
            requests.post("https://api.mail.tm/accounts", json={"address": address, "password": temp_pass}, timeout=10)
            token_resp = requests.post("https://api.mail.tm/token", json={"address": address, "password": temp_pass}, timeout=10)
            token = token_resp.json()['token']
            return address, token
        except Exception as e:
            time.sleep(2)
    return None, None

def generate_random_password():
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    digits = string.digits
    symbols = "!@#$%"
    password_chars = (
        random.choices(lower, k=4) +
        random.choices(upper, k=3) +
        random.choices(digits, k=3) +
        random.choices(symbols, k=2)
    )
    random.shuffle(password_chars)
    return "".join(password_chars)

def save_email_to_file(email, password, phone="N/A"):
    file_path = r"C:\Users\Rakib\Desktop\Honor\generated_emails.txt"
    with file_lock:
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"Email: {email} | Password: {password} | Phone: {phone}\n")

def get_unique_target_url():
    base_url = "https://hnid-dra.cloud.honor.com/CAS/portal/userRegister/regbyemail.html?reqClientType=27&loginChannel=27000000&countryCode=my&loginUrl=https%3A%2F%2Fhnid-dra.cloud.honor.com%2FCAS%2Fportal%2FloginAuth.html&lang=en-gb&themeName=blue&clientID=100381747"
    rand_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{base_url}&rd={rand_suffix}"

def wait_for_verification_code(token, email, timeout=120):
    start_time = time.time()
    headers = {"Authorization": f"Bearer {token}"}
    while time.time() - start_time < timeout:
        try:
            msg_resp = requests.get("https://api.mail.tm/messages", headers=headers, timeout=10)
            if msg_resp.status_code == 200:
                messages = msg_resp.json().get('hydra:member', [])
                if messages:
                    msg_id = messages[0]['id']
                    body_resp = requests.get(f"https://api.mail.tm/messages/{msg_id}", headers=headers, timeout=10)
                    body_data = body_resp.json()
                    text_body = body_data.get('text', '')
                    html_body = body_data.get('html', '')
                    match = re.search(r'\b\d{6}\b', text_body) or re.search(r'\b\d{6}\b', html_body)
                    if match:
                        return match.group(0), msg_id
        except Exception:
            pass
        time.sleep(4) 
    return None, None

def wait_for_new_verification_code(token, timeout=120, ignore_ids=None):
    if ignore_ids is None:
        ignore_ids = set()
    start_time = time.time()
    headers = {"Authorization": f"Bearer {token}"}
    while time.time() - start_time < timeout:
        try:
            msg_resp = requests.get("https://api.mail.tm/messages", headers=headers, timeout=10)
            if msg_resp.status_code == 200:
                messages = msg_resp.json().get('hydra:member', [])
                try:
                    messages = sorted(messages, key=lambda x: x.get('createdAt', ''), reverse=True)
                except:
                    pass
                for msg in messages:
                    msg_id = msg['id']
                    if msg_id not in ignore_ids:
                        body_resp = requests.get(f"https://api.mail.tm/messages/{msg_id}", headers=headers, timeout=10)
                        if body_resp.status_code == 200:
                            body_data = body_resp.json()
                            text_body = body_data.get('text', '') or ''
                            html_body = body_data.get('html', '') or ''
                            match = re.search(r'\b\d{6}\b', text_body) or re.search(r'\b\d{6}\b', html_body)
                            if match:
                                return match.group(0), msg_id
        except Exception:
            pass
        time.sleep(3) 
    return None, None

def delete_old_profiles():
    print("\n--- Purono Profile Folder Delete Kora Hocche ---")
    for browser_dir in ["C:\\Chrome", "C:\\Firefox"]:
        if os.path.exists(browser_dir):
            for folder_name in os.listdir(browser_dir):
                if folder_name.startswith("profile-"):
                    folder_path = os.path.join(browser_dir, folder_name)
                    try: 
                        shutil.rmtree(folder_path)
                    except Exception: 
                        pass
    print("Folder cleanup complete!\n")

def human_delay(min_sec=1.2, max_sec=2.5):
    time.sleep(random.uniform(min_sec, max_sec))


def solve_slider_captcha_v2(driver, instance_id, browser_name):
    """🔧 FIXED - Image slider captcha solver"""
    print(f"{browser_name} #{instance_id}: 🎯 Image slider captcha solve kora jacche...")
    
    try:
        driver.switch_to.default_content()
        time.sleep(0.5)
        
        # Step 1: Slider button খুঁজুন
        slider_buttons_xpath = [
            "//button[@class='geetest_slider_button']",
            "//button[contains(@class, 'slider')]",
            "//div[contains(@class, 'slide-btn')]",
            "//div[@class='geetest_slider_button']",
            "//button[@class='slide-button']",
            "//div[contains(text(), 'Slide')]//ancestor::*//button",
            "//span[contains(text(), 'Slide')]//ancestor::button",
            "//button",
        ]
        
        handle = None
        found_selector = None
        
        for xpath in slider_buttons_xpath:
            try:
                elements = driver.find_elements(By.XPATH, xpath)
                for el in elements:
                    try:
                        if el.is_displayed() and el.size['width'] > 20:
                            handle = el
                            found_selector = xpath
                            print(f"{browser_name} #{instance_id}: ✅ Slider button found!")
                            break
                    except:
                        pass
                if handle:
                    break
            except:
                pass
        
        # iframe এ থাকলে
        if not handle:
            print(f"{browser_name} #{instance_id}: iframe te khujchi...")
            try:
                iframes = driver.find_elements(By.TAG_NAME, "iframe")
                print(f"{browser_name} #{instance_id}: {len(iframes)} iframe found")
                
                for idx, frame in enumerate(iframes):
                    try:
                        driver.switch_to.frame(frame)
                        print(f"{browser_name} #{instance_id}: iframe #{idx} te switch kora holo")
                        time.sleep(0.5)
                        
                        for xpath in slider_buttons_xpath:
                            try:
                                elements = driver.find_elements(By.XPATH, xpath)
                                for el in elements:
                                    try:
                                        if el.is_displayed() and el.size['width'] > 20:
                                            handle = el
                                            found_selector = xpath
                                            print(f"{browser_name} #{instance_id}: ✅ Slider button found in iframe!")
                                            break
                                    except:
                                        pass
                                if handle:
                                    break
                            except:
                                pass
                        
                        if handle:
                            break
                        
                        driver.switch_to.default_content()
                    except:
                        try:
                            driver.switch_to.default_content()
                        except:
                            pass
            except Exception as e:
                print(f"{browser_name} #{instance_id}: iframe search error: {e}")
                try:
                    driver.switch_to.default_content()
                except:
                    pass
        
        if not handle:
            print(f"{browser_name} #{instance_id}: ❌ Slider button paowa jayni!")
            return False
        
        print(f"{browser_name} #{instance_id}: Slider button click kora hocche...")
        
        # Step 2: Drag করুন
        try:
            # JavaScript দিয়ে track info পান
            track_info = driver.execute_script("""
                const handle = arguments[0];
                const parent = handle.parentElement;
                const track = parent.querySelector('.geetest_track, .track, [class*="track"]') || parent;
                
                const handleRect = handle.getBoundingClientRect();
                const trackRect = track.getBoundingClientRect();
                
                return {
                    handleWidth: handleRect.width,
                    handleHeight: handleRect.height,
                    trackWidth: trackRect.width,
                    trackLeft: trackRect.left,
                    trackRight: trackRect.right,
                    handleLeft: handleRect.left
                };
            """, handle)
            
            print(f"{browser_name} #{instance_id}: Track info: {track_info}")
            
            if track_info:
                max_distance = track_info['trackWidth'] - track_info['handleWidth']
                target_distance = int(max_distance * 0.9)  # 90% সরান
            else:
                target_distance = 280
            
            print(f"{browser_name} #{instance_id}: Drag distance: {target_distance}px")
            
        except Exception as e:
            print(f"{browser_name} #{instance_id}: Track info error: {e}")
            target_distance = 280
        
        # Method 1: Selenium ActionChains
        try:
            print(f"{browser_name} #{instance_id}: ActionChains দিয়ে drag করছি...")
            actions = ActionChains(driver)
            actions.move_to_element(handle)
            time.sleep(0.3)
            actions.click_and_hold()
            time.sleep(0.2)
            actions.move_by_offset(target_distance, 0)
            time.sleep(0.2)
            actions.release()
            actions.perform()
            
            print(f"{browser_name} #{instance_id}: ✅ ActionChains drag সফল!")
            time.sleep(1.5)
            return True
        except Exception as e:
            print(f"{browser_name} #{instance_id}: ActionChains failed: {e}")
        
        # Method 2: JavaScript simulation
        try:
            print(f"{browser_name} #{instance_id}: JavaScript দিয়ে drag করছি...")
            js_code = """
            const handle = arguments[0];
            const distance = arguments[1];
            
            // Get starting position
            const startRect = handle.getBoundingClientRect();
            const startX = startRect.left + startRect.width / 2;
            const startY = startRect.top + startRect.height / 2;
            
            // Simulate mouse events
            const mouseDownEvent = new MouseEvent('mousedown', {
                bubbles: true,
                cancelable: true,
                view: window,
                clientX: startX,
                clientY: startY,
                buttons: 1
            });
            handle.dispatchEvent(mouseDownEvent);
            
            // Drag in steps
            for (let i = 1; i <= 20; i++) {
                const currentX = startX + (distance * i / 20);
                const currentY = startY + Math.sin(i / 20 * Math.PI) * 3;
                
                const mouseMoveEvent = new MouseEvent('mousemove', {
                    bubbles: true,
                    cancelable: true,
                    view: window,
                    clientX: currentX,
                    clientY: currentY,
                    buttons: 1
                });
                
                handle.dispatchEvent(mouseMoveEvent);
                document.dispatchEvent(mouseMoveEvent);
            }
            
            // Mouse up
            const mouseUpEvent = new MouseEvent('mouseup', {
                bubbles: true,
                cancelable: true,
                view: window
            });
            handle.dispatchEvent(mouseUpEvent);
            document.dispatchEvent(mouseUpEvent);
            """
            
            driver.execute_script(js_code, handle, target_distance)
            print(f"{browser_name} #{instance_id}: ✅ JavaScript drag সম্পন্ন!")
            time.sleep(1.5)
            return True
        except Exception as e:
            print(f"{browser_name} #{instance_id}: JavaScript drag error: {e}")
            return False
            
    except Exception as e:
        print(f"{browser_name} #{instance_id}: ❌ Slider error: {e}")
        try:
            driver.switch_to.default_content()
        except:
            pass
        return False


def solve_captcha_safely(driver, instance_id, browser_name):
    """Updated captcha solver"""
    print(f"{browser_name} #{instance_id}: Captcha popup load howar jonno wait kora hocche...")
    time.sleep(2.0)

    try:
        driver.switch_to.default_content()

        # Captcha আছে কিনা চেক করুন
        try:
            captcha_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Slide') or contains(text(), 'complete')]")
            if captcha_elements:
                print(f"{browser_name} #{instance_id}: Captcha element found!")
        except:
            pass

        # Slider solve করুন
        slider_solved = solve_slider_captcha_v2(driver, instance_id, browser_name)
        
        if slider_solved:
            print(f"{browser_name} #{instance_id}: ✅ Captcha SOLVED!")
            human_delay(2.0, 3.0)
            return True
        else:
            print(f"{browser_name} #{instance_id}: Slider solve fail, manual continue...")
            human_delay(3.0, 4.0)
            return False
        
    except Exception as e:
        print(f"{browser_name} #{instance_id}: Captcha error: {e}")
        try:
            driver.switch_to.default_content()
        except:
            pass
        return False

def select_dropdown_human_way(driver, wait, dropdown_box, target_value):
    try:
        driver.execute_script("arguments[0].click();", dropdown_box)
        human_delay(1.0, 1.5)
        option_xpath = f"//li[normalize-space()='{target_value}'] | //div[normalize-space()='{target_value}' and (contains(@class, 'item') or contains(@class, 'option'))] | //span[normalize-space()='{target_value}']"
        clicked = False
        for _ in range(15):
            try:
                elements = driver.find_elements(By.XPATH, option_xpath)
                for el in elements:
                    if el.is_displayed():
                        driver.execute_script("arguments[0].scrollIntoView(true);", el)
                        human_delay(0.3, 0.5)
                        driver.execute_script("arguments[0].click();", el)
                        clicked = True
                        break
                if clicked:
                    break
            except:
                pass
            actions = ActionChains(driver)
            actions.send_keys(Keys.ARROW_DOWN).perform()
            human_delay(0.3, 0.5)
        if not clicked:
            val_element = wait.until(EC.element_to_be_clickable((By.XPATH, option_xpath)))
            driver.execute_script("arguments[0].click();", val_element)
        human_delay(1.2, 1.8)
    except Exception as e:
        print(f"Selection Error for {target_value}: {e}")

def launch_and_automate_chrome(instance_id, target_country):
    profile_path = f"C:\\Chrome\\profile-{instance_id}"
    max_restarts = 3
    
    for restart_attempt in range(max_restarts):
        driver = None
        try:
            if os.path.exists(profile_path):
                shutil.rmtree(profile_path, ignore_errors=True)
            os.makedirs(profile_path, exist_ok=True)
            
            target_url = get_unique_target_url()
            temp_email, mail_token = generate_temp_email()
            if not temp_email:
                continue
            account_password = generate_random_password()
            
            options = ChromeOptions()
            options.add_argument(f"user-data-dir={profile_path}")
            debug_port = random.randint(10000, 60000)
            options.add_argument(f"--remote-debugging-port={debug_port}")
            options.add_argument("--no-first-run")
            options.add_argument("--disable-fre")
            options.add_experimental_option("detach", True)

            driver = Chrome(options=options)
            driver.set_window_size(750, 850)
            driver.set_page_load_timeout(60)
            driver.get(target_url)
            print(f"\n---> Chrome #{instance_id} Open Hoyeche (750x850) | Port: {debug_port} | Email: {temp_email}")
            
            wait = WebDriverWait(driver, 25)
            wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
            human_delay(2.0, 3.0)
            
            country_box = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Malaysia')]")))
            country_box.click()
            human_delay(1.0, 1.5)
            
            actions = ActionChains(driver)
            actions.send_keys(target_country).perform()
            human_delay(1.2, 1.8) 
            
            actions.send_keys(Keys.TAB).perform()
            human_delay(0.6, 1.0)
            actions.send_keys(Keys.TAB).perform()
            human_delay(0.6, 1.0)
            actions.send_keys(Keys.ENTER).perform()
            human_delay(1.5, 2.0)
            
            actions.send_keys(Keys.ESCAPE).perform()
            human_delay(1.0, 1.5)
            
            email_box = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='text' and (contains(@placeholder, 'Email') or contains(@id, 'email') or contains(@name, 'email'))]")))
            email_box.click()
            email_box.clear()
            email_box.send_keys(temp_email)
            human_delay(1.2, 1.8)
            
            obtain_code_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Obtain code') or contains(text(), 'Get code') or contains(@class, 'obtain')]")))
            driver.execute_script("arguments[0].click();", obtain_code_btn)
            
            otp, msg_id = wait_for_verification_code(mail_token, temp_email)
            existing_mail_ids = {msg_id} if msg_id else set()
            
            if otp:
                otp_box = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[contains(@placeholder, 'verification code') or contains(@placeholder, 'Code') or contains(@id, 'code')]")))
                otp_box.click()
                otp_box.send_keys(otp)
                human_delay(1.5, 2.0)
                
                pass_box = wait.until(EC.element_to_be_clickable((By.XPATH, "(//input[@type='password'])[1]")))
                pass_box.click()
                pass_box.send_keys(account_password)
                human_delay(1.5, 2.0)
                
                confirm_pass_box = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='password' and (contains(@placeholder, 'Confirm') or contains(@placeholder, 'confirm'))] | (//input[@type='password'])[2]")))
                confirm_pass_box.click()
                confirm_pass_box.send_keys(account_password)
                human_delay(1.5, 2.0)
                
                rand_day = str(random.randint(1, 28))
                rand_month = str(random.randint(1, 12))
                rand_year = str(random.randint(1985, 2004))
                
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                human_delay(1.5, 2.0)

                all_selects = driver.find_elements(By.XPATH, "//div[contains(@class, 'ivu-select') or contains(@class, 'select') or contains(@class, 'picker')]")
                valid_selects = [sel for sel in all_selects if sel.is_displayed()]

                if len(valid_selects) >= 3:
                    day_box = valid_selects[-3]
                    month_box = valid_selects[-2]
                    year_box = valid_selects[-1]
                else:
                    day_box = all_selects[0]
                    month_box = all_selects[1]
                    year_box = all_selects[2]

                select_dropdown_human_way(driver, wait, day_box, rand_day)
                select_dropdown_human_way(driver, wait, month_box, rand_month)
                select_dropdown_human_way(driver, wait, year_box, rand_year)
                
                reg_actions = ActionChains(driver)
                for _ in range(6):
                    reg_actions.send_keys(Keys.TAB)
                    human_delay(0.2, 0.4)
                reg_actions.send_keys(Keys.ENTER)
                reg_actions.perform()
                human_delay(4.0, 5.0)
                
                try:
                    tc_actions1 = ActionChains(driver)
                    for _ in range(3):
                        tc_actions1.send_keys(Keys.TAB)
                        human_delay(0.2, 0.4)
                    tc_actions1.send_keys(Keys.ENTER)
                    tc_actions1.perform()
                    human_delay(2.0, 2.5)
                    
                    tc_actions2 = ActionChains(driver)
                    for _ in range(2):
                        tc_actions2.send_keys(Keys.TAB)
                        human_delay(0.2, 0.4)
                    tc_actions2.send_keys(Keys.ENTER)
                    tc_actions2.perform()
                    human_delay(3.0, 4.0)
                except Exception:
                    pass
                    
                print(f"Chrome #{instance_id}: Page loading complete howar jonno wait kora hocche...")
                try:
                    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
                except Exception:
                    pass
                human_delay(4.0, 6.0)
                
                link_btn_xpath = "//button[.//span[normalize-space()='Link']] | //span[normalize-space()='Link'] | //a[normalize-space()='Link']"
                link_btn = wait.until(EC.element_to_be_clickable((By.XPATH, link_btn_xpath)))
                driver.execute_script("arguments[0].scrollIntoView(true);", link_btn)
                human_delay(0.5, 1.0)
                driver.execute_script("arguments[0].click();", link_btn)
                
                print(f"Chrome #{instance_id}: Identity verification popup wait kora hocche...")
                popup_xpath = "//*[contains(text(), 'Identity verification') or contains(@class, 'el-dialog') or contains(@class, 'modal')]"
                wait.until(EC.visibility_of_element_located((By.XPATH, popup_xpath)))
                human_delay(1.5, 2.0)
                
                try:
                    popup_email_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'dialog') or contains(@class, 'modal') or contains(@class, 'el-dialog')]//input[@type='text' or contains(@placeholder, 'Email') or contains(@placeholder, 'code')] | //input[contains(@placeholder, 'Email code')]")))
                    popup_email_input.click()
                    human_delay(0.5, 0.8)
                    act = ActionChains(driver)
                    act.send_keys(Keys.TAB).send_keys(Keys.ENTER).perform()
                    human_delay(1.0, 1.5)
                except Exception as ex:
                    print(f"Chrome #{instance_id} Popup email box note: {ex}")
                
                try:
                    headers = {"Authorization": f"Bearer {mail_token}"}
                    curr_resp = requests.get("https://api.mail.tm/messages", headers=headers, timeout=10)
                    if curr_resp.status_code == 200:
                        for m in curr_resp.json().get('hydra:member', []):
                            existing_mail_ids.add(m['id'])
                except Exception:
                    pass

                print(f"Chrome #{instance_id}: Notun email code asar jonno wait kora hocche...")
                email_otp, new_msg_id = wait_for_new_verification_code(mail_token, timeout=90, ignore_ids=existing_mail_ids)
                if new_msg_id:
                    existing_mail_ids.add(new_msg_id)
                
                if email_otp:
                    print(f"Chrome #{instance_id}: Email OTP: {email_otp}")
                    try:
                        email_code_box = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'dialog') or contains(@class, 'modal') or contains(@class, 'el-dialog')]//input[@type='text' or contains(@placeholder, 'Email') or contains(@placeholder, 'code')] | //input[contains(@placeholder, 'Email code')]")))
                        email_code_box.click()
                        human_delay(0.5, 0.8)
                        email_code_box.clear()
                        email_code_box.send_keys(email_otp)
                        human_delay(1.0, 1.5)
                    except Exception as e:
                        print(f"Chrome #{instance_id} Error: {e}")

                print(f"Chrome #{instance_id}: Confirm button click kora hocche...")
                confirm_btn_xpath = "//button[.//span[normalize-space()='Confirm']] | //span[normalize-space()='Confirm'] | //a[normalize-space()='Confirm'] | //*[normalize-space()='Confirm']"
                confirm_btn = wait.until(EC.element_to_be_clickable((By.XPATH, confirm_btn_xpath)))
                driver.execute_script("arguments[0].scrollIntoView(true);", confirm_btn)
                human_delay(0.5, 0.8)
                driver.execute_script("arguments[0].click();", confirm_btn)
                human_delay(2.0, 3.0)

                print(f"Chrome #{instance_id}: Phone number await...")
                target_phone = get_and_cut_number()
                
                if target_phone:
                    print(f"Chrome #{instance_id}: Number: {target_phone}")
                    save_email_to_file(temp_email, account_password, target_phone)
                    phone_box = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='tel' or contains(@placeholder, 'Phone') or contains(@placeholder, 'phone') or contains(@name, 'phone') or contains(@id, 'phone')]")))
                    phone_box.click()
                    phone_box.clear()
                    phone_box.send_keys(target_phone)
                    human_delay(1.0, 1.5)
                else:
                    print(f"Chrome #{instance_id}: No numbers left!")
                    save_email_to_file(temp_email, account_password, "NO_NUMBER")

                print(f"Chrome #{instance_id}: 'Get code' button click...")
                sms_clicked = False
                all_sms_get_codes = driver.find_elements(By.XPATH, "//*[normalize-space()='Get code']")
                for el in reversed(all_sms_get_codes):
                    try:
                        if el.is_displayed():
                            driver.execute_script("arguments[0].scrollIntoView(true);", el)
                            human_delay(0.3, 0.5)
                            driver.execute_script("arguments[0].click();", el)
                            sms_clicked = True
                            break
                    except:
                        pass
                
                if not sms_clicked:
                    sms_get_code_xpath = "(//button[.//span[normalize-space()='Get code']] | //span[normalize-space()='Get code'] | //a[normalize-space()='Get code'] | //*[normalize-space()='Get code'])[last()]"
                    sms_get_code_btn = wait.until(EC.element_to_be_clickable((By.XPATH, sms_get_code_xpath)))
                    driver.execute_script("arguments[0].click();", sms_get_code_btn)
                
                # 🔧 FIXED CAPTCHA SOLVER
                solve_captcha_safely(driver, instance_id, "Chrome")
                
                print(f"Chrome #{instance_id}: ✅ Process completed!")
                human_delay(5.0, 8.0)
                return driver
                
        except (WebDriverException, TimeoutException, NoSuchElementException, Exception) as err:
            print(f"\n[ERROR] Chrome #{instance_id}: {err}")
            if driver:
                try:
                    driver.quit()
                except:
                    pass
            print(f"Chrome #{instance_id}: Restart (Attempt {restart_attempt + 1}/{max_restarts})...")
            if os.path.exists(profile_path):
                try:
                    shutil.rmtree(profile_path, ignore_errors=True)
                except:
                    pass
            time.sleep(3.0)
            
    return None


def launch_and_automate_firefox(instance_id, target_country):
    profile_path = f"C:\\Firefox\\profile-{instance_id}"
    max_restarts = 3
    
    for restart_attempt in range(max_restarts):
        driver = None
        try:
            if os.path.exists(profile_path):
                shutil.rmtree(profile_path, ignore_errors=True)
            os.makedirs(profile_path, exist_ok=True)
            
            target_url = get_unique_target_url()
            temp_email, mail_token = generate_temp_email()
            if not temp_email:
                continue
            account_password = generate_random_password()
            
            options = FirefoxOptions()
            options.add_argument("-profile")
            options.add_argument(profile_path)

            ff_port = random.randint(10000, 60000)
            service = FirefoxService(port=ff_port)

            driver = Firefox(service=service, options=options)
            driver.set_window_size(750, 850)
            driver.set_page_load_timeout(60)
            driver.get(target_url)
            print(f"\n---> Firefox #{instance_id} Open (750x850) | Port: {ff_port} | Email: {temp_email}")
            
            wait = WebDriverWait(driver, 25)
            wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
            human_delay(2.0, 3.0)
            
            country_box = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Malaysia')]")))
            country_box.click()
            human_delay(1.0, 1.5)
            
            actions = ActionChains(driver)
            actions.send_keys(target_country).perform()
            human_delay(1.2, 1.8)
            
            actions.send_keys(Keys.TAB).perform()
            human_delay(0.6, 1.0)
            actions.send_keys(Keys.TAB).perform()
            human_delay(0.6, 1.0)
            actions.send_keys(Keys.ENTER).perform()
            human_delay(1.5, 2.0)
            
            actions.send_keys(Keys.ESCAPE).perform()
            human_delay(1.0, 1.5)
            
            email_box = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='text' and (contains(@placeholder, 'Email') or contains(@id, 'email') or contains(@name, 'email'))]")))
            email_box.click()
            email_box.clear()
            email_box.send_keys(temp_email)
            human_delay(1.2, 1.8)
            
            obtain_code_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Obtain code') or contains(text(), 'Get code') or contains(@class, 'obtain')]")))
            driver.execute_script("arguments[0].click();", obtain_code_btn)
            
            otp, msg_id = wait_for_verification_code(mail_token, temp_email)
            existing_mail_ids = {msg_id} if msg_id else set()
            
            if otp:
                otp_box = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[contains(@placeholder, 'verification code') or contains(@placeholder, 'Code') or contains(@id, 'code')]")))
                otp_box.click()
                otp_box.send_keys(otp)
                human_delay(1.5, 2.0)
                
                pass_box = wait.until(EC.element_to_be_clickable((By.XPATH, "(//input[@type='password'])[1]")))
                pass_box.click()
                pass_box.send_keys(account_password)
                human_delay(1.5, 2.0)
                
                confirm_pass_box = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='password' and (contains(@placeholder, 'Confirm') or contains(@placeholder, 'confirm'))] | (//input[@type='password'])[2]")))
                confirm_pass_box.click()
                confirm_pass_box.send_keys(account_password)
                human_delay(1.5, 2.0)
                
                rand_day = str(random.randint(1, 28))
                rand_month = str(random.randint(1, 12))
                rand_year = str(random.randint(1985, 2004))
                
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                human_delay(1.5, 2.0)

                all_selects = driver.find_elements(By.XPATH, "//div[contains(@class, 'ivu-select') or contains(@class, 'select') or contains(@class, 'picker')]")
                valid_selects = [sel for sel in all_selects if sel.is_displayed()]

                if len(valid_selects) >= 3:
                    day_box = valid_selects[-3]
                    month_box = valid_selects[-2]
                    year_box = valid_selects[-1]
                else:
                    day_box = all_selects[0]
                    month_box = all_selects[1]
                    year_box = all_selects[2]

                select_dropdown_human_way(driver, wait, day_box, rand_day)
                select_dropdown_human_way(driver, wait, month_box, rand_month)
                select_dropdown_human_way(driver, wait, year_box, rand_year)
                
                reg_actions = ActionChains(driver)
                for _ in range(6):
                    reg_actions.send_keys(Keys.TAB)
                    human_delay(0.2, 0.4)
                reg_actions.send_keys(Keys.ENTER)
                reg_actions.perform()
                human_delay(4.0, 5.0)
                
                try:
                    tc_actions1 = ActionChains(driver)
                    for _ in range(3):
                        tc_actions1.send_keys(Keys.TAB)
                        human_delay(0.2, 0.4)
                    tc_actions1.send_keys(Keys.ENTER)
                    tc_actions1.perform()
                    human_delay(2.0, 2.5)
                    
                    tc_actions2 = ActionChains(driver)
                    for _ in range(2):
                        tc_actions2.send_keys(Keys.TAB)
                        human_delay(0.2, 0.4)
                    tc_actions2.send_keys(Keys.ENTER)
                    tc_actions2.perform()
                    human_delay(3.0, 4.0)
                except Exception:
                    pass
                    
                print(f"Firefox #{instance_id}: Page loading...")
                try:
                    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
                except Exception:
                    pass
                human_delay(4.0, 6.0)
                
                link_btn_xpath = "//button[.//span[normalize-space()='Link']] | //span[normalize-space()='Link'] | //a[normalize-space()='Link']"
                link_btn = wait.until(EC.element_to_be_clickable((By.XPATH, link_btn_xpath)))
                driver.execute_script("arguments[0].scrollIntoView(true);", link_btn)
                human_delay(0.5, 1.0)
                driver.execute_script("arguments[0].click();", link_btn)
                
                print(f"Firefox #{instance_id}: Verification popup wait...")
                popup_xpath = "//*[contains(text(), 'Identity verification') or contains(@class, 'el-dialog') or contains(@class, 'modal')]"
                wait.until(EC.visibility_of_element_located((By.XPATH, popup_xpath)))
                human_delay(1.5, 2.0)
                
                try:
                    popup_email_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'dialog') or contains(@class, 'modal') or contains(@class, 'el-dialog')]//input[@type='text' or contains(@placeholder, 'Email') or contains(@placeholder, 'code')] | //input[contains(@placeholder, 'Email code')]")))
                    popup_email_input.click()
                    human_delay(0.5, 0.8)
                    act = ActionChains(driver)
                    act.send_keys(Keys.TAB).send_keys(Keys.ENTER).perform()
                    human_delay(1.0, 1.5)
                except Exception as ex:
                    print(f"Firefox #{instance_id} Popup: {ex}")
                
                try:
                    headers = {"Authorization": f"Bearer {mail_token}"}
                    curr_resp = requests.get("https://api.mail.tm/messages", headers=headers, timeout=10)
                    if curr_resp.status_code == 200:
                        for m in curr_resp.json().get('hydra:member', []):
                            existing_mail_ids.add(m['id'])
                except Exception:
                    pass

                print(f"Firefox #{instance_id}: Email OTP wait...")
                email_otp, new_msg_id = wait_for_new_verification_code(mail_token, timeout=90, ignore_ids=existing_mail_ids)
                if new_msg_id:
                    existing_mail_ids.add(new_msg_id)
                
                if email_otp:
                    print(f"Firefox #{instance_id}: Email OTP: {email_otp}")
                    try:
                        email_code_box = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'dialog') or contains(@class, 'modal') or contains(@class, 'el-dialog')]//input[@type='text' or contains(@placeholder, 'Email') or contains(@placeholder, 'code')] | //input[contains(@placeholder, 'Email code')]")))
                        email_code_box.click()
                        human_delay(0.5, 0.8)
                        email_code_box.clear()
                        email_code_box.send_keys(email_otp)
                        human_delay(1.0, 1.5)
                    except Exception as e:
                        print(f"Firefox #{instance_id} Error: {e}")

                print(f"Firefox #{instance_id}: Confirm click...")
                confirm_btn_xpath = "//button[.//span[normalize-space()='Confirm']] | //span[normalize-space()='Confirm'] | //a[normalize-space()='Confirm'] | //*[normalize-space()='Confirm']"
                confirm_btn = wait.until(EC.element_to_be_clickable((By.XPATH, confirm_btn_xpath)))
                driver.execute_script("arguments[0].scrollIntoView(true);", confirm_btn)
                human_delay(0.5, 0.8)
                driver.execute_script("arguments[0].click();", confirm_btn)
                human_delay(2.0, 3.0)

                print(f"Firefox #{instance_id}: Phone number...")
                target_phone = get_and_cut_number()
                
                if target_phone:
                    print(f"Firefox #{instance_id}: {target_phone}")
                    save_email_to_file(temp_email, account_password, target_phone)
                    phone_box = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='tel' or contains(@placeholder, 'Phone') or contains(@placeholder, 'phone') or contains(@name, 'phone') or contains(@id, 'phone')]")))
                    phone_box.click()
                    phone_box.clear()
                    phone_box.send_keys(target_phone)
                    human_delay(1.0, 1.5)
                else:
                    print(f"Firefox #{instance_id}: No numbers!")
                    save_email_to_file(temp_email, account_password, "NO_NUMBER")

                print(f"Firefox #{instance_id}: Get code click...")
                sms_clicked = False
                all_sms_get_codes = driver.find_elements(By.XPATH, "//*[normalize-space()='Get code']")
                for el in reversed(all_sms_get_codes):
                    try:
                        if el.is_displayed():
                            driver.execute_script("arguments[0].scrollIntoView(true);", el)
                            human_delay(0.3, 0.5)
                            driver.execute_script("arguments[0].click();", el)
                            sms_clicked = True
                            break
                    except:
                        pass
                
                if not sms_clicked:
                    sms_get_code_xpath = "(//button[.//span[normalize-space()='Get code']] | //span[normalize-space()='Get code'] | //a[normalize-space()='Get code'] | //*[normalize-space()='Get code'])[last()]"
                    sms_get_code_btn = wait.until(EC.element_to_be_clickable((By.XPATH, sms_get_code_xpath)))
                    driver.execute_script("arguments[0].click();", sms_get_code_btn)
                
                # 🔧 FIXED CAPTCHA SOLVER
                solve_captcha_safely(driver, instance_id, "Firefox")
                
                print(f"Firefox #{instance_id}: ✅ Completed!")
                human_delay(5.0, 8.0)
                return driver
                
        except (WebDriverException, TimeoutException, NoSuchElementException, Exception) as err:
            print(f"\n[ERROR] Firefox #{instance_id}: {err}")
            if driver:
                try:
                    driver.quit()
                except:
                    pass
            print(f"Firefox #{instance_id}: Restart...")
            if os.path.exists(profile_path):
                try:
                    shutil.rmtree(profile_path, ignore_errors=True)
                except:
                    pass
            time.sleep(3.0)
            
    return None


if __name__ == "__main__":
    delete_old_profiles()
        
    try:
        total_pairs = int(input("Kotota pair (Chrome + Firefox) open korbo? "))
    except ValueError:
        total_pairs = 1
        
    selected_text = input("Country type koro (e.g., Egypt): ")
    if not selected_text:
        selected_text = "Egypt"
        
    print("\nShob browser start hocche...\n")
    
    threads = []
    
    for i in range(1, total_pairs + 1):
        t_chrome = threading.Thread(target=launch_and_automate_chrome, args=(i, selected_text))
        threads.append(t_chrome)
        t_chrome.start()
        time.sleep(1.0) 
        
        t_firefox = threading.Thread(target=launch_and_automate_firefox, args=(i, selected_text))
        threads.append(t_firefox)
        t_firefox.start()
        time.sleep(1.0)
        
    for t in threads:
        t.join()
        
    print("\nShob guli complete!")
    input("Enter press korun...")
