# backend/app/core/logger.py

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)

# Export this object
logger = logging.getLogger(__name__)
