"""
Analytics and metrics models
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Float, JSON, Boolean, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id = Column(Integer, primary_key=True)
    event_type = Column(String, nullable=False)  # ticket_created, ticket_resolved, etc.
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    ticket_id = Column(String, ForeignKey("tickets.id"), nullable=True)
    properties = Column(JSON, nullable=True)  # Event-specific data
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class SystemMetric(Base):
    __tablename__ = "system_metrics"

    id = Column(Integer, primary_key=True)
    metric_name = Column(String, nullable=False)  # cpu_usage, memory_usage, etc.
    metric_value = Column(Float, nullable=False)
    unit = Column(String, nullable=True)  # percentage, bytes, etc.
    source = Column(String, nullable=False)  # server name or service
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    system_metadata = Column(JSON, nullable=True)  # Additional metric data


class PerformanceMetric(Base):
    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    metric_type = Column(String, nullable=False)  # resolution_time, sla_compliance, etc.
    metric_value = Column(Float, nullable=False)
    time_period = Column(String, nullable=False)  # daily, weekly, monthly
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    ticket_count = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    system_metadata = Column(JSON, nullable=True)  # Additional context

    # Relationships
    user = relationship("User")


class SLAReport(Base):
    __tablename__ = "sla_reports"

    id = Column(Integer, primary_key=True)
    report_date = Column(DateTime(timezone=True), nullable=False)
    time_period = Column(String, nullable=False)  # daily, weekly, monthly
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    total_tickets = Column(Integer, nullable=False, default=0)
    met_sla = Column(Integer, nullable=False, default=0)
    breached_sla = Column(Integer, nullable=False, default=0)
    at_risk = Column(Integer, nullable=False, default=0)
    compliance_rate = Column(Float, nullable=False, default=0.0)
    avg_resolution_time = Column(Float, nullable=True)  # in hours
    priority_breakdown = Column(JSON, nullable=True)  # Breakdown by priority
    category_breakdown = Column(JSON, nullable=True)  # Breakdown by category
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    department = relationship("Department")


class UserActivityLog(Base):
    __tablename__ = "user_activity_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    activity_type = Column(String, nullable=False)  # login, ticket_update, etc.
    resource_type = Column(String, nullable=True)  # ticket, knowledge_article, etc.
    resource_id = Column(String, nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User")


class DashboardWidget(Base):
    __tablename__ = "dashboard_widgets"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    widget_type = Column(String, nullable=False)  # chart, metric, list, etc.
    title = Column(String, nullable=False)
    position_x = Column(Integer, nullable=False)
    position_y = Column(Integer, nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    config = Column(JSON, nullable=True)  # Widget-specific configuration
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    report_type = Column(String, nullable=False)  # performance, sla, tickets, etc.
    parameters = Column(JSON, nullable=True)  # Report configuration
    schedule = Column(String, nullable=True)  # cron expression for scheduled reports
    recipients = Column(JSON, nullable=True)  # List of email recipients
    last_generated = Column(DateTime(timezone=True), nullable=True)
    file_path = Column(String, nullable=True)  # Path to the generated report file
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    creator = relationship("User")
