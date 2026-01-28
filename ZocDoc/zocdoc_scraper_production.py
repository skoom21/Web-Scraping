"""
ZocDoc Scraper - Production Version

Production-grade web scraper for ZocDoc doctor appointments with comprehensive
error handling, logging, retry logic, and monitoring capabilities.

Features:
- Structured logging with rotation
- Comprehensive error handling and recovery
- Retry mechanisms with exponential backoff
- Health checks and monitoring
- Graceful shutdown
- Performance metrics
- Environment-based configuration
"""

import os
import sys
import time
import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from logging.handlers import RotatingFileHandler
import signal

from camoufox.sync_api import Camoufox
from bs4 import BeautifulSoup
import pandas as pd


# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Production configuration with environment variable support."""
    
    # Proxy settings
    PROXY_ENABLED = os.getenv('ZOCDOC_PROXY_ENABLED', 'true').lower() == 'true'
    PROXY_SERVER = os.getenv('ZOCDOC_PROXY_SERVER', 'http://68.225.23.120:13884')
    PROXY_USERNAME = os.getenv('ZOCDOC_PROXY_USERNAME', 'rockin12345678')
    PROXY_PASSWORD = os.getenv('ZOCDOC_PROXY_PASSWORD', 'Varun123456789')
    
    # Backup proxy list from environment variable (format: ip:port:username:password, comma-separated)
    _backup_proxies_env = os.getenv('ZOCDOC_BACKUP_PROXIES', '')
    PROXY_BACKUP_LIST = [p.strip() for p in _backup_proxies_env.split(',') if p.strip()] if _backup_proxies_env else []
    
    # Scraping settings
    TARGET_URL = os.getenv('ZOCDOC_URL', 'https://www.zocdoc.com/practice/dentistry-at-its-finest-19571?LocIdent=31976')
    
    # Multiple doctors to scrape
    TARGET_DOCTORS = [
        'Dr. Michael Ayzin, DDS',
        'Dr. Ronald Ayzin, DDS'
    ]
    
    # Retry settings
    MAX_RETRIES = int(os.getenv('ZOCDOC_MAX_RETRIES', '3'))
    RETRY_DELAY = int(os.getenv('ZOCDOC_RETRY_DELAY', '5'))
    
    # Timeout settings (milliseconds)
    PAGE_LOAD_TIMEOUT = int(os.getenv('ZOCDOC_PAGE_TIMEOUT', '60000'))
    ELEMENT_TIMEOUT = int(os.getenv('ZOCDOC_ELEMENT_TIMEOUT', '5000'))
    
    # Browser settings
    HEADLESS = os.getenv('ZOCDOC_HEADLESS', 'false').lower() == 'true'
    HUMANIZE = os.getenv('ZOCDOC_HUMANIZE', 'true').lower() == 'true'
    GEOIP = os.getenv('ZOCDOC_GEOIP', 'true').lower() == 'true'
    
    # Output settings
    OUTPUT_DIR = Path(os.getenv('ZOCDOC_OUTPUT_DIR', './output'))
    LOG_DIR = Path(os.getenv('ZOCDOC_LOG_DIR', './logs'))
    
    # Logging settings
    LOG_LEVEL = os.getenv('ZOCDOC_LOG_LEVEL', 'INFO')
    LOG_MAX_BYTES = int(os.getenv('ZOCDOC_LOG_MAX_BYTES', '10485760'))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv('ZOCDOC_LOG_BACKUP_COUNT', '5'))


# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging() -> logging.Logger:
    """
    Configure production-grade logging with rotation and structured output.
    
    Returns:
        Configured logger instance
    """
    # Create log directory
    Config.LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger('zocdoc_scraper')
    logger.setLevel(getattr(logging, Config.LOG_LEVEL.upper()))
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Console handler with color-coded output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    
    # File handler with rotation
    log_file = Config.LOG_DIR / f'zocdoc_scraper_{datetime.now():%Y%m%d}.log'
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=Config.LOG_MAX_BYTES,
        backupCount=Config.LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    
    # Error file handler for ERROR and CRITICAL only
    error_log_file = Config.LOG_DIR / f'zocdoc_errors_{datetime.now():%Y%m%d}.log'
    error_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=Config.LOG_MAX_BYTES,
        backupCount=Config.LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_format)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    
    return logger


