"""
Data seeding utility for development and testing
"""
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.core.security import get_password_hash
from app.models.user import User, UserRole, Department
from app.models.ticket import Ticket, TicketStatus, TicketPriority, TicketCategory, Tag
from app.models.knowledge import KnowledgeArticle, KnowledgeCategory, ArticleType, ArticleStatus
from app.models.chat import ChatMessage
from datetime import datetime, timedelta
import uuid
import logging

logger = logging.getLogger(__name__)


def create_departments(db: Session):
    """Create sample departments"""
    departments = [
        {"name": "IT Support", "description": "General IT support and helpdesk"},
        {"name": "Network Operations", "description": "Network infrastructure and connectivity"},
        {"name": "Security", "description": "Information security and compliance"},
        {"name": "Database Administration", "description": "Database management and optimization"},
        {"name": "Application Development", "description": "Software development and maintenance"}
    ]
    
    for dept_data in departments:
        existing = db.query(Department).filter(Department.name == dept_data["name"]).first()
        if not existing:
            dept = Department(**dept_data)
            db.add(dept)
    
    db.commit()
    logger.info("Created sample departments")


def create_users(db: Session):
    """Create sample users"""
    # Get departments
    it_support = db.query(Department).filter(Department.name == "IT Support").first()
    network_ops = db.query(Department).filter(Department.name == "Network Operations").first()
    security = db.query(Department).filter(Department.name == "Security").first()
    
    users = [
        # End Users
        {
            "email": "john.doe@company.com",
            "name": "John Doe",
            "hashed_password": get_password_hash("password123"),
            "role": UserRole.END_USER,
            "department_id": it_support.id if it_support else None
        },
        {
            "email": "jane.smith@company.com",
            "name": "Jane Smith",
            "hashed_password": get_password_hash("password123"),
            "role": UserRole.END_USER,
            "department_id": it_support.id if it_support else None
        },
        
        # L1 Engineers
        {
            "email": "sarah.tech@company.com",
            "name": "Sarah Tech",
            "hashed_password": get_password_hash("password123"),
            "role": UserRole.L1_ENGINEER,
            "department_id": it_support.id if it_support else None
        },
        {
            "email": "tom.support@company.com",
            "name": "Tom Support",
            "hashed_password": get_password_hash("password123"),
            "role": UserRole.L1_ENGINEER,
            "department_id": it_support.id if it_support else None
        },
        
        # L2 Engineers
        {
            "email": "mike.senior@company.com",
            "name": "Mike Senior",
            "hashed_password": get_password_hash("password123"),
            "role": UserRole.L2_ENGINEER,
            "department_id": network_ops.id if network_ops else None
        },
        {
            "email": "lisa.expert@company.com",
            "name": "Lisa Expert",
            "hashed_password": get_password_hash("password123"),
            "role": UserRole.L2_ENGINEER,
            "department_id": security.id if security else None
        },
        
        # Operations Manager
        {
            "email": "alex.manager@company.com",
            "name": "Alex Manager",
            "hashed_password": get_password_hash("password123"),
            "role": UserRole.OPS_MANAGER,
            "department_id": it_support.id if it_support else None
        },
        
        # Transition Manager
        {
            "email": "chris.transition@company.com",
            "name": "Chris Transition",
            "hashed_password": get_password_hash("password123"),
            "role": UserRole.TRANSITION_MANAGER,
            "department_id": it_support.id if it_support else None
        }
    ]
    
    for user_data in users:
        existing = db.query(User).filter(User.email == user_data["email"]).first()
        if not existing:
            user = User(**user_data)
            db.add(user)
    
    db.commit()
    logger.info("Created sample users")


def create_knowledge_categories(db: Session):
    """Create knowledge base categories"""
    categories = [
        {"name": "Hardware", "description": "Hardware-related procedures and troubleshooting"},
        {"name": "Software", "description": "Software installation, configuration, and issues"},
        {"name": "Network", "description": "Network connectivity and infrastructure"},
        {"name": "Security", "description": "Security policies and procedures"},
        {"name": "Procedures", "description": "Standard operating procedures"},
        {"name": "Troubleshooting", "description": "General troubleshooting guides"}
    ]
    
    for cat_data in categories:
        existing = db.query(KnowledgeCategory).filter(KnowledgeCategory.name == cat_data["name"]).first()
        if not existing:
            category = KnowledgeCategory(**cat_data)
            db.add(category)
    
    db.commit()
    logger.info("Created knowledge categories")


