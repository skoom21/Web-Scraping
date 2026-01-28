# ZocDoc Scraper - Public API Reference

## Base URL
```
http://13.228.79.100:8080
```

## Endpoints

### 1. Health Check
Check if the service is running and healthy.

**Endpoint:** `GET /health`

**Example:**
```bash
curl http://13.228.79.100:8080/health
```

**Response:**
```json
{
    "running": false,
    "service": "zocdoc-scraper",
    "status": "healthy"
}
```

---

### 2. Trigger Scraper
Start a new scraping job for both doctors.

**Endpoint:** `POST /`

**Example:**
```bash
curl -X POST http://13.228.79.100:8080/
```

**Response:**
```json
{
    "message": "Scraper execution started",
    "params": {},
    "status": "started"
}
```

---

### 3. Check Status
Get the current status and last execution results.

**Endpoint:** `GET /status`

**Example:**
```bash
curl http://13.228.79.100:8080/status
```

**Response:**
```json
{
    "last_result": {
        "success": true,
        "appointments_count": 85,
        "unique_count": 80,
        "duration": 115.80,
        "proxy_used": "primary",
        "metrics": {
            "appointments_found": 85,
            "errors": 0,
            "page_loads": 2,
            "retries": 0
        }
    },
    "running": false
}
```

---

### 4. Get Appointments (JSON)
Retrieve all appointments in JSON format.

**Endpoint:** `GET /appointments`

**Example:**
```bash
curl http://13.228.79.100:8080/appointments
```

**Response:**
```json
{
    "appointments": [
        {
            "doctor": "Dr. Michael Ayzin, DDS",
            "date": "Tue, Feb 3",
            "time": "3:00 pm",
            "datetime": "Tue, Feb 3 3:00 pm",
            "scraped_at": "2026-01-28T20:03:05.482844"
        },
        ...
    ],
    "count": 85,
    "unique_count": 80
}
```

---

### 5. Get Appointments (CSV)
Download appointments as CSV file.

**Endpoint:** `GET /appointments?format=csv`

**Example:**
```bash
curl http://13.228.79.100:8080/appointments?format=csv > appointments.csv
```

**Response:**
```csv
doctor,date,time,datetime,scraped_at
"Dr. Michael Ayzin, DDS","Tue, Feb 3",3:00 pm,"Tue, Feb 3 3:00 pm",2026-01-28T20:03:05.482844
...
```

---

### 6. Get Results
Get detailed execution results including file paths and metrics.

**Endpoint:** `GET /results`

**Example:**
```bash
curl http://13.228.79.100:8080/results
```

**Response:**
```json
{
    "appointments": [...],
    "appointments_count": 85,
    "unique_count": 80,
    "cleaned_file": "output/appointments_cleaned_20260128_200410.csv",
    "raw_file": "output/appointments_raw_20260128_200410.csv",
    "duration": 115.80,
    "success": true,
    "proxy_used": "primary",
    "metrics": {
        "appointments_found": 85,
        "errors": 0,
        "page_loads": 2,
        "retries": 0
    }
}
```

---

## Usage Examples

### Python
```python
import requests

# Trigger scraper
response = requests.post('http://13.228.79.100:8080/')
print(response.json())

# Wait for completion, then get results
import time
time.sleep(120)  # Wait 2 minutes

# Get appointments
appointments = requests.get('http://13.228.79.100:8080/appointments').json()
print(f"Found {appointments['count']} appointments")

# Download CSV
csv_data = requests.get('http://13.228.79.100:8080/appointments?format=csv').text
with open('appointments.csv', 'w') as f:
    f.write(csv_data)
```

### JavaScript/Node.js
```javascript
const axios = require('axios');

// Trigger scraper
await axios.post('http://13.228.79.100:8080/');

// Wait and get results
setTimeout(async () => {
    const response = await axios.get('http://13.228.79.100:8080/appointments');
    console.log(`Found ${response.data.count} appointments`);
}, 120000);
```

### cURL
```bash
# Trigger scraper
curl -X POST http://13.228.79.100:8080/

# Wait 2 minutes, then download CSV
sleep 120
curl http://13.228.79.100:8080/appointments?format=csv > appointments.csv

# Check status
curl http://13.228.79.100:8080/status | jq
```

---

## Notes

- **No authentication required** - All endpoints are publicly accessible
- **Execution time**: ~2 minutes per scraping job
- **Doctors scraped**: 
  - Dr. Michael Ayzin, DDS
  - Dr. Ronald Ayzin, DDS
- **Rate limiting**: No built-in rate limiting (use responsibly)
- **Container**: Running on t3.medium EC2 instance with Docker
- **Browser**: Pre-installed Camoufox (no runtime downloads)

---

## EC2 Instance Details

- **Instance ID**: i-0e854ce6ae829b99d
- **Instance Type**: t3.medium (2 vCPU, 4GB RAM)
- **Public IP**: 13.228.79.100
- **Region**: ap-southeast-1 (Singapore)
- **Security Group**: zocdoc-scraper-sg
  - Port 22 (SSH) - Open
  - Port 8080 (HTTP) - Open

---

## Stopping/Starting the Service

### SSH into EC2
```bash
ssh -i zocdoc-scraper-key.pem ubuntu@13.228.79.100
```

### Container Management
```bash
# Stop container
docker stop zocdoc-scraper

# Start container
docker start zocdoc-scraper

# Restart container
docker restart zocdoc-scraper

# View logs
docker logs zocdoc-scraper -f

# Check status
docker ps | grep zocdoc
```

### EC2 Instance Management
```bash
# Stop instance (saves costs when not in use)
aws ec2 stop-instances --instance-ids i-0e854ce6ae829b99d

# Start instance
aws ec2 start-instances --instance-ids i-0e854ce6ae829b99d

# Terminate instance (permanent deletion)
aws ec2 terminate-instances --instance-ids i-0e854ce6ae829b99d
```
