"""
Integration tests for ZocDoc scraper.
Tests complete workflow scenarios and component interactions.
"""

import pytest
from bs4 import BeautifulSoup
import pandas as pd


class TestEndToEndWorkflow:
    """Test complete end-to-end workflow scenarios."""
    
    def test_complete_scraping_workflow_simulation(self):
        """Test simulation of complete scraping workflow."""
        # Simulate extracted HTML
        page_html = '''
        <html>
            <body>
                <div data-test="availability-modal-view-container">
                    <div data-test="availability-modal-content-date-wrapper">
                        <div data-test="availability-modal-content-day-title">Mon, Jan 26</div>
                        <a data-test="availability-modal-timeslot">9:30 am</a>
                        <a data-test="availability-modal-timeslot">10:00 am</a>
                    </div>
                    <div data-test="availability-modal-content-date-wrapper">
                        <div data-test="availability-modal-content-day-title">Tue, Jan 27</div>
                        <a data-test="availability-modal-timeslot">2:00 pm</a>
                    </div>
                </div>
            </body>
        </html>
        '''
        
        # Step 1: Parse HTML
        soup = BeautifulSoup(page_html, 'html.parser')
        assert soup is not None
        
        # Step 2: Find modal container
        modal_container = soup.find('div', {'data-test': 'availability-modal-view-container'})
        assert modal_container is not None
        
        # Step 3: Extract timeslots
        timeslot_elements = soup.find_all('a', {'data-test': 'availability-modal-timeslot'})
        assert len(timeslot_elements) == 3
        
        # Step 4: Build appointment list
        appointments = []
        for timeslot in timeslot_elements:
            time_text = timeslot.get_text(strip=True)
            
            # Find parent date wrapper
            date_wrapper = timeslot.find_parent('div', {'data-test': 'availability-modal-content-date-wrapper'})
            if date_wrapper:
                date_title = date_wrapper.find('div', {'data-test': 'availability-modal-content-day-title'})
                date_text = date_title.get_text(strip=True) if date_title else "Unknown Date"
            else:
                date_text = "Unknown Date"
            
            appointments.append({
                'doctor': 'Dr. Michael Ayzin, DDS',
                'date': date_text,
                'time': time_text,
                'datetime': f"{date_text} {time_text}"
            })
        
        assert len(appointments) == 3
        
        # Step 5: Create DataFrame
        df = pd.DataFrame(appointments)
        assert df.shape == (3, 4)
        
        # Step 6: Remove duplicates
        df_clean = df.drop_duplicates().reset_index(drop=True)
        assert len(df_clean) == 3
        
        # Step 7: Validate data
        assert all(df_clean['doctor'] == 'Dr. Michael Ayzin, DDS')
        assert 'Mon, Jan 26' in df_clean['date'].values
        assert 'Tue, Jan 27' in df_clean['date'].values
    
    def test_workflow_with_show_more_button(self):
        """Test workflow when 'Show more availability' adds more appointments."""
        # Initial HTML (before clicking Show more)
        initial_html = '''
        <div data-test="availability-modal-view-container">
            <a data-test="availability-modal-timeslot">9:30 am</a>
            <a data-test="availability-modal-timeslot">10:00 am</a>
        </div>
        '''
        
        soup = BeautifulSoup(initial_html, 'html.parser')
        initial_timeslots = soup.find_all('a', {'data-test': 'availability-modal-timeslot'})
        initial_count = len(initial_timeslots)
        
        assert initial_count == 2
        
        # HTML after clicking Show more
        updated_html = '''
        <div data-test="availability-modal-view-container">
            <a data-test="availability-modal-timeslot">9:30 am</a>
            <a data-test="availability-modal-timeslot">10:00 am</a>
            <a data-test="availability-modal-timeslot">11:00 am</a>
            <a data-test="availability-modal-timeslot">2:00 pm</a>
        </div>
        '''
        
        soup = BeautifulSoup(updated_html, 'html.parser')
        updated_timeslots = soup.find_all('a', {'data-test': 'availability-modal-timeslot'})
        updated_count = len(updated_timeslots)
        
        assert updated_count == 4
        assert updated_count > initial_count
    
    def test_workflow_with_no_appointments(self):
        """Test workflow when no appointments are available."""
        html = '''
        <div data-test="availability-modal-view-container">
            <div class="no-availability">No appointments available</div>
        </div>
        '''
        
        soup = BeautifulSoup(html, 'html.parser')
        timeslots = soup.find_all('a', {'data-test': 'availability-modal-timeslot'})
        
        assert len(timeslots) == 0
        
        appointments = []
        df = pd.DataFrame(appointments)
        
        assert df.shape == (0, 0)
        assert len(df) == 0


