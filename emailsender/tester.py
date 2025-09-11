#!/usr/bin/env python3
"""
SMTP Server Tester
Tests all SMTP servers and saves working ones to good.txt
"""

import smtplib
import time
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from colorama import Fore, Back, Style, init
from config_manager import ConfigManager
from advanced_mailer import AdvancedMailer
import socket
import dns.resolver
import logging
import random

# Initialize colorama
init(autoreset=True)

class SMTPTester:
    """Test SMTP servers and save working ones"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.advanced_mailer = AdvancedMailer()
        self.test_emails = []
        self.working_servers = []
        self.failed_servers = []
        self.lock = threading.Lock()
        self.test_count = 0
        self.html_template = None
        self.debug_mode = False
        self.setup_debug_logging()
    
    def print_banner(self):
        """Print tester banner"""
        print(f"""
{Fore.CYAN}{Style.BRIGHT}
╔═══════════════════════════════════════════╗
║           📧 SMTP SERVER TESTER 📧        ║
║        🔍 Testing Email Connections 🔍    ║
╚═══════════════════════════════════════════╝
{Style.RESET_ALL}""")
    
    def load_html_template(self):
        """Load the HTML template for testing"""
        try:
            self.html_template = self.config_manager.load_email_template()
            if self.html_template:
                print(f"{Fore.GREEN}✅ HTML template loaded for testing: {self.html_template.subject}")
                return True
            else:
                print(f"{Fore.YELLOW}⚠️  No HTML template found, using simple text message")
                return False
        except Exception as e:
            print(f"{Fore.RED}❌ Failed to load HTML template: {str(e)}")
            return False
    
    def setup_debug_logging(self):
        """Setup enhanced debugging for email delivery"""
        self.debug_logger = logging.getLogger('smtp_debug')
        self.debug_logger.setLevel(logging.DEBUG)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('🔍 %(asctime)s - %(message)s', '%H:%M:%S')
        console_handler.setFormatter(formatter)
        self.debug_logger.handlers.clear()
        self.debug_logger.addHandler(console_handler)
    
    def verify_email_deliverability(self, email: str) -> dict:
        """Enhanced email deliverability verification"""
        result = {
            'email': email,
            'deliverable': False,
            'mx_valid': False,
            'smtp_response': '',
            'score': 0
        }
        
        try:
            domain = email.split('@')[1] if '@' in email else ''
            if not domain:
                return result
                
            # Check MX records
            mx_records = dns.resolver.resolve(domain, 'MX')
            if mx_records:
                result['mx_valid'] = True
                result['score'] += 30
                
                # Try SMTP connection
                for mx in mx_records[:2]:  # Try first 2 MX servers
                    try:
                        mx_host = str(mx).split(' ')[1].rstrip('.')
                        server = smtplib.SMTP(mx_host, timeout=10)
                        server.ehlo()
                        
                        # Test mail acceptance
                        code, response = server.mail('test@verifier.local')
                        if code == 250:
                            code, response = server.rcpt(email)
                            if code in [250, 251, 252]:
                                result['deliverable'] = True
                                result['score'] += 70
                                result['smtp_response'] = 'Accepts mail'
                            else:
                                result['smtp_response'] = f'Rejects: {response.decode()}'
                        server.quit()
                        break
                    except:
                        continue
        except:
            pass
            
        return result
        """Check email domain and MX records for deliverability issues"""
        try:
            domain = email.split('@')[1]
            try:
                mx_records = dns.resolver.resolve(domain, 'MX')
                mx_list = [str(mx) for mx in mx_records]
                mx_status = f"✅ Found {len(mx_list)} MX records"
            except Exception as e:
                mx_status = f"❌ No MX records found: {e}"
                mx_list = []
            try:
                socket.gethostbyname(domain)
                domain_status = "✅ Domain resolves"
            except:
                domain_status = "❌ Domain does not resolve"
            return {
                'domain': domain,
                'mx_status': mx_status,
                'mx_records': mx_list,
                'domain_status': domain_status
            }
        except Exception as e:
            return {
                'domain': 'unknown',
                'mx_status': f"❌ Error: {e}",
                'mx_records': [],
                'domain_status': f"❌ Error: {e}"
            }
    
    def create_inbox_optimized_message(self, smtp_config: dict, test_email: str) -> MIMEMultipart:
        """Create inbox-optimized HTML email message using your htmlletter.html template"""
        if self.html_template:
            # Extract name from email for personalization
            test_name = test_email.split('@')[0].replace('.', ' ').replace('_', ' ').title()
            personalization = {
                'name': test_name,
                'tracking_id': f"test_{int(time.time())}_{smtp_config['host'].replace('.', '_')}"
            }
            
            # Add SMTP server info to personalization for testing identification
            server_info = f"Sent via {smtp_config['host']} at {time.strftime('%H:%M:%S')}"
            
            # Create highly optimized message for inbox delivery
            msg = self.advanced_mailer.create_optimized_message(
                test_email, 
                self.html_template, 
                personalization
            )
            
            # Override subject with test-specific subject that avoids spam triggers
            friendly_subjects = [
                f"Hello {test_name}! Newsletter Test from {smtp_config['host'].split('.')[0].title()}",
                f"Welcome {test_name} - Email Delivery Test",
                f"Hi {test_name}, Testing Email System",
                f"Greetings {test_name}! System Check"
            ]
            import random
            msg['Subject'] = random.choice(friendly_subjects)
            msg['From'] = smtp_config['from_email']
            
            # Add test identification in a hidden div within HTML
            html_body = str(msg.get_payload()[1].get_payload())
            test_marker = f'<!-- Test Email: {server_info} -->'
            html_body = html_body.replace('</body>', f'{test_marker}</body>')
            
            # Update the HTML part
            msg.get_payload()[1].set_payload(html_body)
            
            return msg
        else:
            # Enhanced fallback with better formatting
            msg = MIMEMultipart('alternative')
            msg['From'] = smtp_config['from_email']
            msg['To'] = test_email
            msg['Subject'] = f"Email System Test - {time.strftime('%H:%M:%S')}"
            
            # Create both text and simple HTML versions
            text_body = f"""
