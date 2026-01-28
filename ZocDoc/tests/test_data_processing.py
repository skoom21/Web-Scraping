"""
Unit tests for data processing and CSV export functionality.
Tests pandas DataFrame operations and data validation.
"""

import pytest
import pandas as pd
import os
import tempfile
from pathlib import Path


class TestDataFrameCreation:
    """Test DataFrame creation from appointment data."""
    
    def test_create_dataframe_from_valid_data(self):
        """Test creating DataFrame from valid appointment data."""
        appointments = [
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Mon, Jan 26', 'time': '9:30 am', 'datetime': 'Mon, Jan 26 9:30 am'},
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Mon, Jan 26', 'time': '10:00 am', 'datetime': 'Mon, Jan 26 10:00 am'},
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Tue, Jan 27', 'time': '2:00 pm', 'datetime': 'Tue, Jan 27 2:00 pm'}
        ]
        
        df = pd.DataFrame(appointments)
        
        assert df.shape == (3, 4)
        assert list(df.columns) == ['doctor', 'date', 'time', 'datetime']
        assert len(df) == 3
    
    def test_create_dataframe_from_empty_list(self):
        """Test creating DataFrame from empty list."""
        appointments = []
        df = pd.DataFrame(appointments)
        
        assert df.shape == (0, 0)
        assert len(df) == 0
    
    def test_dataframe_column_types(self):
        """Test DataFrame has correct column data types."""
        appointments = [
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Mon, Jan 26', 'time': '9:30 am', 'datetime': 'Mon, Jan 26 9:30 am'}
        ]
        
        df = pd.DataFrame(appointments)
        
        # Pandas 3.0+ uses StringDtype for string columns, older versions use 'object'
        assert df['doctor'].dtype in ['object', 'string', pd.StringDtype()]  # String type
        assert df['date'].dtype in ['object', 'string', pd.StringDtype()]
        assert df['time'].dtype in ['object', 'string', pd.StringDtype()]
        assert df['datetime'].dtype in ['object', 'string', pd.StringDtype()]
    
    def test_dataframe_with_missing_fields(self):
        """Test DataFrame creation with missing fields."""
        appointments = [
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Mon, Jan 26', 'time': '9:30 am'},  # Missing datetime
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Tue, Jan 27', 'datetime': 'Tue, Jan 27 2:00 pm'}  # Missing time
        ]
        
        df = pd.DataFrame(appointments)
        
        assert df.shape == (2, 4)
        assert pd.isna(df.loc[0, 'datetime'])
        assert pd.isna(df.loc[1, 'time'])


class TestDuplicateRemoval:
    """Test duplicate detection and removal."""
    
    def test_remove_exact_duplicates(self):
        """Test removing exact duplicate rows."""
        appointments = [
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Mon, Jan 26', 'time': '9:30 am', 'datetime': 'Mon, Jan 26 9:30 am'},
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Mon, Jan 26', 'time': '9:30 am', 'datetime': 'Mon, Jan 26 9:30 am'},  # Duplicate
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Tue, Jan 27', 'time': '2:00 pm', 'datetime': 'Tue, Jan 27 2:00 pm'}
        ]
        
        df = pd.DataFrame(appointments)
        df_clean = df.drop_duplicates().reset_index(drop=True)
        
        assert len(df) == 3
        assert len(df_clean) == 2
    
    def test_identify_duplicates_by_date_time(self):
        """Test identifying duplicates based on date and time only."""
        appointments = [
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Mon, Jan 26', 'time': '9:30 am', 'datetime': 'Mon, Jan 26 9:30 am'},
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Mon, Jan 26', 'time': '9:30 am', 'datetime': 'Different datetime'},  # Same date/time
        ]
        
        df = pd.DataFrame(appointments)
        duplicates = df[df.duplicated(subset=['date', 'time'], keep=False)]
        
        assert len(duplicates) == 2
    
    def test_no_duplicates(self):
        """Test when there are no duplicates."""
        appointments = [
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Mon, Jan 26', 'time': '9:30 am', 'datetime': 'Mon, Jan 26 9:30 am'},
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Mon, Jan 26', 'time': '10:00 am', 'datetime': 'Mon, Jan 26 10:00 am'},
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Tue, Jan 27', 'time': '9:30 am', 'datetime': 'Tue, Jan 27 9:30 am'}
        ]
        
        df = pd.DataFrame(appointments)
        df_clean = df.drop_duplicates().reset_index(drop=True)
        
        assert len(df) == len(df_clean)


