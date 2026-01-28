"""
Unit tests for HTML parsing functionality.
Tests BeautifulSoup extraction logic with various HTML structures.
"""

import pytest
from bs4 import BeautifulSoup
from datetime import datetime


class TestTimeslotExtraction:
    """Test appointment timeslot extraction from HTML."""
    
    def test_extract_valid_timeslots(self):
        """Test extraction of valid appointment timeslots."""
        html = '''
        <div data-test="availability-modal-view-container">
            <div data-test="availability-modal-content-date-wrapper">
                <div data-test="availability-modal-content-day-title">Mon, Jan 26</div>
                <a data-test="availability-modal-timeslot">9:30 am</a>
                <a data-test="availability-modal-timeslot">10:00 am</a>
                <a data-test="availability-modal-timeslot">11:30 am</a>
            </div>
        </div>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        timeslots = soup.find_all('a', {'data-test': 'availability-modal-timeslot'})
        
        assert len(timeslots) == 3
        assert timeslots[0].get_text(strip=True) == '9:30 am'
        assert timeslots[1].get_text(strip=True) == '10:00 am'
        assert timeslots[2].get_text(strip=True) == '11:30 am'
    
    def test_extract_empty_timeslots(self):
        """Test extraction when no timeslots are present."""
        html = '''
        <div data-test="availability-modal-view-container">
            <div data-test="availability-modal-content-date-wrapper">
                <div data-test="availability-modal-content-day-title">Mon, Jan 26</div>
            </div>
        </div>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        timeslots = soup.find_all('a', {'data-test': 'availability-modal-timeslot'})
        
        assert len(timeslots) == 0
    
    def test_extract_multiple_dates(self):
        """Test extraction across multiple date wrappers."""
        html = '''
        <div data-test="availability-modal-view-container">
            <div data-test="availability-modal-content-date-wrapper">
                <div data-test="availability-modal-content-day-title">Mon, Jan 26</div>
                <a data-test="availability-modal-timeslot">9:30 am</a>
                <a data-test="availability-modal-timeslot">10:00 am</a>
            </div>
            <div data-test="availability-modal-content-date-wrapper">
                <div data-test="availability-modal-content-day-title">Tue, Jan 27</div>
                <a data-test="availability-modal-timeslot">2:00 pm</a>
                <a data-test="availability-modal-timeslot">3:30 pm</a>
            </div>
        </div>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        date_wrappers = soup.find_all('div', {'data-test': 'availability-modal-content-date-wrapper'})
        
        assert len(date_wrappers) == 2
        
        # Check first date
        first_date = date_wrappers[0].find('div', {'data-test': 'availability-modal-content-day-title'})
        assert first_date.get_text(strip=True) == 'Mon, Jan 26'
        first_timeslots = date_wrappers[0].find_all('a', {'data-test': 'availability-modal-timeslot'})
        assert len(first_timeslots) == 2
        
        # Check second date
        second_date = date_wrappers[1].find('div', {'data-test': 'availability-modal-content-day-title'})
        assert second_date.get_text(strip=True) == 'Tue, Jan 27'
        second_timeslots = date_wrappers[1].find_all('a', {'data-test': 'availability-modal-timeslot'})
        assert len(second_timeslots) == 2
    
    def test_extract_with_malformed_html(self):
        """Test extraction with missing required elements."""
        html = '''
        <div data-test="availability-modal-view-container">
            <a data-test="availability-modal-timeslot">9:30 am</a>
        </div>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        timeslots = soup.find_all('a', {'data-test': 'availability-modal-timeslot'})
        
        # Timeslots should still be found
        assert len(timeslots) == 1
        
        # But date wrapper should be missing
        date_wrapper = timeslots[0].find_parent('div', {'data-test': 'availability-modal-content-date-wrapper'})
        assert date_wrapper is None
    
    def test_extract_with_extra_whitespace(self):
        """Test extraction handles extra whitespace correctly."""
        html = '''
        <div data-test="availability-modal-view-container">
            <div data-test="availability-modal-content-date-wrapper">
                <div data-test="availability-modal-content-day-title">
                    
                    Mon, Jan 26
                    
                </div>
                <a data-test="availability-modal-timeslot">
                    9:30 am
                </a>
            </div>
        </div>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        
        date_title = soup.find('div', {'data-test': 'availability-modal-content-day-title'})
        assert date_title.get_text(strip=True) == 'Mon, Jan 26'
        
        timeslot = soup.find('a', {'data-test': 'availability-modal-timeslot'})
        assert timeslot.get_text(strip=True) == '9:30 am'
    
    def test_modal_container_detection(self):
        """Test modal container detection with different selectors."""
        html_with_availability = '''
        <div data-test="availability-modal-view-container">
            <a data-test="availability-modal-timeslot">9:30 am</a>
        </div>
        '''
        soup = BeautifulSoup(html_with_availability, 'html.parser')
        container = soup.find('div', {'data-test': 'availability-modal-view-container'})
        assert container is not None
        
        html_with_modal_content = '''
        <div data-test="modal-content">
            <div data-test="availability-modal-view-container">
                <a data-test="availability-modal-timeslot">9:30 am</a>
            </div>
        </div>
        '''
        soup = BeautifulSoup(html_with_modal_content, 'html.parser')
        container = soup.find('div', {'data-test': 'modal-content'})
        assert container is not None
    
    def test_timeslot_without_href(self):
        """Test timeslots that might not have href attributes."""
        html = '''
        <div data-test="availability-modal-view-container">
            <a data-test="availability-modal-timeslot">9:30 am</a>
            <a data-test="availability-modal-timeslot" href="/book?time=1000">10:00 am</a>
        </div>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        timeslots = soup.find_all('a', {'data-test': 'availability-modal-timeslot'})
        
        assert len(timeslots) == 2
        assert timeslots[0].get_text(strip=True) == '9:30 am'
        assert timeslots[0].get('href') is None
        assert timeslots[1].get_text(strip=True) == '10:00 am'
        assert timeslots[1].get('href') == '/book?time=1000'


