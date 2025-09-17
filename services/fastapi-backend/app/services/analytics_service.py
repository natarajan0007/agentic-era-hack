"""
Analytics service for generating insights and reports
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from app.models.ticket import Ticket, TicketStatus, TicketPriority, TicketCategory
from app.models.user import User, UserRole
from app.models.analytics import AnalyticsEvent, SystemMetric
import logging

logger = logging.getLogger(__name__)


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_ticket_analytics(self, 
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None,
                           department_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get comprehensive ticket analytics
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Base query
        query = Ticket.__table__.select().where(
            and_(
                Ticket.created_at >= start_date,
                Ticket.created_at <= end_date
            )
        )
        
        if department_id:
            query = query.where(Ticket.department_id == department_id)
        
        tickets_query = await self.db.execute(query)
        tickets = tickets_query.fetchall()
        
        # Basic metrics
        total_tickets = len(tickets)
        resolved_tickets = len([t for t in tickets if t.status == TicketStatus.RESOLVED])
        open_tickets = len([t for t in tickets if t.status == TicketStatus.OPEN])
        in_progress_tickets = len([t for t in tickets if t.status == TicketStatus.IN_PROGRESS])
        escalated_tickets = len([t for t in tickets if t.is_escalated])
        
        # Priority distribution
        priority_distribution = {}
        for priority in TicketPriority:
            count = len([t for t in tickets if t.priority == priority])
            priority_distribution[priority.value] = count
        
        # Category distribution
        category_distribution = {}
        for category in TicketCategory:
            count = len([t for t in tickets if t.category == category])
            category_distribution[category.value] = count
        
        # Resolution time analysis
        resolved_with_time = [t for t in tickets if t.resolved_at and t.status == TicketStatus.RESOLVED]
        if resolved_with_time:
            resolution_times = [
                (t.resolved_at - t.created_at).total_seconds() / 3600 
                for t in resolved_with_time
            ]
            avg_resolution_time = sum(resolution_times) / len(resolution_times)
            min_resolution_time = min(resolution_times)
            max_resolution_time = max(resolution_times)
        else:
            avg_resolution_time = 0
            min_resolution_time = 0
            max_resolution_time = 0
        
        # SLA compliance
        sla_compliant = len([
            t for t in resolved_with_time 
            if t.resolved_at <= t.sla_deadline
        ])
        sla_compliance_rate = (sla_compliant / len(resolved_with_time) * 100) if resolved_with_time else 100
        
        # Daily trends
        daily_trends = await self._get_daily_ticket_trends(start_date, end_date, department_id)
        
        return {
            "summary": {
                "total_tickets": total_tickets,
                "resolved_tickets": resolved_tickets,
                "open_tickets": open_tickets,
                "in_progress_tickets": in_progress_tickets,
                "escalated_tickets": escalated_tickets,
                "resolution_rate": (resolved_tickets / total_tickets * 100) if total_tickets > 0 else 0
            },
            "priority_distribution": priority_distribution,
            "category_distribution": category_distribution,
            "resolution_metrics": {
                "avg_resolution_time_hours": round(avg_resolution_time, 2),
                "min_resolution_time_hours": round(min_resolution_time, 2),
                "max_resolution_time_hours": round(max_resolution_time, 2),
                "sla_compliance_rate": round(sla_compliance_rate, 2)
            },
            "daily_trends": daily_trends
        }
    
    async def _get_daily_ticket_trends(self, 
                                start_date: datetime, 
                                end_date: datetime,
                                department_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get daily ticket creation and resolution trends
        """
        trends = []
        current_date = start_date.date()
        end_date_only = end_date.date()
        
        while current_date <= end_date_only:
            next_date = current_date + timedelta(days=1)
            
            # Query for tickets created on this date
            created_query = Ticket.__table__.select().where(
                and_(
                    func.date(Ticket.created_at) == current_date
                )
            )
            
            # Query for tickets resolved on this date
            resolved_query = Ticket.__table__.select().where(
                and_(
                    func.date(Ticket.resolved_at) == current_date,
                    Ticket.status == TicketStatus.RESOLVED
                )
            )
            
            if department_id:
                created_query = created_query.where(Ticket.department_id == department_id)
                resolved_query = resolved_query.where(Ticket.department_id == department_id)
            
            created_count_query = await self.db.execute(created_query)
            created_count = len(created_count_query.fetchall())
            resolved_count_query = await self.db.execute(resolved_query)
            resolved_count = len(resolved_count_query.fetchall())
            
            trends.append({
                "date": current_date.isoformat(),
                "created": created_count,
                "resolved": resolved_count
            })
            
            current_date = next_date
        
        return trends
    
    async def get_team_performance(self, 
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get team performance analytics
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Get all engineers
        engineers_query = await self.db.execute(User.__table__.select().where(
            User.role.in_([UserRole.L1_ENGINEER, UserRole.L2_ENGINEER])
        ))
        engineers = engineers_query.fetchall()
        
        team_stats = []
        for engineer in engineers:
            # Get tickets assigned to this engineer
            assigned_tickets_query = await self.db.execute(Ticket.__table__.select().where(
                and_(
                    Ticket.assigned_to_id == engineer.id,
                    Ticket.created_at >= start_date,
                    Ticket.created_at <= end_date
                )
            ))
            assigned_tickets = assigned_tickets_query.fetchall()
            
            # Get resolved tickets
            resolved_tickets = [t for t in assigned_tickets if t.status == TicketStatus.RESOLVED]
            
            # Calculate metrics
            total_assigned = len(assigned_tickets)
            total_resolved = len(resolved_tickets)
            resolution_rate = (total_resolved / total_assigned * 100) if total_assigned > 0 else 0
            
            # Calculate average resolution time
            if resolved_tickets:
                resolution_times = [
                    (t.resolved_at - t.created_at).total_seconds() / 3600 
                    for t in resolved_tickets if t.resolved_at
                ]
                avg_resolution_time = sum(resolution_times) / len(resolution_times)
            else:
                avg_resolution_time = 0
            
            # Calculate SLA compliance
            sla_compliant = len([
                t for t in resolved_tickets 
                if t.resolved_at and t.resolved_at <= t.sla_deadline
            ])
            sla_compliance = (sla_compliant / len(resolved_tickets) * 100) if resolved_tickets else 100
            
            # Current workload (open + in progress tickets)
            current_workload_query = await self.db.execute(Ticket.__table__.select().where(
                and_(
                    Ticket.assigned_to_id == engineer.id,
                    Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS])
                )
            ))
            current_workload = len(current_workload_query.fetchall())
            
            team_stats.append({
                "engineer_id": engineer.id,
                "engineer_name": engineer.name,
                "role": engineer.role.value,
                "department": engineer.department.name if engineer.department else "Unknown",
                "tickets_assigned": total_assigned,
                "tickets_resolved": total_resolved,
                "resolution_rate": round(resolution_rate, 1),
                "avg_resolution_time": round(avg_resolution_time, 2),
                "sla_compliance": round(sla_compliance, 1),
                "current_workload": current_workload
            })
        
        # Calculate team averages
        if team_stats:
            avg_resolution_rate = sum([s["resolution_rate"] for s in team_stats]) / len(team_stats)
            avg_resolution_time = sum([s["avg_resolution_time"] for s in team_stats]) / len(team_stats)
            avg_sla_compliance = sum([s["sla_compliance"] for s in team_stats]) / len(team_stats)
            total_workload = sum([s["current_workload"] for s in team_stats])
        else:
            avg_resolution_rate = 0
            avg_resolution_time = 0
            avg_sla_compliance = 0
            total_workload = 0
        
        return {
            "team_members": team_stats,
            "team_averages": {
                "avg_resolution_rate": round(avg_resolution_rate, 1),
                "avg_resolution_time": round(avg_resolution_time, 2),
                "avg_sla_compliance": round(avg_sla_compliance, 1),
                "total_current_workload": total_workload
            }
        }
    
    async def get_sla_metrics(self, 
                       start_date: Optional[datetime] = None,
                       end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get detailed SLA compliance metrics
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Get resolved tickets in date range
        resolved_tickets_query = await self.db.execute(Ticket.__table__.select().where(
            and_(
                Ticket.status == TicketStatus.RESOLVED,
                Ticket.resolved_at >= start_date,
                Ticket.resolved_at <= end_date
            )
        ))
        resolved_tickets = resolved_tickets_query.fetchall()
        
        if not resolved_tickets:
            return {
                "overall_compliance": 100.0,
                "by_priority": {},
                "by_category": {},
                "breached_tickets": [],
                "at_risk_tickets": []
            }
        
        # Overall compliance
        sla_compliant = [t for t in resolved_tickets if t.resolved_at <= t.sla_deadline]
        overall_compliance = len(sla_compliant) / len(resolved_tickets) * 100
        
        # Compliance by priority
        priority_compliance = {}
        for priority in TicketPriority:
            priority_tickets = [t for t in resolved_tickets if t.priority == priority]
            if priority_tickets:
                priority_compliant = [t for t in priority_tickets if t.resolved_at <= t.sla_deadline]
                compliance_rate = len(priority_compliant) / len(priority_tickets) * 100
                priority_compliance[priority.value] = {
                    "total": len(priority_tickets),
                    "compliant": len(priority_compliant),
                    "compliance_rate": round(compliance_rate, 1)
                }
        
        # Compliance by category
        category_compliance = {}
        for category in TicketCategory:
            category_tickets = [t for t in resolved_tickets if t.category == category]
            if category_tickets:
                category_compliant = [t for t in category_tickets if t.resolved_at <= t.sla_deadline]
                compliance_rate = len(category_compliant) / len(category_tickets) * 100
                category_compliance[category.value] = {
                    "total": len(category_tickets),
                    "compliant": len(category_compliant),
                    "compliance_rate": round(compliance_rate, 1)
                }
        
        # Breached tickets
        breached_tickets = [
            {
                "id": t.id,
                "title": t.title,
                "priority": t.priority.value,
                "sla_deadline": t.sla_deadline.isoformat(),
                "resolved_at": t.resolved_at.isoformat(),
                "breach_time_hours": round((t.resolved_at - t.sla_deadline).total_seconds() / 3600, 2)
            }
            for t in resolved_tickets if t.resolved_at > t.sla_deadline
        ]
        
        # At-risk tickets (currently open/in-progress, approaching SLA)
        at_risk_tickets_query = await self.db.execute(Ticket.__table__.select().where(
            and_(
                Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS]),
                Ticket.sla_deadline <= datetime.utcnow() + timedelta(hours=4)  # Within 4 hours of SLA
            )
        ))
        at_risk_tickets = at_risk_tickets_query.fetchall()
        
        at_risk_list = [
            {
                "id": t.id,
                "title": t.title,
                "priority": t.priority.value,
                "sla_deadline": t.sla_deadline.isoformat(),
                "time_remaining_hours": round((t.sla_deadline - datetime.utcnow()).total_seconds() / 3600, 2)
            }
            for t in at_risk_tickets
        ]
        
        return {
            "overall_compliance": round(overall_compliance, 1),
            "by_priority": priority_compliance,
            "by_category": category_compliance,
            "breached_tickets": breached_tickets,
            "at_risk_tickets": at_risk_list
        }
    
    async def log_event(self, event_type: str, user_id: Optional[int] = None, 
                  ticket_id: Optional[str] = None, properties: Optional[Dict[str, Any]] = None):
        """
        Log an analytics event
        """
        try:
            event = AnalyticsEvent(
                event_type=event_type,
                user_id=user_id,
                ticket_id=ticket_id,
                properties=properties
            )
            self.db.add(event)
            await self.db.commit()
        except Exception as e:
            logger.error(f"Error logging analytics event: {str(e)}")
            await self.db.rollback()
    
    async def get_user_activity(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Get user activity analytics
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get user events
        events_query = await self.db.execute(AnalyticsEvent.__table__.select().where(
            and_(
                AnalyticsEvent.user_id == user_id,
                AnalyticsEvent.timestamp >= start_date
            )
        ))
        events = events_query.fetchall()
        
        # Group events by type
        event_counts = {}
        for event in events:
            event_counts[event.event_type] = event_counts.get(event.event_type, 0) + 1
        
        # Get user's tickets
        user_tickets_query = await self.db.execute(Ticket.__table__.select().where(
            or_(
                Ticket.reported_by_id == user_id,
                Ticket.assigned_to_id == user_id
            )
        ).where(Ticket.created_at >= start_date))
        user_tickets = user_tickets_query.fetchall()
        
        reported_tickets = len([t for t in user_tickets if t.reported_by_id == user_id])
        assigned_tickets = len([t for t in user_tickets if t.assigned_to_id == user_id])
        resolved_tickets = len([
            t for t in user_tickets 
            if t.assigned_to_id == user_id and t.status == TicketStatus.RESOLVED
        ])
        
        return {
            "user_id": user_id,
            "period_days": days,
            "event_counts": event_counts,
            "ticket_activity": {
                "reported": reported_tickets,
                "assigned": assigned_tickets,
                "resolved": resolved_tickets
            },
            "total_events": len(events)
        }