class TestCSVExport:
    """Test CSV file export functionality."""
    
    def test_export_to_csv(self):
        """Test exporting DataFrame to CSV."""
        appointments = [
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Mon, Jan 26', 'time': '9:30 am', 'datetime': 'Mon, Jan 26 9:30 am'},
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Tue, Jan 27', 'time': '2:00 pm', 'datetime': 'Tue, Jan 27 2:00 pm'}
        ]
        
        df = pd.DataFrame(appointments)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            temp_path = f.name
        
        try:
            df.to_csv(temp_path, index=False)
            
            # Verify file exists
            assert os.path.exists(temp_path)
            
            # Read back and verify
            df_read = pd.read_csv(temp_path)
            assert df_read.shape == df.shape
            assert list(df_read.columns) == list(df.columns)
            assert len(df_read) == len(df)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_export_empty_dataframe(self):
        """Test exporting empty DataFrame."""
        df = pd.DataFrame()
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            temp_path = f.name
        
        try:
            df.to_csv(temp_path, index=False)
            assert os.path.exists(temp_path)
            
            # Empty CSV will raise EmptyDataError in pandas, that's expected
            try:
                df_read = pd.read_csv(temp_path)
                assert len(df_read) == 0
            except pd.errors.EmptyDataError:
                # This is expected for empty DataFrames
                pass
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_csv_preserves_special_characters(self):
        """Test CSV export preserves special characters."""
        appointments = [
            {'doctor': 'Dr. O\'Brien, DDS', 'date': 'Mon, Jan 26', 'time': '9:30 am', 'datetime': 'Mon, Jan 26 9:30 am'},
            {'doctor': 'Dr. Smith-Jones, DDS', 'date': 'Tue, Jan 27', 'time': '2:00 pm', 'datetime': 'Tue, Jan 27 2:00 pm'}
        ]
        
        df = pd.DataFrame(appointments)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            temp_path = f.name
        
        try:
            df.to_csv(temp_path, index=False)
            df_read = pd.read_csv(temp_path)
            
            assert "O'Brien" in df_read.loc[0, 'doctor']
            assert "Smith-Jones" in df_read.loc[1, 'doctor']
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def test_csv_column_order(self):
        """Test CSV maintains correct column order."""
        appointments = [
            {'time': '9:30 am', 'doctor': 'Dr. Michael Ayzin, DDS', 'datetime': 'Mon, Jan 26 9:30 am', 'date': 'Mon, Jan 26'}
        ]
        
        df = pd.DataFrame(appointments)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            temp_path = f.name
        
        try:
            df.to_csv(temp_path, index=False)
            
            with open(temp_path, 'r') as f:
                header = f.readline().strip()
            
            # Pandas will use the order from the dict (Python 3.7+ preserves insertion order)
            assert header.split(',') == ['time', 'doctor', 'datetime', 'date']
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


class TestDataValidation:
    """Test data validation and integrity checks."""
    
    def test_validate_required_fields(self):
        """Test validation of required fields."""
        valid_appointment = {
            'doctor': 'Dr. Michael Ayzin, DDS',
            'date': 'Mon, Jan 26',
            'time': '9:30 am',
            'datetime': 'Mon, Jan 26 9:30 am'
        }
        
        required_fields = ['doctor', 'date', 'time', 'datetime']
        assert all(field in valid_appointment for field in required_fields)
        
        invalid_appointment = {
            'doctor': 'Dr. Michael Ayzin, DDS',
            'date': 'Mon, Jan 26'
            # Missing time and datetime
        }
        
        assert not all(field in invalid_appointment for field in required_fields)
    
    def test_validate_non_empty_values(self):
        """Test validation that values are not empty."""
        valid_appointment = {
            'doctor': 'Dr. Michael Ayzin, DDS',
            'date': 'Mon, Jan 26',
            'time': '9:30 am',
            'datetime': 'Mon, Jan 26 9:30 am'
        }
        
        assert all(len(str(value).strip()) > 0 for value in valid_appointment.values())
        
        invalid_appointment = {
            'doctor': '',
            'date': 'Mon, Jan 26',
            'time': '9:30 am',
            'datetime': 'Mon, Jan 26 9:30 am'
        }
        
        assert not all(len(str(value).strip()) > 0 for value in invalid_appointment.values())
    
    def test_validate_doctor_name_format(self):
        """Test validation of doctor name format."""
        valid_names = [
            'Dr. Michael Ayzin, DDS',
            'Dr. John Smith, MD',
            'Dr. Jane Doe, DMD'
        ]
        
        for name in valid_names:
            assert name.startswith('Dr.')
            assert ',' in name
    
    def test_validate_time_format(self):
        """Test validation of time format."""
        valid_times = [
            '9:30 am',
            '10:00 am',
            '2:45 pm',
            '12:00 pm'
        ]
        
        for time_str in valid_times:
            assert ' ' in time_str
            assert time_str.endswith('am') or time_str.endswith('pm')
            assert ':' in time_str.split()[0]
    
    def test_dataframe_integrity_after_operations(self):
        """Test DataFrame integrity after various operations."""
        appointments = [
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Mon, Jan 26', 'time': '9:30 am', 'datetime': 'Mon, Jan 26 9:30 am'},
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Tue, Jan 27', 'time': '2:00 pm', 'datetime': 'Tue, Jan 27 2:00 pm'}
        ]
        
        df = pd.DataFrame(appointments)
        original_shape = df.shape
        
        # Various operations
        df_sorted = df.sort_values('time')
        df_filtered = df[df['date'] == 'Mon, Jan 26']
        df_reset = df.reset_index(drop=True)
        
        # Original should be unchanged
        assert df.shape == original_shape
        
        # Operations should produce valid DataFrames
        assert isinstance(df_sorted, pd.DataFrame)
        assert isinstance(df_filtered, pd.DataFrame)
        assert isinstance(df_reset, pd.DataFrame)


