"""
Utility functions for ticket management
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.models.ticket import Ticket, TicketStatus, TicketPriority, TicketCategory
from app.models.user import User, UserRole
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


def auto_assign_ticket(ticket: Ticket, db: Session) -> Optional[User]:
    """
    Automatically assign a ticket to the best available engineer
    """
    try:
        # Get available engineers based on ticket priority and category
        if ticket.priority == TicketPriority.CRITICAL:
            # Critical tickets go to L2 engineers first
            engineers = db.query(User).filter(
                User.role == UserRole.L2_ENGINEER,
                User.is_active == True
            ).all()
        else:
            # Other tickets go to L1 engineers first
            engineers = db.query(User).filter(
                User.role == UserRole.L1_ENGINEER,
                User.is_active == True
            ).all()
        
        if not engineers:
            # Fallback to any available engineer
            engineers = db.query(User).filter(
                User.role.in_([UserRole.L1_ENGINEER, UserRole.L2_ENGINEER]),
                User.is_active == True
            ).all()
        
        if not engineers:
            return None
        
        # Calculate workload for each engineer
        engineer_workloads = []
        for engineer in engineers:
            current_workload = db.query(Ticket).filter(
                Ticket.assigned_to_id == engineer.id,
                Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS])
            ).count()
            
            engineer_workloads.append({
                "engineer": engineer,
                "workload": current_workload
            })
        
        # Sort by workload (ascending) and assign to engineer with least workload
        engineer_workloads.sort(key=lambda x: x["workload"])
        selected_engineer = engineer_workloads[0]["engineer"]
        
        # Assign the ticket
        ticket.assigned_to_id = selected_engineer.id
        ticket.status = TicketStatus.IN_PROGRESS
        
        db.commit()
        
        logger.info(f"Auto-assigned ticket {ticket.id} to {selected_engineer.name}")
        return selected_engineer
        
    except Exception as e:
        logger.error(f"Error auto-assigning ticket {ticket.id}: {str(e)}")
        db.rollback()
        return None


def calculate_sla_deadline(priority: TicketPriority, category: TicketCategory, 
                          created_at: datetime = None) -> datetime:
    """
    Calculate SLA deadline based on priority and category
    """
    if not created_at:
        created_at = datetime.utcnow()
    
    # Base SLA times in hours
    sla_hours = {
        TicketPriority.CRITICAL: 2,
        TicketPriority.HIGH: 8,
        TicketPriority.MEDIUM: 24,
        TicketPriority.LOW: 72
    }
    
    base_hours = sla_hours.get(priority, 24)
    
    # Adjust based on category
    category_multipliers = {
        TicketCategory.INCIDENT: 1.0,      # Standard time for incidents
        TicketCategory.SERVICE_REQUEST: 1.5,  # Longer for service requests
        TicketCategory.PROBLEM: 2.0,       # Longer for problem analysis
        TicketCategory.CHANGE: 3.0,        # Much longer for changes
        TicketCategory.HARDWARE: 1.2,      # Slightly longer for hardware
        TicketCategory.SOFTWARE: 1.0,      # Standard for software
        TicketCategory.NETWORK: 1.5,       # Longer for network issues
        TicketCategory.SECURITY: 0.8       # Faster for security issues
    }
    
    multiplier = category_multipliers.get(category, 1.0)
    final_hours = base_hours * multiplier
    
    return created_at + timedelta(hours=final_hours)


def check_sla_breaches(db: Session) -> List[Dict[str, Any]]:
    """
    Check for tickets that have breached or are about to breach SLA
    """
    now = datetime.utcnow()
    
    # Find tickets that have breached SLA
    breached_tickets = db.query(Ticket).filter(
        Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS]),
        Ticket.sla_deadline < now
    ).all()
    
    # Find tickets approaching SLA breach (within 1 hour)
    approaching_breach = db.query(Ticket).filter(
        Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS]),
        Ticket.sla_deadline >= now,
        Ticket.sla_deadline <= now + timedelta(hours=1)
    ).all()
    
    results = []
    
    for ticket in breached_tickets:
        breach_time = now - ticket.sla_deadline
        results.append({
            "ticket_id": ticket.id,
            "title": ticket.title,
            "priority": ticket.priority.value,
            "assignee": ticket.assignee.name if ticket.assignee else "Unassigned",
            "status": "breached",
            "breach_time_hours": round(breach_time.total_seconds() / 3600, 2),
            "sla_deadline": ticket.sla_deadline.isoformat()
        })
    
    for ticket in approaching_breach:
        time_remaining = ticket.sla_deadline - now
        results.append({
            "ticket_id": ticket.id,
            "title": ticket.title,
            "priority": ticket.priority.value,
            "assignee": ticket.assignee.name if ticket.assignee else "Unassigned",
            "status": "approaching_breach",
            "time_remaining_hours": round(time_remaining.total_seconds() / 3600, 2),
            "sla_deadline": ticket.sla_deadline.isoformat()
        })
    
    return results


def escalate_ticket(ticket: Ticket, reason: str, escalated_by: User, db: Session) -> bool:
    """
    Escalate a ticket to the next level
    """
    try:
        # Determine escalation target based on current assignment
        if ticket.assignee and ticket.assignee.role == UserRole.L1_ENGINEER:
            # Escalate from L1 to L2
            target_role = UserRole.L2_ENGINEER
        else:
            # Escalate to management
            target_role = UserRole.OPS_MANAGER
        
        # Find available engineers/managers
        available_users = db.query(User).filter(
            User.role == target_role,
            User.is_active == True
        ).all()
        
        if not available_users:
            logger.warning(f"No available {target_role.value} for escalation of ticket {ticket.id}")
            return False
        
        # For now, assign to first available user
        # In production, implement more sophisticated assignment logic
        new_assignee = available_users[0]
        
        # Update ticket
        old_assignee = ticket.assignee
        ticket.assigned_to_id = new_assignee.id
        ticket.status = TicketStatus.ESCALATED
        ticket.escalation_reason = reason
        ticket.is_escalated = True
        
        # Log escalation activity
        from app.models.ticket import TicketActivity
        activity = TicketActivity(
            ticket_id=ticket.id,
            user_id=escalated_by.id,
            activity_type="escalated",
            details={
                "reason": reason,
                "from_user": old_assignee.name if old_assignee else "Unassigned",
                "to_user": new_assignee.name,
                "escalated_by": escalated_by.name
            }
        )
        
        db.add(activity)
        db.commit()
        
        logger.info(f"Escalated ticket {ticket.id} from {old_assignee.name if old_assignee else 'Unassigned'} to {new_assignee.name}")
        return True
        
    except Exception as e:
        logger.error(f"Error escalating ticket {ticket.id}: {str(e)}")
        db.rollback()
        return False


def get_ticket_metrics(tickets: List[Ticket]) -> Dict[str, Any]:
    """
    Calculate various metrics for a list of tickets
    """
    if not tickets:
        return {
            "total_tickets": 0,
            "avg_resolution_time": 0,
            "sla_compliance_rate": 100,
            "priority_distribution": {},
            "status_distribution": {},
            "category_distribution": {}
        }
    
    total_tickets = len(tickets)
    resolved_tickets = [t for t in tickets if t.status == TicketStatus.RESOLVED and t.resolved_at]
    
    # Calculate average resolution time
    if resolved_tickets:
        resolution_times = [
            (t.resolved_at - t.created_at).total_seconds() / 3600 
            for t in resolved_tickets
        ]
        avg_resolution_time = sum(resolution_times) / len(resolution_times)
    else:
        avg_resolution_time = 0
    
    # Calculate SLA compliance
    if resolved_tickets:
        sla_compliant = [t for t in resolved_tickets if t.resolved_at <= t.sla_deadline]
        sla_compliance_rate = len(sla_compliant) / len(resolved_tickets) * 100
    else:
        sla_compliance_rate = 100
    
    # Priority distribution
    priority_distribution = {}
    for priority in TicketPriority:
        count = len([t for t in tickets if t.priority == priority])
        priority_distribution[priority.value] = count
    
    # Status distribution
    status_distribution = {}
    for status in TicketStatus:
        count = len([t for t in tickets if t.status == status])
        status_distribution[status.value] = count
    
    # Category distribution
    category_distribution = {}
    for category in TicketCategory:
        count = len([t for t in tickets if t.category == category])
        category_distribution[category.value] = count
    
    return {
        "total_tickets": total_tickets,
        "avg_resolution_time": round(avg_resolution_time, 2),
        "sla_compliance_rate": round(sla_compliance_rate, 1),
        "priority_distribution": priority_distribution,
        "status_distribution": status_distribution,
        "category_distribution": category_distribution
    }


def suggest_ticket_assignment(ticket: Ticket, db: Session) -> List[Dict[str, Any]]:
    """
    Suggest the best engineers to assign a ticket to
    """
    # Get engineers based on ticket requirements
    if ticket.priority == TicketPriority.CRITICAL:
        engineers = db.query(User).filter(
            User.role.in_([UserRole.L2_ENGINEER, UserRole.L1_ENGINEER]),
            User.is_active == True
        ).all()
    else:
        engineers = db.query(User).filter(
            User.role == UserRole.L1_ENGINEER,
            User.is_active == True
        ).all()
    
    suggestions = []
    for engineer in engineers:
        # Calculate current workload
        current_workload = db.query(Ticket).filter(
            Ticket.assigned_to_id == engineer.id,
            Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS])
        ).count()
        
        # Calculate skill match (simplified - in production, use skill matrix)
        skill_match = 80  # Mock skill matching
        if engineer.role == UserRole.L2_ENGINEER:
            skill_match += 10
        
        # Calculate availability score
        max_workload = 10  # Assume max 10 tickets per engineer
        availability_score = max(0, (max_workload - current_workload) / max_workload * 100)
        
        # Calculate overall score
        overall_score = (skill_match * 0.6) + (availability_score * 0.4)
        
        suggestions.append({
            "engineer_id": engineer.id,
            "engineer_name": engineer.name,
            "role": engineer.role.value,
            "current_workload": current_workload,
            "skill_match": skill_match,
            "availability_score": round(availability_score, 1),
            "overall_score": round(overall_score, 1)
        })
    
    # Sort by overall score (descending)
    suggestions.sort(key=lambda x: x["overall_score"], reverse=True)
    
    return suggestions[:5]  # Return top 5 suggestions
