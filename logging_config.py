import logging
import logging.handlers
import os
from datetime import datetime

def setup_logging(app_name='ΔΕΨ Ticket Verifier', log_level='INFO', log_file='logs/app.log'):
    """
    Set up structured logging for the application
    
    Args:
        app_name (str): Name of the application
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file (str): Path to log file
    """
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Configure logging format
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create logger
    logger = logging.getLogger(app_name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Console handler (for development)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)
    
    # File handler (for all logs)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(getattr(logging, log_level.upper()))
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)
    
    # Error file handler (for errors only)
    error_handler = logging.handlers.RotatingFileHandler(
        'logs/errors.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(log_format)
    logger.addHandler(error_handler)
    
    return logger

def get_logger(name=None):
    """
    Get a logger instance
    
    Args:
        name (str): Logger name (optional)
    
    Returns:
        logging.Logger: Logger instance
    """
    if name:
        return logging.getLogger(f'ΔΕΨ Ticket Verifier.{name}')
    return logging.getLogger('ΔΕΨ Ticket Verifier')

# Custom log levels for specific use cases
def log_order_submission(logger, order_data):
    """Log order submission with structured data"""
    logger.info(
        f"Order submitted - UUID: {order_data.get('uuid')}, "
        f"Name: {order_data.get('name')}, "
        f"Email: {order_data.get('email')}, "
        f"Boys: {order_data.get('boys_count')}, "
        f"Girls: {order_data.get('girls_count')}, "
        f"Expected Amount: ${order_data.get('expected_amount')}"
    )

def log_ocr_processing(logger, filename, ocr_text, parsed_data):
    """Log OCR processing results"""
    logger.info(
        f"OCR Processing - File: {filename}, "
        f"Text Length: {len(ocr_text)}, "
        f"Parsed Amount: {parsed_data.get('amount')}, "
        f"Parsed Date: {parsed_data.get('date')}, "
        f"Parsed Name: {parsed_data.get('name')}"
    )

def log_csv_upload(logger, filename, upload_type, records_processed, new_records, updated_records):
    """Log CSV upload results"""
    logger.info(
        f"CSV Upload - File: {filename}, "
        f"Type: {upload_type}, "
        f"Total Processed: {records_processed}, "
        f"New Records: {new_records}, "
        f"Updated Records: {updated_records}"
    )

def log_admin_action(logger, admin_user, action, details=None):
    """Log admin actions"""
    log_message = f"Admin Action - User: {admin_user}, Action: {action}"
    if details:
        log_message += f", Details: {details}"
    logger.info(log_message)

def log_error(logger, error, context=None):
    """Log errors with context"""
    error_message = f"Error: {str(error)}"
    if context:
        error_message += f", Context: {context}"
    logger.error(error_message, exc_info=True)

def log_performance(logger, operation, duration, details=None):
    """Log performance metrics"""
    log_message = f"Performance - Operation: {operation}, Duration: {duration:.3f}s"
    if details:
        log_message += f", Details: {details}"
    logger.info(log_message) 