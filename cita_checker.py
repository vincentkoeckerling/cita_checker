#!/usr/bin/env python3
"""
Cita Previa Extranjería Checker Bot
Monitors availability for "POLICIA-CERTIFICADO DE REGISTRO DE CIUDADANO DE LA U.E." appointments in S.Cruz Tenerife
"""

import logging
import os
import random
import smtplib
import time
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("cita_checker.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class CitaChecker:
    """Check for available Cita Previa appointments"""

    # Cita Previa URLs
    BASE_URL = "https://icp.administracionelectronica.gob.es/icpplustieb/index"
    PROVINCIA_URL = (
        "https://icp.administracionelectronica.gob.es/icpco/citar?p=38&locale=es"
    )

    # Values for desired office
    OFFICE_VALUE = "7"
    OFFICE_NAME = "CNP San Cristobal de LA LAGUNA, CALLE NAVA Y GRIMON, 66, Santa Cruz de Tenerife"

    # Form values for S.Cruz Tenerife - POLICIA-CERTIFICADO DE REGISTRO DE CIUDADANO DE LA U.E.
    PROVINCIA = "S.Cruz Tenerife"
    TRAMITE_VALUE = "4038"
    TRAMITE_NAME = "POLICIA-CERTIFICADO DE REGISTRO DE CIUDADANO DE LA U.E."

    def __init__(self, headless=True):
        """Initialize the checker with browser options"""
        self.headless = headless
        self.driver = None
        self.last_notification_time = None

    def setup_driver(self):
        """Setup Chrome WebDriver with options"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)
        logger.info("WebDriver initialized")

    def close_driver(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver closed")

    def set_random_window_size(self):
        """Set radom window size to prevent bot detection"""
        width = random.randint(800, 1600)
        height_factor = random.uniform(1.5, 2.5)
        height = (width * height_factor) // 3
        self.driver.set_window_size(width, height)

    def sleep_random(self):
        """Sleep between 2 and 5 seconds to prevent bot detection"""
        time.sleep(random.randint(2, 5))

    def check_availability(self):
        """
        Check if appointments are available
        Returns: tuple (available: bool, message: str)
        """
        try:
            logger.info("Starting availability check...")
            self.setup_driver()
            self.set_random_window_size()

            # Navigate directly to provincia page
            self.driver.get(self.PROVINCIA_URL)
            logger.info(f"Navigated to: {self.PROVINCIA_URL}")

            # Wait for the page to load
            wait = WebDriverWait(self.driver, 15)
            self.sleep_random()

            # Dismiss cookie banner if present
            try:
                # Try to find and click the cookie accept button
                cookie_button = self.driver.find_element(
                    By.ID, "cookie_action_close_header"
                )
                cookie_button.click()
                logger.info("Dismissed cookie banner")
                self.sleep_random()
            except NoSuchElementException:
                logger.info("No cookie banner found or already dismissed")
            except Exception as e:
                logger.warning(f"Could not dismiss cookie banner: {str(e)}")

            # Select correct office
            try:
                oficina_select = wait.until(
                    EC.presence_of_element_located((By.ID, "sede"))
                )
                select_oficina = Select(oficina_select)
                select_oficina.select_by_value(self.OFFICE_VALUE)
                logger.info(f"Selected '{self.OFFICE_NAME}'")

                # Wait for page to refresh and load tramites
                time.sleep(2)
                self.sleep_random()
            except Exception as e:
                logger.error(f"Could not select office: {str(e)}")
                return None, "Could not select office"

            # Select the tramite
            try:
                tramite_select_element = wait.until(
                    EC.presence_of_element_located((By.ID, "tramiteGrupo[0]"))
                )
                tramite_select = Select(tramite_select_element)

                # Check if our tramite is available
                tramite_available = False
                for option in tramite_select.options:
                    if option.get_attribute("value") == self.TRAMITE_VALUE:
                        tramite_available = True
                        break

                if not tramite_available:
                    logger.error(f"Tramite '{self.TRAMITE_NAME}' not available")
                    return None, "Tramite not available"

                # Select the tramite
                tramite_select.select_by_value(self.TRAMITE_VALUE)
                logger.info(f"Selected tramite: {self.TRAMITE_NAME}")
                time.sleep(2)
                self.sleep_random()

            except Exception as e:
                logger.error(f"Could not select tramite: {str(e)}")
                return None, f"Could not select tramite: {str(e)}"

            # Click "Aceptar" to proceed to acInfo page
            try:
                aceptar_btn = wait.until(
                    EC.element_to_be_clickable((By.ID, "btnAceptar"))
                )
                aceptar_btn.click()
                logger.info("Clicked Aceptar button")
                self.sleep_random()

                # Verify we reached the acInfo page
                current_url = self.driver.current_url
                logger.info(f"Current page: {current_url}")

            except Exception as e:
                logger.error(f"Could not find or click Aceptar button: {str(e)}")
                return None, f"Could not click Aceptar: {str(e)}"

            # Click "Presentación sin Cl@ve" on acInfo page
            try:
                # Wait longer for the page to fully load
                logger.info("Waiting for acInfo page to load...")
                time.sleep(3)  # Give page more time to load
                self.sleep_random()

                # Create a longer wait for this specific button
                long_wait = WebDriverWait(self.driver, 30)  # 30 seconds timeout

                # Try multiple methods to find and click the button
                btn_clicked = False

                # Method 1: Try by ID with explicit wait
                try:
                    logger.info("Attempting to find btnEntrar by ID...")
                    btn_entrar = long_wait.until(
                        EC.presence_of_element_located((By.ID, "btnEntrar"))
                    )
                    # Wait a bit more for it to be clickable
                    self.sleep_random()
                    btn_entrar.click()
                    logger.info("✓ Clicked 'btnEntrar' by ID")
                    btn_clicked = True
                except TimeoutException:
                    logger.warning("Timeout waiting for btnEntrar by ID")
                except Exception as e:
                    logger.warning(f"Could not click btnEntrar by ID: {str(e)}")

                # Method 2: Try by XPath with input type
                if not btn_clicked:
                    try:
                        logger.info("Attempting to find button by XPath...")
                        btn_entrar = self.driver.find_element(
                            By.XPATH, "//input[@id='btnEntrar']"
                        )
                        btn_entrar.click()
                        logger.info("✓ Clicked button by XPath")
                        btn_clicked = True
                    except Exception as e:
                        logger.warning(f"Could not click button by XPath: {str(e)}")

                # Method 3: Try JavaScript click as fallback
                if not btn_clicked:
                    try:
                        logger.info("Attempting JavaScript click...")
                        btn_entrar = self.driver.find_element(By.ID, "btnEntrar")
                        self.driver.execute_script("arguments[0].click();", btn_entrar)
                        logger.info("✓ Clicked button with JavaScript")
                        btn_clicked = True
                    except Exception as e:
                        logger.warning(
                            f"Could not click button with JavaScript: {str(e)}"
                        )

                if btn_clicked:
                    self.sleep_random()
                    # Verify we reached the acEntrada page
                    current_url = self.driver.current_url
                    logger.info(f"Current page: {current_url}")
                else:
                    # Log page info for debugging
                    logger.error(
                        "Failed to click 'Presentación sin Cl@ve' button with all methods"
                    )
                    logger.error(f"Current URL: {self.driver.current_url}")
                    # Save screenshot for debugging (optional)
                    try:
                        self.driver.save_screenshot("debug_acinfo_page.png")
                        logger.info("Saved debug screenshot to debug_acinfo_page.png")
                    except Exception:
                        pass
                    return None, "Could not click 'Presentación sin Cl@ve' button"

            except Exception as e:
                logger.error(
                    f"Unexpected error clicking 'Presentación sin Cl@ve' button: {str(e)}"
                )
                return None, f"Could not click 'Presentación sin Cl@ve': {str(e)}"

            # Fill in personal data on acEntrada page
            try:
                # Select Pasaporte
                pasaporte_select = wait.until(
                    EC.element_to_be_clickable((By.ID, "rdbTipoDocPas"))
                )
                pasaporte_select.click()
                logger.info("Selected Pasaporte")

                # Enter NIE
                nie_input = wait.until(
                    EC.presence_of_element_located((By.ID, "txtIdCitado"))
                )
                nie_input.clear()
                nie_input.send_keys(os.getenv("NIE_NUMBER", "X1234567A"))
                logger.info("Filled NIE number")

                # Enter name
                nombre_input = self.driver.find_element(By.ID, "txtDesCitado")
                nombre_input.clear()
                nombre_input.send_keys(os.getenv("FULL_NAME", "TEST USER"))
                logger.info("Filled full name")

                # Select country (CHINA) - value 406
                # pais_select = Select(self.driver.find_element(By.ID, "txtPaisNac"))
                # country_value = os.getenv("COUNTRY_CODE", "406")  # 406 = CHINA
                # pais_select.select_by_value(country_value)
                # logger.info(f"Selected country with code: {country_value}")

                self.sleep_random()
            except Exception as e:
                logger.error(f"Could not fill personal data: {str(e)}")
                return None, f"Could not fill personal data: {str(e)}"

            # Click second "Aceptar" to submit form and validate
            try:
                aceptar_btn2 = wait.until(
                    EC.element_to_be_clickable((By.ID, "btnEnviar"))
                )
                aceptar_btn2.click()
                logger.info("Clicked Aceptar button to submit form")
                self.sleep_random()

                # Verify we reached the validation page
                current_url = self.driver.current_url
                logger.info(f"Current page after submission: {current_url}")

            except Exception as e:
                logger.error(f"Could not find or click Aceptar button: {str(e)}")
                return None, f"Could not submit form: {str(e)}"

            # Click "Solicitar Cita" button on validation page
            try:
                solicitar_btn = wait.until(
                    EC.element_to_be_clickable((By.ID, "btnEnviar"))
                )
                solicitar_btn.click()
                logger.info("Clicked 'Solicitar Cita' button")
                self.sleep_random()

                # Log current URL after requesting appointment
                current_url = self.driver.current_url
                logger.info(f"Current page after 'Solicitar Cita': {current_url}")

            except Exception as e:
                logger.error(
                    f"Could not find or click 'Solicitar Cita' button: {str(e)}"
                )
                return None, f"Could not request cita: {str(e)}"

            # Check for availability message on acCitar page
            page_source = self.driver.page_source.lower()

            # Check for the specific "no appointments" message
            no_citas_phrases = [
                "no hay citas disponibles",
                "en este momento no hay citas disponibles",
                "no existen citas disponibles",
                "agotadas las citas",
                "no hay citas disponibles para la reserva sin cl@ve",
            ]

            has_no_citas = any(phrase in page_source for phrase in no_citas_phrases)

            # Check for the specific message about Cl@ve availability
            clave_available = (
                "sí tienen a su disposición mediante el uso de cl@ve" in page_source
            )

            if has_no_citas:
                if clave_available:
                    logger.info(
                        "❌ No appointments available without Cl@ve (appointments available WITH Cl@ve)"
                    )
                    return (
                        False,
                        "No hay citas disponibles sin Cl@ve. Hay citas disponibles CON Cl@ve.",
                    )
                else:
                    logger.info("❌ No appointments available")
                    return False, "No hay citas disponibles en ninguna oficina"
            else:
                # Check if we can see a calendar, date selector, or appointment form
                try:
                    # Look for calendar or date selection elements
                    self.driver.find_element(By.ID, "idCaptcha")
                    logger.info("✅ APPOINTMENTS AVAILABLE! Calendar detected")
                    return True, "¡Citas disponibles! Check the website immediately."
                except NoSuchElementException:
                    # Check for other date selection indicators
                    try:
                        self.driver.find_element(By.ID, "idSede")
                        logger.info("✅ APPOINTMENTS MIGHT BE AVAILABLE! Form detected")
                        return (
                            True,
                            "¡Posibles citas disponibles! Check the website immediately.",
                        )
                    except NoSuchElementException:
                        # Check if we see the date/hour selection page
                        if "selecciona" in page_source and (
                            "fecha" in page_source or "hora" in page_source
                        ):
                            logger.info(
                                "✅ APPOINTMENTS AVAILABLE! Date selection detected"
                            )
                            return (
                                True,
                                "¡Citas disponibles! Check the website immediately.",
                            )
                        else:
                            # If no clear "no citas" message and no form elements, might be available
                            logger.info(
                                "⚠️ Status unclear - no clear 'no citas' message found"
                            )
                            return (
                                True,
                                "Possible appointments! Please check the website manually to confirm.",
                            )

        except Exception as e:
            logger.error(f"Error checking availability: {str(e)}")
            return None, f"Error: {str(e)}"

        finally:
            self.close_driver()

    def send_email_notification(self, subject, message):
        """Send email notification"""
        try:
            sender_email = os.getenv("SENDER_EMAIL")
            sender_password = os.getenv("SENDER_PASSWORD")
            receiver_email = os.getenv("RECEIVER_EMAIL")
            smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
            smtp_port = int(os.getenv("SMTP_PORT", "587"))

            if not all([sender_email, sender_password, receiver_email]):
                logger.warning(
                    "Email credentials not configured. Skipping email notification."
                )
                return False

            # Create message
            msg = MIMEMultipart()
            msg["From"] = sender_email
            msg["To"] = receiver_email
            msg["Subject"] = subject

            body = f"""
            Cita Previa Alert
            =================

            {message}

            Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

            URL: {self.BASE_URL}

            Check the website immediately if appointments are available!

            ---
            This is an automated message from Cita Previa Checker Bot
            """

            msg.attach(MIMEText(body, "plain"))

            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)

            logger.info(f"✉️ Email notification sent to {receiver_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False

    def run_continuous_check(self, interval_minutes=15):
        """
        Run continuous checking loop
        Args:
            interval_minutes: Minutes between checks (default 15)
        """
        logger.info("🤖 Starting Cita Previa Checker Bot")
        logger.info(f"📍 Location: {self.PROVINCIA}")
        logger.info(f"📋 Tramite: {self.TRAMITE_NAME}")
        logger.info(f"⏱️ Check interval: {interval_minutes} minutes")
        logger.info("=" * 60)

        check_count = 0

        try:
            while True:
                check_count += 1
                logger.info(f"\n{'=' * 60}")
                logger.info(
                    f"Check #{check_count} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                logger.info(f"{'=' * 60}")

                available, message = self.check_availability()

                if available:
                    # Appointments found! Send notification
                    subject = f"🎉 CITA PREVIA AVAILABLE – {self.TRAMITE_NAME}"
                    self.send_email_notification(subject, message)

                    # You can choose to stop checking or continue
                    # Uncomment the next line to stop after finding availability
                    # break

                elif available is None:
                    # Unclear status - might want to notify
                    logger.warning("Status unclear - manual check recommended")

                # Wait before next check
                logger.info(
                    f"⏳ Waiting {interval_minutes} minutes until next check..."
                )
                # variation by +-2min
                time.sleep(interval_minutes * 60 + random.randint(-2, 2) * 60)

        except KeyboardInterrupt:
            logger.info("\n\n🛑 Bot stopped by user")
            logger.info(f"Total checks performed: {check_count}")
        except Exception as e:
            logger.error(f"Fatal error in main loop: {str(e)}")
            raise


def main():
    """Main entry point"""
    # Configuration
    CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL_MINUTES", "15"))
    HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"

    # Create checker instance
    checker = CitaChecker(headless=HEADLESS)

    # Run continuous checking
    checker.run_continuous_check(interval_minutes=CHECK_INTERVAL)


if __name__ == "__main__":
    main()
