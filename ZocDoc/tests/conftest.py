"""
Pytest configuration and shared fixtures for ZocDoc scraper tests.
"""

import pytest
import os
import sys

# Add parent directory to path so tests can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def sample_appointment():
    """Fixture providing a sample appointment dict."""
    return {
        'doctor': 'Dr. Michael Ayzin, DDS',
        'date': 'Mon, Jan 26',
        'time': '9:30 am',
        'datetime': 'Mon, Jan 26 9:30 am'
    }


@pytest.fixture
def sample_appointments_list():
    """Fixture providing a list of sample appointments."""
    return [
        {
            'doctor': 'Dr. Michael Ayzin, DDS',
            'date': 'Mon, Jan 26',
            'time': '9:30 am',
            'datetime': 'Mon, Jan 26 9:30 am'
        },
        {
            'doctor': 'Dr. Michael Ayzin, DDS',
            'date': 'Mon, Jan 26',
            'time': '10:00 am',
            'datetime': 'Mon, Jan 26 10:00 am'
        },
        {
            'doctor': 'Dr. Michael Ayzin, DDS',
            'date': 'Tue, Jan 27',
            'time': '2:00 pm',
            'datetime': 'Tue, Jan 27 2:00 pm'
        }
    ]


@pytest.fixture
def sample_modal_html():
    """Fixture providing sample modal HTML."""
    return '''
    <div data-test="availability-modal-view-container">
        <div data-test="availability-modal-content-date-wrapper">
            <div data-test="availability-modal-content-day-title">Mon, Jan 26</div>
            <a data-test="availability-modal-timeslot">9:30 am</a>
            <a data-test="availability-modal-timeslot">10:00 am</a>
            <a data-test="availability-modal-timeslot">11:30 am</a>
        </div>
        <div data-test="availability-modal-content-date-wrapper">
            <div data-test="availability-modal-content-day-title">Tue, Jan 27</div>
            <a data-test="availability-modal-timeslot">2:00 pm</a>
            <a data-test="availability-modal-timeslot">3:30 pm</a>
        </div>
    </div>
    '''


@pytest.fixture
def sample_proxy_config():
    """Fixture providing sample proxy configuration."""
    return {
        "server": "http://68.225.23.120:13884",
        "username": "rockin12345678",
        "password": "Varun123456789"
    }


@pytest.fixture
def sample_url():
    """Fixture providing the ZocDoc URL."""
    return "https://www.zocdoc.com/practice/dentistry-at-its-finest-19571?LocIdent=31976"