class TestDateParsing:
    """Test date parsing and formatting."""
    
    def test_parse_standard_date_format(self):
        """Test parsing standard ZocDoc date format."""
        date_strings = [
            "Mon, Jan 26",
            "Tue, Feb 3",
            "Wed, Dec 31",
            "Thu, Mar 5",
            "Fri, Apr 15",
            "Sat, May 20",
            "Sun, Jun 1"
        ]
        
        for date_str in date_strings:
            assert len(date_str.split(',')) == 2
            day, date = date_str.split(',')
            assert day.strip() in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            assert len(date.strip().split()) == 2  # Month and day
    
    def test_parse_time_format(self):
        """Test parsing time format variations."""
        time_strings = [
            "9:30 am",
            "10:00 am",
            "11:30 am",
            "12:00 pm",
            "1:00 pm",
            "2:30 pm",
            "4:45 pm"
        ]
        
        for time_str in time_strings:
            parts = time_str.split()
            assert len(parts) == 2
            time_part, period = parts
            assert period in ['am', 'pm']
            assert ':' in time_part
            hour, minute = time_part.split(':')
            assert 1 <= int(hour) <= 12
            assert 0 <= int(minute) <= 59


class TestAppointmentDataStructure:
    """Test appointment data structure and validation."""
    
    def test_valid_appointment_structure(self):
        """Test valid appointment data structure."""
        appointment = {
            'doctor': 'Dr. Michael Ayzin, DDS',
            'date': 'Mon, Jan 26',
            'time': '9:30 am',
            'datetime': 'Mon, Jan 26 9:30 am'
        }
        
        assert 'doctor' in appointment
        assert 'date' in appointment
        assert 'time' in appointment
        assert 'datetime' in appointment
        assert isinstance(appointment['doctor'], str)
        assert isinstance(appointment['date'], str)
        assert isinstance(appointment['time'], str)
        assert isinstance(appointment['datetime'], str)
    
    def test_appointment_datetime_concatenation(self):
        """Test datetime field is correctly concatenated."""
        appointments = [
            {'date': 'Mon, Jan 26', 'time': '9:30 am'},
            {'date': 'Tue, Feb 3', 'time': '2:00 pm'},
            {'date': 'Wed, Mar 5', 'time': '11:00 am'}
        ]
        
        for apt in appointments:
            expected_datetime = f"{apt['date']} {apt['time']}"
            apt['datetime'] = expected_datetime
            assert apt['datetime'] == expected_datetime
            assert apt['date'] in apt['datetime']
            assert apt['time'] in apt['datetime']
    
    def test_duplicate_detection(self):
        """Test detection of duplicate appointments."""
        appointments = [
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Mon, Jan 26', 'time': '9:30 am'},
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Mon, Jan 26', 'time': '10:00 am'},
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Mon, Jan 26', 'time': '9:30 am'},  # Duplicate
        ]
        
        # Create set of unique (date, time) tuples
        unique_times = {(apt['date'], apt['time']) for apt in appointments}
        assert len(unique_times) == 2  # Should have only 2 unique
        
    def test_empty_appointment_list(self):
        """Test handling of empty appointment list."""
        appointments = []
        assert len(appointments) == 0
        assert isinstance(appointments, list)


