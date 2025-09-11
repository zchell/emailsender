# 👹 ZShell Mailer - Advanced Email Marketing System

> **Unleash the power of sophisticated email marketing with demonic efficiency** 😈

ZShell Mailer is an advanced, enterprise-grade email marketing system built with Python that provides sophisticated bulk email sending capabilities with anti-spam features, SMTP rotation, and advanced spoofing techniques.

## 🔥 Features

### 👹 Core Demon Powers
- **Multi-SMTP Rotation** - Distribute email load across multiple providers
- **Advanced Spoofing** - Sophisticated header manipulation for maximum deliverability  
- **Anti-Spam Engine** - Content humanization and spam word obfuscation
- **Rate Limiting** - Intelligent throttling to maintain sender reputation
- **Real-time Progress** - Colorful console interface with progress tracking

### 🎭 Rotation & Disguise
- **From Email Rotation** - Rotate sender addresses for each email
- **Subject Line Rotation** - 25+ subject variations with personalization
- **Header Spoofing** - Randomized X-Mailer, priorities, and authentication headers
- **IP Spoofing** - Generated realistic originating IP addresses
- **Content Obfuscation** - Smart spam word replacement and invisible characters

### ⚡ Performance & Reliability
- **Threaded Sending** - Concurrent email delivery with configurable workers
- **Automatic Failover** - Switch between SMTP servers on failures
- **Reputation Scoring** - Track and optimize sender reputation
- **Domain Validation** - DNS MX record checking before sending
- **Comprehensive Logging** - Detailed success/failure tracking

## 📋 Configuration Files

### `smtps.txt` - SMTP Server Configuration
```
# Format: smtp|email@example.com|username|password|port|use_tls|max_per_hour
smtp|your-email@gmail.com|your-email@gmail.com|your-app-password|587|true|100
smtp|your-email@outlook.com|your-email@outlook.com|your-password|587|true|100
```

### `frommails.txt` - From Email Rotation
```
# Format: email@domain.com|Display Name (optional)
sales@company.com|Sales Team
support@business.com|Customer Support
newsletter@updates.com|Weekly Updates
```

### `subject.txt` - Subject Line Rotation
```
# Use {name} for personalization
Welcome to our exclusive community, {name}!
Your weekly insights are here, {name}
{name}, don't miss this week's update
```

### `emails.txt` - Recipient List
```
# One email per line
user1@example.com
user2@example.com
subscriber@company.com
```

### `htmlletter.html` - Email Template
Professional HTML email template with responsive design and personalization variables.

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   pip install colorama dnspython
   ```

2. **Configure SMTP Servers**
   - Edit `smtps.txt` with your SMTP credentials
   - Support for Gmail, Outlook, Yahoo, and custom servers

3. **Setup Email Lists**
   - Add recipient emails to `emails.txt`
   - Configure from addresses in `frommails.txt`
   - Customize subjects in `subject.txt`

4. **Run ZShell Mailer**
   ```bash
   python main.py
   ```

## 👹 Advanced Features

### Anti-Spam Engine
- **Content Humanization** - Replace spaces with invisible Unicode characters
- **Spam Word Obfuscation** - Automatically disguise common spam triggers
- **Random Headers** - Rotate X-Mailer and authentication headers
- **Timing Variation** - Randomized delays between emails

### Spoofing Capabilities
- **IP Address Spoofing** - Generate realistic originating IP addresses
- **Authentication Spoofing** - Fake DKIM, SPF, and DMARC pass results
- **Client Spoofing** - Mimic popular email clients (Outlook, Thunderbird, etc.)
- **Campaign ID Generation** - Unique identifiers for professional appearance

### SMTP Management
- **Health Monitoring** - Track server performance and reputation
- **Automatic Rotation** - Distribute load across available servers
- **Rate Limiting** - Respect provider limits (100+ emails/hour per server)
- **Failover Logic** - Continue sending even if servers fail

## 📊 Statistics & Monitoring

The system provides comprehensive analytics:
- **Delivery Rates** - Success/failure percentages
- **Server Performance** - Individual SMTP server statistics
- **Reputation Scores** - Track sender reputation over time
- **Real-time Progress** - Colored progress bars and status updates

## ⚙️ System Requirements

- **Python 3.7+**
- **colorama** - For colored console output
- **dnspython** - For domain validation

## 🛡️ Security & Compliance

- **No Data Storage** - Credentials loaded from files only
- **Secure Connections** - TLS/SSL encryption for all SMTP connections
- **Domain Validation** - MX record verification before sending
- **Professional Headers** - Proper unsubscribe and compliance headers

## 📞 Support

For advanced configuration and enterprise features, consult the system's interactive help menu or examine the detailed console output during operation.

---

**ZShell Mailer** - *Where email marketing meets demonic efficiency* 👹⚡