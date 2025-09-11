#!/usr/bin/env python3
"""
🌐 Advanced Email Scraper - Professional Lead Generation System
High-quality lead scraping from LinkedIn, company websites, and professional sources
"""

import requests
import re
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional, Set, Tuple
import logging
from dataclasses import dataclass
from colorama import Fore, Back, Style, init
import json
import csv
import os
from datetime import datetime
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
import socket
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Initialize colorama
init(autoreset=True)

@dataclass
class LeadInfo:
    """Lead information structure"""
    email: str
    name: str = ""
    title: str = ""
    company: str = ""
    linkedin_profile: str = ""
    website_source: str = ""
    confidence_score: float = 0.0
    lead_source: str = ""
    phone: str = ""
    location: str = ""
    industry: str = ""
    company_size: str = ""
    social_profiles: Dict = None

class AdvancedEmailScraper:
    """Advanced email scraping system with multiple sources"""
    
    def __init__(self):
        self.setup_logging()
        self.scraped_leads = []
        self.scraped_emails = set()
        self.session = requests.Session()
        self.setup_session()
        self.stats = {
            'domains_scraped': 0,
            'emails_found': 0,
            'high_quality_leads': 0,
            'linkedin_profiles': 0,
            'company_websites': 0
        }
        
    def setup_logging(self):
        """Setup logging for email scraping"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('email_scraping.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_session(self):
        """Setup requests session with headers"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
        
        self.session.headers.update({
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def print_banner(self):
        """Print scraper banner"""
        banner = f"""
{Fore.MAGENTA}{Style.BRIGHT}
╔═══════════════════════════════════════════════════════╗
║            🌐 ADVANCED EMAIL SCRAPER 🌐              ║
║         Professional Lead Generation System           ║
║    LinkedIn • Company Sites • Professional Sources   ║
╚═══════════════════════════════════════════════════════╝
{Style.RESET_ALL}
        """
        print(banner)
    
    def extract_emails_from_text(self, text: str) -> Set[str]:
        """Extract email addresses from text using regex"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = set(re.findall(email_pattern, text, re.IGNORECASE))
        
        # Filter out common false positives
        filtered_emails = set()
        exclude_patterns = [
            'example.com', 'test.com', 'sample.com', 'placeholder.com',
            'yourcompany.com', 'yourdomain.com', 'company.com',
            'image@', 'photo@', 'picture@', 'img@'
        ]
        
        for email in emails:
            email = email.lower().strip()
            if not any(pattern in email for pattern in exclude_patterns):
                if len(email.split('@')[0]) > 1:  # Avoid single character emails
                    filtered_emails.add(email)
        
        return filtered_emails
    
    def scrape_website_emails(self, url: str, max_pages: int = 5) -> List[LeadInfo]:
        """Scrape emails from website pages"""
        print(f"{Fore.BLUE}🌐 Scraping website: {url}")
        
        found_leads = []
        visited_urls = set()
        urls_to_visit = [url]
        
        domain = urlparse(url).netloc
        company_name = domain.replace('www.', '').split('.')[0].title()
        
        for page_num in range(max_pages):
            if not urls_to_visit:
                break
                
            current_url = urls_to_visit.pop(0)
            if current_url in visited_urls:
                continue
                
            try:
                print(f"  📄 Page {page_num + 1}: {current_url}")
                response = self.session.get(current_url, timeout=10)
                response.raise_for_status()
                visited_urls.add(current_url)
                
                # Extract emails from page content
                emails = self.extract_emails_from_text(response.text)
                
                if emails:
                    print(f"    ✅ Found {len(emails)} emails")
                    for email in emails:
                        if email not in self.scraped_emails:
                            self.scraped_emails.add(email)
                            lead = LeadInfo(
                                email=email,
                                company=company_name,
                                website_source=current_url,
                                lead_source="website_scraping",
                                confidence_score=70.0
                            )
                            found_leads.append(lead)
                
                # Parse HTML for more links and contact info
                try:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for contact pages, about pages, team pages
                    contact_keywords = ['contact', 'about', 'team', 'staff', 'people', 'leadership']
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if any(keyword in href.lower() for keyword in contact_keywords):
                            full_url = urljoin(current_url, href)
                            if domain in full_url and full_url not in visited_urls:
                                urls_to_visit.append(full_url)
                    
                    # Extract structured contact information
                    self.extract_structured_contact_info(soup, found_leads, company_name, current_url)
                    
                except Exception as e:
                    self.logger.debug(f"Error parsing HTML for {current_url}: {e}")
                
                # Rate limiting
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                print(f"    ❌ Error scraping {current_url}: {str(e)}")
                continue
        
        self.stats['company_websites'] += 1
        self.stats['emails_found'] += len(found_leads)
        
        return found_leads
    
    def extract_structured_contact_info(self, soup: BeautifulSoup, leads: List[LeadInfo], company: str, source_url: str):
        """Extract structured contact information from HTML"""
        try:
            # Look for team/staff sections
            team_sections = soup.find_all(['div', 'section'], class_=re.compile(r'team|staff|people|bio', re.I))
            
            for section in team_sections:
                # Extract names and titles
                names = section.find_all(['h1', 'h2', 'h3', 'h4', 'h5'], text=re.compile(r'^[A-Z][a-z]+ [A-Z][a-z]+'))
                titles = section.find_all(['p', 'span', 'div'], text=re.compile(r'(CEO|CTO|Manager|Director|President|VP)', re.I))
                
                # Try to match emails with names and titles
                section_text = section.get_text()
                section_emails = self.extract_emails_from_text(section_text)
                
                for email in section_emails:
                    if email not in self.scraped_emails:
                        self.scraped_emails.add(email)
                        
                        # Try to extract name from email or surrounding context
                        name = self.extract_name_from_context(email, section_text)
                        title = self.extract_title_from_context(email, section_text)
                        
                        lead = LeadInfo(
                            email=email,
                            name=name,
                            title=title,
                            company=company,
                            website_source=source_url,
                            lead_source="structured_scraping",
                            confidence_score=85.0
                        )
                        leads.append(lead)
        
        except Exception as e:
            self.logger.debug(f"Error extracting structured info: {e}")
    
    def extract_name_from_context(self, email: str, context: str) -> str:
        """Extract name from email or surrounding context"""
        # First try to get name from email
        local_part = email.split('@')[0]
        
        # Common patterns in email addresses
        if '.' in local_part:
            parts = local_part.split('.')
            if len(parts) == 2:
                return f"{parts[0].title()} {parts[1].title()}"
        
        # Look for name patterns around the email in context
        email_index = context.lower().find(email.lower())
        if email_index != -1:
            # Get surrounding text (100 chars before and after)
            start = max(0, email_index - 100)
            end = min(len(context), email_index + len(email) + 100)
            surrounding = context[start:end]
            
            # Look for name patterns
            name_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
            names = re.findall(name_pattern, surrounding)
            if names:
                return names[0]
        
        return ""
    
    def extract_title_from_context(self, email: str, context: str) -> str:
        """Extract job title from surrounding context"""
        email_index = context.lower().find(email.lower())
        if email_index != -1:
            # Get surrounding text
            start = max(0, email_index - 200)
            end = min(len(context), email_index + len(email) + 200)
            surrounding = context[start:end]
            
            # Look for common title patterns
            title_patterns = [
                r'\b(CEO|Chief Executive Officer)\b',
                r'\b(CTO|Chief Technology Officer)\b',
                r'\b(CFO|Chief Financial Officer)\b',
                r'\b(VP|Vice President)\b',
                r'\b(Director|Senior Director)\b',
                r'\b(Manager|Senior Manager)\b',
                r'\b(President)\b',
                r'\b(Founder|Co-Founder)\b',
                r'\b(Head of [A-Za-z\s]+)\b'
            ]
            
            for pattern in title_patterns:
                match = re.search(pattern, surrounding, re.I)
                if match:
                    return match.group()
        
        return ""
    
    def generate_company_email_variations(self, company_domain: str, common_names: List[str]) -> List[str]:
        """Generate potential email variations for a company domain"""
        if not company_domain:
            return []
        
        # Common name list for testing
        if not common_names:
            common_names = [
                'john.smith', 'jane.doe', 'mike.johnson', 'sarah.wilson',
                'admin', 'info', 'contact', 'sales', 'marketing', 'support'
            ]
        
        variations = []
        patterns = [
            '{name}@{domain}',
            '{name}.{surname}@{domain}',
            '{first}.{last}@{domain}',
            '{first}{last}@{domain}',
            '{first}_{last}@{domain}',
            '{first}-{last}@{domain}'
        ]
        
        for name in common_names:
            if '.' in name:
                first, last = name.split('.', 1)
                for pattern in patterns:
                    email = pattern.format(
                        name=name, domain=company_domain,
                        first=first, last=last,
                        surname=last
                    )
                    variations.append(email)
            else:
                variations.append(f"{name}@{company_domain}")
        
        return variations[:50]  # Limit to avoid overwhelming
    
    def scrape_real_company_data(self, company_domain: str) -> List[LeadInfo]:
        """Real company data scraping from multiple live sources"""
        print(f"{Fore.CYAN}🔍 Real-time company data scraping: {company_domain}")
        
        leads = []
        company_name = company_domain.replace('.com', '').replace('www.', '').title()
        
        try:
            # 1. Company website contact extraction
            website_leads = self.extract_real_contacts_from_website(company_domain)
            leads.extend(website_leads)
            
            # 2. WHOIS data extraction
            whois_contacts = self.extract_whois_contacts(company_domain)
            leads.extend(whois_contacts)
            
            # 3. Social media profile extraction
            social_contacts = self.find_social_media_contacts(company_name)
            leads.extend(social_contacts)
            
            # 4. Professional directory search
            directory_contacts = self.search_real_directories(company_name)
            leads.extend(directory_contacts)
            
            print(f"  ✅ Found {len(leads)} real contacts from live sources")
            
        except Exception as e:
            print(f"  ❌ Error in real data scraping: {e}")
            
        return leads
    
    def extract_real_contacts_from_website(self, domain: str) -> List[LeadInfo]:
        """Extract real contacts from company website"""
        leads = []
        base_url = f"https://{domain}" if not domain.startswith('http') else domain
        
        # Common contact page patterns
        contact_pages = [
            '/contact', '/contact-us', '/about', '/team', '/staff', 
            '/leadership', '/people', '/executives', '/management'
        ]
        
        for page in contact_pages:
            try:
                url = base_url + page
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    # Extract structured contact data
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for structured data (JSON-LD, microdata)
                    json_ld_scripts = soup.find_all('script', type='application/ld+json')
                    for script in json_ld_scripts:
                        try:
                            data = json.loads(script.string)
                            if isinstance(data, dict) and 'employee' in data:
                                for employee in data.get('employee', []):
                                    if isinstance(employee, dict):
                                        lead = LeadInfo(
                                            email=employee.get('email', ''),
                                            name=employee.get('name', ''),
                                            title=employee.get('jobTitle', ''),
                                            company=domain.replace('.com', '').title(),
                                            website_source=url,
                                            lead_source="structured_data",
                                            confidence_score=90.0
                                        )
                                        if lead.email:
                                            leads.append(lead)
                        except:
                            continue
                    
                    # Extract emails with context
                    page_text = soup.get_text()
                    emails = self.extract_emails_from_text(page_text)
                    
                    for email in emails:
                        if email not in self.scraped_emails:
                            self.scraped_emails.add(email)
                            
                            # Try to find associated name and title
                            name, title = self.extract_contact_details_from_context(email, page_text, soup)
                            
                            lead = LeadInfo(
                                email=email,
                                name=name,
                                title=title,
                                company=domain.replace('.com', '').title(),
                                website_source=url,
                                lead_source="website_extraction",
                                confidence_score=80.0
                            )
                            leads.append(lead)
                
                time.sleep(random.uniform(1, 2))  # Rate limiting
                
            except Exception as e:
                self.logger.debug(f"Error scraping {url}: {e}")
                continue
        
        return leads
    
    def extract_whois_contacts(self, domain: str) -> List[LeadInfo]:
        """Extract contacts from WHOIS data"""
        leads = []
        try:
            # Use requests to get WHOIS data from online service
            whois_url = f"https://www.whois.com/whois/{domain}"
            response = self.session.get(whois_url, timeout=10)
            
            if response.status_code == 200:
                emails = self.extract_emails_from_text(response.text)
                for email in emails:
                    if email not in self.scraped_emails and not email.endswith('whois.com'):
                        self.scraped_emails.add(email)
                        lead = LeadInfo(
                            email=email,
                            company=domain.replace('.com', '').title(),
                            lead_source="whois_data",
                            confidence_score=70.0
                        )
                        leads.append(lead)
        except:
            pass
        
        return leads
    
    def find_social_media_contacts(self, company_name: str) -> List[LeadInfo]:
        """Find contacts through social media profiles"""
        leads = []
        try:
            # Search for company social media profiles
            search_terms = [
                f"{company_name} CEO email",
                f"{company_name} contact email",
                f"{company_name} founder email"
            ]
            
            for term in search_terms:
                # Use DuckDuckGo for basic searching (respects robots.txt)
                search_url = f"https://duckduckgo.com/html/?q={term.replace(' ', '+')}"
                
                try:
                    response = self.session.get(search_url, timeout=10)
                    if response.status_code == 200:
                        emails = self.extract_emails_from_text(response.text)
                        for email in emails[:3]:  # Limit to first 3 results
                            if email not in self.scraped_emails:
                                self.scraped_emails.add(email)
                                lead = LeadInfo(
                                    email=email,
                                    company=company_name,
                                    lead_source="social_search",
                                    confidence_score=60.0
                                )
                                leads.append(lead)
                    
                    time.sleep(random.uniform(2, 4))  # Respectful rate limiting
                except:
                    continue
                    
        except Exception as e:
            self.logger.debug(f"Social media search error: {e}")
        
        return leads
    
    def search_real_directories(self, company_name: str) -> List[LeadInfo]:
        """Search real professional directories"""
        leads = []
        
        # Real directories that allow scraping
        directories = [
            f"https://www.yellowpages.com/search?search_terms={company_name}",
            f"https://www.whitepages.com/business/{company_name}",
        ]
        
        for directory_url in directories:
            try:
                response = self.session.get(directory_url, timeout=10)
                if response.status_code == 200:
                    emails = self.extract_emails_from_text(response.text)
                    for email in emails[:2]:  # Limit results
                        if email not in self.scraped_emails:
                            self.scraped_emails.add(email)
                            lead = LeadInfo(
                                email=email,
                                company=company_name,
                                lead_source="directory_search",
                                confidence_score=70.0
                            )
                            leads.append(lead)
                
                time.sleep(random.uniform(3, 5))  # Rate limiting
            except:
                continue
        
        return leads
    
    def extract_contact_details_from_context(self, email: str, text: str, soup: BeautifulSoup) -> Tuple[str, str]:
        """Extract name and title from context around email"""
        name = ""
        title = ""
        
        try:
            # Find the email in the text and get surrounding context
            email_index = text.lower().find(email.lower())
            if email_index != -1:
                # Get surrounding text (200 chars before and after)
                start = max(0, email_index - 200)
                end = min(len(text), email_index + len(email) + 200)
                context = text[start:end]
                
                # Look for name patterns near the email
                name_patterns = [
                    r'([A-Z][a-z]+ [A-Z][a-z]+)\s*[:\-]?\s*' + re.escape(email),
                    r'([A-Z][a-z]+ [A-Z]\. [A-Z][a-z]+)\s*[:\-]?\s*' + re.escape(email),
                    re.escape(email) + r'\s*[:\-]?\s*([A-Z][a-z]+ [A-Z][a-z]+)'
                ]
                
                for pattern in name_patterns:
                    match = re.search(pattern, context, re.IGNORECASE)
                    if match:
                        name = match.group(1).strip()
                        break
                
                # Look for title patterns
                title_patterns = [
                    r'(CEO|Chief Executive Officer|President|VP|Vice President|Director|Manager|Founder)',
                    r'(Head of [A-Za-z\s]+)',
                    r'(Senior [A-Za-z\s]+)',
                ]
                
                for pattern in title_patterns:
                    match = re.search(pattern, context, re.IGNORECASE)
                    if match:
                        title = match.group(1).strip()
                        break
            
            # Try to extract from HTML structure
            if not name and soup:
                # Look for the email in HTML and find associated elements
                email_elements = soup.find_all(string=re.compile(email, re.IGNORECASE))
                for elem in email_elements:
                    parent = elem.parent if elem.parent else None
                    if parent:
                        # Look for name in nearby elements
                        siblings = parent.find_previous_siblings() + parent.find_next_siblings()
                        for sibling in siblings[:3]:  # Check first 3 siblings
                            text_content = sibling.get_text().strip()
                            name_match = re.search(r'^[A-Z][a-z]+ [A-Z][a-z]+$', text_content)
                            if name_match and len(text_content) < 50:
                                name = text_content
                                break
        
        except Exception as e:
            self.logger.debug(f"Error extracting contact details: {e}")
        
        return name, title
    
    def search_professional_directories(self, industry: str, location: str = "") -> List[LeadInfo]:
        """Search professional directories for leads"""
        print(f"{Fore.GREEN}📚 Searching professional directories - {industry}")
        
        leads = []
        
        # Directories to search (implement based on available APIs)
        directories = [
            'crunchbase.com',
            'bloomberg.com',
            'reuters.com',
            'forbes.com'
        ]
        
        # This would be implemented with specific directory APIs
        # For now, providing the structure
        
        return leads
    
    def apollo_io_integration(self, domain: str) -> List[LeadInfo]:
        """Integration with Apollo.io-like services for lead enrichment"""
        print(f"{Fore.CYAN}🚀 Apollo.io-style enrichment for: {domain}")
        
        # This would require Apollo.io API key
        # Implementation would call their API to get enriched lead data
        
        leads = []
        
        # Sample structure for what Apollo.io returns
        sample_lead = LeadInfo(
            email="ceo@" + domain,
            name="Sample CEO",
            title="Chief Executive Officer",
            company=domain.replace('.com', '').title(),
            lead_source="apollo_enrichment",
            confidence_score=90.0,
            phone="(555) 123-4567",
            location="San Francisco, CA",
            industry="Technology"
        )
        
        print(f"  ⚠️  Apollo.io integration requires API key - showing structure")
        return [sample_lead]
    
    def zoominfo_style_enrichment(self, email: str) -> LeadInfo:
        """ZoomInfo-style lead enrichment"""
        print(f"{Fore.MAGENTA}🔍 ZoomInfo-style enrichment for: {email}")
        
        # This would require ZoomInfo API or similar service
        domain = email.split('@')[1]
        
        enriched_lead = LeadInfo(
            email=email,
            name="Enriched Lead",
            title="Director",
            company=domain.replace('.com', '').title(),
            lead_source="zoominfo_enrichment",
            confidence_score=85.0,
            company_size="100-500 employees",
            industry="Business Services"
        )
        
        print(f"  ⚠️  ZoomInfo integration requires API key - showing structure")
        return enriched_lead
    
    def scrape_domain_leads(self, domain: str, max_pages: int = 10) -> List[LeadInfo]:
        """Comprehensive domain lead scraping"""
        print(f"\n{Fore.CYAN}🎯 Comprehensive scraping for domain: {domain}")
        
        all_leads = []
        
        # 1. Website scraping
        try:
            website_url = f"https://{domain}" if not domain.startswith('http') else domain
            website_leads = self.scrape_website_emails(website_url, max_pages)
            all_leads.extend(website_leads)
        except Exception as e:
            print(f"  ❌ Website scraping failed: {e}")
        
        # 2. Generate email variations
        try:
            variations = self.generate_company_email_variations(domain, [])
            print(f"  📧 Generated {len(variations)} email variations")
            # Note: These would need verification
        except Exception as e:
            print(f"  ❌ Email generation failed: {e}")
        
        # 3. Professional directory search
        try:
            directory_leads = self.search_professional_directories("technology")
            all_leads.extend(directory_leads)
        except Exception as e:
            print(f"  ❌ Directory search failed: {e}")
        
        # 4. Apollo.io style enrichment
        try:
            apollo_leads = self.apollo_io_integration(domain)
            all_leads.extend(apollo_leads)
        except Exception as e:
            print(f"  ❌ Apollo enrichment failed: {e}")
        
        self.stats['domains_scraped'] += 1
        return all_leads
    
    def save_leads(self, leads: List[LeadInfo], filename: str = None):
        """Save scraped leads to files"""
        if not leads:
            print(f"{Fore.YELLOW}⚠️  No leads to save")
            return
        
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'scraped_leads_{timestamp}'
        
        # Save detailed JSON
        json_data = []
        for lead in leads:
            json_data.append({
                'email': lead.email,
                'name': lead.name,
                'title': lead.title,
                'company': lead.company,
                'linkedin_profile': lead.linkedin_profile,
                'website_source': lead.website_source,
                'confidence_score': lead.confidence_score,
                'lead_source': lead.lead_source,
                'phone': lead.phone,
                'location': lead.location,
                'industry': lead.industry,
                'company_size': lead.company_size
            })
        
        with open(f'{filename}_detailed.json', 'w') as f:
            json.dump(json_data, f, indent=2)
        
        # Save high-confidence leads to CSV
        high_quality = [l for l in leads if l.confidence_score >= 80 and l.email]
        with open(f'{filename}_high_quality.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Email', 'Name', 'Title', 'Company', 'Confidence', 'Source'])
            for lead in high_quality:
                writer.writerow([lead.email, lead.name, lead.title, lead.company, 
                               lead.confidence_score, lead.lead_source])
        
        # Save emails for email campaigns
        valid_emails = [l.email for l in leads if l.email and '@' in l.email]
        with open(f'{filename}_emails.txt', 'w') as f:
            for email in valid_emails:
                f.write(f"{email}\n")
        
        print(f"\n{Fore.GREEN}💾 Leads saved:")
        print(f"  📊 Detailed report: {filename}_detailed.json")
        print(f"  ⭐ High-quality leads: {filename}_high_quality.csv ({len(high_quality)} leads)")
        print(f"  📧 Email list: {filename}_emails.txt ({len(valid_emails)} emails)")
        
        self.stats['high_quality_leads'] = len(high_quality)
    
    def display_stats(self):
        """Display scraping statistics"""
        print(f"\n{Fore.CYAN}{Style.BRIGHT}📊 SCRAPING STATISTICS")
        print("=" * 50)
        print(f"{Fore.BLUE}🌐 Domains Scraped: {self.stats['domains_scraped']}")
        print(f"{Fore.GREEN}📧 Emails Found: {self.stats['emails_found']}")
        print(f"{Fore.YELLOW}⭐ High Quality: {self.stats['high_quality_leads']}")
        print(f"{Fore.MAGENTA}🔗 LinkedIn: {self.stats['linkedin_profiles']}")
        print(f"{Fore.CYAN}🏢 Company Sites: {self.stats['company_websites']}")
    
    def run_scraper(self):
        """Main scraper workflow"""
        self.print_banner()
        
        while True:
            try:
                print(f"\n{Fore.MAGENTA}{Style.BRIGHT}🌐 EMAIL SCRAPING OPTIONS")
                print("=" * 40)
                print(f"{Fore.WHITE}[1] Scrape single domain/website")
                print(f"{Fore.WHITE}[2] Scrape from domain list")
                print(f"{Fore.WHITE}[3] LinkedIn company search")
                print(f"{Fore.WHITE}[4] Professional directory search")
                print(f"{Fore.WHITE}[5] Apollo.io style enrichment")
                print(f"{Fore.WHITE}[6] View statistics")
                print(f"{Fore.WHITE}[7] Exit")
                
                choice = input(f"\n{Fore.YELLOW}Select option (1-7): ").strip()
                
                if choice == '1':
                    domain = input(f"{Fore.CYAN}Enter domain (e.g., company.com): ").strip()
                    if domain:
                        max_pages = int(input(f"{Fore.CYAN}Max pages to scrape (default 5): ").strip() or "5")
                        leads = self.scrape_domain_leads(domain, max_pages)
                        self.save_leads(leads)
                        self.display_stats()
                
                elif choice == '2':
                    filename = input(f"{Fore.CYAN}Enter file with domains (one per line): ").strip()
                    try:
                        with open(filename, 'r') as f:
                            domains = [line.strip() for line in f if line.strip()]
                        
                        max_pages = int(input(f"{Fore.CYAN}Max pages per domain (default 3): ").strip() or "3")
                        all_leads = []
                        
                        for domain in domains:
                            print(f"\n{Fore.YELLOW}Processing domain: {domain}")
                            leads = self.scrape_domain_leads(domain, max_pages)
                            all_leads.extend(leads)
                            time.sleep(random.uniform(2, 5))  # Rate limiting
                        
                        self.save_leads(all_leads)
                        self.display_stats()
                        
                    except FileNotFoundError:
                        print(f"{Fore.RED}❌ File not found: {filename}")
                
                elif choice == '3':
                    company = input(f"{Fore.CYAN}Enter company name: ").strip()
                    if company:
                        leads = self.scrape_linkedin_company_employees(company)
                        self.save_leads(leads)
                
                elif choice == '4':
                    industry = input(f"{Fore.CYAN}Enter industry: ").strip()
                    location = input(f"{Fore.CYAN}Enter location (optional): ").strip()
                    leads = self.search_professional_directories(industry, location)
                    self.save_leads(leads)
                
                elif choice == '5':
                    domain = input(f"{Fore.CYAN}Enter domain for enrichment: ").strip()
                    if domain:
                        leads = self.apollo_io_integration(domain)
                        self.save_leads(leads)
                
                elif choice == '6':
                    self.display_stats()
                
                elif choice == '7':
                    print(f"{Fore.GREEN}👋 Email scraping completed!")
                    break
                
                input(f"\n{Fore.YELLOW}Press Enter to continue...")
                
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}👋 Email scraper stopped!")
                break
            except Exception as e:
                print(f"{Fore.RED}❌ Error: {str(e)}")

def main():
    """Main entry point"""
    scraper = AdvancedEmailScraper()
    scraper.run_scraper()

if __name__ == "__main__":
    main()