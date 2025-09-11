#!/usr/bin/env python3
"""
👹 Zshell Mailer - Consolidated Portable Email Marketing System
Simple, reliable bulk email sender with SMTP rotation and TLS control
All functionality embedded in a single file for easy portability
"""

import os
import sys
import time
import smtplib
import logging
import re
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from colorama import Fore, Back, Style, init

# Initialize colorama and logging
init(autoreset=True)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class SMTPConfig:
    """Simple SMTP server configuration"""
    host: str
    port: int
    username: str
    password: str
    use_tls: bool = True

@dataclass
class EmailTemplate:
    """Simple email template"""
    subject: str
    html_body: str
    from_name: str

# =============================================================================
# PROGRESS BAR CLASS
# =============================================================================

class ProgressBar:
    """Colored progress bar for email sending"""
    
    def __init__(self, total: int, width: int = 50):
        self.total = total
        self.width = width
        self.current = 0
        self.start_time = time.time()
    
    def update(self, current: int, success: bool = True, email: str = "", message: str = ""):
        """Update progress bar with colored status"""
        self.current = current
        progress = current / self.total if self.total > 0 else 0
        filled = int(progress * self.width)
        bar = '█' * filled + '░' * (self.width - filled)
        
        # Calculate stats
        elapsed = time.time() - self.start_time
        rate = current / elapsed if elapsed > 0 else 0
        eta = (self.total - current) / rate if rate > 0 else 0
        
        # Color based on success rate
        if progress < 0.5:
            bar_color = Fore.RED
        elif progress < 0.8:
            bar_color = Fore.YELLOW
        else:
            bar_color = Fore.GREEN
        
        # Status indicator with demon theme
        status_icon = f"{Fore.GREEN}😈" if success else f"{Fore.RED}💀"
        
        # Clear line and print progress
        sys.stdout.write('\r' + ' ' * 120)  # Clear line
        sys.stdout.write(f'\r{bar_color}[{bar}] {progress*100:.1f}% ({current}/{self.total}) '
                        f'{Fore.CYAN}⚡ {rate:.1f}/s '
                        f'{Fore.MAGENTA}⏱️ ETA: {int(eta//60)}:{int(eta%60):02d} '
                        f'{status_icon}')
        sys.stdout.flush()
        
        if current >= self.total:
            print()  # New line when complete

# =============================================================================
# SIMPLE MAILER CLASS
# =============================================================================

