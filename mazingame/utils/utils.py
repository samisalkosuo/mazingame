"""Generic utility functions for MazinGame.

The MIT License (MIT)

Copyright (c) 2015 Sami Salkosuo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from datetime import datetime
import logging
import sys
import time
import sqlite3
import hashlib
from typing import Any, List, Optional, Tuple
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

# Legacy debug settings (deprecated, use logging instead)
DEBUG = True
DEBUG_FILE = "debug.log"
ERROR_FILE = "error.log"


def debug(message: str) -> None:
    """Legacy debug function. Use logging.debug() instead.
    
    Args:
        message: Debug message to log
    """
    if DEBUG:
        msg = f"{datetime.now()}: {message}"
        if DEBUG_FILE is not None:
            try:
                with open(DEBUG_FILE, "a", encoding="utf-8") as file:
                    file.write(f"{msg}\n")
            except OSError as e:
                logger.error(f"Failed to write to debug file: {e}")


def boolValue(value: Any) -> bool:
    """Convert a value to boolean.
    
    Args:
        value: Value to convert
        
    Returns:
        Boolean representation of the value
    """
    string = str(value)
    return string.lower() in ("yes", "y", "true", "on", "t", "1")


def error() -> None:
    """Log exception traceback. Use logging.exception() instead."""
    import traceback
    
    error_msg = traceback.format_exc()
    print(error_msg)
    msg = f"{datetime.now()}: {error_msg}"
    try:
        appendToFile(ERROR_FILE, msg)
    except OSError as e:
        logger.error(f"Failed to write error to file: {e}")


def appendToFile(filename: str, content: str) -> None:
    """Append content to a file.
    
    Args:
        filename: Path to the file
        content: Content to append
        
    Raises:
        OSError: If file cannot be written
    """
    try:
        with open(filename, "a", encoding="utf-8") as file:
            file.write(content)
            file.write("\n")
    except OSError as e:
        logger.error(f"Failed to append to file {filename}: {e}")
        raise


def appendToLogFile(message: str) -> None:
    """Append message to mazingame log file.
    
    Args:
        message: Message to log
    """
    try:
        with open("mazingame_log.txt", "a", encoding="utf-8") as file:
            file.write(message)
            file.write("\n")
    except OSError as e:
        logger.error(f"Failed to write to log file: {e}")


def readFileAsString(filename: str) -> str:
    """Read entire file as a string.
    
    Args:
        filename: Path to the file
        
    Returns:
        File contents as string
        
    Raises:
        OSError: If file cannot be read
    """
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return file.read()
    except OSError as e:
        logger.error(f"Failed to read file {filename}: {e}")
        raise


def sha256(data: str) -> str:
    """Calculate SHA256 hash of string.
    
    Args:
        data: String to hash
        
    Returns:
        Hexadecimal hash string
    """
    sha = hashlib.sha256(data.encode("utf-8"))
    return sha.hexdigest()


def currentDate() -> str:
    """Get current date as string.
    
    Returns:
        Current date in YYYY-MM-DD format
    """
    return datetime.now().strftime('%Y-%m-%d')


def currentTimeMillis() -> int:
    """Get current time in milliseconds.
    
    Returns:
        Current time as milliseconds since epoch
    """
    return int(round(time.time() * 1000))


def currentTimestamp() -> float:
    """Get current timestamp.
    
    Returns:
        Current time as seconds since epoch
    """
    return time.time()


def formatTimestamp(timestamp: float) -> str:
    """Format timestamp as readable string.
    
    Args:
        timestamp: Unix timestamp
        
    Returns:
        Formatted timestamp string
    """
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


def currentTimeISO8601() -> str:
    """Return current time as ISO8601 timestamp.
    
    Returns:
        ISO8601 formatted timestamp (YYYY-MM-DD HH:MM:SS.SSS)
    """
    return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]


# SQLITE
def openDatabase(file: str, inMemory: bool = False) -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
    """Open SQLite database and return connection and cursor.
    
    Args:
        file: Path to database file
        inMemory: If True, create in-memory database
        
    Returns:
        Tuple of (connection, cursor)
        
    Raises:
        sqlite3.Error: If database cannot be opened
    """
    try:
        if inMemory:
            conn = sqlite3.connect(':memory:')
        else:
            conn = sqlite3.connect(file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        logger.debug(f"Opened database: {file if not inMemory else ':memory:'}")
        return (conn, cursor)
    except sqlite3.Error as e:
        logger.error(f"Failed to open database {file}: {e}")
        raise


def closeDatabase(connection: Optional[sqlite3.Connection]) -> None:
    """Close SQLite database connection.
    
    Args:
        connection: Database connection to close
    """
    if connection is not None:
        try:
            connection.close()
            logger.debug("Closed database connection")
        except sqlite3.Error as e:
            logger.error(f"Error closing database: {e}")