class TestHTMLStructureVariations:
    """Test handling of various HTML structure variations."""
    
    def test_nested_modal_structure(self):
        """Test deeply nested modal structure."""
        html = '''
        <div role="dialog">
            <div data-test="modal-content">
                <div data-test="availability-modal-view-container">
                    <div class="outer-wrapper">
                        <div class="inner-wrapper">
                            <div data-test="availability-modal-content-date-wrapper">
                                <div data-test="availability-modal-content-day-title">Mon, Jan 26</div>
                                <a data-test="availability-modal-timeslot">9:30 am</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        
        # Should find modal content regardless of nesting
        modal_content = soup.find('div', {'data-test': 'modal-content'})
        assert modal_content is not None
        
        # Should find availability container
        availability_container = soup.find('div', {'data-test': 'availability-modal-view-container'})
        assert availability_container is not None
        
        # Should find timeslots
        timeslots = soup.find_all('a', {'data-test': 'availability-modal-timeslot'})
        assert len(timeslots) == 1
    
    def test_missing_modal_container(self):
        """Test handling when modal container is missing."""
        html = '''
        <div role="dialog">
            <a data-test="availability-modal-timeslot">9:30 am</a>
        </div>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        
        container = soup.find('div', {'data-test': 'availability-modal-view-container'})
        assert container is None
        
        # But timeslots should still be found
        timeslots = soup.find_all('a', {'data-test': 'availability-modal-timeslot'})
        assert len(timeslots) == 1
    
    def test_multiple_modals_on_page(self):
        """Test handling when multiple modals exist on page."""
        html = '''
        <div role="dialog" id="modal1">
            <div data-test="modal-content">
                <p>Different modal</p>
            </div>
        </div>
        <div role="dialog" id="modal2">
            <div data-test="availability-modal-view-container">
                <a data-test="availability-modal-timeslot">9:30 am</a>
            </div>
        </div>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        
        # Should find multiple dialogs
        dialogs = soup.find_all('div', {'role': 'dialog'})
        assert len(dialogs) == 2
        
        # But only one availability container
        availability_container = soup.find('div', {'data-test': 'availability-modal-view-container'})
        assert availability_container is not None
        
        # Should find timeslots only in the correct modal
        timeslots = soup.find_all('a', {'data-test': 'availability-modal-timeslot'})
        assert len(timeslots) == 1
    
    def test_timeslots_in_page_html(self):
        """Test checking if timeslots exist in page HTML."""
        html_with_timeslots = '''
        <html>
            <body>
                <div data-test="availability-modal-view-container">
                    <a data-test="availability-modal-timeslot">9:30 am</a>
                </div>
            </body>
        </html>
        '''
        assert 'availability-modal-timeslot' in html_with_timeslots
        
        html_without_timeslots = '''
        <html>
            <body>
                <div class="no-appointments">No availability</div>
            </body>
        </html>
        '''
        assert 'availability-modal-timeslot' not in html_without_timeslots


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_html(self):
        """Test handling of empty HTML."""
        html = ''
        soup = BeautifulSoup(html, 'html.parser')
        timeslots = soup.find_all('a', {'data-test': 'availability-modal-timeslot'})
        assert len(timeslots) == 0
    
    def test_invalid_html(self):
        """Test handling of malformed HTML."""
        html = '<div><a data-test="availability-modal-timeslot">9:30 am'  # Missing closing tags
        soup = BeautifulSoup(html, 'html.parser')
        
        # BeautifulSoup should handle gracefully
        timeslots = soup.find_all('a', {'data-test': 'availability-modal-timeslot'})
        assert len(timeslots) == 1
        assert timeslots[0].get_text(strip=True) == '9:30 am'
    
    def test_special_characters_in_text(self):
        """Test handling of special characters."""
        html = '''
        <div data-test="availability-modal-view-container">
            <div data-test="availability-modal-content-day-title">Mon, Jan 26 – Special</div>
            <a data-test="availability-modal-timeslot">9:30 am & more</a>
        </div>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        
        date_title = soup.find('div', {'data-test': 'availability-modal-content-day-title'})
        assert '–' in date_title.get_text(strip=True)
        
        timeslot = soup.find('a', {'data-test': 'availability-modal-timeslot'})
        assert '&' in timeslot.get_text(strip=True)
    
    def test_unicode_characters(self):
        """Test handling of unicode characters."""
        html = '''
        <div data-test="availability-modal-view-container">
            <div data-test="availability-modal-content-day-title">Mon, Jan 26 ✓</div>
            <a data-test="availability-modal-timeslot">9:30 am 🕐</a>
        </div>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        
        date_title = soup.find('div', {'data-test': 'availability-modal-content-day-title'})
        assert '✓' in date_title.get_text(strip=True)
        
        timeslot = soup.find('a', {'data-test': 'availability-modal-timeslot'})
        assert '🕐' in timeslot.get_text(strip=True)
    
    def test_very_large_html(self):
        """Test handling of large HTML with many timeslots."""
        # Generate HTML with 100 timeslots
        timeslot_html = '\n'.join([
            f'<a data-test="availability-modal-timeslot">{i}:00 am</a>'
            for i in range(1, 101)
        ])
        html = f'''
        <div data-test="availability-modal-view-container">
            <div data-test="availability-modal-content-date-wrapper">
                <div data-test="availability-modal-content-day-title">Mon, Jan 26</div>
                {timeslot_html}
            </div>
        </div>
        '''
        
        soup = BeautifulSoup(html, 'html.parser')
        timeslots = soup.find_all('a', {'data-test': 'availability-modal-timeslot'})
        assert len(timeslots) == 100
    
    def test_case_sensitivity_in_attributes(self):
        """Test that attribute matching is case-sensitive."""
        html = '''
        <div data-test="availability-modal-view-container">
            <a data-test="AVAILABILITY-MODAL-TIMESLOT">9:30 am</a>
            <a data-test="availability-modal-timeslot">10:00 am</a>
        </div>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        
        # Should only find exact match (case-sensitive)
        timeslots = soup.find_all('a', {'data-test': 'availability-modal-timeslot'})
        assert len(timeslots) == 1
        assert timeslots[0].get_text(strip=True) == '10:00 am'