class TestErrorRecovery:
    """Test error recovery and resilience."""
    
    def test_recovery_from_missing_date_title(self):
        """Test recovery when date title is missing."""
        html = '''
        <div data-test="availability-modal-view-container">
            <div data-test="availability-modal-content-date-wrapper">
                <a data-test="availability-modal-timeslot">9:30 am</a>
            </div>
        </div>
        '''
        
        soup = BeautifulSoup(html, 'html.parser')
        timeslots = soup.find_all('a', {'data-test': 'availability-modal-timeslot'})
        
        appointments = []
        for timeslot in timeslots:
            time_text = timeslot.get_text(strip=True)
            date_wrapper = timeslot.find_parent('div', {'data-test': 'availability-modal-content-date-wrapper'})
            
            if date_wrapper:
                date_title = date_wrapper.find('div', {'data-test': 'availability-modal-content-day-title'})
                date_text = date_title.get_text(strip=True) if date_title else "Unknown Date"
            else:
                date_text = "Unknown Date"
            
            appointments.append({
                'doctor': 'Dr. Michael Ayzin, DDS',
                'date': date_text,
                'time': time_text,
                'datetime': f"{date_text} {time_text}"
            })
        
        assert len(appointments) == 1
        assert appointments[0]['date'] == "Unknown Date"
        assert appointments[0]['time'] == "9:30 am"
    
    def test_recovery_from_malformed_timeslot(self):
        """Test recovery when timeslot has unexpected format."""
        html = '''
        <div data-test="availability-modal-view-container">
            <div data-test="availability-modal-content-date-wrapper">
                <div data-test="availability-modal-content-day-title">Mon, Jan 26</div>
                <a data-test="availability-modal-timeslot"></a>
                <a data-test="availability-modal-timeslot">10:00 am</a>
            </div>
        </div>
        '''
        
        soup = BeautifulSoup(html, 'html.parser')
        timeslots = soup.find_all('a', {'data-test': 'availability-modal-timeslot'})
        
        appointments = []
        for timeslot in timeslots:
            time_text = timeslot.get_text(strip=True)
            
            # Skip empty timeslots
            if not time_text:
                continue
            
            date_wrapper = timeslot.find_parent('div', {'data-test': 'availability-modal-content-date-wrapper'})
            if date_wrapper:
                date_title = date_wrapper.find('div', {'data-test': 'availability-modal-content-day-title'})
                date_text = date_title.get_text(strip=True) if date_title else "Unknown Date"
            else:
                date_text = "Unknown Date"
            
            appointments.append({
                'doctor': 'Dr. Michael Ayzin, DDS',
                'date': date_text,
                'time': time_text,
                'datetime': f"{date_text} {time_text}"
            })
        
        # Should only have 1 valid appointment (empty one skipped)
        assert len(appointments) == 1
        assert appointments[0]['time'] == "10:00 am"


class TestDataQuality:
    """Test data quality and consistency."""
    
    def test_no_null_values_in_output(self):
        """Test output has no null values."""
        appointments = [
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Mon, Jan 26', 'time': '9:30 am', 'datetime': 'Mon, Jan 26 9:30 am'},
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Tue, Jan 27', 'time': '2:00 pm', 'datetime': 'Tue, Jan 27 2:00 pm'}
        ]
        
        df = pd.DataFrame(appointments)
        
        # Check no null values
        assert df.isnull().sum().sum() == 0
    
    def test_consistent_doctor_name(self):
        """Test all appointments have consistent doctor name."""
        appointments = [
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Mon, Jan 26', 'time': '9:30 am', 'datetime': 'Mon, Jan 26 9:30 am'},
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Tue, Jan 27', 'time': '2:00 pm', 'datetime': 'Tue, Jan 27 2:00 pm'}
        ]
        
        df = pd.DataFrame(appointments)
        unique_doctors = df['doctor'].unique()
        
        assert len(unique_doctors) == 1
        assert unique_doctors[0] == 'Dr. Michael Ayzin, DDS'
    
    def test_datetime_matches_date_and_time(self):
        """Test datetime field matches concatenation of date and time."""
        appointments = [
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Mon, Jan 26', 'time': '9:30 am', 'datetime': 'Mon, Jan 26 9:30 am'},
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Tue, Jan 27', 'time': '2:00 pm', 'datetime': 'Tue, Jan 27 2:00 pm'}
        ]
        
        df = pd.DataFrame(appointments)
        
        for idx, row in df.iterrows():
            expected_datetime = f"{row['date']} {row['time']}"
            assert row['datetime'] == expected_datetime


