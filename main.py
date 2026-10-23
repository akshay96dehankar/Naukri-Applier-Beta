import os
import time
import traceback
import pyautogui
import pyperclip
import keyboard

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


USERNAME = os.getenv("NAUKRI_USERNAME", "akshay.dehankar.official@gmail.com")
PASSWORD = os.getenv("NAUKRI_PASSWORD", "9850329727ad")

SEARCH_TEXT = "data engineer, 3 year, noida,"
SEARCH_X, SEARCH_Y = 698, 175


def check_failsafe():
    """Universal fail-safe: if '9' is pressed, exit immediately."""
    try:
        if keyboard.is_pressed('9'):
            print("\n[FAIL-SAFE TRIGGERED] '9' key pressed by user. Aborting automation...")
            raise KeyboardInterrupt
    except KeyboardInterrupt:
        raise
    except Exception:
        pass


def wait_click(driver, xpath, timeout=10):
    check_failsafe()
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    ).click()


def close_login_sidebar(driver):
    """Closes any prompt, popup, or sidebar that appears immediately after login."""
    try:
        check_failsafe()
        close_xpaths = [
            "//div[contains(@class, 'cross')]",
            "//span[contains(@class, 'cross')]",
            "//button[contains(@class, 'cross')]",
            "//*[local-name()='svg' and contains(@class, 'cross')]",
            "//div[@class='modal-close']",
            "//em[contains(@class, 'icon-close')]"
        ]
        for xpath in close_xpaths:
            elements = driver.find_elements(By.XPATH, xpath)
            for el in elements:
                if el.is_displayed():
                    el.click()
                    time.sleep(1)
                    print("Closed post-login sidebar/popup.")
                    return
    except Exception:
        pass


def check_sidebar_appeared(driver):
    """Checks if a sidebar or form panel asking for more info appeared after clicking apply."""
    try:
        script = """
        const visible = el => {
            const r = el.getBoundingClientRect();
            const s = getComputedStyle(el);
            return r.width > 0 && r.height > 0 && s.display !== "none" && s.visibility !== "hidden";
        };
        const panels = [...document.querySelectorAll("div,section,aside,form")].filter(el => 
            visible(el) && el.getBoundingClientRect().left > innerWidth * 0.5 && 
            ((el.innerText || "").includes("?") || (el.innerText || "").includes("Details"))
        );
        return panels.length > 0;
        """
        return bool(driver.execute_script(script))
    except:
        return False


def find_apply(driver):
    check_failsafe()
    xpath = """
    //button[contains(
        translate(normalize-space(.),
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
        'abcdefghijklmnopqrstuvwxyz'),'apply')]
    |
    //a[contains(
        translate(normalize-space(.),
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
        'abcdefghijklmnopqrstuvwxyz'),'apply')]
    """

    for el in driver.find_elements(By.XPATH, xpath):
        check_failsafe()
        try:
            if el.is_displayed() and el.is_enabled():
                return el
        except:
            pass

    return None


def login(driver):
    driver.get("https://www.naukri.com/")
    time.sleep(3)

    check_failsafe()
    WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//a[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
            "'abcdefghijklmnopqrstuvwxyz'),'login')]"
            " | "
            "//button[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
            "'abcdefghijklmnopqrstuvwxyz'),'login')]"
        ))
    ).click()

    email = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((
            By.XPATH,
            "//input[@type='email' or "
            "contains(translate(@placeholder,"
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'email') or "
            "contains(translate(@placeholder,"
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'username')]"
        ))
    )

    email.send_keys(USERNAME)

    driver.find_element(
        By.XPATH,
        "//input[@type='password']"
    ).send_keys(PASSWORD)

    WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//button[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
            "'abcdefghijklmnopqrstuvwxyz'),'login')]"
        ))
    ).click()

    time.sleep(4)
    close_login_sidebar(driver)


def close_job(driver, listing):
    try:
        if len(driver.window_handles) > 1:
            if driver.current_window_handle != listing:
                driver.close()
            driver.switch_to.window(listing)
    except Exception as e:
        print("Close error:", e)