class SimpleMailer:
    """Simple, reliable email sender"""
    
    def __init__(self):
        self.smtp_configs: List[SMTPConfig] = []
        self.current_smtp_index = 0
        self.sent_emails = []
        self.failed_emails = []
        self.from_emails: List[str] = []
        self.from_names: List[str] = []
        self.subjects: List[str] = []
        
    def add_smtp_server(self, host: str, port: int, username: str, password: str, use_tls: bool = True):
        """Add SMTP server configuration"""
        config = SMTPConfig(host, port, username, password, use_tls)
        self.smtp_configs.append(config)
        logger.info(f"Added SMTP server: {host}:{port}")
    
    def set_from_emails(self, from_emails: List[str]):
        """Set from email rotation list"""
        self.from_emails = from_emails
        logger.info(f"Loaded {len(from_emails)} from emails for rotation")
    
    def set_from_names(self, from_names: List[str]):
        """Set from name rotation list"""
        self.from_names = from_names
        logger.info(f"Loaded {len(from_names)} from names for rotation")
    
    def set_subjects(self, subjects: List[str]):
        """Set subject rotation list"""
        self.subjects = subjects
        logger.info(f"Loaded {len(subjects)} subjects for rotation")
    
    def get_next_smtp(self) -> SMTPConfig:
        """Get next SMTP server for rotation"""
        if not self.smtp_configs:
            raise Exception("No SMTP servers configured")
        
        config = self.smtp_configs[self.current_smtp_index]
        self.current_smtp_index = (self.current_smtp_index + 1) % len(self.smtp_configs)
        return config
    
    def get_next_from_email(self) -> str:
        """Get next from email for rotation"""
        if not self.from_emails:
            return ""
        
        from_email = self.from_emails[self.current_smtp_index % len(self.from_emails)]
        return from_email
    
    def get_next_from_name(self) -> str:
        """Get next from name for rotation"""
        if not self.from_names:
            return ""
        
        from_name = self.from_names[self.current_smtp_index % len(self.from_names)]
        return from_name
    
    def get_next_subject(self, base_subject: str) -> str:
        """Get next subject for rotation"""
        if not self.subjects:
            return base_subject
        
        subject = self.subjects[self.current_smtp_index % len(self.subjects)]
        return subject
    
    def test_smtp_connection(self, smtp_config: SMTPConfig) -> Dict[str, Any]:
        """Test SMTP connection and return result"""
        try:
            with smtplib.SMTP(smtp_config.host, smtp_config.port, timeout=10) as server:
                if smtp_config.use_tls:
                    server.starttls()
                server.login(smtp_config.username, smtp_config.password)
                return {'success': True, 'message': 'Connection successful'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def send_email(self, to_email: str, template: EmailTemplate, personalization: Optional[Dict] = None) -> bool:
        """Send a single email using HTML template with proper formatting"""
        try:
            # Get SMTP config
            smtp_config = self.get_next_smtp()
            
            # Get from email, from name and subject  
            from_email = self.get_next_from_email() or smtp_config.username
            from_name = self.get_next_from_name() or template.from_name
            subject = self.get_next_subject(template.subject)
            
            # Apply personalization to subject
            if personalization:
                subject = subject.format(**personalization)
            
            # Get HTML content from template and apply personalization
            html_content = template.html_body
            if personalization:
                try:
                    html_content = html_content.format(**personalization)
                except KeyError as e:
                    # If some keys are missing, use default values
                    safe_personalization = {
                        'name': personalization.get('name', 'Valued Customer'),
                        **personalization
                    }
                    html_content = html_content.format(**safe_personalization)
            else:
                # Default personalization if none provided
                html_content = html_content.format(name='Valued Customer')
            
            # Create multipart message for HTML email
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{from_name} <{from_email}>"
            msg['To'] = to_email
            msg['Message-ID'] = f"<{time.time()}.{hash(to_email)}@{smtp_config.host}>"
            
            # Create plain text version as fallback
            plain_text = f"""
Hello {personalization.get('name', 'Valued Customer') if personalization else 'Valued Customer'},

You have received an important document review notice.

Please access your secure account portal to view your document.

Best regards,
{from_name}
"""
            
            # Create HTML and text parts
            text_part = MIMEText(plain_text, 'plain', 'utf-8')
            html_part = MIMEText(html_content, 'html', 'utf-8')
            
            # Attach parts to message
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(smtp_config.host, smtp_config.port) as server:
                if smtp_config.use_tls:
                    server.starttls()
                server.login(smtp_config.username, smtp_config.password)
                server.send_message(msg)
            
            self.sent_emails.append(to_email)
            logger.info(f"HTML email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            self.failed_emails.append({'email': to_email, 'error': str(e)})
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_bulk_emails(self, email_list: List[str], template: EmailTemplate, 
                        personalization_data: Dict = {}, delay_between_emails: float = 1.0,
                        progress_callback=None) -> Dict:
        """Send emails to multiple recipients"""
        total_emails = len(email_list)
        sent_count = 0
        failed_count = 0
        
        logger.info(f"Starting bulk email send to {total_emails} recipients")
        
        for i, email in enumerate(email_list):
            try:
                # Get personalization for this email
                personalization = personalization_data.get(email, {}) if personalization_data else {}
                
                # Send email
                success = self.send_email(email, template, personalization)
                
                if success:
                    sent_count += 1
                else:
                    failed_count += 1
                
                # Progress callback
                if progress_callback:
                    status_message = "Sent successfully" if success else "Failed to send"
                    progress_callback(i + 1, total_emails, success, email, status_message)
                
                # Delay between emails
                if i < total_emails - 1:  # Don't delay after the last email
                    time.sleep(delay_between_emails)
                    
            except KeyboardInterrupt:
                logger.info("Bulk email sending interrupted by user")
                break
            except Exception as e:
                failed_count += 1
                logger.error(f"Unexpected error sending to {email}: {str(e)}")
        
        # Return results
        results = {
            'total_emails': total_emails,
            'sent_count': sent_count,
            'failed_count': failed_count,
            'success_rate': (sent_count / total_emails * 100) if total_emails > 0 else 0
        }
        
        logger.info(f"Bulk email completed: {sent_count}/{total_emails} sent successfully")
        return results
    
    def get_stats(self) -> Dict:
        """Get sending statistics"""
        total_sent = len(self.sent_emails)
        total_failed = len(self.failed_emails)
        total_emails = total_sent + total_failed
        
        return {
            'total_sent': total_sent,
            'total_failed': total_failed,
            'total_emails': total_emails,
            'success_rate': (total_sent / total_emails * 100) if total_emails > 0 else 0
        }

# =============================================================================
# CONFIGURATION MANAGER CLASS
# =============================================================================

class ConfigManager:
    """Manages configuration files for the email marketing system"""
    
    def __init__(self):
        self.smtp_file = "smtps.txt"
        self.emails_file = "emails.txt"
        self.template_file = "htmlletter.html"
        self.frommails_file = "frommails.txt"
        self.fromnames_file = "fromname.txt"
        self.subjects_file = "subject.txt"
    
    def load_smtp_configs(self) -> List[Dict]:
        """Load SMTP configurations from smtps.txt file"""
        configs = []
        
        if not os.path.exists(self.smtp_file):
            print(f"{Fore.YELLOW}⚠️  Warning: {self.smtp_file} not found. Creating sample file...")
            self.create_sample_smtp_file()
            return configs
        
        try:
            with open(self.smtp_file, 'r') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                try:
                    parts = line.split('|')
                    if len(parts) < 4:
                        print(f"{Fore.RED}❌ Error on line {line_num}: Invalid format - need at least 4 fields")
                        continue
                    
                    host = parts[0]
                    port = parts[1]
                    username = parts[2]
                    password = parts[3]
                    
                    # Check if TLS setting is specified
                    use_tls = True  # default
                    if len(parts) >= 5:
                        tls_setting = parts[4].lower().strip()
                        use_tls = tls_setting in ['true', 'yes', '1', 'on']
                    
                    config = {
                        'host': host,
                        'port': int(port),
                        'username': username,
                        'password': password,
                        'use_tls': use_tls,
                        'max_emails_per_hour': 100,
                        'from_email': username
                    }
                    configs.append(config)
                    print(f"{Fore.GREEN}😈 Demon SMTP: {config['host']} ({config['username']})")
                    
                except (ValueError, IndexError) as e:
                    print(f"{Fore.RED}❌ Error parsing line {line_num}: {str(e)}")
                    continue
            
            print(f"\n{Fore.CYAN}👹 Total demon servers loaded: {len(configs)}")
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error reading {self.smtp_file}: {str(e)}")
        
        return configs
    
    def load_email_list(self) -> List[str]:
        """Load email list from emails.txt file"""
        emails = []
        
        if not os.path.exists(self.emails_file):
            print(f"{Fore.YELLOW}⚠️  Warning: {self.emails_file} not found. Creating sample file...")
            self.create_sample_emails_file()
            return emails
        
        try:
            with open(self.emails_file, 'r') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Basic email validation
                if '@' in line and '.' in line.split('@')[1]:
                    emails.append(line)
                    if len(emails) <= 5:  # Show first 5 emails only
                        print(f"{Fore.GREEN}🎯 Target: {line}")
                else:
                    print(f"{Fore.RED}❌ Invalid email on line {line_num}: {line}")
            
            if len(emails) > 5:
                print(f"{Fore.GREEN}📧 ... and {len(emails) - 5} more emails")
            
            print(f"\n{Fore.CYAN}🎯 Total targets loaded: {len(emails)}")
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error reading {self.emails_file}: {str(e)}")
        
        return emails
    
    def load_from_emails(self) -> List[str]:
        """Load from email addresses from frommails.txt file"""
        from_emails = []
        
        if not os.path.exists(self.frommails_file):
            print(f"{Fore.YELLOW}⚠️  Warning: {self.frommails_file} not found. Creating sample file...")
            self.create_sample_frommails_file()
            return from_emails
        
        try:
            with open(self.frommails_file, 'r') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Extract just the email part (before | if exists)
                email = line.split('|')[0].strip()
                
                if '@' in email and '.' in email.split('@')[1]:
                    from_emails.append(email)
                    if len(from_emails) <= 5:
                        print(f"{Fore.GREEN}😈 Demon Email: {email}")
                else:
                    print(f"{Fore.RED}❌ Invalid email on line {line_num}: {line}")
            
            if len(from_emails) > 5:
                print(f"{Fore.GREEN}😈 ... and {len(from_emails) - 5} more demon emails")
            
            print(f"\n{Fore.CYAN}👹 Total demon emails loaded: {len(from_emails)}")
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error reading {self.frommails_file}: {str(e)}")
        
        return from_emails
    
    def load_from_names(self) -> List[str]:
        """Load from names from fromname.txt file"""
        from_names = []
        
        if not os.path.exists(self.fromnames_file):
            print(f"{Fore.YELLOW}⚠️  Warning: {self.fromnames_file} not found. Creating sample file...")
            self.create_sample_fromnames_file()
            return from_names
        
        try:
            with open(self.fromnames_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                from_names.append(line)
                if len(from_names) <= 5:
                    print(f"{Fore.GREEN}😈 Demon Name: {line}")
            
            if len(from_names) > 5:
                print(f"{Fore.GREEN}😈 ... and {len(from_names) - 5} more demon names")
            
            print(f"\n{Fore.CYAN}👹 Total demon names loaded: {len(from_names)}")
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error reading {self.fromnames_file}: {str(e)}")
        
        return from_names
    
    def load_subjects(self) -> List[str]:
        """Load subject variations from subject.txt file"""
        subjects = []
        
        if not os.path.exists(self.subjects_file):
            print(f"{Fore.YELLOW}⚠️  Warning: {self.subjects_file} not found. Creating sample file...")
            self.create_sample_subjects_file()
            return subjects
        
        try:
            with open(self.subjects_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                subjects.append(line)
                if len(subjects) <= 5:  # Show first 5 subjects
                    print(f"{Fore.GREEN}🔥 Demon Subject: {line}")
            
            if len(subjects) > 5:
                print(f"{Fore.GREEN}🔥 ... and {len(subjects) - 5} more demon subjects")
            
            print(f"\n{Fore.CYAN}👹 Total demon subjects loaded: {len(subjects)}")
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error reading {self.subjects_file}: {str(e)}")
        
        return subjects
    
    def load_email_template(self) -> Optional[EmailTemplate]:
        """Load email template from htmlletter.html file"""
        if not os.path.exists(self.template_file):
            print(f"{Fore.YELLOW}⚠️  Warning: {self.template_file} not found. Creating sample file...")
            self.create_sample_template_file()
            return None
        
        try:
            with open(self.template_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Extract subject from HTML if present
            subject_match = html_content.find('<title>')
            if subject_match != -1:
                subject_end = html_content.find('</title>', subject_match)
                subject = html_content[subject_match + 7:subject_end].strip()
            else:
                subject = "Newsletter - {name}"
            
            # Extract from name from HTML if present
            from_name_match = re.search(r'<!--\s*from_name:\s*(.*?)\s*-->', html_content)
            if from_name_match:
                from_name = from_name_match.group(1).strip()
            else:
                from_name = "Newsletter Team"
            
            template = EmailTemplate(
                subject=subject,
                html_body=html_content,
                from_name=from_name
            )
            
            print(f"{Fore.GREEN}😈 Demon template loaded successfully")
            print(f"{Fore.BLUE}🔥 Demon Subject: {subject}")
            print(f"{Fore.BLUE}👤 Default From Name: {from_name}")
            
            return template
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error reading {self.template_file}: {str(e)}")
            return None
    
    # Create sample files methods
    def create_sample_smtp_file(self):
        """Create a sample SMTP configuration file"""
        sample_content = """# SMTP Configuration File
# Format: host|port|username|password|tls_enabled
# tls_enabled: true/false (optional, defaults to true)

# Gmail SMTP (requires app password)
# smtp.gmail.com|587|your-email@gmail.com|your-app-password|true

# Outlook/Hotmail SMTP
# smtp-mail.outlook.com|587|your-email@outlook.com|your-password|true

# Yahoo SMTP
# smtp.mail.yahoo.com|587|your-email@yahoo.com|your-password|true

# Example with TLS disabled
# mail.example.com|25|user@example.com|password|false

# Add your SMTP servers here:
mail.example.com|587|user@example.com|password123|true
"""
        try:
            with open(self.smtp_file, 'w') as f:
                f.write(sample_content)
            print(f"{Fore.GREEN}✅ Created sample {self.smtp_file} file")
        except Exception as e:
            print(f"{Fore.RED}❌ Error creating {self.smtp_file}: {str(e)}")
    
    def create_sample_emails_file(self):
        """Create a sample emails file"""
        sample_content = """# Email Recipients File
# One email address per line
# Lines starting with # are comments

test1@example.com
test2@example.com
test3@example.com
"""
        try:
            with open(self.emails_file, 'w') as f:
                f.write(sample_content)
            print(f"{Fore.GREEN}✅ Created sample {self.emails_file} file")
        except Exception as e:
            print(f"{Fore.RED}❌ Error creating {self.emails_file}: {str(e)}")
    
    def create_sample_template_file(self):
        """Create a sample HTML template file"""
        sample_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome Newsletter - {name}</title>
    <!-- from_name: Newsletter Team -->
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #007bff; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background: #f9f9f9; }
        .footer { background: #333; color: white; padding: 15px; text-align: center; font-size: 12px; }
        .btn { display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Hello {name}!</h1>
            <p>Welcome to our newsletter</p>
        </div>
        
        <div class="content">
            <h2>Dear {name},</h2>
            <p>Thank you for subscribing to our newsletter. We're excited to share updates with you!</p>
            
            <p>Here's what you can expect:</p>
            <ul>
                <li>Weekly industry insights</li>
                <li>Exclusive offers and deals</li>
                <li>Product updates and announcements</li>
            </ul>
            
            <p style="text-align: center; margin: 30px 0;">
                <a href="https://example.com" class="btn">Visit Our Website</a>
            </p>
        </div>
        
        <div class="footer">
            <p>© 2025 Your Company Name. All rights reserved.</p>
            <p>You received this email because you subscribed to our newsletter.</p>
        </div>
    </div>
</body>
</html>"""
        try:
            with open(self.template_file, 'w', encoding='utf-8') as f:
                f.write(sample_content)
            print(f"{Fore.GREEN}✅ Created sample {self.template_file} file")
        except Exception as e:
            print(f"{Fore.RED}❌ Error creating {self.template_file}: {str(e)}")
    
    def create_sample_frommails_file(self):
        """Create a sample from emails file"""
        sample_content = """# From Email Rotation File
# One email per line for rotating sender addresses
# Lines starting with # are comments
# Format: email@domain.com|Display Name (optional)

# Professional business emails
sales@company.com
support@business.com
info@enterprise.com
marketing@corp.com
no-reply@service.com

# Newsletter variations
newsletter@updates.com
news@insights.com
alerts@notifications.com
digest@summary.com
bulletin@announcements.com
"""
        
        try:
            with open(self.frommails_file, 'w') as f:
                f.write(sample_content)
            print(f"{Fore.GREEN}✅ Created sample {self.frommails_file} file")
        except Exception as e:
            print(f"{Fore.RED}❌ Error creating {self.frommails_file}: {str(e)}")
    
    def create_sample_fromnames_file(self):
        """Create a sample from names file"""
        sample_content = """# From Name Rotation File
# One name per line for rotating sender names
# Lines starting with # are comments

# Professional business names
Sales Department
Customer Support Team
Information Desk
Marketing Team
Service Notifications

# Newsletter variations
Weekly Updates Team
Industry Insights
Alert System
Daily Digest
Announcements Bulletin
"""
        
        try:
            with open(self.fromnames_file, 'w', encoding='utf-8') as f:
                f.write(sample_content)
            print(f"{Fore.GREEN}✅ Created sample {self.fromnames_file} file")
        except Exception as e:
            print(f"{Fore.RED}❌ Error creating {self.fromnames_file}: {str(e)}")
    
    def create_sample_subjects_file(self):
        """Create a sample subjects file"""
        sample_content = """# Subject Line Rotation File
# One subject per line for rotating email subjects
# Lines starting with # are comments
# Use {name} for personalization

# Professional newsletter subjects
Welcome to our exclusive community, {name}!
Your weekly insights are here, {name}
{name}, don't miss this week's update
Special newsletter just for you, {name}
{name}, your personalized digest has arrived

# Promotional subjects
Exclusive offer inside, {name}
{name}, limited time deal alert
Your special discount awaits, {name}
{name}, member-only access granted
Don't miss out, {name}

# Informational subjects
Important updates for you, {name}
{name}, your monthly report is ready
Latest news and trends, {name}
{name}, here's what's new
Your customized briefing, {name}

# Engagement subjects
We missed you, {name}
{name}, let's catch up
Your feedback matters, {name}
{name}, join the conversation
Thanks for being awesome, {name}
"""
        
        try:
            with open(self.subjects_file, 'w', encoding='utf-8') as f:
                f.write(sample_content)
            print(f"{Fore.GREEN}✅ Created sample {self.subjects_file} file")
        except Exception as e:
            print(f"{Fore.RED}❌ Error creating {self.subjects_file}: {str(e)}")

# =============================================================================
# MAIN APPLICATION CLASS
# =============================================================================

class ZShellMailer:
    """👹 Main ZShell Mailer application class with demonic powers"""
    
    def __init__(self):
        self.mailer = SimpleMailer()
        self.config_manager = ConfigManager()
        self.template = None
        self.email_list = []
        self.smtp_configs = []
        self.from_emails = []
        self.from_names = []
        self.subjects = []
    
    def display_banner(self):
        """Display the ZShell Mailer banner"""
        banner = f"""
{Fore.RED}███████╗███████╗██╗  ██╗███████╗██╗     ██╗         
╚══███╔╝██╔════╝██║  ██║██╔════╝██║     ██║         
  ███╔╝ ███████╗███████║█████╗  ██║     ██║         
 ███╔╝  ╚════██║██╔══██║██╔══╝  ██║     ██║         
███████╗███████║██║  ██║███████╗███████╗███████╗    
╚══════╝╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝    

{Fore.YELLOW}███╗   ███╗ █████╗ ██╗██╗     ███████╗██████╗ 
████╗ ████║██╔══██╗██║██║     ██╔════╝██╔══██╗
██╔████╔██║███████║██║██║     █████╗  ██████╔╝
██║╚██╔╝██║██╔══██║██║██║     ██╔══╝  ██╔══██╗
██║ ╚═╝ ██║██║  ██║██║███████╗███████╗██║  ██║
╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚═╝  ╚═╝

                {Fore.CYAN}👹 ZShell Mailer v2.0 👹
        {Fore.GREEN}🔥 Simple Email Marketing Power 🔥
        {Fore.MAGENTA}😈 Portable Single-File Version 😈
{Style.RESET_ALL}
"""
        print(banner)
    
    def load_configurations(self) -> bool:
        """Load all configuration files"""
        try:
            print(f"\n{Fore.CYAN}⚙️ Loading Configurations")
            print("─" * 25)
            
            # Load SMTP configurations
            self.smtp_configs = self.config_manager.load_smtp_configs()
            if not self.smtp_configs:
                print(f"{Fore.RED}❌ No valid SMTP configurations found")
                return False
            
            # Load email list
            self.email_list = self.config_manager.load_email_list()
            if not self.email_list:
                print(f"{Fore.RED}❌ No valid emails found")
                return False
            
            # Load from emails rotation
            self.from_emails = self.config_manager.load_from_emails()
            if self.from_emails:
                self.mailer.set_from_emails(self.from_emails)
            
            # Load from names rotation
            self.from_names = self.config_manager.load_from_names()
            if self.from_names:
                self.mailer.set_from_names(self.from_names)
            
            # Load subjects rotation
            self.subjects = self.config_manager.load_subjects()
            if self.subjects:
                self.mailer.set_subjects(self.subjects)
            
            # Load email template
            self.template = self.config_manager.load_email_template()
            if not self.template:
                print(f"{Fore.RED}❌ No valid email template found")
                return False
            
            print(f"{Fore.GREEN}😈 All configurations loaded successfully!")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Failed to load configurations: {str(e)}")
            return False
    
    def send_bulk_emails(self):
        """Send bulk emails with progress tracking"""
        if not self.template or not self.email_list:
            print(f"{Fore.RED}❌ Configurations not loaded. Please load configurations first.")
            return
        
        # Show sending header
        print(f"\n{Fore.CYAN}============================================================")
        print(f"                {Fore.RED}👹 ZSHELL DEMON SENDING 👹")
        print(f"{Fore.CYAN}============================================================")
        print(f"{Fore.BLUE}👹 Total souls to harvest: {len(self.email_list)}")
        print(f"{Fore.YELLOW}🔥 Hell opened at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{Fore.CYAN}{'─' * 60}")
        
        # Confirm action
        confirm = input(f"\n{Fore.RED}🔥 Start bulk sending? (y/N): ").lower()
        if confirm != 'y':
            print(f"{Fore.YELLOW}👹 Sending cancelled by demon master")
            return
        
        # Get sending parameters
        try:
            delay = input(f"{Fore.CYAN}⏱️  Delay between emails in seconds (default 1.0): ").strip()
            delay = float(delay) if delay else 1.0
            
            # TLS choice
            tls_choice = input(f"{Fore.CYAN}🔒 Use TLS/SSL? (y/n, default y): ").strip().lower()
            use_tls = tls_choice not in ['n', 'no', 'false', '0']
            
            print(f"{Fore.BLUE}🔧 TLS/SSL: {'Enabled' if use_tls else 'Disabled'}")
            
        except ValueError:
            delay = 1.0
            use_tls = True
        
        # Create personalization data (extract names from emails)
        personalization_data = {}
        for email in self.email_list:
            name = email.split('@')[0].replace('.', ' ').replace('_', ' ').title()
            personalization_data[email] = {'name': name}
        
        # Clear and rebuild SMTP servers with user's TLS choice
        self.mailer.smtp_configs = []
        for config in self.smtp_configs:
            self.mailer.add_smtp_server(
                config['host'],
                config['port'],
                config['username'],
                config['password'],
                use_tls  # Use user's choice instead of config file
            )
        
        # Create progress bar
        progress_bar = ProgressBar(len(self.email_list))
        
        def progress_callback(current, total, success, email, message):
            progress_bar.update(current, success, email, message)
        
        # Start sending
        print(f"\n{Fore.GREEN}{Style.BRIGHT}🚀 Starting bulk email sending...")
        print(f"{Fore.BLUE}⚙️  Settings: {delay}s delay, TLS: {'On' if use_tls else 'Off'}")
        
        try:
            results = self.mailer.send_bulk_emails(
                self.email_list,
                self.template,
                personalization_data,
                delay_between_emails=delay,
                progress_callback=progress_callback
            )
            
            # Show summary
            print(f"\n\n{Fore.CYAN}============================================================")
            print(f"                {Fore.GREEN}👹 DEMON SENDING COMPLETE 👹")
            print(f"{Fore.CYAN}============================================================")
            print(f"{Fore.GREEN}✅ Total emails sent: {results['sent_count']}")
            print(f"{Fore.RED}❌ Failed emails: {results['failed_count']}")
            print(f"{Fore.YELLOW}📊 Success rate: {results['success_rate']:.1f}%")
            print(f"{Fore.BLUE}📧 Total processed: {results['total_emails']}")
            print(f"{Fore.CYAN}{'─' * 60}")
            
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}⚠️  Email sending interrupted by user")
        except Exception as e:
            print(f"\n{Fore.RED}❌ Error during bulk sending: {str(e)}")
    
    def test_smtp_connections(self):
        """Test all SMTP connections"""
        if not self.smtp_configs:
            print(f"{Fore.RED}❌ No SMTP configurations loaded")
            return
        
        print(f"\n{Fore.CYAN}🔧 Testing SMTP Connections")
        print("─" * 30)
        
        for i, config in enumerate(self.smtp_configs, 1):
            print(f"{Fore.BLUE}Testing {i}: {config['host']}:{config['port']}...")
            
            smtp_config = SMTPConfig(
                config['host'],
                config['port'],
                config['username'],
                config['password'],
                config['use_tls']
            )
            
            result = self.mailer.test_smtp_connection(smtp_config)
            
            if result['success']:
                print(f"{Fore.GREEN}✅ Connection successful")
            else:
                print(f"{Fore.RED}❌ Connection failed: {result['message']}")
            print()
    
    def view_statistics(self):
        """View sending statistics"""
        print(f"\n{Fore.CYAN}📊 System Statistics")
        print("─" * 20)
        
        stats = self.mailer.get_stats()
        
        print(f"{Fore.GREEN}✅ Total emails sent: {stats['total_sent']}")
        print(f"{Fore.RED}❌ Total failed: {stats['total_failed']}")
        print(f"{Fore.BLUE}📧 Total processed: {stats['total_emails']}")
        print(f"{Fore.YELLOW}📊 Success rate: {stats['success_rate']:.1f}%")
        
        # Configuration status
        print(f"\n{Fore.CYAN}⚙️ Configuration Status:")
        print(f"{Fore.BLUE}📧 Emails loaded: {len(self.email_list)}")
        print(f"{Fore.GREEN}✉️  Template loaded: {'Yes' if self.template else 'No'}")
        print(f"{Fore.YELLOW}🌐 SMTP servers: {len(self.smtp_configs)}")
        print(f"{Fore.MAGENTA}📧 From emails: {len(self.from_emails)}")
        print(f"{Fore.CYAN}👤 From names: {len(self.from_names)}")
        print(f"{Fore.CYAN}📝 Subject variations: {len(self.subjects)}")
    
    def view_configuration_status(self):
        """View current configuration status"""
        print(f"\n{Fore.CYAN}⚙️ Configuration Status")
        print("─" * 25)
        
        # SMTP Status
        if self.smtp_configs:
            print(f"{Fore.GREEN}✅ SMTP servers loaded: {len(self.smtp_configs)}")
            for i, config in enumerate(self.smtp_configs[:3], 1):
                print(f"  {Fore.BLUE}{i}. {config['host']}:{config['port']} ({config['username']})")
            if len(self.smtp_configs) > 3:
                print(f"  {Fore.YELLOW}... and {len(self.smtp_configs) - 3} more servers")
        else:
            print(f"{Fore.RED}❌ No SMTP servers loaded")
        
        # Email list status
        print(f"\n{Fore.CYAN}📧 Email List Status:")
        if self.email_list:
            print(f"{Fore.GREEN}✅ {len(self.email_list)} emails loaded")
            for email in self.email_list[:5]:
                print(f"  {Fore.BLUE}• {email}")
            if len(self.email_list) > 5:
                print(f"  {Fore.YELLOW}... and {len(self.email_list) - 5} more")
        else:
            print(f"{Fore.RED}❌ No emails loaded")
        
        # Template status
        print(f"\n{Fore.CYAN}📝 Template Status:")
        if self.template:
            print(f"{Fore.GREEN}✅ Template loaded")
            print(f"  {Fore.BLUE}📄 Subject: {self.template.subject}")
            print(f"  {Fore.BLUE}👤 From: {self.template.from_name}")
        else:
            print(f"{Fore.RED}❌ No template loaded")
    
    def view_sample_files(self):
        """View sample configuration files"""
        print(f"\n{Fore.CYAN}📝 Configuration Files")
        print("─" * 25)
        
        files = [
            ("smtps.txt", "SMTP server configurations"),
            ("emails.txt", "Email recipient list"),
            ("frommails.txt", "From email addresses"),
            ("fromname.txt", "From name variations"),
            ("subject.txt", "Subject line variations"),
            ("htmlletter.html", "Email template")
        ]
        
        for filename, description in files:
            if os.path.exists(filename):
                file_size = os.path.getsize(filename)
                print(f"{Fore.GREEN}✅ {filename} - {description} ({file_size} bytes)")
            else:
                print(f"{Fore.RED}❌ {filename} - {description} (missing)")
        
        print(f"\n{Fore.BLUE}💡 Tip: Edit these files to customize your email campaign")
    
    def show_menu(self):
        """Display the main menu"""
        print(f"\n{Fore.CYAN}============================================================")
        print(f"                {Fore.RED}👹 ZSHELL DEMON MENU 👹")
        print(f"{Fore.CYAN}============================================================")
        print(f"{Fore.GREEN}[1] {Fore.RED}👹 Send Bulk Emails")
        print(f"{Fore.GREEN}[2] {Fore.BLUE}🔧 Test SMTP Connection")
        print(f"{Fore.GREEN}[3] {Fore.YELLOW}📊 View Statistics")
        print(f"{Fore.GREEN}[4] {Fore.CYAN}😈 Configuration Status")
        print(f"{Fore.GREEN}[5] {Fore.MAGENTA}📝 View Sample Files")
        print(f"{Fore.GREEN}[6] {Fore.WHITE}💀 Exit ZShell")
        print(f"{Fore.CYAN}============================================================")
    
    def run(self):
        """Main application loop"""
        self.display_banner()
        
        # Load configurations on startup
        if not self.load_configurations():
            print(f"{Fore.RED}❌ Failed to load configurations. Please check your config files.")
            return
        
        while True:
            self.show_menu()
            
            try:
                choice = input(f"\nSelect option (1-6): ").strip()
                
                if choice == '1':
                    self.send_bulk_emails()
                elif choice == '2':
                    self.test_smtp_connections()
                elif choice == '3':
                    self.view_statistics()
                elif choice == '4':
                    self.view_configuration_status()
                elif choice == '5':
                    self.view_sample_files()
                elif choice == '6':
                    print(f"{Fore.RED}👹 ZShell Mailer closing... Farewell, demon master!")
                    break
                else:
                    print(f"{Fore.RED}❌ Invalid choice. Please select 1-6.")
                    
            except KeyboardInterrupt:
                print(f"\n{Fore.RED}👹 ZShell Mailer interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"{Fore.RED}❌ Unexpected error: {str(e)}")

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    try:
        app = ZShellMailer()
        app.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}👹 ZShell Mailer terminated. Until we meet again!")
    except Exception as e:
        print(f"{Fore.RED}💀 Fatal error: {str(e)}")
        sys.exit(1)