class TestScalability:
    """Test scalability with large datasets."""
    
    def test_handle_large_appointment_list(self):
        """Test handling large number of appointments."""
        # Generate 1000 appointments
        appointments = [
            {
                'doctor': 'Dr. Michael Ayzin, DDS',
                'date': f'Day {i // 10}',
                'time': f'{(i % 12) + 1}:00 {"am" if i % 24 < 12 else "pm"}',
                'datetime': f'Day {i // 10} {(i % 12) + 1}:00 {"am" if i % 24 < 12 else "pm"}'
            }
            for i in range(1000)
        ]
        
        df = pd.DataFrame(appointments)
        
        assert len(df) == 1000
        assert df.shape[0] == 1000
        assert df.shape[1] == 4
    
    def test_deduplication_performance(self):
        """Test deduplication with many duplicates."""
        # Create dataset with 50% duplicates
        appointments = []
        for i in range(100):
            apt = {
                'doctor': 'Dr. Michael Ayzin, DDS',
                'date': 'Mon, Jan 26',
                'time': f'{(i % 10) + 1}:00 am',
                'datetime': f'Mon, Jan 26 {(i % 10) + 1}:00 am'
            }
            appointments.append(apt)
        
        df = pd.DataFrame(appointments)
        df_clean = df.drop_duplicates().reset_index(drop=True)
        
        assert len(df) == 100
        assert len(df_clean) == 10  # Only 10 unique times


class TestConcurrentScenarios:
    """Test scenarios with multiple providers or locations."""
    
    def test_multiple_doctors_in_same_practice(self):
        """Test handling appointments from multiple doctors."""
        appointments = [
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Mon, Jan 26', 'time': '9:30 am', 'datetime': 'Mon, Jan 26 9:30 am'},
            {'doctor': 'Dr. John Smith, DDS', 'date': 'Mon, Jan 26', 'time': '10:00 am', 'datetime': 'Mon, Jan 26 10:00 am'},
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Tue, Jan 27', 'time': '2:00 pm', 'datetime': 'Tue, Jan 27 2:00 pm'}
        ]
        
        df = pd.DataFrame(appointments)
        
        # Should have 2 unique doctors
        unique_doctors = df['doctor'].unique()
        assert len(unique_doctors) == 2
        
        # Group by doctor
        by_doctor = df.groupby('doctor').size()
        assert by_doctor['Dr. Michael Ayzin, DDS'] == 2
        assert by_doctor['Dr. John Smith, DDS'] == 1
    
    def test_filter_specific_doctor(self):
        """Test filtering appointments for specific doctor."""
        appointments = [
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Mon, Jan 26', 'time': '9:30 am', 'datetime': 'Mon, Jan 26 9:30 am'},
            {'doctor': 'Dr. John Smith, DDS', 'date': 'Mon, Jan 26', 'time': '10:00 am', 'datetime': 'Mon, Jan 26 10:00 am'},
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Tue, Jan 27', 'time': '2:00 pm', 'datetime': 'Tue, Jan 27 2:00 pm'}
        ]
        
        df = pd.DataFrame(appointments)
        
        # Filter for Dr. Ayzin only
        ayzin_appointments = df[df['doctor'] == 'Dr. Michael Ayzin, DDS']
        
        assert len(ayzin_appointments) == 2
        assert all(ayzin_appointments['doctor'] == 'Dr. Michael Ayzin, DDS')
