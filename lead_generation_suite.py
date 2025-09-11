#!/usr/bin/env python3
"""
🎯 Complete Lead Generation Suite
Integration of email verification, scraping, and sending
"""

import sys
import os
from colorama import Fore, Back, Style, init
from datetime import datetime

# Initialize colorama
init(autoreset=True)

def print_suite_banner():
    """Print main suite banner"""
    banner = f"""
{Fore.GREEN}{Style.BRIGHT}
╔════════════════════════════════════════════════════════════╗
║              🎯 COMPLETE LEAD GENERATION SUITE 🎯         ║
║                                                            ║
║  📧 Email Verification  🌐 Lead Scraping  💌 Bulk Sending ║
║                                                            ║
║     Generate → Verify → Target → Send → Dominate          ║
╚════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
    """
    print(banner)

def show_workflow_guide():
    """Show recommended workflow"""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}📋 RECOMMENDED WORKFLOW")
    print("=" * 60)
    print(f"{Fore.YELLOW}1. 🌐 SCRAPE LEADS:")
    print(f"   → Use emailscraper.py to find professional emails")
    print(f"   → Target company websites, LinkedIn, directories")
    print(f"   → Generate high-quality corporate leads")
    
    print(f"\n{Fore.BLUE}2. 🔍 VERIFY EMAILS:")
    print(f"   → Use emailverifier.py to validate scraped emails")
    print(f"   → Check deliverability and lead quality")
    print(f"   → Filter out invalid/risky addresses")
    
    print(f"\n{Fore.GREEN}3. 💌 SEND CAMPAIGNS:")
    print(f"   → Use main.py (ZShell Mailer) for bulk sending")
    print(f"   → Automatically optimized for ISP providers")
    print(f"   → Track delivery and engagement rates")
    
    print(f"\n{Fore.MAGENTA}4. 📊 MONITOR & OPTIMIZE:")
    print(f"   → Review delivery statistics")
    print(f"   → Refine targeting based on results")
    print(f"   → Continuously improve lead quality")

def run_email_verifier():
    """Run email verification tool"""
    print(f"\n{Fore.BLUE}🔍 Starting Email Verifier...")
    os.system('python emailverifier.py')

def run_email_scraper():
    """Run email scraping tool"""
    print(f"\n{Fore.MAGENTA}🌐 Starting Email Scraper...")
    os.system('python emailscraper.py')

def run_bulk_mailer():
    """Run bulk email system"""
    print(f"\n{Fore.GREEN}💌 Starting ZShell Mailer...")
    os.system('python main.py')

def quick_verification():
    """Quick verification of existing emails.txt"""
    print(f"\n{Fore.CYAN}⚡ Quick verification of emails.txt")
    try:
        from emailverifier import AdvancedEmailVerifier
        verifier = AdvancedEmailVerifier()
        
        # Load emails from emails.txt
        emails = verifier.load_emails_from_file('emails.txt')
        if emails:
            print(f"Found {len(emails)} emails to verify...")
            results = verifier.verify_email_list(emails[:10], max_workers=5)  # Verify first 10
            verifier.display_stats()
            
            # Show high quality leads
            high_quality = verifier.filter_high_quality_leads(results)
            if high_quality:
                print(f"\n{Fore.GREEN}⭐ High Quality Leads Found:")
                for lead in high_quality[:5]:  # Show first 5
                    print(f"  ✅ {lead.email} - {lead.confidence_score}% confidence")
        else:
            print(f"{Fore.YELLOW}No emails found in emails.txt")
    except Exception as e:
        print(f"{Fore.RED}❌ Error: {str(e)}")

def integration_examples():
    """Show integration examples"""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}🔗 INTEGRATION EXAMPLES")
    print("=" * 50)
    
    examples = [
        ("🎯 Target ISP Customers", "Scrape ISP company websites → Verify emails → Send personalized campaigns"),
        ("🏢 Enterprise Outreach", "LinkedIn company search → Email verification → Executive targeting"),
        ("📊 Lead Scoring Pipeline", "Multi-source scraping → Quality verification → Tiered campaigns"),
        ("🚀 Apollo.io Integration", "API enrichment → Verification → High-value targeting"),
        ("🎪 Conference Attendees", "Event website scraping → Email validation → Follow-up campaigns")
    ]
    
    for title, description in examples:
        print(f"\n{Fore.YELLOW}{title}")
        print(f"  → {description}")

def file_status():
    """Show status of all files"""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}📁 FILE STATUS")
    print("=" * 40)
    
    files_to_check = [
        ('emails.txt', 'Target email list'),
        ('smtps.txt', 'SMTP server configurations'),
        ('htmlletter.html', 'Email template'),
        ('frommails.txt', 'Sender identities'),
        ('subject.txt', 'Subject variations'),
        ('emailverifier.py', 'Email verification tool'),
        ('emailscraper.py', 'Lead scraping tool'),
        ('main.py', 'Bulk mailer system'),
        ('advanced_mailer.py', 'Core mailing engine')
    ]
    
    for filename, description in files_to_check:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"  {Fore.GREEN}✅ {filename:<20} - {description} ({size:,} bytes)")
        else:
            print(f"  {Fore.RED}❌ {filename:<20} - {description} (missing)")

def main():
    """Main menu"""
    print_suite_banner()
    
    while True:
        try:
            print(f"\n{Fore.GREEN}{Style.BRIGHT}🎯 LEAD GENERATION SUITE")
            print("=" * 50)
            print(f"{Fore.WHITE}[1] 🌐 Run Email Scraper (Generate Leads)")
            print(f"{Fore.WHITE}[2] 🔍 Run Email Verifier (Validate Leads)")
            print(f"{Fore.WHITE}[3] 💌 Run Bulk Mailer (Send Campaigns)")
            print(f"{Fore.WHITE}[4] ⚡ Quick Verify emails.txt")
            print(f"{Fore.WHITE}[5] 📋 Show Workflow Guide")
            print(f"{Fore.WHITE}[6] 🔗 Integration Examples")
            print(f"{Fore.WHITE}[7] 📁 File Status")
            print(f"{Fore.WHITE}[8] Exit")
            
            choice = input(f"\n{Fore.YELLOW}Select option (1-8): ").strip()
            
            if choice == '1':
                run_email_scraper()
            elif choice == '2':
                run_email_verifier()
            elif choice == '3':
                run_bulk_mailer()
            elif choice == '4':
                quick_verification()
            elif choice == '5':
                show_workflow_guide()
            elif choice == '6':
                integration_examples()
            elif choice == '7':
                file_status()
            elif choice == '8':
                print(f"{Fore.GREEN}🎯 Lead generation suite completed!")
                break
            else:
                print(f"{Fore.RED}Invalid option. Please select 1-8.")
            
            input(f"\n{Fore.YELLOW}Press Enter to continue...")
            
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}👋 Suite stopped!")
            break
        except Exception as e:
            print(f"{Fore.RED}❌ Error: {str(e)}")

if __name__ == "__main__":
    main()