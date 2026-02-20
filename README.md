> [!NOTE]
> Adjusted for checking "POLICIA-CERTIFICADO DE REGISTRO DE CIUDADANO DE LA U.E." appointments in La Laguna, S.Cruz Tenerife

# Cita Previa Extranjería Checker Bot

A Python bot that automatically monitors the Cita Previa Extranjería website for available appointments for **Toma de Huellas (fingerprinting)** in **Barcelona**. When appointments become available, it sends you an email notification.

## ⚠️ Important Disclaimer

This bot is designed as a **monitoring tool only**. It:
- ✅ Checks for appointment availability
- ✅ Sends you notifications when appointments are found
- ❌ Does NOT automatically book appointments
- ❌ Does NOT bypass CAPTCHAs or security measures
- ❌ Does NOT fill out forms automatically

**You must manually complete the booking** when notified. This approach is ethical and avoids legal issues.

## Features

- Continuous monitoring at configurable intervals
- Automatically checks ALL offices in Barcelona
- Email notifications when appointments are available
- Detailed logging of all checks
- Headless browser mode (runs in background)
- Easy configuration via environment variables
- Safe and legal - no automation of booking process

## Requirements

- Python 3.8 or higher
- Chrome browser installed
- Gmail account (or other SMTP email service)

## Installation

### 1. Clone or download this repository

```bash
cd /Users/zhitinglu/Projects/cita_alert
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Install ChromeDriver

The bot uses Selenium with Chrome. You have two options:

**Option A: Automatic (using webdriver-manager)**
The bot will automatically download the correct ChromeDriver on first run.

**Option B: Manual**
```bash
# On macOS using Homebrew
brew install chromedriver

# Verify installation
chromedriver --version
```

### 4. Configure your settings

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` with your information:
```bash
nano .env
```

**Required settings:**
- `NIE_NUMBER`: Your NIE or passport number
- `FULL_NAME`: Your full name as it appears on documents
- `SENDER_EMAIL`: Your Gmail address
- `SENDER_PASSWORD`: Your Gmail App Password (see below)
- `RECEIVER_EMAIL`: Email where you want to receive notifications

### 5. Set up Gmail App Password

For Gmail users, you need to create an App Password:

1. Go to your [Google Account](https://myaccount.google.com/)
2. Select **Security**
3. Under "Signing in to Google," select **App Passwords**
   - You may need to enable 2-Step Verification first
4. Select **Mail** and **Other (Custom name)**
5. Generate the password
6. Copy the 16-character password to your `.env` file

## How to Run

1. Create and activate a Python virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure your `.env` file with your NIE, name, country code, and email credentials.

4. Run the bot:

```bash
python cita_checker.py
```

## Usage

### Basic Usage

Run the bot:
```bash
python cita_checker.py
```

The bot will:
1. Start checking for appointments every 15 minutes (configurable)
2. Log all activities to both console and `cita_checker.log`
3. Send an email when appointments are found
4. Continue running until you stop it (Ctrl+C)

### Advanced Configuration

Edit `.env` to customize:

```bash
# Check every 10 minutes instead of 15
CHECK_INTERVAL_MINUTES=10

# Run browser in visible mode (useful for debugging)
HEADLESS=false
```

### Running in Background

To keep the bot running even when you close the terminal:

```bash
# Using nohup
nohup python cita_checker.py > output.log 2>&1 &

# Check if it's running
ps aux | grep cita_checker

# Stop it
pkill -f cita_checker.py
```

Or use `screen` or `tmux`:
```bash
# Using screen
screen -S cita_bot
python cita_checker.py
# Press Ctrl+A then D to detach

# Reattach later
screen -r cita_bot
```

## Output Example

```
2025-11-28 14:30:00 - INFO - 🤖 Starting Cita Previa Checker Bot
2025-11-28 14:30:00 - INFO - 📍 Location: Barcelona
2025-11-28 14:30:00 - INFO - 📋 Tramite: Toma de Huellas
2025-11-28 14:30:00 - INFO - ⏱️ Check interval: 15 minutes
============================================================
2025-11-28 14:30:00 - INFO - Check #1 at 2025-11-28 14:30:00
============================================================
2025-11-28 14:30:05 - INFO - WebDriver initialized
2025-11-28 14:30:08 - INFO - Navigated to: https://icp.administracionelectronica.gob.es/icpplus/citar
2025-11-28 14:30:12 - INFO - Selected province: Barcelona
2025-11-28 14:30:15 - INFO - Selected tramite: POLICIA-TOMA DE HUELLAS...
2025-11-28 14:30:20 - INFO - No appointments available
2025-11-28 14:30:21 - INFO - WebDriver closed
2025-11-28 14:30:21 - INFO - Waiting 15 minutes until next check...
```

## Troubleshooting

### ChromeDriver Issues
```bash
# Error: ChromeDriver version mismatch
# Solution: Update Chrome browser and reinstall ChromeDriver
brew upgrade chromedriver
```

### Email Not Sending
- Verify Gmail App Password is correct
- Check that 2-Step Verification is enabled on your Google Account
- Try using a different SMTP server if not using Gmail

### Bot Not Finding Appointments
- The website structure may have changed
- Try running with `HEADLESS=false` to see what's happening
- Check `cita_checker.log` for detailed error messages

### Permission Denied on ChromeDriver
```bash
# On macOS, you may need to allow ChromeDriver
xattr -d com.apple.quarantine /path/to/chromedriver
```

## Legal and Ethical Considerations

This bot is designed to be:
- **Legal**: Only monitors public information
- **Ethical**: Doesn't automate booking or bypass security
- **Respectful**: Uses reasonable check intervals (15+ minutes)
- **Transparent**: Identifies itself with standard user agent

**Best Practices:**
- Don't set check intervals too short (< 5 minutes)
- Don't run multiple instances simultaneously
- Manually complete the booking when notified
- Respect the website's terms of service

## File Structure

```
cita_alert/
├── cita_checker.py      # Main bot script
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
├── .env.example        # Example environment variables
├── .env                # Your actual config (don't commit!)
├── .gitignore          # Git ignore rules
├── README.md           # This file
└── cita_checker.log    # Log file (created on first run)
```

## Contributing

Feel free to improve this bot! Some ideas:
- Support for other provinces
- Support for other tramite types
- Telegram notifications
- Web dashboard
- Docker support

## Disclaimer

This software is provided "as is" without warranty. Use at your own risk. The authors are not responsible for:
- Any issues arising from use of this bot
- Changes to the Cita Previa website
- Missed appointments
- Any consequences of automated checking

Always verify appointment availability manually on the official website before making plans.

## Support

If you encounter issues:
1. Check the troubleshooting section
2. Review `cita_checker.log` for detailed errors
3. Ensure all configuration is correct
4. Try running with `HEADLESS=false` to debug visually

## License

This project is open source and available for personal use. Please use responsibly.

---

**Good luck with your cita!**