class TestDataSorting:
    """Test data sorting functionality."""
    
    def test_sort_by_datetime(self):
        """Test sorting appointments by datetime."""
        appointments = [
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Tue, Jan 27', 'time': '2:00 pm', 'datetime': 'Tue, Jan 27 2:00 pm'},
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Mon, Jan 26', 'time': '9:30 am', 'datetime': 'Mon, Jan 26 9:30 am'},
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Mon, Jan 26', 'time': '10:00 am', 'datetime': 'Mon, Jan 26 10:00 am'}
        ]
        
        df = pd.DataFrame(appointments)
        # Note: This is lexicographic sorting, not chronological
        df_sorted = df.sort_values('datetime').reset_index(drop=True)
        
        # Verify it's sorted (lexicographically)
        for i in range(len(df_sorted) - 1):
            assert df_sorted.loc[i, 'datetime'] <= df_sorted.loc[i + 1, 'datetime']
    
    def test_sort_by_time(self):
        """Test sorting by time field."""
        appointments = [
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Mon, Jan 26', 'time': '2:00 pm', 'datetime': 'Mon, Jan 26 2:00 pm'},
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Mon, Jan 26', 'time': '9:30 am', 'datetime': 'Mon, Jan 26 9:30 am'},
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Mon, Jan 26', 'time': '10:00 am', 'datetime': 'Mon, Jan 26 10:00 am'}
        ]
        
        df = pd.DataFrame(appointments)
        df_sorted = df.sort_values('time').reset_index(drop=True)
        
        # Check first is am
        assert 'am' in df_sorted.loc[0, 'time']


class TestDataAggregation:
    """Test data aggregation and statistics."""
    
    def test_count_appointments_by_date(self):
        """Test counting appointments per date."""
        appointments = [
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Mon, Jan 26', 'time': '9:30 am', 'datetime': 'Mon, Jan 26 9:30 am'},
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Mon, Jan 26', 'time': '10:00 am', 'datetime': 'Mon, Jan 26 10:00 am'},
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Tue, Jan 27', 'time': '2:00 pm', 'datetime': 'Tue, Jan 27 2:00 pm'}
        ]
        
        df = pd.DataFrame(appointments)
        counts = df.groupby('date').size()
        
        assert counts['Mon, Jan 26'] == 2
        assert counts['Tue, Jan 27'] == 1
    
    def test_get_unique_dates(self):
        """Test getting unique dates."""
        appointments = [
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Mon, Jan 26', 'time': '9:30 am', 'datetime': 'Mon, Jan 26 9:30 am'},
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Mon, Jan 26', 'time': '10:00 am', 'datetime': 'Mon, Jan 26 10:00 am'},
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Tue, Jan 27', 'time': '2:00 pm', 'datetime': 'Tue, Jan 27 2:00 pm'}
        ]
        
        df = pd.DataFrame(appointments)
        unique_dates = df['date'].unique()
        
        assert len(unique_dates) == 2
        assert 'Mon, Jan 26' in unique_dates
        assert 'Tue, Jan 27' in unique_dates
    
    def test_get_total_appointment_count(self):
        """Test getting total appointment count."""
        appointments = [
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Mon, Jan 26', 'time': '9:30 am', 'datetime': 'Mon, Jan 26 9:30 am'},
            {'doctor': 'Dr. Michael Ayzin, DDS', 'date': 'Tue, Jan 27', 'time': '2:00 pm', 'datetime': 'Tue, Jan 27 2:00 pm'}
        ]
        
        df = pd.DataFrame(appointments)
        total = len(df)
        
        assert total == 2
        assert total == df.shape[0]
