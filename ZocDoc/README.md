# ZocDoc Appointment Scraper

A production-grade web scraper for extracting available appointment slots from ZocDoc for multiple doctors. Built with Camoufox (anti-detection browser) and designed for deployment on AWS EC2 or containerized environments.

## Features

- **Multi-Doctor Support**: Scrape appointments for multiple doctors sequentially
- **Anti-Detection**: Uses Camoufox browser with randomized fingerprints
- **Proxy Rotation**: Supports 11 proxies with automatic rotation and retry logic
- **Production-Ready**: Comprehensive error handling, logging, and retry mechanisms
- **HTTP API**: Flask-based REST API with 6 endpoints for easy integration
- **Docker Support**: Containerized deployment with pre-installed browsers
- **Test Suite**: 105 comprehensive tests with 99% code coverage

## Quick Start

### Prerequisites

- Python 3.13+
- Docker (optional, for containerized deployment)
- AWS CLI (optional, for EC2 deployment)

### Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/Web-Scraping.git
   cd Web-Scraping/ZocDoc
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # For testing
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your proxy credentials and target doctors
   ```

5. **Run the scraper**:
   ```bash
   python zocdoc_scraper_production.py
   ```

### Docker Deployment

1. **Build the image**:
   ```bash
   docker build -t zocdoc-scraper .
   ```

2. **Run with docker-compose**:
   ```bash
   docker-compose up
   ```

The API will be available at `http://localhost:8080`

## API Endpoints

The Flask HTTP server provides the following endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/` | Trigger scraper execution |
| GET | `/health` | Health check |
| GET | `/status` | Execution status |
| GET | `/results` | Full results with metadata |
| GET | `/appointments` | Appointments in JSON format |
| GET | `/appointments?format=csv` | Download appointments as CSV |

### Example Usage

**Trigger scraper**:
```bash
curl -X POST http://localhost:8080/
```

**Get appointments as CSV**:
```bash
curl http://localhost:8080/appointments?format=csv > appointments.csv
```

**Check status**:
```bash
curl http://localhost:8080/status
```

See [API_ENDPOINTS.md](API_ENDPOINTS.md) for complete documentation.

## AWS EC2 Deployment

1. **Create EC2 instance** (t3.medium or larger recommended):
   ```bash
   aws ec2 run-instances \
     --image-id ami-0c55b159cbfafe1f0 \
     --instance-type t3.medium \
     --key-name your-key \
     --security-group-ids sg-xxxxx \
     --user-data file://ec2-user-data.sh
   ```

2. **Transfer Docker image**:
   ```bash
   docker save zocdoc-scraper | gzip > zocdoc-image.tar.gz
   scp -i your-key.pem zocdoc-image.tar.gz ubuntu@<EC2-IP>:~
   ```

3. **Deploy on EC2**:
   ```bash
   ssh -i your-key.pem ubuntu@<EC2-IP>
   docker load < zocdoc-image.tar.gz
   docker run -d -p 8080:8080 --name zocdoc-scraper zocdoc-scraper
   ```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Primary Proxy Configuration
ZOCDOC_PROXY_SERVER=proxy.example.com:port
ZOCDOC_PROXY_USERNAME=your_username
ZOCDOC_PROXY_PASSWORD=your_password

# Backup Proxies (comma-separated)
ZOCDOC_BACKUP_PROXIES=proxy1.example.com:port:user:pass,proxy2.example.com:port:user:pass

# Target Doctors (comma-separated)
ZOCDOC_TARGET_DOCTORS=Dr. Michael Ayzin DDS,Dr. Ronald Ayzin DDS

# Optional: Logging
LOG_LEVEL=INFO
```

See `.env.example` for a complete template.

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_scraper.py -v
```

The test suite includes:
- 105 test cases covering all functionality
- 99% code coverage
- Edge case testing
- Mock-based unit tests

## Project Structure

```
ZocDoc/
├── zocdoc_scraper_production.py  # Main scraper implementation
├── app.py                        # Flask HTTP API server
├── Dockerfile                    # Container image definition
├── docker-compose.yml            # Docker Compose configuration
├── requirements.txt              # Python dependencies
├── requirements-dev.txt          # Development dependencies
├── pytest.ini                    # Test configuration
├── .env.example                  # Environment template
├── .gitignore                    # Git ignore rules
├── .dockerignore                 # Docker ignore rules
├── preload_camoufox.py          # Browser pre-download script
├── ec2-user-data.sh             # EC2 bootstrap script
├── API_ENDPOINTS.md             # API documentation
├── tests/                       # Test suite
└── proxy_auth_extension/        # Proxy authentication extension
```

## How It Works

1. **Browser Automation**: Uses Camoufox (Firefox-based anti-detection browser) with Playwright
2. **Proxy Rotation**: Rotates through 11 proxies with automatic failover
3. **Multi-Doctor Processing**: Sequentially processes each target doctor with page reload
4. **Appointment Extraction**: Parses appointment slots with date, time, and doctor information
5. **Data Export**: Saves results as CSV and provides via HTTP API

## Performance

- **Execution Time**: ~2 minutes for 2 doctors
- **Success Rate**: 100% with proper proxy configuration
- **Appointments Extracted**: 80-85 unique appointments per run
- **Resource Usage**: 2 vCPU, 4GB RAM recommended

## Troubleshooting

### Common Issues

**Browser download errors**:
- Ensure sufficient disk space (5GB+ for browser downloads)
- Check internet connectivity
- Verify Playwright installation: `playwright install firefox`

**Proxy connection failures**:
- Verify proxy credentials in `.env`
- Test proxy connectivity manually
- Check proxy server status

**Docker timeouts**:
- Use `docker-compose up` for local testing
- Increase Docker memory limit (4GB minimum)
- Check Docker logs: `docker logs zocdoc-scraper`

## Security Notes

**⚠️ Important for Public Repositories**:
- Never commit `.env` files with real credentials
- Use `.env.example` as a template only
- Keep SSH keys (`.pem` files) private
- Rotate proxy credentials regularly
- Use environment variables or secrets management in production

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is provided as-is for educational and research purposes. Please ensure compliance with ZocDoc's Terms of Service and robots.txt before use.

## Disclaimer

This scraper is for educational purposes only. Web scraping may violate terms of service of the target website. Use responsibly and at your own risk. The authors are not responsible for any misuse or violations.

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check existing documentation in `API_ENDPOINTS.md`
- Review test cases for usage examples

---

**Built with**: Python 3.13, Camoufox, Playwright, Flask, BeautifulSoup4, Docker
