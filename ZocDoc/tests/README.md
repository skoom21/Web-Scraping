# ZocDoc Scraper Test Suite

Production-grade test suite for the ZocDoc appointment scraper.

## Test Structure

```
tests/
├── __init__.py                     # Test package initialization
├── conftest.py                     # Shared fixtures and configuration
├── test_html_parser.py            # HTML parsing and BeautifulSoup tests
├── test_data_processing.py        # DataFrame and CSV export tests
├── test_proxy_configuration.py    # Proxy and URL configuration tests
├── test_selectors.py              # CSS selector validation tests
└── test_integration.py            # End-to-end integration tests
```

## Running Tests

### Run all tests
```bash
cd /home/skoom/Web-Scraping/ZocDoc
source venv/bin/activate
pytest
```

### Run specific test file
```bash
pytest tests/test_html_parser.py
pytest tests/test_data_processing.py
pytest tests/test_selectors.py
```

### Run specific test class
```bash
pytest tests/test_html_parser.py::TestTimeslotExtraction
pytest tests/test_data_processing.py::TestDataFrameCreation
```

### Run specific test function
```bash
pytest tests/test_html_parser.py::TestTimeslotExtraction::test_extract_valid_timeslots
```

### Run with verbose output
```bash
pytest -v
```

### Run with coverage report
```bash
# Install pytest-cov first: pip install pytest-cov
pytest --cov=. --cov-report=html --cov-report=term
```

### Run tests matching keyword
```bash
pytest -k "timeslot"
pytest -k "dataframe"
pytest -k "proxy"
```

### Run only fast tests (exclude slow tests)
```bash
pytest -m "not slow"
```

## Test Categories

### Unit Tests

#### HTML Parser Tests (`test_html_parser.py`)
- ✅ Extract valid timeslots from HTML
- ✅ Handle empty timeslots
- ✅ Extract multiple dates
- ✅ Handle malformed HTML
- ✅ Handle extra whitespace
- ✅ Modal container detection
- ✅ Date parsing validation
- ✅ Time format validation
- ✅ Edge cases (empty HTML, invalid HTML, special characters)

#### Data Processing Tests (`test_data_processing.py`)
- ✅ DataFrame creation from valid data
- ✅ Handle empty datasets
- ✅ Column type validation
- ✅ Duplicate detection and removal
- ✅ CSV export and import
- ✅ Data validation (required fields, non-empty values)
- ✅ Data sorting and aggregation
- ✅ Large dataset handling

#### Proxy Configuration Tests (`test_proxy_configuration.py`)
- ✅ Valid proxy configuration
- ✅ Proxy enable/disable toggle
- ✅ Server format validation
- ✅ Credentials validation
- ✅ Missing fields detection
- ✅ URL format validation
- ✅ Retry logic configuration
- ✅ Timeout configuration

#### Selector Tests (`test_selectors.py`)
- ✅ Modal selector strategies
- ✅ Timeslot selectors
- ✅ Date wrapper selectors
- ✅ Button selectors
- ✅ Dropdown selectors
- ✅ Selector combinations
- ✅ Edge cases (empty selectors, special characters)

### Integration Tests (`test_integration.py`)
- ✅ End-to-end workflow simulation
- ✅ "Show more availability" workflow
- ✅ No appointments scenario
- ✅ Error recovery (missing data, malformed content)
- ✅ Data quality validation
- ✅ Scalability with large datasets
- ✅ Multiple doctors handling

## Test Coverage

### Components Tested
1. **HTML Parsing** (BeautifulSoup)
   - Element extraction
   - Attribute matching
   - Parent/child navigation
   - Text extraction

2. **Data Processing** (Pandas)
   - DataFrame creation
   - Duplicate removal
   - CSV export/import
   - Data validation

3. **Configuration**
   - Proxy settings
   - URL validation
   - Timeout values
   - Retry logic

4. **Selectors**
   - CSS selectors
   - XPath alternatives
   - Playwright locators
   - Fallback strategies

5. **Integration**
   - Complete workflows
   - Error handling
   - Data quality
   - Scalability

### Edge Cases Covered
- ✅ Empty HTML
- ✅ Malformed HTML
- ✅ Missing elements
- ✅ Extra whitespace
- ✅ Special characters
- ✅ Unicode characters
- ✅ Large datasets
- ✅ No appointments
- ✅ Duplicate appointments
- ✅ Multiple modals on page

## Assertions

All tests use comprehensive assertions:
- `assert` - Standard assertions
- `assert len()` - Length checks
- `assert isinstance()` - Type checks
- `assert in` / `assert not in` - Membership checks
- `assert <` / `assert >` - Comparison checks
- Pandas assertions (`isnull()`, `shape`, `columns`)

## Fixtures

Shared test fixtures in `conftest.py`:
- `sample_appointment` - Single appointment dict
- `sample_appointments_list` - List of appointments
- `sample_modal_html` - Sample modal HTML
- `sample_proxy_config` - Proxy configuration
- `sample_url` - ZocDoc URL

## Best Practices

1. **Isolation**: Each test is independent
2. **Clarity**: Descriptive test names and docstrings
3. **Coverage**: Tests cover happy path, edge cases, and error conditions
4. **Assertions**: Multiple assertions verify different aspects
5. **Fixtures**: Reusable test data via fixtures
6. **Fast**: Most tests run in milliseconds

## Adding New Tests

1. Create test in appropriate file or new file
2. Follow naming convention: `test_<feature>.py`
3. Use fixtures for common test data
4. Add comprehensive assertions
5. Document with docstring
6. Run test to verify

Example:
```python
def test_new_feature(sample_appointment):
    """Test description of what is being tested."""
    # Arrange
    data = sample_appointment
    
    # Act
    result = process_data(data)
    
    # Assert
    assert result is not None
    assert isinstance(result, dict)
    assert 'doctor' in result
```

## Continuous Integration

These tests are designed for CI/CD pipelines:
- Fast execution (< 1 second for most tests)
- No external dependencies required
- Clear pass/fail indicators
- Detailed error messages

## Troubleshooting

### Test failures
```bash
# Run with full traceback
pytest --tb=long

# Run with print output
pytest -s
```

### Import errors
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Install test dependencies
pip install pytest pytest-cov beautifulsoup4 pandas
```

### Module not found
The `conftest.py` adds parent directory to path automatically.
If issues persist, verify file structure matches expected layout.
