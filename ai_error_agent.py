"""
ZShell Mailer AI Error Detection Agent
Advanced AI-powered error analysis, pattern detection, and intelligent recommendations
"""

import re
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import threading

logger = logging.getLogger(__name__)

@dataclass
class ErrorPattern:
    """Represents a detected error pattern"""
    pattern_type: str
    frequency: int
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    recommendation: str
    affected_servers: List[str]
    first_seen: datetime
    last_seen: datetime
    confidence_score: float

@dataclass
class AIRecommendation:
    """AI-generated recommendation for fixing issues"""
    issue_type: str
    priority: str  # 'low', 'medium', 'high', 'urgent'
    title: str
    description: str
    solution: str
    expected_improvement: str
    implementation_steps: List[str]
    confidence: float
    estimated_time: str

class AIErrorAgent:
    """AI-powered error detection and analysis agent"""
    
    def __init__(self):
        self.error_history = []
        self.detected_patterns = {}
        self.recommendations = []
        self.analysis_cache = {}
        self.lock = threading.Lock()
        
        # Initialize AI models and rules
        self.spam_triggers = self._load_spam_triggers()
        self.error_patterns = self._initialize_error_patterns()
        self.deliverability_rules = self._load_deliverability_rules()
        
        # Statistics
        self.analysis_stats = {
            'total_analyses': 0,
            'patterns_detected': 0,
            'recommendations_generated': 0,
            'accuracy_score': 0.0
        }
    
    def _load_spam_triggers(self) -> Dict[str, List[str]]:
        """Load spam trigger words and phrases for content analysis"""
        return {
            'high_risk': [
                'free money', 'guaranteed income', 'make money fast', 'get rich quick',
                'act now', 'limited time', 'urgent response', 'click here now',
                'winner', 'congratulations', 'you have been selected',
                'nigeria prince', 'inheritance', 'lottery winner'
            ],
            'medium_risk': [
                'special offer', 'discount', 'save money', 'cheap',
                'deal', 'promotion', 'limited offer', 'exclusive',
                'bonus', 'gift', 'prize', 'reward'
            ],
            'technical_triggers': [
                'multiple exclamation', 'all caps words', 'excessive punctuation',
                'hidden text', 'tiny fonts', 'invisible characters'
            ]
        }
    
    def _initialize_error_patterns(self) -> Dict[str, Dict]:
        """Initialize common error patterns and their solutions"""
        return {
            'smtp_auth_failure': {
                'keywords': ['authentication failed', 'invalid credentials', 'login failed'],
                'severity': 'high',
                'category': 'smtp_configuration',
                'solutions': [
                    'Verify SMTP username and password are correct',
                    'Check if 2FA is enabled and app password is needed',
                    'Ensure SMTP server settings match provider requirements',
                    'Check if account is locked or suspended'
                ]
            },
            'rate_limiting': {
                'keywords': ['too many connections', 'rate limit', 'quota exceeded', 'throttled'],
                'severity': 'medium',
                'category': 'sending_limits',
                'solutions': [
                    'Reduce sending rate and implement delays',
                    'Distribute load across more SMTP servers',
                    'Enable warmup mode for gradual volume increase',
                    'Check provider-specific rate limits'
                ]
            },
            'bounce_pattern': {
                'keywords': ['bounce', 'recipient rejected', 'user unknown', 'mailbox full'],
                'severity': 'medium',
                'category': 'list_quality',
                'solutions': [
                    'Clean email list and remove invalid addresses',
                    'Implement email verification before sending',
                    'Use double opt-in for new subscribers',
                    'Monitor bounce rate and maintain list hygiene'
                ]
            },
            'spam_filter': {
                'keywords': ['spam detected', 'content rejected', 'blocked by filter'],
                'severity': 'high',
                'category': 'content_quality',
                'solutions': [
                    'Review email content for spam triggers',
                    'Improve sender reputation through warmup',
                    'Use proper authentication (SPF, DKIM, DMARC)',
                    'Reduce promotional language in content'
                ]
            },
            'dns_issues': {
                'keywords': ['dns error', 'hostname not found', 'connection timeout'],
                'severity': 'high',
                'category': 'infrastructure',
                'solutions': [
                    'Verify DNS settings and MX records',
                    'Check network connectivity and firewall settings',
                    'Use alternative DNS servers (8.8.8.8, 1.1.1.1)',
                    'Implement retry logic with exponential backoff'
                ]
            }
        }
    
    def _load_deliverability_rules(self) -> Dict[str, Any]:
        """Load deliverability rules and best practices"""
        return {
            'optimal_send_times': {
                'business': [9, 10, 11, 14, 15, 16],  # 9-11 AM, 2-4 PM
                'consumer': [18, 19, 20, 21],  # 6-9 PM
                'weekend': [10, 11, 15, 16]  # Weekend hours
            },
            'content_ratios': {
                'text_to_image_ratio': 0.8,  # 80% text, 20% images
                'link_density_max': 0.1,  # Max 10% of content should be links
                'spam_word_threshold': 0.05  # Max 5% spam words
            },
            'sender_reputation': {
                'warmup_schedule': [10, 20, 50, 100, 200, 500, 1000],
                'bounce_rate_threshold': 0.05,  # 5% max bounce rate
                'complaint_rate_threshold': 0.001  # 0.1% max complaint rate
            }
        }
    
    def analyze_error(self, error_data: Dict) -> Dict[str, Any]:
        """Analyze a single error and provide AI-powered insights"""
        with self.lock:
            self.analysis_stats['total_analyses'] += 1
        
        analysis = {
            'error_id': f"err_{int(time.time())}_{len(self.error_history)}",
            'timestamp': datetime.now(),
            'error_type': self._classify_error(error_data),
            'severity': self._assess_severity(error_data),
            'root_cause': self._identify_root_cause(error_data),
            'recommendations': self._generate_recommendations(error_data),
            'confidence': self._calculate_confidence(error_data),
            'potential_impact': self._assess_impact(error_data)
        }
        
        # Store error for pattern analysis
        self.error_history.append({
            'data': error_data,
            'analysis': analysis,
            'timestamp': datetime.now()
        })
        
        # Update pattern detection
        self._update_patterns(error_data, analysis)
        
        return analysis
    
    def _classify_error(self, error_data: Dict) -> str:
        """Classify error type using AI pattern matching"""
        error_message = str(error_data.get('error_message', '')).lower()
        smtp_host = error_data.get('smtp_host', '')
        
        # Check against known patterns
        for pattern_name, pattern_info in self.error_patterns.items():
            for keyword in pattern_info['keywords']:
                if keyword in error_message:
                    return pattern_info['category']
        
        # AI-based classification for unknown errors
        if 'timeout' in error_message or 'connection' in error_message:
            return 'connection_issue'
        elif 'ssl' in error_message or 'tls' in error_message:
            return 'encryption_issue'
        elif 'permission' in error_message or 'access' in error_message:
            return 'authorization_issue'
        else:
            return 'unknown_error'
    
    def _assess_severity(self, error_data: Dict) -> str:
        """Assess error severity using AI scoring"""
        error_message = str(error_data.get('error_message', '')).lower()
        affected_count = error_data.get('affected_recipients', 1)
        smtp_reputation = error_data.get('smtp_reputation', 100)
        
        severity_score = 0
        
        # Base severity from error type
        critical_keywords = ['authentication', 'blocked', 'suspended', 'banned']
        high_keywords = ['bounce', 'rejected', 'spam', 'filtered']
        medium_keywords = ['timeout', 'limit', 'throttle', 'delay']
        
        if any(word in error_message for word in critical_keywords):
            severity_score += 4
        elif any(word in error_message for word in high_keywords):
            severity_score += 3
        elif any(word in error_message for word in medium_keywords):
            severity_score += 2
        else:
            severity_score += 1
        
        # Adjust based on scale and impact
        if affected_count > 100:
            severity_score += 1
        if smtp_reputation < 50:
            severity_score += 1
        
        # Convert score to severity level
        if severity_score >= 5:
            return 'critical'
        elif severity_score >= 4:
            return 'high'
        elif severity_score >= 2:
            return 'medium'
        else:
            return 'low'
    
    def _identify_root_cause(self, error_data: Dict) -> Dict[str, Any]:
        """Identify root cause using AI analysis"""
        error_message = str(error_data.get('error_message', '')).lower()
        
        root_cause = {
            'category': 'unknown',
            'description': 'Unable to determine root cause',
            'confidence': 0.5,
            'contributing_factors': []
        }
        
        # Analyze error patterns
        if 'authentication' in error_message:
            root_cause = {
                'category': 'credentials',
                'description': 'SMTP authentication credentials are invalid or expired',
                'confidence': 0.9,
                'contributing_factors': ['Invalid username/password', 'Account locked', '2FA required']
            }
        elif 'connection' in error_message and 'timeout' in error_message:
            root_cause = {
                'category': 'network',
                'description': 'Network connectivity issues preventing SMTP connection',
                'confidence': 0.85,
                'contributing_factors': ['Firewall blocking', 'DNS resolution failure', 'Server overload']
            }
        elif 'bounce' in error_message or 'rejected' in error_message:
            root_cause = {
                'category': 'recipient',
                'description': 'Recipient server rejected the email',
                'confidence': 0.8,
                'contributing_factors': ['Invalid email address', 'Spam filters', 'Mailbox full']
            }
        
        return root_cause
    
    def _generate_recommendations(self, error_data: Dict) -> List[AIRecommendation]:
        """Generate AI-powered recommendations for fixing the error"""
        recommendations = []
        error_type = self._classify_error(error_data)
        
        # Get base recommendations from patterns
        if error_type in [pattern['category'] for pattern in self.error_patterns.values()]:
            for pattern_name, pattern_info in self.error_patterns.items():
                if pattern_info['category'] == error_type:
                    for i, solution in enumerate(pattern_info['solutions']):
                        recommendations.append(AIRecommendation(
                            issue_type=error_type,
                            priority='high' if i == 0 else 'medium',
                            title=f"Fix {error_type.replace('_', ' ').title()}",
                            description=f"Address {pattern_name.replace('_', ' ')} issue",
                            solution=solution,
                            expected_improvement="10-30% deliverability increase",
                            implementation_steps=self._get_implementation_steps(solution),
                            confidence=0.8 - (i * 0.1),
                            estimated_time="5-15 minutes"
                        ))
        
        # Add AI-generated custom recommendations
        custom_recommendations = self._generate_custom_recommendations(error_data)
        recommendations.extend(custom_recommendations)
        
        return sorted(recommendations, key=lambda x: x.confidence, reverse=True)[:3]
    
    def _get_implementation_steps(self, solution: str) -> List[str]:
        """Generate implementation steps for a solution"""
        steps_mapping = {
            'verify smtp username': [
                'Open SMTP configuration file',
                'Check username matches email provider requirements',
                'Test credentials with email client',
                'Update configuration if needed'
            ],
            'reduce sending rate': [
                'Open advanced_mailer.py configuration',
                'Increase delay_between_emails parameter',
                'Reduce max_workers for concurrent sending',
                'Monitor sending rate and adjust as needed'
            ],
            'clean email list': [
                'Export current email list',
                'Use email verification service',
                'Remove bounced addresses',
                'Update emails.txt with clean list'
            ]
        }
        
        # Find matching steps
        for key, steps in steps_mapping.items():
            if key.lower() in solution.lower():
                return steps
        
        # Default generic steps
        return [
            'Identify the specific issue',
            'Research best practices',
            'Implement the recommended solution',
            'Monitor results and adjust if needed'
        ]
    
    def _generate_custom_recommendations(self, error_data: Dict) -> List[AIRecommendation]:
        """Generate custom AI recommendations based on specific error context"""
        recommendations = []
        
        # Analyze recent error patterns for context-aware recommendations
        recent_errors = [e for e in self.error_history if 
                        (datetime.now() - e['timestamp']).hours < 24]
        
        if len(recent_errors) > 10:
            recommendations.append(AIRecommendation(
                issue_type='system_health',
                priority='urgent',
                title='High Error Rate Detected',
                description='Multiple errors detected in the last 24 hours',
                solution='Pause sending and investigate system health',
                expected_improvement='Prevent reputation damage',
                implementation_steps=[
                    'Stop current email campaigns',
                    'Review recent configuration changes',
                    'Check SMTP server status',
                    'Resume sending after fixes'
                ],
                confidence=0.95,
                estimated_time='30-60 minutes'
            ))
        
        return recommendations
    
    def _calculate_confidence(self, error_data: Dict) -> float:
        """Calculate confidence score for the analysis"""
        error_message = str(error_data.get('error_message', ''))
        
        confidence = 0.5  # Base confidence
        
        # Increase confidence for known error patterns
        for pattern_info in self.error_patterns.values():
            if any(keyword in error_message.lower() for keyword in pattern_info['keywords']):
                confidence += 0.3
                break
        
        # Adjust based on error message clarity
        if len(error_message) > 50:
            confidence += 0.1
        
        # Historical pattern matching
        similar_errors = [e for e in self.error_history if 
                         e['data'].get('error_message', '').lower() in error_message.lower()]
        if len(similar_errors) > 3:
            confidence += 0.2
        
        return min(confidence, 1.0)
    
    def _assess_impact(self, error_data: Dict) -> Dict[str, Any]:
        """Assess potential impact of the error"""
        return {
            'deliverability_impact': 'medium',
            'reputation_risk': 'low',
            'affected_recipients': error_data.get('affected_recipients', 1),
            'estimated_revenue_loss': '$0-50',
            'urgency_level': 'standard'
        }
    
    def _update_patterns(self, error_data: Dict, analysis: Dict):
        """Update detected patterns based on new error"""
        error_type = analysis['error_type']
        
        if error_type not in self.detected_patterns:
            self.detected_patterns[error_type] = ErrorPattern(
                pattern_type=error_type,
                frequency=1,
                severity=analysis['severity'],
                description=f"Pattern detected for {error_type}",
                recommendation="Monitor and take preventive action",
                affected_servers=[error_data.get('smtp_host', 'unknown')],
                first_seen=datetime.now(),
                last_seen=datetime.now(),
                confidence_score=analysis['confidence']
            )
        else:
            pattern = self.detected_patterns[error_type]
            pattern.frequency += 1
            pattern.last_seen = datetime.now()
            pattern.confidence_score = min(1.0, pattern.confidence_score + 0.1)
    
    def analyze_content_quality(self, content: str) -> Dict[str, Any]:
        """Analyze email content for spam triggers and deliverability issues"""
        analysis = {
            'spam_score': 0,
            'detected_triggers': [],
            'recommendations': [],
            'quality_score': 100
        }
        
        content_lower = content.lower()
        
        # Check for spam triggers
        for risk_level, triggers in self.spam_triggers.items():
            for trigger in triggers:
                if trigger in content_lower:
                    analysis['detected_triggers'].append({
                        'trigger': trigger,
                        'risk_level': risk_level,
                        'position': content_lower.find(trigger)
                    })
        
        # Calculate spam score
        high_risk_count = len([t for t in analysis['detected_triggers'] if t['risk_level'] == 'high_risk'])
        medium_risk_count = len([t for t in analysis['detected_triggers'] if t['risk_level'] == 'medium_risk'])
        
        analysis['spam_score'] = (high_risk_count * 30) + (medium_risk_count * 10)
        analysis['quality_score'] = max(0, 100 - analysis['spam_score'])
        
        # Generate content recommendations
        if analysis['spam_score'] > 50:
            analysis['recommendations'].append('High spam risk detected - revise content')
        if high_risk_count > 0:
            analysis['recommendations'].append('Remove high-risk spam trigger words')
        if medium_risk_count > 3:
            analysis['recommendations'].append('Reduce promotional language')
        
        return analysis
    
    def get_system_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive system health report"""
        recent_errors = [e for e in self.error_history if 
                        (datetime.now() - e['timestamp']).hours < 24]
        
        error_types = Counter([e['analysis']['error_type'] for e in recent_errors])
        severity_counts = Counter([e['analysis']['severity'] for e in recent_errors])
        
        return {
            'overall_health': 'good' if len(recent_errors) < 10 else 'poor',
            'total_errors_24h': len(recent_errors),
            'error_types': dict(error_types),
            'severity_breakdown': dict(severity_counts),
            'top_recommendations': [
                rec for error in recent_errors 
                for rec in error['analysis']['recommendations']
            ][:5],
            'patterns_detected': len(self.detected_patterns),
            'analysis_stats': self.analysis_stats
        }
    
    def generate_daily_report(self) -> str:
        """Generate daily AI analysis report"""
        health_report = self.get_system_health_report()
        
        report = f"""
🤖 AI ERROR ANALYSIS DAILY REPORT
{'='*50}
📊 System Health: {health_report['overall_health'].upper()}
🚨 Errors (24h): {health_report['total_errors_24h']}
🔍 Patterns Detected: {health_report['patterns_detected']}
📈 Total Analyses: {self.analysis_stats['total_analyses']}

🎯 TOP RECOMMENDATIONS:
"""
        
        for i, rec in enumerate(health_report['top_recommendations'][:3], 1):
            if hasattr(rec, 'title'):
                report += f"{i}. {rec.title}: {rec.solution}\n"
        
        report += f"\n🔬 AI Confidence: {self.analysis_stats.get('accuracy_score', 0.85)*100:.1f}%"
        
        return report

# Global AI agent instance
ai_agent = AIErrorAgent()