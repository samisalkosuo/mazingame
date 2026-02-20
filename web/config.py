"""Configuration management for Mazingame web application."""

import os
from typing import Optional


class Config:
    """Base configuration class."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Session settings
    MAX_CONCURRENT_SESSIONS = int(os.environ.get('MAX_CONCURRENT_SESSIONS', '50'))
    MAX_SESSIONS_PER_IP = int(os.environ.get('MAX_SESSIONS_PER_IP', '3'))
    SESSION_IDLE_TIMEOUT = int(os.environ.get('SESSION_TIMEOUT', '1800'))  # 30 minutes
    SESSION_ABSOLUTE_TIMEOUT = int(os.environ.get('SESSION_ABSOLUTE_TIMEOUT', '7200'))  # 2 hours
    SESSION_CLEANUP_INTERVAL = int(os.environ.get('SESSION_CLEANUP_INTERVAL', '300'))  # 5 minutes
    
    # Terminal settings - Full-screen mode (entire maze visible)
    TERMINAL_ROWS = int(os.environ.get('TERMINAL_ROWS', '43'))
    TERMINAL_COLS = int(os.environ.get('TERMINAL_COLS', '102'))
    TERM_TYPE = os.environ.get('TERM_TYPE', 'xterm-256color')
    
    # Mazingame settings
    MAZINGAME_HIGHSCORE_FILE = os.environ.get(
        'MAZINGAME_HIGHSCORE_FILE',
        os.path.join(os.path.dirname(__file__), '..', 'data', 'mazingame_highscores.sqlite')
    )
    MAZINGAME_DATA_DIR = os.environ.get(
        'MAZINGAME_DATA_DIR',
        os.path.join(os.path.dirname(__file__), '..', 'data')
    )
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    @classmethod
    def init_app(cls, app):
        """Initialize application with configuration."""
        # Ensure data directory exists
        os.makedirs(cls.MAZINGAME_DATA_DIR, exist_ok=True)
        
        # Set environment variable for mazingame
        os.environ['MAZINGAME_HIGHSCORE_FILE'] = cls.MAZINGAME_HIGHSCORE_FILE


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    MAX_CONCURRENT_SESSIONS = 10


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    
    @classmethod
    def init_app(cls, app):
        """Initialize production app."""
        Config.init_app(app)
        
        # Production-specific initialization
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug:
            file_handler = RotatingFileHandler(
                'logs/mazingame-web.log',
                maxBytes=10240000,
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(cls.LOG_FORMAT))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info('Mazingame web startup')


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    MAX_CONCURRENT_SESSIONS = 5
    SESSION_IDLE_TIMEOUT = 60  # 1 minute for testing


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name: Optional[str] = None) -> Config:
    """Get configuration object based on environment."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    return config.get(config_name, config['default'])

# Made with Bob