def create_knowledge_articles(db: Session):
    """Create sample knowledge articles"""
    # Get categories and authors
    hardware_cat = db.query(KnowledgeCategory).filter(KnowledgeCategory.name == "Hardware").first()
    software_cat = db.query(KnowledgeCategory).filter(KnowledgeCategory.name == "Software").first()
    network_cat = db.query(KnowledgeCategory).filter(KnowledgeCategory.name == "Network").first()
    
    mike = db.query(User).filter(User.email == "mike.senior@company.com").first()
    lisa = db.query(User).filter(User.email == "lisa.expert@company.com").first()
    
    articles = [
        {
            "title": "How to Reset User Password in Active Directory",
            "content": """
# Password Reset Procedure

## Overview
This procedure describes how to reset a user password in Active Directory.

## Prerequisites
- Administrative access to Active Directory
- User account information

## Steps
1. Open Active Directory Users and Computers
2. Navigate to the user's organizational unit
3. Right-click on the user account
4. Select "Reset Password"
5. Enter new temporary password
6. Check "User must change password at next logon"
7. Click OK
8. Notify user of temporary password

## Notes
- Temporary passwords should be complex
- User should change password immediately
- Document the reset in ticket system
            """,
            "summary": "Step-by-step guide for resetting user passwords in Active Directory",
            "article_type": ArticleType.PROCEDURE,
            "status": ArticleStatus.PUBLISHED,
            "author_id": mike.id if mike else 1,
            "category_id": software_cat.id if software_cat else 1,
            "tags": "password,active directory,user management",
            "is_featured": True
        },
        {
            "title": "Troubleshooting Network Connectivity Issues",
            "content": """
# Network Connectivity Troubleshooting

## Common Issues
- No internet access
- Slow connection
- Intermittent connectivity

## Diagnostic Steps
1. Check physical connections
2. Verify IP configuration
3. Test DNS resolution
4. Check firewall settings
5. Ping gateway and external hosts

## Tools
- ipconfig/ifconfig
- ping
- traceroute
- nslookup

## Resolution Steps
1. Restart network adapter
2. Renew IP address
3. Flush DNS cache
4. Check cable connections
5. Contact network team if issue persists
            """,
            "summary": "Comprehensive guide for diagnosing and resolving network connectivity problems",
            "article_type": ArticleType.TROUBLESHOOTING,
            "status": ArticleStatus.PUBLISHED,
            "author_id": lisa.id if lisa else 1,
            "category_id": network_cat.id if network_cat else 1,
            "tags": "network,connectivity,troubleshooting",
            "view_count": 156,
            "helpful_count": 23,
            "not_helpful_count": 2
        },
        {
            "title": "Printer Installation and Configuration",
            "content": """
# Printer Setup Guide

## Network Printer Installation
1. Open Control Panel
2. Go to Devices and Printers
3. Click "Add a printer"
4. Select "Add a network printer"
5. Enter printer IP address
6. Install appropriate drivers
7. Set as default if needed

## Troubleshooting
- Check network connectivity
- Verify printer IP address
- Update printer drivers
- Clear print queue if stuck

## Common Issues
- Driver conflicts
- Network connectivity
- Print queue problems
- Paper jams
            """,
            "summary": "Guide for installing and configuring network printers",
            "article_type": ArticleType.PROCEDURE,
            "status": ArticleStatus.PUBLISHED,
            "author_id": mike.id if mike else 1,
            "category_id": hardware_cat.id if hardware_cat else 1,
            "tags": "printer,installation,hardware",
            "view_count": 89,
            "helpful_count": 15,
            "not_helpful_count": 1
        }
    ]
    
    for article_data in articles:
        existing = db.query(KnowledgeArticle).filter(KnowledgeArticle.title == article_data["title"]).first()
        if not existing:
            article = KnowledgeArticle(**article_data)
            db.add(article)
    
    db.commit()
    logger.info("Created sample knowledge articles")


def create_tags(db: Session):
    """Create sample tags"""
    tag_names = [
        "urgent", "hardware", "software", "network", "security", 
        "password", "email", "printer", "login", "database",
        "server", "backup", "maintenance", "upgrade", "installation"
    ]
    
    for tag_name in tag_names:
        existing = db.query(Tag).filter(Tag.name == tag_name).first()
        if not existing:
            tag = Tag(name=tag_name, color=f"#{hash(tag_name) % 0xFFFFFF:06x}")
            db.add(tag)
    
    db.commit()
    logger.info("Created sample tags")


