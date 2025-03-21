# Author: Fengze Yang, Email: fred.yang@utah.edu
# Date: 2025-03-21

import unittest
import os
from pathlib import Path
from utils.logger import logger


class TestLogger(unittest.TestCase):

    def test_logger_file_write(self):
        """
        Verifies logger is configured to write to a file in property/shield_rsu.log.
        We'll log a message and see if the file was appended.
        """
        log_file = Path("property/shield_rsu.log")
        # Get file size before logging
        old_size = log_file.stat().st_size if log_file.exists() else 0

        logger.info("Test logger file write")

        new_size = log_file.stat().st_size if log_file.exists() else 0
        self.assertTrue(new_size > old_size, "Log file was not appended after logging a message")


if __name__ == '__main__':
    unittest.main()