Hello,

This is a test email to verify email delivery.

Server Details:
- SMTP Host: {smtp_config['host']}
- Port: {smtp_config['port']}
- Test Time: {time.strftime('%Y-%m-%d %H:%M:%S')}

If you received this email, the SMTP configuration is working correctly.

Best regards,
Email System
            """
            
            simple_html = f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #4a90e2;">📧 Email System Test</h2>
        <p>Hello,</p>
        <p>This is a test email to verify email delivery.</p>
        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #666;">Server Details:</h3>
            <ul style="margin: 10px 0;">
                <li><strong>SMTP Host:</strong> {smtp_config['host']}</li>
                <li><strong>Port:</strong> {smtp_config['port']}</li>
                <li><strong>Test Time:</strong> {time.strftime('%Y-%m-%d %H:%M:%S')}</li>
            </ul>
        </div>
        <p>If you received this email, the SMTP configuration is working correctly.</p>
        <p style="color: #666; font-size: 14px;">Best regards,<br>Email System</p>
    </div>
</body>
</html>
            """
            
            # Attach both parts
            text_part = MIMEText(text_body, 'plain', 'utf-8')
            html_part = MIMEText(simple_html, 'html', 'utf-8')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            return msg
    
    def create_test_message(self, smtp_config: dict, test_email: str) -> MIMEMultipart:
        """Wrapper method that calls inbox-optimized message creation"""
        return self.create_inbox_optimized_message(smtp_config, test_email)
    
    def test_smtp_server_fast(self, smtp_config: dict, connection_only: bool = True) -> tuple[bool, str]:
        """Fast SMTP server test with retry logic for 421 errors"""
        max_retries = 3
        base_delay = 0.1  # Start with 100ms delay
        
        for attempt in range(max_retries):
            try:
                # Fast connection with short timeout
                if smtp_config['use_tls']:
                    server = smtplib.SMTP(smtp_config['host'], smtp_config['port'], timeout=5)
                    server.starttls()
                else:
                    server = smtplib.SMTP_SSL(smtp_config['host'], smtp_config['port'], timeout=5)
                
                # Test authentication
                server.login(smtp_config['username'], smtp_config['password'])
                
                if not connection_only:
                    # Optional: send actual test email (slower)
                    msg = self.create_test_message(smtp_config, self.test_emails[0] if self.test_emails else 'test@example.com')
                    server.sendmail(smtp_config['from_email'], self.test_emails[0] if self.test_emails else 'test@example.com', msg.as_string())
                
                server.quit()
                return True, "Connection and authentication successful"
                
            except smtplib.SMTPAuthenticationError as e:
                # Authentication errors are permanent, don't retry
                return False, f"Authentication failed: {str(e)}"
                
            except smtplib.SMTPConnectError as e:
                error_msg = f"Connection failed: {str(e)}"
                # Check for 421 errors (temporary failure)
                if "421" in str(e) and attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)  # Exponential backoff
                    time.sleep(delay)
                    continue
                return False, error_msg
                
            except Exception as e:
                error_msg = str(e)
                # Check for 421 errors in general exceptions
                if "421" in error_msg and attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)  # Exponential backoff
                    time.sleep(delay)
                    continue
                return False, f"Error: {error_msg}"
        
        return False, "Max retries exceeded"
    
    def test_single_server(self, config: dict, index: int, total: int) -> dict:
        """Test a single server (for parallel execution)"""
        with self.lock:
            self.test_count += 1
            current_test = self.test_count
        
        print(f"\n{Fore.BLUE}[{current_test}/{total}] 🔍 Testing {config['host']}:{config['port']} ({config['username']})...")
        
        success, message = self.test_smtp_server_fast(config, connection_only=True)
        
        result = {
            'config': config,
            'success': success,
            'message': message,
            'index': index
        }
        
        if success:
            print(f"{Fore.GREEN}✅ SUCCESS: {config['host']} is working!")
        else:
            print(f"{Fore.RED}❌ FAILED: {config['host']} - {message}")
        
        return result
    
    def test_all_servers_parallel(self, max_workers: int = 10):
        """Test all SMTP servers in parallel for maximum speed"""
        print(f"{Fore.CYAN}📧 Loading SMTP configurations...")
        smtp_configs = self.config_manager.load_smtp_configs()
        
        if not smtp_configs:
            print(f"{Fore.RED}❌ No SMTP configurations found in smtps.txt")
            return
        
        print(f"{Fore.CYAN}📧 Loading test email addresses...")
        self.test_emails = self.config_manager.load_email_list()
        
        print(f"{Fore.GREEN}✅ Found {len(smtp_configs)} SMTP servers to test")
        print(f"{Fore.CYAN}🚀 Using {max_workers} parallel connections for ultra-fast testing")
        print(f"{Fore.YELLOW}⚡ Testing mode: Connection + Authentication only (no emails sent)")
        
        try:
            confirm = input(f"{Fore.YELLOW}⚠️  Continue with fast parallel testing? (y/n): ").lower()
            if not confirm.startswith('y'):
                print(f"{Fore.YELLOW}🚫 Testing cancelled")
                return
        except EOFError:
            # Auto-continue in non-interactive mode
            print(f"{Fore.GREEN}🚀 Auto-starting fast tests in non-interactive mode...")
        
        print(f"\n{Fore.CYAN}{Style.BRIGHT}🚀 Starting Ultra-Fast Parallel SMTP Tests...")
        print("=" * 70)
        
        start_time = time.time()
        
        # Test servers in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_config = {
                executor.submit(self.test_single_server, config, i, len(smtp_configs)): config 
                for i, config in enumerate(smtp_configs, 1)
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_config):
                try:
                    result = future.result()
                    if result['success']:
                        self.working_servers.append(result['config'])
                    else:
                        self.failed_servers.append({'config': result['config'], 'error': result['message']})
                except Exception as e:
                    config = future_to_config[future]
                    print(f"{Fore.RED}❌ EXCEPTION: {config['host']} - {str(e)}")
                    self.failed_servers.append({'config': config, 'error': f"Exception: {str(e)}"})
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"\n{Fore.CYAN}{Style.BRIGHT}⚡ Testing completed in {total_time:.2f} seconds!")
        print(f"{Fore.GREEN}🚀 Average speed: {len(smtp_configs)/total_time:.1f} servers/second")
        
        self.show_results()
        self.save_working_servers()
    
    def test_all_servers(self):
        """Test all SMTP servers (legacy method - now calls parallel version)"""
        self.test_all_servers_parallel(max_workers=10)
    
    def show_results(self):
        """Show test results summary"""
        print(f"\n{Fore.CYAN}{Style.BRIGHT}📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        print(f"{Fore.GREEN}✅ Working Servers: {len(self.working_servers)}")
        for config in self.working_servers:
            print(f"   🔥 {config['host']} ({config['username']})")
        
        print(f"\n{Fore.RED}❌ Failed Servers: {len(self.failed_servers)}")
        for failed in self.failed_servers:
            config = failed['config']
            print(f"   💀 {config['host']} ({config['username']}) - {failed['error']}")
        
        success_rate = (len(self.working_servers) / (len(self.working_servers) + len(self.failed_servers))) * 100 if (self.working_servers or self.failed_servers) else 0
        print(f"\n{Fore.CYAN}📈 Success Rate: {success_rate:.1f}%")
    
    def save_working_servers(self):
        """Save working SMTP servers to good.txt"""
        if not self.working_servers:
            print(f"{Fore.YELLOW}⚠️  No working servers to save")
            return
        
        try:
            with open('good.txt', 'w') as f:
                f.write("# Working SMTP Servers - Tested and Verified\n")
                f.write("# Format: smtp|port|email|username|password\n")
                f.write(f"# Tested on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# Test emails sent to: {', '.join(self.test_emails)}\n\n")
                
                for config in self.working_servers:
                    line = f"{config['host']}|{config['port']}|{config['from_email']}|{config['username']}|{config['password']}"
                    f.write(line + "\n")
            
            print(f"\n{Fore.GREEN}{Style.BRIGHT}✅ Saved {len(self.working_servers)} working servers to good.txt")
            print(f"{Fore.CYAN}💡 You can now use good.txt as your SMTP configuration!")
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error saving to good.txt: {str(e)}")
    
    def run_fast_test(self, max_workers: int = 20):
        """Run ultra-fast SMTP testing without sending emails"""
        self.print_banner()
        print(f"{Fore.YELLOW}⚡ ULTRA-FAST MODE: Testing {max_workers} servers simultaneously")
        print(f"{Fore.CYAN}💪 No emails will be sent - connection + auth testing only")
        self.test_all_servers_parallel(max_workers=max_workers)
    
    def test_single_server_with_email(self, config: dict, index: int, total: int, test_email: str) -> dict:
        """Test a single server by actually sending an email (for parallel execution)"""
        with self.lock:
            self.test_count += 1
            current_test = self.test_count
        
        print(f"\n{Fore.BLUE}[{current_test}/{total}] 📧 Testing {config['host']}:{config['port']} ({config['username']}) - SENDING EMAIL...")
        
        success, message = self.test_smtp_server_with_email(config, test_email)
        
        result = {
            'config': config,
            'success': success,
            'message': message,
            'index': index
        }
        
        if success:
            print(f"{Fore.GREEN}✅ SUCCESS: {config['host']} - Email sent successfully!")
        else:
            print(f"{Fore.RED}❌ FAILED: {config['host']} - {message}")
        
        return result
    
    def test_smtp_server_with_email(self, smtp_config: dict, test_email: str) -> tuple[bool, str]:
        """Test SMTP server by actually sending an email with retry logic"""
        max_retries = 2
        base_delay = 0.5
        
        for attempt in range(max_retries):
            try:
                # Create test message
                msg = self.create_test_message(smtp_config, test_email)
                
                # Connect to SMTP server
                if smtp_config['use_tls']:
                    server = smtplib.SMTP(smtp_config['host'], smtp_config['port'], timeout=10)
                    server.starttls()
                else:
                    server = smtplib.SMTP_SSL(smtp_config['host'], smtp_config['port'], timeout=10)
                
                # Login
                server.login(smtp_config['username'], smtp_config['password'])
                
                # Send actual test email
                server.sendmail(smtp_config['from_email'], test_email, msg.as_string())
                server.quit()
                
                return True, "Email sent successfully"
                
            except smtplib.SMTPAuthenticationError as e:
                return False, f"Authentication failed: {str(e)}"
                
            except smtplib.SMTPConnectError as e:
                error_msg = f"Connection failed: {str(e)}"
                if "421" in str(e) and attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    time.sleep(delay)
                    continue
                return False, error_msg
                
            except Exception as e:
                error_msg = str(e)
                if "421" in error_msg and attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    time.sleep(delay)
                    continue
                return False, f"Error: {error_msg}"
        
        return False, "Max retries exceeded"
    
    def test_all_servers_with_email_fast(self, max_workers: int = 15):
        """Fast parallel testing with actual HTML email sending to one recipient"""
        print(f"{Fore.CYAN}📧 Loading SMTP configurations...")
        smtp_configs = self.config_manager.load_smtp_configs()
        
        if not smtp_configs:
            print(f"{Fore.RED}❌ No SMTP configurations found in smtps.txt")
            return
        
        print(f"{Fore.CYAN}📧 Loading test email addresses...")
        self.test_emails = self.config_manager.load_email_list()
        
        if not self.test_emails:
            print(f"{Fore.RED}❌ No email addresses found in emails.txt")
            return
        
        # Load HTML template for testing
        print(f"{Fore.CYAN}🎨 Loading your HTML letter template...")
        template_loaded = self.load_html_template()
        if template_loaded:
            print(f"{Fore.GREEN}✨ HTML letter loaded successfully - ready for inbox delivery testing!")
        else:
            print(f"{Fore.YELLOW}⚠️  Using fallback HTML template for testing")
        
        # Use only the first email for fast testing
        test_email = self.test_emails[0]
        
        print(f"{Fore.GREEN}✅ Found {len(smtp_configs)} SMTP servers to test")
        print(f"{Fore.CYAN}🚀 Using {max_workers} parallel connections for fast email testing")
        print(f"{Fore.YELLOW}📧 Test emails will be sent to: {test_email}")
        if self.html_template:
            print(f"{Fore.MAGENTA}🎨 Using your HTML letter: {self.html_template.subject}")
            print(f"{Fore.GREEN}✨ Inbox optimization: Anti-spam headers, content humanization, authentication spoofing")
            print(f"{Fore.BLUE}📱 Mobile-responsive design with personalization")
        else:
            print(f"{Fore.YELLOW}📝 Using enhanced HTML fallback template")
        
        try:
            confirm = input(f"{Fore.YELLOW}⚠️  Continue with fast email testing? (y/n): ").lower()
            if not confirm.startswith('y'):
                print(f"{Fore.YELLOW}🚫 Testing cancelled")
                return
        except EOFError:
            print(f"{Fore.GREEN}🚀 Auto-starting fast email tests in non-interactive mode...")
        
        print(f"\n{Fore.CYAN}{Style.BRIGHT}🚀 Starting Fast Parallel Email Tests...")
        print("=" * 70)
        
        start_time = time.time()
        
        # Test servers in parallel with actual email sending
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_config = {
                executor.submit(self.test_single_server_with_email, config, i, len(smtp_configs), test_email): config 
                for i, config in enumerate(smtp_configs, 1)
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_config):
                try:
                    result = future.result()
                    if result['success']:
                        self.working_servers.append(result['config'])
                    else:
                        self.failed_servers.append({'config': result['config'], 'error': result['message']})
                except Exception as e:
                    config = future_to_config[future]
                    print(f"{Fore.RED}❌ EXCEPTION: {config['host']} - {str(e)}")
                    self.failed_servers.append({'config': config, 'error': f"Exception: {str(e)}"})
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"\n{Fore.CYAN}{Style.BRIGHT}⚡ Email testing completed in {total_time:.2f} seconds!")
        print(f"{Fore.GREEN}🚀 Average speed: {len(smtp_configs)/total_time:.1f} servers/second")
        print(f"{Fore.MAGENTA}📧 Test emails sent to: {test_email}")
        if self.html_template:
            print(f"{Fore.BLUE}🎨 Your HTML letter delivered: {self.html_template.subject}")
            print(f"{Fore.GREEN}✨ Inbox delivery features applied: Content humanization, header spoofing, authentication")
            print(f"{Fore.CYAN}📱 Professional design with mobile responsiveness and personalization")
        else:
            print(f"{Fore.GREEN}✨ Enhanced HTML template sent with inbox optimization")
        
        self.show_results()
        self.save_working_servers()
    
    def run(self):
        """Run the SMTP tester with options"""
        self.print_banner()
        
        try:
            mode = input(f"{Fore.CYAN}Choose testing mode:\n1. ⚡ Ultra-Fast (no emails sent, 20 parallel)\n2. 🚀 Fast (no emails sent, 10 parallel)\n3. 🎨 HTML Letter Test (sends your htmlletter.html to hit inbox, 15 parallel)\n4. 📮 Standard (sends test emails, slower)\nEnter choice (1-4): ").strip()
            
            if mode == '1':
                self.run_fast_test(max_workers=20)
            elif mode == '2':
                self.test_all_servers_parallel(max_workers=10)
            elif mode == '3':
                self.test_all_servers_with_email_fast(max_workers=15)
            else:
                self.test_all_servers_parallel(max_workers=5)
                
        except EOFError:
            # Auto-run ultra-fast mode in non-interactive
            print(f"{Fore.GREEN}⚡ Auto-running ultra-fast mode...")
            self.run_fast_test(max_workers=20)

def main():
    """Main entry point"""
    try:
        tester = SMTPTester()
        tester.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}🚫 Testing interrupted by user")
    except Exception as e:
        print(f"{Fore.RED}💀 Error: {str(e)}")

if __name__ == "__main__":
    main()