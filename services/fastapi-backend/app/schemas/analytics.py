"""
Analytics Pydantic schemas
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class AnalyticsEventBase(BaseModel):
    event_type: str
    properties: Optional[Dict[str, Any]] = None


class AnalyticsEvent(AnalyticsEventBase):
    id: int
    user_id: Optional[int] = None
    ticket_id: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class SystemMetricBase(BaseModel):
    metric_name: str
    metric_value: float
    unit: Optional[str] = None
    source: str
    metadata: Optional[Dict[str, Any]] = None


class SystemMetric(SystemMetricBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class AnalyticsData(BaseModel):
    ticket_stats: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    team_stats: Dict[str, Any]
    sla_metrics: Dict[str, Any]
    trend_data: Dict[str, Any]


class SystemMetrics(BaseModel):
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    active_connections: int
    response_time: float


class DashboardMetrics(BaseModel):
    total_tickets: int
    open_tickets: int
    resolved_today: int
    sla_compliance: float
    avg_resolution_time: float
    team_utilization: float
    system_health: SystemMetrics
    recent_activities: List[Dict[str, Any]]


class TeamPerformance(BaseModel):
    engineer_stats: List[Dict[str, Any]]
    department_stats: List[Dict[str, Any]]
    resolution_trends: List[Dict[str, Any]]
    workload_distribution: Dict[str, Any]

class TeamMemberPerformance(BaseModel):
    name: str
    role: str
    ticketsResolved: int
    avgTime: str
    satisfaction: float
    slaCompliance: int

class TeamPerformanceResponse(BaseModel):
    team_members: List[TeamMemberPerformance]

class SLAReportBase(BaseModel):
    report_date: datetime
    time_period: str
    department_id: Optional[int] = None
    total_tickets: int
    met_sla: int
    breached_sla: int
    at_risk: int
    compliance_rate: float
    avg_resolution_time: Optional[float] = None
    priority_breakdown: Optional[Dict[str, Any]] = None
    category_breakdown: Optional[Dict[str, Any]] = None
    created_at: datetime

class SLAReportResponse(SLAReportBase):
    id: int

    class Config:
        from_attributes = True

class TicketAnalyticsItem(BaseModel):
    ticket_id: str
    status: str
    priority: str
    category: str
    resolution_time: Optional[float] = None
    created_at: datetime
    updated_at: datetime

class TicketAnalyticsResponse(BaseModel):
    tickets: List[TicketAnalyticsItem]
    summary: Dict[str, Any]

    class Config:
        from_attributes = True

class KnowledgeArticleAnalytics(BaseModel):
    article_id: int
    title: str
    view_count: int
    average_rating: Optional[float] = None
    rating_count: int

class KnowledgeCategoryAnalytics(BaseModel):
    category_id: int
    name: str
    article_count: int

class KnowledgeTagAnalytics(BaseModel):
    tag_id: int
    name: str
    usage_count: int

class KnowledgeAnalyticsResponse(BaseModel):
    total_articles: int
    published_articles: int
    draft_articles: int
    total_categories: int
    total_views: int
    average_rating: Optional[float] = None
    most_viewed_articles: List[KnowledgeArticleAnalytics]
    recent_articles: List[KnowledgeArticleAnalytics]
    popular_categories: List[KnowledgeCategoryAnalytics]
    popular_tags: List[KnowledgeTagAnalytics]

    class Config:
        from_attributes = True

class SystemComponentHealth(BaseModel):
    status: str
    details: Optional[Dict[str, str]] = None

class SystemHealthResponse(BaseModel):
    timestamp: datetime
    overall_status: str
    components: Dict[str, SystemComponentHealth]

    class Config:
        from_attributes = True

class WeeklyPerformance(BaseModel):
    week: str
    l1Performance: int
    l2Performance: int

class PerformanceTrendResponse(BaseModel):
    weekly_trends: List[WeeklyPerformance]

    class Config:
        from_attributes = True