# Email Marketing System

## Overview

This project is an advanced, Python-based email marketing system designed for efficient bulk email sending. It focuses on maintaining high sender reputation through intelligent SMTP server management, anti-spam features, and delivery optimization. The system aims to provide sophisticated email sending capabilities comparable to commercial tools, targeting high deliverability and engagement for marketing campaigns. It includes advanced features like proxy rotation, domain warmup, and comprehensive analytics.

**Current Status**: ✅ **READY TO USE** - Successfully imported GitHub repository and fully configured for Replit environment. All dependencies installed via UV package manager. Console application is running with interactive menu system. Configuration files loaded (1 SMTP server, 2 targets, 2 identities, 25 subjects, HTML template). The ZShell Mailer is operational and ready for email marketing campaigns.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Components
**Multi-SMTP Management**: Implements SMTP server rotation across multiple providers with rate limiting, reputation scoring, and automatic failover.
**Configuration-Driven Design**: Externalizes system settings through dedicated configuration files for SMTPs, recipients, and templates.
**Modular Architecture**: Organized into specialized modules for core logic (`advanced_mailer.py`), configuration (`config_manager.py`), UI (`console_interface.py`), and orchestration (`main.py`).
**Anti-Spam Features**: Includes rate limiting, delivery timing randomization, SMTP health monitoring, and intelligent server rotation to maintain sender reputation.
**Template System**: Supports HTML email templates with variable substitution for personalized and responsive messaging.
**Progress Monitoring**: Provides a real-time, colored console interface for delivery progress, success rates, timing, and error reporting.
**Advanced HTML Encryption**: Features a multi-layered HTML encryption tool (`html_to_base64_8bit.py`) for obfuscation and anti-AI detection, bypassing spam filters with client-side decryption.
**Email Verification System**: (`emailverifier.py`) Offers comprehensive email validation including SMTP, MX record, and domain checks, with lead quality scoring and parallel processing.
**Lead Scraping System**: (`emailscraper.py`) A multi-source tool for lead generation, extracting emails from websites, with potential for LinkedIn and professional directory integration.
**SOCKS Proxy Rotation System**: Supports SOCKS4, SOCKS5, and HTTP proxy rotation for IP diversification, with health monitoring and intelligent failover.
**Domain Warmup System**: Implements gradual volume increases and per-SMTP warmup schedules to build sender reputation.
**Bounce Handling & List Cleaning**: Features intelligent retry logic, automatic bounce detection and categorization, and automated list hygiene.
**Engagement Tracking & Analytics**: Includes open tracking (invisible pixel), click tracking (link redirects), unsubscribe tracking, and real-time analytics.
**Link Personalization & Tracking**: Supports dynamic link wrapping, click analytics, UTM parameters, and personalized URLs.
**Timezone Optimization**: Detects recipient timezones for optimal send times and allows delayed sending.
**Enhanced Anti-Spam & Deliverability**: Incorporates ISP-specific optimizations, advanced header spoofing, invisible character injection, and dynamic reputation scoring.

### Design Patterns
**Dataclass Configuration Objects**: Utilizes Python dataclasses for type-safe and validated configuration management.
**Thread Pool Execution**: Employs concurrent email sending with configurable thread pools for performance while respecting rate limits.
**Factory Pattern**: Manages SMTP connections through factory methods to handle various provider configurations.
**Observer Pattern**: Implements a progress tracking system for real-time console feedback during operations.

## External Dependencies

**Email Infrastructure**: Standard Python SMTP library, supports Gmail, Outlook, Yahoo, and custom SMTP servers, with TLS/SSL encryption.
**DNS Services**: `dnspython` for domain validation and MX record lookups.
**User Interface**: `colorama` for cross-platform colored terminal output.
**System Libraries**: `threading`, `concurrent.futures`, `dataclasses`, and `logging`.
**File System**: Local storage for configuration and template files, with automatic sample generation.
**Web Scraping & Parsing**: `Beautiful Soup 4` for HTML parsing, `requests` for HTTP requests, and `Selenium` for advanced web automation.
**Communication**: Telegram Bot API for real-time notifications (requires custom bot integration).