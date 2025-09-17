from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc

from app.core.database import get_db
from app.api.dependencies import get_current_user, require_roles
from app.models.user import User
from app.models.ticket import Ticket
from app.models.knowledge import KnowledgeArticle
from app.models.analytics import PerformanceMetric, SLAReport
from app.schemas.analytics import (
    DashboardMetrics,
    TeamPerformanceResponse,
    SLAReportResponse,
    TicketAnalyticsResponse,
    KnowledgeAnalyticsResponse,
    SystemHealthResponse,
    PerformanceTrendResponse
)
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])

def get_analytics_service(db: Session = Depends(get_db)) -> AnalyticsService:
    """Dependency to provide AnalyticsService instance"""
    return AnalyticsService(db)

@router.get("/dashboard", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Get dashboard metrics for the current user's role"""
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Base metrics for all roles
    total_tickets_query = await db.execute(Ticket.__table__.select().where(
        Ticket.created_at >= start_date
    ))
    total_tickets = len(total_tickets_query.fetchall())
    
    resolved_tickets_query = await db.execute(Ticket.__table__.select().where(
        and_(
            Ticket.created_at >= start_date,
            Ticket.status == "resolved"
        )
    ))
    resolved_tickets = len(resolved_tickets_query.fetchall())
    
    # Role-specific metrics
    if current_user.role == "end_user":
        my_tickets_query = await db.execute(Ticket.__table__.select().where(
            and_(
                Ticket.reporter_id == current_user.id,
                Ticket.created_at >= start_date
            )
        ))
        my_tickets = len(my_tickets_query.fetchall())
        
        my_open_tickets_query = await db.execute(Ticket.__table__.select().where(
            and_(
                Ticket.reporter_id == current_user.id,
                Ticket.status.in_(["open", "in_progress"])
            )
        ))
        my_open_tickets = len(my_open_tickets_query.fetchall())
        
        return DashboardMetrics(
            total_tickets=my_tickets,
            open_tickets=my_open_tickets,
            resolved_tickets=my_tickets - my_open_tickets,
            sla_compliance=0,  # Not applicable for end users
            avg_resolution_time=0,
            user_role=current_user.role
        )
    
    elif current_user.role in ["l1_engineer", "l2_engineer"]:
        assigned_tickets_query = await db.execute(Ticket.__table__.select().where(
            and_(
                Ticket.assigned_to == current_user.id,
                Ticket.created_at >= start_date
            )
        ))
        assigned_tickets = len(assigned_tickets_query.fetchall())
        
        my_resolved_query = await db.execute(Ticket.__table__.select().where(
            and_(
                Ticket.assigned_to == current_user.id,
                Ticket.status == "resolved",
                Ticket.created_at >= start_date
            )
        ))
        my_resolved = len(my_resolved_query.fetchall())
        
        # Calculate average resolution time
        avg_resolution = await analytics_service.get_avg_resolution_time(
            current_user.id, start_date, end_date
        )
        
        # Calculate SLA compliance
        sla_compliance = await analytics_service.get_sla_compliance(
            current_user.id, start_date, end_date
        )
        
        return DashboardMetrics(
            total_tickets=assigned_tickets,
            open_tickets=assigned_tickets - my_resolved,
            resolved_tickets=my_resolved,
            sla_compliance=sla_compliance,
            avg_resolution_time=avg_resolution,
            user_role=current_user.role
        )
    
    else:  # Manager roles
        sla_compliance = await analytics_service.get_team_sla_compliance(
            start_date, end_date
        )
        
        avg_resolution = await analytics_service.get_team_avg_resolution_time(
            start_date, end_date
        )
        
        return DashboardMetrics(
            total_tickets=total_tickets,
            open_tickets=total_tickets - resolved_tickets,
            resolved_tickets=resolved_tickets,
            sla_compliance=sla_compliance,
            avg_resolution_time=avg_resolution,
            user_role=current_user.role
        )

@router.get("/team-performance", response_model=TeamPerformanceResponse)
async def get_team_performance(
    days: int = Query(30, ge=1, le=365),
    team_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ops_manager", "transition_manager"])),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Get team performance analytics"""
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get team members
    team_query = User.__table__.select().where(
        User.role.in_(["l1_engineer", "l2_engineer"])
    )
    
    if team_id:
        team_query = team_query.where(User.team_id == team_id)
    
    team_members_query = await db.execute(team_query)
    team_members = team_members_query.fetchall()
    
    performance_data = []
    
    for member in team_members:
        # Get member's ticket statistics
        member_tickets_query = await db.execute(Ticket.__table__.select().where(
            and_(
                Ticket.assigned_to == member.id,
                Ticket.created_at >= start_date
            )
        ))
        member_tickets = len(member_tickets_query.fetchall())
        
        member_resolved_query = await db.execute(Ticket.__table__.select().where(
            and_(
                Ticket.assigned_to == member.id,
                Ticket.status == "resolved",
                Ticket.created_at >= start_date
            )
        ))
        member_resolved = len(member_resolved_query.fetchall())
        
        # Calculate metrics
        avg_resolution = await analytics_service.get_avg_resolution_time(
            member.id, start_date, end_date
        )
        
        sla_compliance = await analytics_service.get_sla_compliance(
            member.id, start_date, end_date
        )
        
        # Get current workload
        current_workload_query = await db.execute(Ticket.__table__.select().where(
            and_(
                Ticket.assigned_to == member.id,
                Ticket.status.in_(["open", "in_progress"])
            )
        ))
        current_workload = len(current_workload_query.fetchall())
        
        performance_data.append({
            "user_id": member.id,
            "name": member.full_name,
            "role": member.role,
            "total_tickets": member_tickets,
            "resolved_tickets": member_resolved,
            "avg_resolution_time": avg_resolution,
            "sla_compliance": sla_compliance,
            "current_workload": current_workload,
            "skills": member.skills or []
        })
    
    # Calculate team averages
    total_team_tickets = sum(p["total_tickets"] for p in performance_data)
    total_team_resolved = sum(p["resolved_tickets"] for p in performance_data)
    avg_team_resolution = sum(p["avg_resolution_time"] for p in performance_data) / len(performance_data) if performance_data else 0
    avg_team_sla = sum(p["sla_compliance"] for p in performance_data) / len(performance_data) if performance_data else 0
    
    return TeamPerformanceResponse(
        period_days=days,
        team_members=performance_data,
        team_summary={
            "total_tickets": total_team_tickets,
            "resolved_tickets": total_team_resolved,
            "avg_resolution_time": avg_team_resolution,
            "sla_compliance": avg_team_sla,
            "team_size": len(performance_data)
        }
    )

@router.get("/sla-report", response_model=SLAReportResponse)
async def get_sla_report(
    days: int = Query(30, ge=1, le=365),
    priority: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ops_manager", "transition_manager"])),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Get SLA compliance report"""
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Build query
    query = Ticket.__table__.select().where(
        Ticket.created_at >= start_date
    )
    
    if priority:
        query = query.where(Ticket.priority == priority)
    
    if category:
        query = query.where(Ticket.category == category)
    
    tickets_query = await db.execute(query)
    tickets = tickets_query.fetchall()
    
    # Calculate SLA metrics
    sla_data = await analytics_service.calculate_sla_metrics(tickets)
    
    # Group by priority
    priority_breakdown = {}
    for ticket in tickets:
        if ticket.priority not in priority_breakdown:
            priority_breakdown[ticket.priority] = {
                "total": 0,
                "met": 0,
                "breached": 0,
                "at_risk": 0
            }
        
        priority_breakdown[ticket.priority]["total"] += 1
        
        if ticket.sla_status == "met":
            priority_breakdown[ticket.priority]["met"] += 1
        elif ticket.sla_status == "breached":
            priority_breakdown[ticket.priority]["breached"] += 1
        else:
            priority_breakdown[ticket.priority]["at_risk"] += 1
    
    # Calculate compliance percentages
    for priority_data in priority_breakdown.values():
        if priority_data["total"] > 0:
            priority_data["compliance_rate"] = (
                priority_data["met"] / priority_data["total"] * 100
            )
        else:
            priority_data["compliance_rate"] = 0
    
    return SLAReportResponse(
        period_days=days,
        overall_compliance=sla_data["overall_compliance"],
        total_tickets=len(tickets),
        met_sla=sla_data["met_count"],
        breached_sla=sla_data["breached_count"],
        at_risk=sla_data["at_risk_count"],
        priority_breakdown=priority_breakdown,
        trends=sla_data["trends"]
    )

@router.get("/tickets", response_model=TicketAnalyticsResponse)
async def get_ticket_analytics(
    days: int = Query(30, ge=1, le=365),
    group_by: str = Query("day", regex="^(day|week|month|category|priority|status)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ops_manager", "transition_manager"])),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Get ticket analytics and trends"""
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get ticket data
    tickets_query = await db.execute(Ticket.__table__.select().where(
        Ticket.created_at >= start_date
    ))
    tickets = tickets_query.fetchall()
    
    # Generate analytics based on grouping
    analytics_data = await analytics_service.generate_ticket_analytics(
        tickets, group_by, start_date, end_date
    )
    
    # Calculate trends
    trends = await analytics_service.calculate_ticket_trends(
        tickets, start_date, end_date
    )
    
    # Top categories and priorities
    category_stats = {}
    priority_stats = {}
    
    for ticket in tickets:
        # Category stats
        if ticket.category not in category_stats:
            category_stats[ticket.category] = {"count": 0, "resolved": 0}
        category_stats[ticket.category]["count"] += 1
        if ticket.status == "resolved":
            category_stats[ticket.category]["resolved"] += 1
        
        # Priority stats
        if ticket.priority not in priority_stats:
            priority_stats[ticket.priority] = {"count": 0, "resolved": 0}
        priority_stats[ticket.priority]["count"] += 1
        if ticket.status == "resolved":
            priority_stats[ticket.priority]["resolved"] += 1
    
    return TicketAnalyticsResponse(
        period_days=days,
        total_tickets=len(tickets),
        analytics_data=analytics_data,
        trends=trends,
        category_breakdown=category_stats,
        priority_breakdown=priority_stats,
        resolution_rate=len([t for t in tickets if t.status == "resolved"]) / len(tickets) * 100 if tickets else 0
    )

@router.get("/knowledge", response_model=KnowledgeAnalyticsResponse)
async def get_knowledge_analytics(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ops_manager", "transition_manager"])),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Get knowledge base analytics"""
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get knowledge articles
    articles_query = await db.execute(KnowledgeArticle.__table__.select())
    articles = articles_query.fetchall()
    
    # Calculate metrics
    total_articles = len(articles)
    published_articles = len([a for a in articles if a.status == "published"])
    draft_articles = len([a for a in articles if a.status == "draft"])
    
    # Most viewed articles
    popular_articles = sorted(
        articles, 
        key=lambda x: x.view_count or 0, 
        reverse=True
    )[:10]
    
    # Articles by category
    category_stats = {}
    for article in articles:
        category_name = article.category.name if article.category else "Uncategorized"
        if category_name not in category_stats:
            category_stats[category_name] = {
                "total": 0,
                "published": 0,
                "views": 0
            }
        category_stats[category_name]["total"] += 1
        if article.status == "published":
            category_stats[category_name]["published"] += 1
        category_stats[category_name]["views"] += article.view_count or 0
    
    # Usage trends
    usage_trends = await analytics_service.get_knowledge_usage_trends(
        start_date, end_date
    )
    
    return KnowledgeAnalyticsResponse(
        total_articles=total_articles,
        published_articles=published_articles,
        draft_articles=draft_articles,
        total_views=sum(a.view_count or 0 for a in articles),
        popular_articles=[
            {
                "id": a.id,
                "title": a.title,
                "views": a.view_count or 0,
                "rating": a.average_rating or 0
            }
            for a in popular_articles
        ],
        category_breakdown=category_stats,
        usage_trends=usage_trends
    )

@router.get("/system-health", response_model=SystemHealthResponse)
async def get_system_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ops_manager", "transition_manager"])),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Get system health metrics"""
    
    # Get current system metrics
    health_data = await analytics_service.get_system_health_metrics()
    
    # Get queue status
    unassigned_tickets_query = await db.execute(Ticket.__table__.select().where(
        and_(
            Ticket.assigned_to.is_(None),
            Ticket.status.in_(["open", "in_progress"])
        )
    ))
    unassigned_tickets = len(unassigned_tickets_query.fetchall())
    
    # Get team availability
    available_engineers_query = await db.execute(User.__table__.select().where(
        and_(
            User.role.in_(["l1_engineer", "l2_engineer"]),
            User.is_active == True
        )
    ))
    available_engineers = len(available_engineers_query.fetchall())
    
    # Calculate system load
    total_open_tickets_query = await db.execute(Ticket.__table__.select().where(
        Ticket.status.in_(["open", "in_progress"])
    ))
    total_open_tickets = len(total_open_tickets_query.fetchall())
    
    system_load = (total_open_tickets / available_engineers) if available_engineers > 0 else 0
    
    # Determine overall health status
    if system_load > 10 or unassigned_tickets > 20:
        health_status = "critical"
    elif system_load > 5 or unassigned_tickets > 10:
        health_status = "warning"
    else:
        health_status = "healthy"
    
    return SystemHealthResponse(
        status=health_status,
        system_load=system_load,
        queue_size=unassigned_tickets,
        available_engineers=available_engineers,
        response_time=health_data.get("avg_response_time", 0),
        uptime=health_data.get("uptime", 99.9),
        alerts=[
            {
                "level": "warning" if unassigned_tickets > 10 else "info",
                "message": f"{unassigned_tickets} unassigned tickets in queue",
                "timestamp": datetime.utcnow().isoformat()
            }
        ] if unassigned_tickets > 0 else []
    )

@router.get("/trends", response_model=PerformanceTrendResponse)
async def get_performance_trends(
    days: int = Query(90, ge=7, le=365),
    metric: str = Query("resolution_time", regex="^(resolution_time|sla_compliance|ticket_volume|satisfaction)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ops_manager", "transition_manager"])),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Get performance trends over time"""
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Generate trend data
    trend_data = await analytics_service.generate_performance_trends(
        metric, start_date, end_date, db
    )
    
    return PerformanceTrendResponse(
        metric=metric,
        period_days=days,
        data_points=trend_data["data_points"],
        trend_direction=trend_data["trend_direction"],
        percentage_change=trend_data["percentage_change"],
        insights=trend_data["insights"]
    )

@router.post("/reports/generate")
async def generate_custom_report(
    report_config: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ops_manager", "transition_manager"])),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Generate a custom analytics report"""
    
    try:
        report_data = await analytics_service.generate_custom_report(
            report_config, db
        )
        
        return {
            "report_id": report_data["report_id"],
            "status": "generated",
            "download_url": report_data["download_url"],
            "expires_at": report_data["expires_at"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Report generation failed: {str(e)}"
        )

@router.get("/export/{format}")
async def export_analytics(
    format: str,  # This is a path parameter, so no need to use Query
    report_type: str = Query("dashboard", regex="^(dashboard|team|sla|tickets|knowledge)$"),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ops_manager", "transition_manager"])),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Export analytics data in various formats"""

    # Validate the format parameter manually if needed
    if format not in ["csv", "xlsx", "pdf"]:
        raise HTTPException(status_code=400, detail="Invalid format. Choose from: csv, xlsx, pdf")

    try:
        export_data = await analytics_service.export_analytics_data(
            report_type, format, days, db
        )

        return {
            "download_url": export_data["download_url"],
            "filename": export_data["filename"],
            "expires_at": export_data["expires_at"]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Export failed: {str(e)}"
        )