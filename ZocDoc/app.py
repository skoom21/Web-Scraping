"""
Cloud Run HTTP Server for ZocDoc Scraper

Provides HTTP endpoints for triggering the scraper and checking health status.
Designed for scheduled execution via Cloud Scheduler or external workflows.
"""

import os
import json
import logging
from flask import Flask, request, jsonify
from threading import Thread
import traceback
import pandas as pd

from zocdoc_scraper_production import ZocDocScraper, setup_logging

app = Flask(__name__)

# Global state for tracking scraper execution
scraper_status = {
    'running': False,
    'last_run': None,
    'last_result': None,
    'appointments': []  # Store actual appointment data
}
def run_scraper_async():
    """Run scraper in background thread."""
    global scraper_status
    
    logger = logging.getLogger('zocdoc_scraper')
    
    try:
        scraper_status['running'] = True
        scraper_status['last_run'] = 'in_progress'
        
        logger.info("Starting scraper execution...")
        scraper = ZocDocScraper(logger)
        result = scraper.run()
        
        # Store appointments data
        if result['success'] and scraper.appointments:
            scraper_status['appointments'] = scraper.appointments
            result['appointments'] = scraper.appointments
            logger.info(f"Stored {len(scraper.appointments)} appointments in memory")
        
        scraper_status['last_result'] = result
        scraper_status['running'] = False
        
        if result['success']:
            logger.info("✅ Scraper completed successfully")
        else:
            logger.error(f"❌ Scraper failed: {result.get('error')}")
    
    except Exception as e:
        logger.error(f"Scraper execution failed: {str(e)}")
        logger.error(traceback.format_exc())
        scraper_status['last_result'] = {
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }
        scraper_status['running'] = False


@app.route('/', methods=['GET', 'POST'])
def trigger_scraper():
    """
    Trigger scraper execution.
    
    Accepts both GET and POST requests.
    POST can include optional parameters in JSON body.
    
    Returns:
        JSON response with execution status
    """
    logger = logging.getLogger('zocdoc_scraper')
    
    # Check if scraper is already running
    if scraper_status['running']:
        return jsonify({
            'status': 'already_running',
            'message': 'Scraper is already running. Please wait for completion.'
        }), 409
    
    # Parse optional parameters from POST body
    params = {}
    if request.method == 'POST' and request.is_json:
        params = request.get_json()
        logger.info(f"Received trigger request with params: {params}")
    
    # Start scraper in background thread
    thread = Thread(target=run_scraper_async)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'status': 'started',
        'message': 'Scraper execution started',
        'params': params
    }), 202


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    
    Returns:
        JSON response with health status
    """
    return jsonify({
        'status': 'healthy',
        'service': 'zocdoc-scraper',
        'running': scraper_status['running']
    }), 200


@app.route('/status', methods=['GET'])
def get_status():
    """
    Get scraper execution status.
    
    Returns:
        JSON response with current and last execution status
    """
    return jsonify({
        'running': scraper_status['running'],
        'last_result': scraper_status['last_result']
    }), 200


@app.route('/results', methods=['GET'])
def get_results():
    """
    Get results from last scraper execution.
    
    Returns:
        JSON response with last execution results and appointments
    """
    if scraper_status['last_result'] is None:
        return jsonify({
            'status': 'no_results',
            'message': 'No scraper runs completed yet'
        }), 404
    
    result_data = scraper_status['last_result'].copy()
    
    # Include appointments in response
    if scraper_status['appointments']:
        result_data['appointments'] = scraper_status['appointments']
        result_data['appointments_count'] = len(scraper_status['appointments'])
    
    return jsonify({
        'status': 'success' if scraper_status['last_result'].get('success') else 'failed',
        'result': result_data
    }), 200


@app.route('/appointments', methods=['GET'])
def get_appointments():
    """
    Get only the appointments data from last scraper execution.
    
    Query params:
        format: 'json' (default) or 'csv'
    
    Returns:
        JSON array of appointments or CSV download
    """
    if not scraper_status['appointments']:
        return jsonify({
            'status': 'no_appointments',
            'message': 'No appointments available. Run the scraper first.',
            'appointments': []
        }), 404
    
    format_type = request.args.get('format', 'json').lower()
    
    if format_type == 'csv':
        # Return CSV
        df = pd.DataFrame(scraper_status['appointments'])
        csv_data = df.to_csv(index=False)
        
        from flask import Response
        return Response(
            csv_data,
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=appointments.csv'}
        )
    else:
    # Return JSON
        return jsonify({
            'status': 'success',
            'count': len(scraper_status['appointments']),
            'appointments': scraper_status['appointments']
        }), 200


@app.errorhandler(Exception)
def handle_error(error):
    """Global error handler."""
    logger = logging.getLogger('zocdoc_scraper')
    logger.error(f"Unhandled error: {str(error)}")
    logger.error(traceback.format_exc())
    
    return jsonify({
        'status': 'error',
        'message': str(error)
    }), 500


if __name__ == '__main__':
    # Setup logging
    logger = setup_logging()
    logger.info("Starting ZocDoc Scraper HTTP Server...")
    
    # Get port from environment (Cloud Run sets PORT)
    port = int(os.getenv('PORT', 8080))
    
    # Run server
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        threaded=True
    )