def main():
    start_time = time.time()
    driver = webdriver.Chrome()
    driver.maximize_window()

    total_attempted = 0
    sidebar_detected_count = 0
    direct_apply_count = 0

    try:
        login(driver)
        time.sleep(2)

        check_failsafe()
        pyautogui.click(SEARCH_X, SEARCH_Y)
        pyautogui.hotkey("ctrl", "a")
        pyautogui.write(SEARCH_TEXT, interval=.02)
        pyautogui.press("enter")

        time.sleep(3)

        try:
            wait_click(driver, "//*[normalize-space()='Recommended']", 3)
            wait_click(driver, "//*[normalize-space()='Date']", 3)
        except:
            pass

        time.sleep(2)
        listing = driver.current_window_handle

        # Iterate through 5 pages
        for page in range(1, 2
        ):
            check_failsafe()
            print(f"\n================ PAGE {page} ================")
            
            jobs = driver.find_elements(
                By.XPATH,
                "//a[contains(@class,'title')]"
            )

            urls = list(dict.fromkeys(
                j.get_attribute("href")
                for j in jobs
                if j.get_attribute("href")
            ))

            print(f"Jobs found on page {page}: {len(urls)}")

            # Apply to up to 20 jobs on the current page
            for i, url in enumerate(urls[:20], 1):
                check_failsafe()
                print(f"\n--- JOB {i}/20 (Page {page}) ---")

                driver.switch_to.window(listing)
                driver.execute_script(
                    "window.open(arguments[0], '_blank');",
                    url
                )

                time.sleep(2)

                if len(driver.window_handles) < 2:
                    continue

                driver.switch_to.window(
                    driver.window_handles[-1]
                )

                apply = find_apply(driver)

                if not apply:
                    print("Apply not found.")
                    close_job(driver, listing)
                    continue

                # Check if it's an external 'Apply on company site' button
                apply_text = apply.text.strip().lower()
                if "company site" in apply_text:
                    print("External 'Apply on company site' detected. Skipping and closing...")
                    close_job(driver, listing)
                    continue

                try:
                    driver.execute_script(
                        "arguments[0].scrollIntoView({block:'center'});",
                        apply
                    )
                    time.sleep(0.5)

                    try:
                        apply.click()
                    except:
                        driver.execute_script(
                            "arguments[0].click();",
                            apply
                        )

                    print("Apply clicked.")
                    total_attempted += 1

                except Exception as e:
                    print("Apply error:", e)
                    close_job(driver, listing)
                    continue

                # Check if sidebar/question panel appeared for more info
                time.sleep(1.5)
                if check_sidebar_appeared(driver):
                    print("-> Sidebar / Extra Info panel detected!")
                    sidebar_detected_count += 1
                else:
                    print("-> Direct apply (No sidebar detected).")
                    direct_apply_count += 1

                # Close and continue
                time.sleep(1.5)
                close_job(driver, listing)
                time.sleep(1)

            # Navigate to the next page if not the last page
            if page < 5:
                try:
                    check_failsafe()
                    next_btn = WebDriverWait(driver, 8).until(
                        EC.element_to_be_clickable((
                            By.XPATH, 
                            "//*[normalize-space()='Next' or contains(@class, 'ficon-right')]"
                        ))
                    )
                    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", next_btn)
                    time.sleep(0.5)
                    next_btn.click()
                    print(f"Moving to Page {page + 1}...")
                    time.sleep(3)
                except Exception as e:
                    print("Could not find or click the 'Next' button. Stopping pagination.", e)
                    break

    except KeyboardInterrupt:
        print("\nAutomation stopped safely via Fail-Safe (Key '9').")
    except Exception as e:
        print("ERROR:", e)
        traceback.print_exc()

    finally:
        elapsed_time = time.time() - start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)

        print("\n================ SESSION SUMMARY ================")
        print(f"Total Applications Attempted: {total_attempted}")
        print(f"Direct Applies (No Sidebar): {direct_apply_count}")
        print(f"Sidebars/More Info Panels Detected: {sidebar_detected_count}")
        print(f"Total Processing Time: {minutes} minutes {seconds} seconds")
        print("==================================================")
        
        input("\nPress Enter to close Chrome...")
        driver.quit()


if __name__ == "__main__":
    main()