"""
Configuration settings for Cita Previa Checker Bot
You can modify these values or use environment variables
"""

# Check interval (in minutes)
CHECK_INTERVAL_MINUTES = 15  # Check every 15 minutes

# Browser settings
HEADLESS_MODE = True  # Set to False to see the browser in action

# Cita Previa Details
PROVINCIA = "Barcelona"
TRAMITE_TYPE = "TOMA DE HUELLAS"

# Email notification settings (configure in .env file)
# SENDER_EMAIL = your email
# SENDER_PASSWORD = your app password (for Gmail, use App Password, not regular password)
# RECEIVER_EMAIL = email to receive notifications
# SMTP_SERVER = smtp.gmail.com (for Gmail)
# SMTP_PORT = 587

# Personal information (required by the form)
# NIE_NUMBER = your NIE or passport number
# FULL_NAME = your full name as it appears on documents

# Logging
LOG_FILE = "cita_checker.log"

# Advanced settings
TIMEOUT_SECONDS = 15  # Timeout for page loads
RETRY_ON_ERROR = True
MAX_RETRIES = 3