# ============================================================================
# CUSTOM EXCEPTIONS
# ============================================================================

class ZocDocScraperError(Exception):
    """Base exception for ZocDoc scraper."""
    pass


class ProxyConnectionError(ZocDocScraperError):
    """Raised when proxy connection fails."""
    pass


class PageLoadError(ZocDocScraperError):
    """Raised when page fails to load."""
    pass


class DoctorSelectionError(ZocDocScraperError):
    """Raised when doctor cannot be selected."""
    pass


class ModalNotFoundError(ZocDocScraperError):
    """Raised when modal dialog cannot be found."""
    pass


class DataExtractionError(ZocDocScraperError):
    """Raised when data extraction fails."""
    pass


# ============================================================================
# SCRAPER CLASS
# ============================================================================

class ZocDocScraper:
    """Production-grade ZocDoc appointment scraper."""
    
    def __init__(self, logger: logging.Logger):
        """
        Initialize scraper with logger.
        
        Args:
            logger: Configured logger instance
        """
        self.logger = logger
        self.start_time = None
        self.appointments: List[Dict] = []
        self.current_doctor = None  # Track current doctor being processed
        self.metrics = {
            'page_loads': 0,
            'retries': 0,
            'errors': 0,
            'appointments_found': 0
        }
        
        # Ensure output directory exists
        Config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        self.logger.info("=" * 80)
        self.logger.info("ZocDoc Scraper - Production Version")
        self.logger.info("=" * 80)
        self.logger.info(f"Target URL: {Config.TARGET_URL}")
        self.logger.info(f"Target Doctors: {', '.join(Config.TARGET_DOCTORS)}")
        self.logger.info(f"Proxy Enabled: {Config.PROXY_ENABLED}")
        self.logger.info(f"Headless Mode: {Config.HEADLESS}")
        self.logger.info("=" * 80)
    
    def _get_proxy_config(self, use_backup=False, backup_index=0):
        """
        Get proxy configuration if enabled.
        
        Args:
            use_backup: Whether to use backup proxy list
            backup_index: Index of backup proxy to use
        
        Returns:
            Proxy configuration dict or None
        """
        if not Config.PROXY_ENABLED:
            return None
        
        if use_backup and backup_index < len(Config.PROXY_BACKUP_LIST):
            # Parse backup proxy (format: ip:port:username:password)
            proxy_str = Config.PROXY_BACKUP_LIST[backup_index]
            parts = proxy_str.split(':')
            if len(parts) == 4:
                ip, port, username, password = parts
                self.logger.info(f"Using backup proxy {backup_index + 1}/{len(Config.PROXY_BACKUP_LIST)}: {ip}:{port}")
                return {
                    "server": f"http://{ip}:{port}",
                    "username": username,
                    "password": password
                }
        
        # Use primary proxy
        return {
            "server": Config.PROXY_SERVER,
            "username": Config.PROXY_USERNAME,
            "password": Config.PROXY_PASSWORD
        }
    
    def _retry_with_backoff(self, func, *args, max_retries=None, **kwargs):
        """
        Execute function with exponential backoff retry logic.
        
        Args:
            func: Function to execute
            *args: Function arguments
            max_retries: Maximum retry attempts
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Last exception if all retries fail
        """
        max_retries = max_retries or Config.MAX_RETRIES
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                self.metrics['retries'] += 1
                
                if attempt < max_retries - 1:
                    delay = Config.RETRY_DELAY * (2 ** attempt)  # Exponential backoff
                    self.logger.warning(
                        f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}. "
                        f"Retrying in {delay} seconds..."
                    )
                    time.sleep(delay)
                else:
                    self.logger.error(
                        f"All {max_retries} attempts failed. Last error: {str(e)}"
                    )
        
        raise last_exception
    
    def _load_page(self, page, url: str) -> None:
        """
        Load page with retry logic and validation.
        
        Args:
            page: Playwright page object
            url: URL to load
            
        Raises:
            PageLoadError: If page load fails
        """
        try:
            self.logger.info(f"Loading page: {url}")
            page.goto(url, wait_until="networkidle", timeout=Config.PAGE_LOAD_TIMEOUT)
            self.metrics['page_loads'] += 1
            
            # Wait for dynamic content
            time.sleep(10)
            
            page_title = page.title()
            self.logger.info(f"Page loaded successfully: {page_title}")
            
            # Validate page loaded correctly
            if "Dentistry At Its Finest" not in page_title:
                raise PageLoadError(f"Unexpected page title: {page_title}")
            
            # Check for 403 or blocks
            page_html = page.content()
            if "403" in page_html and "restricted" in page_html.lower():
                self.logger.warning("Detected 403 Restricted page, attempting reload...")
                page.reload(wait_until="networkidle", timeout=Config.PAGE_LOAD_TIMEOUT)
                time.sleep(5)
                
                if "403" in page.content() and "restricted" in page.content().lower():
                    raise PageLoadError("Page still restricted after reload")
                
                self.logger.info("Page reloaded successfully")
        
        except Exception as e:
            self.logger.error(f"Page load failed: {str(e)}")
            raise PageLoadError(f"Failed to load page: {str(e)}") from e
    
    def _select_doctor(self, page, doctor_name: str) -> None:
        """
        Select target doctor from dropdown.
        
        Args:
            page: Playwright page object
            doctor_name: Full doctor name to select (e.g., "Dr. Michael Ayzin, DDS")
            
        Raises:
            DoctorSelectionError: If doctor selection fails
        """
        try:
            self.logger.info(f"Searching for provider dropdown to select {doctor_name}...")
            time.sleep(5)
            
            provider_dropdowns = page.locator(
                '.css-nm0j11-control, '
                '.css-eio9xs-control, '
                'div[class*="control"]:has-text("provider"), '
                'div[class*="control"]:has-text("All provider")'
            )
            
            dropdown_count = provider_dropdowns.count()
            self.logger.debug(f"Found {dropdown_count} provider dropdowns")
            
            if dropdown_count == 0:
                self.logger.error("No provider dropdowns found")
                self._save_debug_artifacts(page, "no_dropdown")
                raise DoctorSelectionError("No provider dropdowns found on page")
            
            doctor_selected = False
            
            for i in range(dropdown_count):
                try:
                    dropdown = provider_dropdowns.nth(i)
                    dropdown_text = dropdown.inner_text()
                    self.logger.debug(f"Dropdown {i+1}: {dropdown_text[:80]}")
                    
                    if doctor_name.split(',')[0] in dropdown_text:
                        self.logger.info(f"{doctor_name} already selected")
                        doctor_selected = True
                        break
                    
                    elif 'All provider' in dropdown_text or 'provider availability' in dropdown_text.lower():
                        self.logger.info("Found 'All provider availability' dropdown")
                        dropdown.scroll_into_view_if_needed()
                        time.sleep(1)
                        dropdown.click()
                        time.sleep(3)
                        
                        # Try multiple selection strategies
                        ayzin_option = self._find_doctor_option(page, doctor_name)
                        
                        if ayzin_option and ayzin_option.is_visible(timeout=2000):
                            self.logger.info(f"Clicking {doctor_name} option...")
                            ayzin_option.scroll_into_view_if_needed()
                            time.sleep(1)
                            
                            try:
                                ayzin_option.click(timeout=3000)
                            except:
                                self.logger.warning("Normal click failed, using force click")
                                ayzin_option.click(force=True)
                            
                            self.logger.info(f"Successfully selected {doctor_name}")
                            time.sleep(4)
                            doctor_selected = True
                            break
                        else:
                            self.logger.error(f"Could not find {doctor_name} in options")
                            self._save_debug_artifacts(page, "doctor_option_not_found")
                
                except Exception as e:
                    self.logger.warning(f"Error with dropdown {i+1}: {str(e)}")
                    continue
            
            if not doctor_selected:
                raise DoctorSelectionError(f"Could not select {doctor_name}")
        
        except DoctorSelectionError:
            raise
        except Exception as e:
            self.logger.error(f"Doctor selection failed: {str(e)}")
            raise DoctorSelectionError(f"Failed to select doctor: {str(e)}") from e
    
    def _find_doctor_option(self, page, doctor_name_full):
        """
        Find doctor option using multiple strategies.
        
        Args:
            page: Playwright page object
            doctor_name_full: Full doctor name (e.g., "Dr. Michael Ayzin, DDS")
            
        Returns:
            Doctor option locator or None
        """
        doctor_name = doctor_name_full.split(',')[0]  # "Dr. Michael Ayzin"
        
        # Strategy 1: role="option" filter
        try:
            option = page.locator('[role="option"]').filter(has_text=doctor_name).first
            if option.is_visible(timeout=2000):
                self.logger.debug("Found via role='option' filter")
                return option
        except:
            pass
        
        # Strategy 2: data-test="provider-option"
        try:
            all_opts = page.locator('[data-test="provider-option"]')
            for i in range(all_opts.count()):
                opt = all_opts.nth(i)
                if doctor_name in opt.inner_text():
                    self.logger.debug("Found via data-test='provider-option'")
                    return opt
        except:
            pass
        
        # Strategy 3: div text search
        try:
            option = page.locator(f'div:has-text("{doctor_name_full}")').first
            if option.is_visible(timeout=2000):
                self.logger.debug("Found via div text search")
                return option
        except:
            pass
        
        return None
    
    def _extract_appointments_from_modal(self, page, modal_html: str) -> List[Dict]:
        """
        Extract appointments from modal HTML.
        
        Args:
            page: Playwright page object
            modal_html: Modal HTML content
            
        Returns:
            List of appointment dictionaries
            
        Raises:
            DataExtractionError: If extraction fails
        """
        try:
            soup = BeautifulSoup(modal_html, 'html.parser')
            timeslot_elements = soup.find_all('a', {'data-test': 'availability-modal-timeslot'})
            
            self.logger.info(f"Found {len(timeslot_elements)} appointment timeslots")
            
            if len(timeslot_elements) == 0:
                self.logger.warning("No timeslots found in modal")
                self._save_html_artifact(modal_html, "empty_modal")
                return []
            
            appointments = []
            
            for timeslot in timeslot_elements:
                try:
                    time_text = timeslot.get_text(strip=True)
                    
                    date_wrapper = timeslot.find_parent('div', {'data-test': 'availability-modal-content-date-wrapper'})
                    if date_wrapper:
                        date_title = date_wrapper.find('div', {'data-test': 'availability-modal-content-day-title'})
                        date_text = date_title.get_text(strip=True) if date_title else "Unknown Date"
                    else:
                        date_text = "Unknown Date"
                        self.logger.debug(f"No date wrapper for timeslot: {time_text}")
                    
                    appointment = {
                        'doctor': self.current_doctor,
                        'date': date_text,
                        'time': time_text,
                        'datetime': f"{date_text} {time_text}",
                        'scraped_at': datetime.now().isoformat()
                    }
                    
                    appointments.append(appointment)
                    self.logger.debug(f"Extracted: {date_text} - {time_text}")
                
                except Exception as e:
                    self.logger.warning(f"Failed to extract timeslot: {str(e)}")
                    continue
            
            return appointments
        
        except Exception as e:
            self.logger.error(f"Appointment extraction failed: {str(e)}")
            raise DataExtractionError(f"Failed to extract appointments: {str(e)}") from e
    
    def _process_modal(self, page, button_index: int) -> List[Dict]:
        """
        Process a single modal and extract appointments.
        
        Args:
            page: Playwright page object
            button_index: Index of button to click
            
        Returns:
            List of appointments from this modal
        """
        try:
            self.logger.info(f"Processing modal {button_index + 1}")
            
            buttons = page.locator('span:has-text("View more availability")')
            button = buttons.nth(button_index)
            
            button.scroll_into_view_if_needed()
            time.sleep(1)
            button.click()
            self.logger.debug("Modal opened, waiting for content...")
            
            # Wait for modal to appear first
            time.sleep(2)
            
            # Wait for timeslots to load - increased timeout for slower loads
            self.logger.info("Waiting for appointment timeslots to load...")
            try:
                page.wait_for_selector('[data-test="availability-modal-timeslot"]', timeout=20000)
                time.sleep(3)  # Extra time for all slots to render completely
                self.logger.debug("Timeslots loaded successfully")
            except Exception as e:
                self.logger.warning(f"Timeslots did not appear within timeout: {str(e)}")
                # Wait a bit more before giving up
                time.sleep(2)
            
            # Get modal HTML
            page_html = page.content()
            soup = BeautifulSoup(page_html, 'html.parser')
            
            # Find modal container
            modal_container = soup.find('div', {'data-test': 'availability-modal-view-container'})
            
            if not modal_container:
                self.logger.warning("Modal container not found, trying alternative")
                modal_container = soup.find('div', {'data-test': 'modal-content'})
            
            if not modal_container:
                if 'availability-modal-timeslot' in page_html:
                    self.logger.info("Timeslots found in page HTML, extracting directly")
                    modal_container = soup
                else:
                    raise ModalNotFoundError("Modal container not found in page")
            
            # Extract appointments
            appointments = self._extract_appointments_from_modal(page, str(modal_container))
            
            # Try to load more appointments
            try:
                show_more_btn = page.locator('button:has-text("Show more availability")').first
                if show_more_btn.is_visible(timeout=2000):
                    self.logger.info("Loading more appointments...")
                    show_more_btn.click()
                    time.sleep(5)
                    
                    # Re-extract
                    page_html = page.content()
                    soup = BeautifulSoup(page_html, 'html.parser')
                    modal_container = soup.find('div', {'data-test': 'availability-modal-view-container'})
                    
                    if modal_container:
                        new_appointments = self._extract_appointments_from_modal(page, str(modal_container))
                        
                        # Deduplicate
                        existing = {(apt['date'], apt['time']) for apt in appointments}
                        new_count = 0
                        
                        for apt in new_appointments:
                            if (apt['date'], apt['time']) not in existing:
                                appointments.append(apt)
                                new_count += 1
                        
                        self.logger.info(f"Added {new_count} new appointments after loading more")
            except:
                self.logger.debug("No 'Show more' button or already showing all")
            
            # Close modal
            try:
                close_btn = page.locator('button[aria-label="Close"]').first
                if close_btn.is_visible(timeout=2000):
                    close_btn.click()
                else:
                    page.keyboard.press('Escape')
                time.sleep(1)
            except:
                page.keyboard.press('Escape')
                time.sleep(1)
            
            return appointments
        
        except Exception as e:
            self.logger.error(f"Modal processing failed: {str(e)}")
            self.metrics['errors'] += 1
            return []
    
    def _save_debug_artifacts(self, page, prefix: str) -> None:
        """
        Save debug artifacts (screenshots and HTML).
        
        Args:
            page: Playwright page object
            prefix: Filename prefix
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            screenshot_path = Config.OUTPUT_DIR / f"{prefix}_{timestamp}.png"
            page.screenshot(path=str(screenshot_path), full_page=True)
            self.logger.info(f"Saved screenshot: {screenshot_path}")
            
            html_path = Config.OUTPUT_DIR / f"{prefix}_{timestamp}.html"
            html_path.write_text(page.content(), encoding='utf-8')
            self.logger.info(f"Saved HTML: {html_path}")
        
        except Exception as e:
            self.logger.warning(f"Failed to save debug artifacts: {str(e)}")
    
    def _save_html_artifact(self, html_content: str, prefix: str) -> None:
        """
        Save HTML content to file.
        
        Args:
            html_content: HTML content to save
            prefix: Filename prefix
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            html_path = Config.OUTPUT_DIR / f"{prefix}_{timestamp}.html"
            html_path.write_text(html_content, encoding='utf-8')
            self.logger.debug(f"Saved HTML artifact: {html_path}")
        except Exception as e:
            self.logger.warning(f"Failed to save HTML artifact: {str(e)}")
    
    def _save_results(self) -> Tuple[Path, Path]:
        """
        Save scraping results to CSV files.
        
        Returns:
            Tuple of (raw_csv_path, cleaned_csv_path)
            
        Raises:
            DataExtractionError: If saving fails
        """
        try:
            if not self.appointments:
                raise DataExtractionError("No appointments to save")
            
            df = pd.DataFrame(self.appointments)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Save raw data
            raw_path = Config.OUTPUT_DIR / f'appointments_raw_{timestamp}.csv'
            df.to_csv(raw_path, index=False)
            self.logger.info(f"Saved raw data: {raw_path} ({len(df)} appointments)")
            
            # Save cleaned data
            df_clean = df.drop_duplicates(subset=['date', 'time']).reset_index(drop=True)
            clean_path = Config.OUTPUT_DIR / f'appointments_cleaned_{timestamp}.csv'
            df_clean.to_csv(clean_path, index=False)
            self.logger.info(f"Saved cleaned data: {clean_path} ({len(df_clean)} unique appointments)")
            
            return raw_path, clean_path
        
        except Exception as e:
            self.logger.error(f"Failed to save results: {str(e)}")
            raise DataExtractionError(f"Failed to save results: {str(e)}") from e
    
    def _print_summary(self, duration: float) -> None:
        """
        Print execution summary.
        
        Args:
            duration: Total execution time in seconds
        """
        self.logger.info("=" * 80)
        self.logger.info("EXECUTION SUMMARY")
        self.logger.info("=" * 80)
        self.logger.info(f"Execution Time: {duration:.2f} seconds")
        self.logger.info(f"Appointments Found: {self.metrics['appointments_found']}")
        self.logger.info(f"Page Loads: {self.metrics['page_loads']}")
        self.logger.info(f"Retries: {self.metrics['retries']}")
        self.logger.info(f"Errors: {self.metrics['errors']}")
        self.logger.info("=" * 80)
    
    def run(self) -> Dict:
        """
        Execute scraping workflow with proxy rotation on failure.
        
        Returns:
            Dictionary with execution results
            
        Raises:
            ZocDocScraperError: If scraping fails with all proxies
        """
        self.start_time = time.time()
        last_error = None
        
        # Try primary proxy first, then backup proxies
        max_proxy_attempts = 1 + len(Config.PROXY_BACKUP_LIST) if Config.PROXY_ENABLED else 1
        
        for proxy_attempt in range(max_proxy_attempts):
            try:
                # Get proxy config (primary or backup)
                use_backup = proxy_attempt > 0
                backup_index = proxy_attempt - 1 if use_backup else 0
                proxy = self._get_proxy_config(use_backup=use_backup, backup_index=backup_index)
                
                if proxy_attempt == 0:
                    self.logger.info("Launching browser with primary proxy...")
                
                with Camoufox(
                    headless=Config.HEADLESS,
                    proxy=proxy,
                    humanize=Config.HUMANIZE,
                    geoip=False  # Disabled - requires: pip install camoufox[geoip]
                ) as browser:
                    page = browser.new_page()
                    
                    try:
                        # Process each doctor sequentially
                        for doctor_index, doctor_name in enumerate(Config.TARGET_DOCTORS):
                            self.current_doctor = doctor_name
                            self.logger.info(f"\n{'='*80}")
                            self.logger.info(f"Processing doctor {doctor_index + 1}/{len(Config.TARGET_DOCTORS)}: {doctor_name}")
                            self.logger.info(f"{'='*80}")
                            
                            # Load page with retry
                            self._retry_with_backoff(self._load_page, page, Config.TARGET_URL)
                            
                            # Select doctor with retry
                            self._retry_with_backoff(self._select_doctor, page, doctor_name)
                            
                            self.logger.info("Waiting for page to update after doctor selection...")
                            time.sleep(5)  # Increased wait time for page to fully update
                            
                            # Find modal buttons
                            view_more_buttons = page.locator('span:has-text("View more availability")')
                            button_count = view_more_buttons.count()
                            
                            if button_count == 0:
                                self.logger.warning(f"No 'View more availability' buttons found for {doctor_name}")
                                self._save_debug_artifacts(page, f"no_buttons_{doctor_name.replace(' ', '_').replace(',', '')}")
                                # Continue to next doctor instead of failing completely
                                continue
                            
                            self.logger.info(f"Found {button_count} 'View more availability' buttons for {doctor_name}")
                            
                            # Process each modal
                            for idx in range(button_count):
                                try:
                                    appointments = self._process_modal(page, idx)
                                    self.appointments.extend(appointments)
                                except Exception as e:
                                    self.logger.error(f"Failed to process modal {idx + 1} for {doctor_name}: {str(e)}")
                                    continue
                            
                            self.logger.info(f"Collected {len([a for a in self.appointments if a['doctor'] == doctor_name])} appointments for {doctor_name}")
                            
                            # Navigate to URL again for next doctor (except for the last one)
                            # Using goto instead of reload is more reliable
                            if doctor_index < len(Config.TARGET_DOCTORS) - 1:
                                self.logger.info(f"Loading page for next doctor...")
                                time.sleep(3)  # Give page time to settle before navigating
                        
                        self.metrics['appointments_found'] = len(self.appointments)
                        
                        if not self.appointments:
                            raise DataExtractionError("No appointments collected for any doctor")
                        
                        # Save results
                        raw_path, clean_path = self._save_results()
                        
                        duration = time.time() - self.start_time
                        self._print_summary(duration)
                        
                        return {
                            'success': True,
                            'appointments_count': len(self.appointments),
                            'unique_count': len(set((apt['date'], apt['time']) for apt in self.appointments)),
                            'raw_file': str(raw_path),
                            'cleaned_file': str(clean_path),
                            'duration': duration,
                            'metrics': self.metrics,
                            'proxy_used': f"backup_{backup_index + 1}" if use_backup else "primary"
                        }
                    
                    except (PageLoadError, ProxyConnectionError) as e:
                        # Connection errors - try next proxy
                        last_error = e
                        self.logger.warning(f"Proxy attempt {proxy_attempt + 1} failed: {str(e)}")
                        if proxy_attempt < max_proxy_attempts - 1:
                            self.logger.info("Trying next proxy...")
                            continue
                        else:
                            self.logger.error(f"All {max_proxy_attempts} proxy attempts failed")
                            raise
            
                    except Exception as e:
                        # Other errors - save debug and fail immediately
                        self.logger.error(f"Scraping error: {str(e)}")
                        try:
                            self._save_debug_artifacts(page, "error")
                        except:
                            pass
                        raise

            except Exception as final_error:
                duration = time.time() - self.start_time if self.start_time else 0
                self.logger.error(f"Fatal error: {str(final_error)}")
                self.logger.error(traceback.format_exc())
                
                return {
                    'success': False,
                    'error': str(final_error),
                    'error_type': type(final_error).__name__,
                    'duration': duration,
                    'metrics': self.metrics
                }
  



# ============================================================================
# MAIN EXECUTION
# ============================================================================

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger = logging.getLogger('zocdoc_scraper')
    logger.warning(f"Received signal {signum}, shutting down gracefully...")
    sys.exit(0)


def main():
    """Main entry point with comprehensive error handling."""
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger = setup_logging()
    
    try:
        scraper = ZocDocScraper(logger)
        result = scraper.run()
        
        if result['success']:
            logger.info("✅ Scraping completed successfully")
            sys.exit(0)
        else:
            logger.error(f"❌ Scraping failed: {result.get('error')}")
            sys.exit(1)
    
    except KeyboardInterrupt:
        logger.warning("Interrupted by user")
        sys.exit(130)
    
    except Exception as e:
        logger.critical(f"Unhandled exception: {str(e)}")
        logger.critical(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
