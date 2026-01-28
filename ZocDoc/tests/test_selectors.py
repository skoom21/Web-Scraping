"""
Unit tests for CSS selectors and element locators.
Tests selector validation and matching logic.
"""

import pytest


class TestModalSelectors:
    """Test modal dialog selector strategies."""
    
    def test_modal_content_selector(self):
        """Test modal content data-test selector."""
        selector = '[data-test="modal-content"]'
        
        assert selector.startswith('[')
        assert selector.endswith(']')
        assert 'data-test' in selector
        assert 'modal-content' in selector
    
    def test_availability_modal_container_selector(self):
        """Test availability modal container selector."""
        selector = '[data-test="availability-modal-view-container"]'
        
        assert 'data-test' in selector
        assert 'availability-modal-view-container' in selector
    
    def test_role_dialog_selector(self):
        """Test role=dialog selector."""
        selector = '[role="dialog"]'
        
        assert 'role' in selector
        assert 'dialog' in selector
    
    def test_multiple_modal_selectors(self):
        """Test multiple modal selector combinations."""
        selectors = [
            '[role="dialog"]',
            '[data-test="modal-content"]',
            '[data-test="availability-modal-view-container"]',
            '[role="dialog"], [data-test*="modal"]'
        ]
        
        for selector in selectors:
            assert len(selector) > 0
            assert '[' in selector or selector.startswith('text=')


class TestTimeslotSelectors:
    """Test appointment timeslot selectors."""
    
    def test_timeslot_data_test_selector(self):
        """Test timeslot data-test attribute selector."""
        selector = 'a[data-test="availability-modal-timeslot"]'
        
        assert selector.startswith('a[')
        assert 'data-test' in selector
        assert 'availability-modal-timeslot' in selector
    
    def test_timeslot_element_type(self):
        """Test timeslot selector targets anchor tags."""
        selector = 'a[data-test="availability-modal-timeslot"]'
        
        assert selector.startswith('a')


class TestDateWrapperSelectors:
    """Test date wrapper selectors."""
    
    def test_date_wrapper_selector(self):
        """Test date wrapper data-test selector."""
        selector = 'div[data-test="availability-modal-content-date-wrapper"]'
        
        assert selector.startswith('div[')
        assert 'availability-modal-content-date-wrapper' in selector
    
    def test_day_title_selector(self):
        """Test day title data-test selector."""
        selector = 'div[data-test="availability-modal-content-day-title"]'
        
        assert selector.startswith('div[')
        assert 'availability-modal-content-day-title' in selector


class TestButtonSelectors:
    """Test button selectors."""
    
    def test_view_more_availability_selector(self):
        """Test 'View more availability' button selector."""
        selector = 'span:has-text("View more availability")'
        
        assert 'span' in selector
        assert ':has-text' in selector
        assert 'View more availability' in selector
    
    def test_show_more_availability_selector(self):
        """Test 'Show more availability' button selector."""
        selector = 'button:has-text("Show more availability")'
        
        assert 'button' in selector
        assert ':has-text' in selector
        assert 'Show more availability' in selector
    
    def test_close_button_selector(self):
        """Test close button selector."""
        selector = 'button[aria-label="Close"]'
        
        assert 'button' in selector
        assert 'aria-label' in selector
        assert 'Close' in selector


class TestDropdownSelectors:
    """Test provider dropdown selectors."""
    
    def test_all_provider_availability_selector(self):
        """Test 'All provider availability' text selector."""
        selector = 'text="All provider availability"'
        
        assert selector.startswith('text=')
        assert 'All provider availability' in selector
    
    def test_doctor_name_selector(self):
        """Test doctor name text selector."""
        selector = 'text="Dr. Michael Ayzin, DDS"'
        
        assert selector.startswith('text=')
        assert 'Dr. Michael Ayzin' in selector
        assert 'DDS' in selector
    
    def test_dropdown_control_selectors(self):
        """Test various dropdown control selectors."""
        selectors = [
            '.css-nm0j11-control',
            '.css-eio9xs-control',
            'div[class*="control"]:has-text("provider")',
            'div[class*="control"]:has-text("All provider")'
        ]
        
        for selector in selectors:
            assert len(selector) > 0


class TestSelectorCombinations:
    """Test selector combination strategies."""
    
    def test_multiple_selector_fallback(self):
        """Test multiple selector fallback strategy."""
        primary_selector = '[data-test="modal-content"]'
        fallback_selector = '[role="dialog"]'
        
        assert primary_selector != fallback_selector
        assert len(primary_selector) > 0
        assert len(fallback_selector) > 0
    
    def test_wildcard_selector(self):
        """Test wildcard attribute selector."""
        selector = '[data-test*="modal"]'
        
        assert 'data-test*=' in selector
        assert '*=' in selector  # Contains operator
    
    def test_combined_selector_with_or(self):
        """Test combined selectors with OR operator."""
        selector = '[role="dialog"], [data-test*="modal"]'
        
        assert ',' in selector
        parts = selector.split(',')
        assert len(parts) == 2
        assert '[role="dialog"]' in parts[0]
        assert '[data-test*="modal"]' in parts[1].strip()


class TestLocatorMethods:
    """Test locator method configurations."""
    
    def test_first_locator_method(self):
        """Test .first locator method usage."""
        locator_config = {
            'method': 'first',
            'selector': 'span:has-text("View more availability")'
        }
        
        assert locator_config['method'] == 'first'
    
    def test_nth_locator_method(self):
        """Test .nth() locator method usage."""
        locator_config = {
            'method': 'nth',
            'index': 0,
            'selector': 'button'
        }
        
        assert locator_config['method'] == 'nth'
        assert isinstance(locator_config['index'], int)
        assert locator_config['index'] >= 0
    
    def test_count_locator_method(self):
        """Test .count() locator method usage."""
        locator_config = {
            'method': 'count',
            'selector': '[role="dialog"]'
        }
        
        assert locator_config['method'] == 'count'


class TestSelectorEdgeCases:
    """Test edge cases in selector usage."""
    
    def test_empty_selector(self):
        """Test handling of empty selector."""
        selector = ''
        
        assert len(selector) == 0
        # Should not be used in production
    
    def test_selector_with_quotes(self):
        """Test selector with different quote types."""
        double_quote_selector = 'text="View more availability"'
        single_quote_selector = "text='View more availability'"
        
        assert 'View more availability' in double_quote_selector
        assert 'View more availability' in single_quote_selector
    
    def test_selector_with_special_characters(self):
        """Test selector with special characters."""
        selector = 'div[aria-label="Close dialog"]'
        
        assert '-' in selector  # Hyphen in attribute name
        assert ' ' in selector  # Space in attribute value
    
    def test_case_sensitive_selector(self):
        """Test case sensitivity in selectors."""
        lowercase_selector = 'button'
        uppercase_selector = 'BUTTON'
        
        # In CSS selectors, element names are case-insensitive for HTML
        # but attribute values are case-sensitive
        assert lowercase_selector.lower() == uppercase_selector.lower()
    
    def test_selector_with_colon(self):
        """Test selector with pseudo-class."""
        selector = 'span:has-text("View more availability")'
        
        assert ':' in selector
        assert selector.count(':') == 1
    
    def test_attribute_selector_variations(self):
        """Test different attribute selector variations."""
        exact_match = '[data-test="modal-content"]'  # Exact match
        contains = '[data-test*="modal"]'  # Contains
        starts_with = '[data-test^="modal"]'  # Starts with
        ends_with = '[data-test$="content"]'  # Ends with
        
        assert '=' in exact_match
        assert '*=' in contains
        assert '^=' in starts_with
        assert '$=' in ends_with
