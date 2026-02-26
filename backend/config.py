"""App config from env vars."""

import os
from typing import Optional


class Config:
    """Application configuration."""

    DEBUG: bool = os.getenv('APP_DEBUG', 'false').lower() in ('true', '1', 'yes')
    HOST: str = os.getenv('APP_HOST', '0.0.0.0')
    PORT: int = int(os.getenv('APP_PORT', '8000'))
    CORS_ORIGINS: str = os.getenv('CORS_ORIGINS', '*')

    # Computation limits
    MAX_EXPRESSION_LENGTH: int = int(os.getenv('MAX_EXPRESSION_LENGTH', '500'))
    MAX_MONTE_CARLO_SAMPLES: int = int(os.getenv('MAX_MONTE_CARLO_SAMPLES', '100000'))
    COMPUTATION_TIMEOUT: int = int(os.getenv('COMPUTATION_TIMEOUT', '30'))

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv('RATE_LIMIT_PER_MINUTE', '60'))

    # Logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
