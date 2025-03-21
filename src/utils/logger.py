# Author: Fengze Yang, Email: fred.yang@utah.edu
# Date: 2025-03-21

"""
logger.py

Configure logging to write to a file in the 'property' folder.
"""

import logging
from pathlib import Path

# Ensure the log file directory exists
log_file_path = Path("properties/shield_rsu.log")
log_file_path.parent.mkdir(exist_ok=True, parents=True)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
    filename=str(log_file_path),  # Send logs to file
    filemode='a'  # Append logs
)

logger = logging.getLogger("SHIELD_RSU")