def create_tickets(db: Session):
    """Create sample tickets"""
    # Get users and departments
    john = db.query(User).filter(User.email == "john.doe@company.com").first()
    jane = db.query(User).filter(User.email == "jane.smith@company.com").first()
    sarah = db.query(User).filter(User.email == "sarah.tech@company.com").first()
    tom = db.query(User).filter(User.email == "tom.support@company.com").first()
    mike = db.query(User).filter(User.email == "mike.senior@company.com").first()
    
    it_support = db.query(Department).filter(Department.name == "IT Support").first()
    
    # Generate ticket IDs
    def generate_ticket_id():
        today = datetime.now().strftime("%Y%m%d")
        random_suffix = str(uuid.uuid4().int)[:5]
        return f"INC-{today}-{random_suffix}"
    
    tickets = [
        {
            "id": generate_ticket_id(),
            "title": "Unable to login to company portal",
            "description": "User reports getting 'Invalid credentials' error when trying to login to the company portal. Password reset was attempted but issue persists.",
            "status": TicketStatus.IN_PROGRESS,
            "priority": TicketPriority.HIGH,
            "category": TicketCategory.SOFTWARE,
            "reported_by_id": john.id if john else 1,
            "assigned_to_id": sarah.id if sarah else None,
            "department_id": it_support.id if it_support else 1,
            "created_at": datetime.utcnow() - timedelta(hours=2),
            "sla_deadline": datetime.utcnow() + timedelta(hours=6)
        },
        {
            "id": generate_ticket_id(),
            "title": "Email not syncing on mobile device",
            "description": "Employee's email is not syncing properly on their mobile device. They can receive emails but cannot send them.",
            "status": TicketStatus.OPEN,
            "priority": TicketPriority.MEDIUM,
            "category": TicketCategory.SOFTWARE,
            "reported_by_id": jane.id if jane else 1,
            "department_id": it_support.id if it_support else 1,
            "created_at": datetime.utcnow() - timedelta(hours=1),
            "sla_deadline": datetime.utcnow() + timedelta(hours=23)
        },
        {
            "id": generate_ticket_id(),
            "title": "Printer not responding",
            "description": "Office printer on 3rd floor is not responding to print jobs. Status shows as offline.",
            "status": TicketStatus.RESOLVED,
            "priority": TicketPriority.LOW,
            "category": TicketCategory.HARDWARE,
            "reported_by_id": john.id if john else 1,
            "assigned_to_id": tom.id if tom else None,
            "department_id": it_support.id if it_support else 1,
            "created_at": datetime.utcnow() - timedelta(days=1),
            "resolved_at": datetime.utcnow() - timedelta(hours=2),
            "sla_deadline": datetime.utcnow() + timedelta(hours=70),
            "resolution": "Printer was offline due to network cable disconnection. Reconnected cable and printer is now working normally."
        },
        {
            "id": generate_ticket_id(),
            "title": "VPN connection keeps dropping",
            "description": "VPN connection is unstable and keeps disconnecting every few minutes. This is affecting remote work productivity.",
            "status": TicketStatus.ESCALATED,
            "priority": TicketPriority.HIGH,
            "category": TicketCategory.NETWORK,
            "reported_by_id": jane.id if jane else 1,
            "assigned_to_id": mike.id if mike else None,
            "department_id": it_support.id if it_support else 1,
            "created_at": datetime.utcnow() - timedelta(hours=4),
            "sla_deadline": datetime.utcnow() + timedelta(hours=4),
            "escalation_reason": "Complex network issue requiring L2 expertise",
            "is_escalated": True
        },
        {
            "id": generate_ticket_id(),
            "title": "Software installation request",
            "description": "Need to install Adobe Acrobat Pro on workstation for document editing tasks.",
            "status": TicketStatus.OPEN,
            "priority": TicketPriority.LOW,
            "category": TicketCategory.SERVICE_REQUEST,
            "reported_by_id": john.id if john else 1,
            "department_id": it_support.id if it_support else 1,
            "created_at": datetime.utcnow() - timedelta(minutes=30),
            "sla_deadline": datetime.utcnow() + timedelta(hours=71)
        }
    ]
    
    for ticket_data in tickets:
        existing = db.query(Ticket).filter(Ticket.id == ticket_data["id"]).first()
        if not existing:
            ticket = Ticket(**ticket_data)
            db.add(ticket)
    
    db.commit()
    logger.info("Created sample tickets")


def create_chat_messages(db: Session):
    """Create sample chat messages"""
    # Get a ticket and users
    ticket = db.query(Ticket).filter(Ticket.status == TicketStatus.IN_PROGRESS).first()
    if not ticket:
        return
    
    sarah = db.query(User).filter(User.email == "sarah.tech@company.com").first()
    john = db.query(User).filter(User.email == "john.doe@company.com").first()
    
    messages = [
        {
            "ticket_id": ticket.id,
            "sender_id": sarah.id if sarah else None,
            "message": "Hi John, I'm looking into your login issue. Can you tell me which browser you're using?",
            "created_at": datetime.utcnow() - timedelta(minutes=30)
        },
        {
            "ticket_id": ticket.id,
            "sender_id": john.id if john else None,
            "message": "I'm using Chrome. I've also tried Firefox with the same result.",
            "created_at": datetime.utcnow() - timedelta(minutes=25)
        },
        {
            "ticket_id": ticket.id,
            "sender_id": sarah.id if sarah else None,
            "message": "Thanks for that information. Let me check your account status in Active Directory.",
            "created_at": datetime.utcnow() - timedelta(minutes=20)
        },
        {
            "ticket_id": ticket.id,
            "sender_id": None,
            "message": "I found some similar issues in the knowledge base. Here are some troubleshooting steps you can try...",
            "is_ai_message": True,
            "created_at": datetime.utcnow() - timedelta(minutes=15)
        }
    ]
    
    for msg_data in messages:
        message = ChatMessage(**msg_data)
        db.add(message)
    
    db.commit()
    logger.info("Created sample chat messages")


def seed_database():
    """
    Seed the database with sample data
    """
    db = SessionLocal()
    try:
        logger.info("Starting database seeding...")
        
        create_departments(db)
        create_users(db)
        create_knowledge_categories(db)
        create_knowledge_articles(db)
        create_tags(db)
        create_tickets(db)
        create_chat_messages(db)
        
        logger.info("Database seeding completed successfully!")
        
    except Exception as e:
        logger.error(f"Error seeding database: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
