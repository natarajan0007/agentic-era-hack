"""
Transition management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.api.dependencies import get_db, get_current_user, require_manager
from app.models.user import User as UserModel
from app.models.knowledge import KnowledgeArticle as KnowledgeArticleModel, ArticleStatus
from app.models.ticket import Ticket as TicketModel

router = APIRouter(prefix="/transition", tags=["transition"])


@router.get("/projects")
async def get_transition_projects(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_manager)
):
    """
    Get all transition projects
    """
    # Mock data - in production, this would come from a dedicated transition projects table
    projects = [
        {
            "id": 1,
            "name": "System Alpha Migration",
            "description": "Migration of legacy system to new platform",
            "status": "in_progress",
            "progress": 85,
            "start_date": "2024-11-01",
            "target_date": "2024-12-20",
            "team_lead": "Alex Transition",
            "stakeholders": ["John Doe", "Jane Smith", "Mike Johnson"],
            "phases": [
                {"name": "Planning", "progress": 100, "status": "completed"},
                {"name": "Documentation", "progress": 85, "status": "in_progress"},
                {"name": "Knowledge Transfer", "progress": 80, "status": "in_progress"},
                {"name": "Team Training", "progress": 60, "status": "in_progress"},
                {"name": "Go-Live", "progress": 0, "status": "pending"},
                {"name": "Post-Transition", "progress": 0, "status": "pending"}
            ]
        },
        {
            "id": 2,
            "name": "Network Infrastructure Handover",
            "description": "Transition of network management to new team",
            "status": "planning",
            "progress": 25,
            "start_date": "2024-12-01",
            "target_date": "2025-01-15",
            "team_lead": "Alex Transition",
            "stakeholders": ["Network Team", "Security Team"],
            "phases": [
                {"name": "Planning", "progress": 75, "status": "in_progress"},
                {"name": "Documentation", "progress": 0, "status": "pending"},
                {"name": "Knowledge Transfer", "progress": 0, "status": "pending"},
                {"name": "Team Training", "progress": 0, "status": "pending"},
                {"name": "Go-Live", "progress": 0, "status": "pending"},
                {"name": "Post-Transition", "progress": 0, "status": "pending"}
            ]
        }
    ]
    
    return {"projects": projects}


@router.get("/projects/{project_id}")
async def get_transition_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_manager)
):
    """
    Get detailed information about a specific transition project
    """
    # Mock detailed project data
    if project_id == 1:
        return {
            "id": 1,
            "name": "System Alpha Migration",
            "description": "Migration of legacy system to new platform",
            "status": "in_progress",
            "progress": 85,
            "start_date": "2024-11-01",
            "target_date": "2024-12-20",
            "team_lead": "Alex Transition",
            "stakeholders": ["John Doe", "Jane Smith", "Mike Johnson"],
            "deliverables": [
                {
                    "name": "System Architecture Document",
                    "status": "completed",
                    "progress": 100,
                    "due_date": "2024-11-15",
                    "assignee": "Mike Senior"
                },
                {
                    "name": "Operational Procedures",
                    "status": "in_progress",
                    "progress": 83,
                    "due_date": "2024-12-10",
                    "assignee": "Sarah Tech",
                    "details": "15 of 18 procedures completed"
                },
                {
                    "name": "Training Materials",
                    "status": "in_progress",
                    "progress": 67,
                    "due_date": "2024-12-15",
                    "assignee": "Tom Support",
                    "details": "8 of 12 modules completed"
                },
                {
                    "name": "Knowledge Base Articles",
                    "status": "in_progress",
                    "progress": 83,
                    "due_date": "2024-12-18",
                    "assignee": "Jane Helper",
                    "details": "25 of 30 articles completed"
                }
            ],
            "team_readiness": [
                {
                    "member": "Sarah Tech",
                    "role": "L1 Engineer",
                    "readiness": 80,
                    "needs": ["Advanced Training"],
                    "certifications": ["Basic System Admin"],
                    "missing_skills": ["Database Management"]
                },
                {
                    "member": "Tom Support",
                    "role": "L1 Engineer", 
                    "readiness": 60,
                    "needs": ["System Knowledge", "Hands-on Training"],
                    "certifications": [],
                    "missing_skills": ["System Architecture", "Troubleshooting"]
                },
                {
                    "member": "Mike Senior",
                    "role": "L2 Engineer",
                    "readiness": 100,
                    "needs": [],
                    "certifications": ["Advanced System Admin", "Database Admin"],
                    "missing_skills": []
                }
            ],
            "risks": [
                {
                    "level": "medium",
                    "description": "Training schedule behind by 1 week",
                    "impact": "May delay go-live date",
                    "mitigation": "Accelerate training schedule, add weekend sessions"
                },
                {
                    "level": "high",
                    "description": "Key team member availability uncertain",
                    "impact": "Critical knowledge transfer at risk",
                    "mitigation": "Identify backup resources, document all procedures"
                }
            ],
            "milestones": [
                {
                    "name": "Documentation Complete",
                    "date": "2024-12-10",
                    "status": "at_risk"
                },
                {
                    "name": "Training Complete",
                    "date": "2024-12-15",
                    "status": "on_track"
                },
                {
                    "name": "Go-Live Ready",
                    "date": "2024-12-20",
                    "status": "pending"
                }
            ]
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )


@router.get("/knowledge-artifacts")
async def get_knowledge_artifacts(
    project_id: Optional[int] = None,
    status: Optional[str] = None,
    artifact_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_manager)
):
    """
    Get knowledge artifacts for transition management
    """
    # Get knowledge articles that are part of transition
    query = KnowledgeArticleModel.__table__.select()
    
    # Filter by status if provided
    if status:
        if status == "complete":
            query = query.where(KnowledgeArticleModel.status == ArticleStatus.PUBLISHED)
        elif status == "in_progress":
            query = query.where(KnowledgeArticleModel.status.in_([ArticleStatus.DRAFT, ArticleStatus.REVIEW]))
        elif status == "missing":
            # This would require a separate tracking system for required vs existing articles
            pass
    
    # Filter by type if provided
    if artifact_type:
        query = query.where(KnowledgeArticleModel.article_type == artifact_type)
    
    articles_query = await db.execute(query)
    articles = articles_query.fetchall()
    
    # Transform to artifact format
    artifacts = []
    for article in articles:
        artifacts.append({
            "id": f"DOC-{article.id:03d}",
            "title": article.title,
            "type": article.article_type.value,
            "status": "complete" if article.status == ArticleStatus.PUBLISHED else "in_progress",
            "author": article.author.name if article.author else "Unknown",
            "created_at": article.created_at.isoformat(),
            "updated_at": article.updated_at.isoformat() if article.updated_at else None,
            "progress": 100 if article.status == ArticleStatus.PUBLISHED else 50
        })
    
    # Add some mock missing artifacts
    missing_artifacts = [
        {
            "id": "DOC-999",
            "title": "User Account Management Procedure",
            "type": "procedure",
            "status": "missing",
            "author": None,
            "created_at": None,
            "updated_at": None,
            "progress": 0
        }
    ]
    
    if not status or status == "missing":
        artifacts.extend(missing_artifacts)
    
    # Calculate summary statistics
    total_artifacts = len(artifacts)
    complete_artifacts = len([a for a in artifacts if a["status"] == "complete"])
    in_progress_artifacts = len([a for a in artifacts if a["status"] == "in_progress"])
    missing_artifacts_count = len([a for a in artifacts if a["status"] == "missing"])
    
    completion_percentage = (complete_artifacts / total_artifacts * 100) if total_artifacts > 0 else 0
    
    return {
        "artifacts": artifacts,
        "summary": {
            "total": total_artifacts,
            "complete": complete_artifacts,
            "in_progress": in_progress_artifacts,
            "missing": missing_artifacts_count,
            "completion_percentage": round(completion_percentage, 1)
        }
    }


@router.get("/team-readiness")
async def get_team_readiness(
    project_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_manager)
):
    """
    Get team readiness assessment for transition
    """
    # Get all engineers
    engineers_query = await db.execute(UserModel.__table__.select().where(
        UserModel.role.in_(["l1-engineer", "l2-engineer"])
    ))
    engineers = engineers_query.fetchall()
    
    readiness_data = []
    for engineer in engineers:
        # Mock readiness calculation
        base_readiness = 70 if engineer.role.value == "l2-engineer" else 50
        
        # Adjust based on experience (mock calculation)
        experience_bonus = min(20, len(engineer.name) * 2)  # Mock based on name length
        
        total_readiness = min(100, base_readiness + experience_bonus)
        
        # Determine needs based on readiness level
        needs = []
        if total_readiness < 70:
            needs.append("Full Training Program")
        elif total_readiness < 85:
            needs.append("Advanced Training")
        elif total_readiness < 95:
            needs.append("Certification")
        
        readiness_data.append({
            "id": engineer.id,
            "name": engineer.name,
            "role": engineer.role.value,
            "department": engineer.department.name if engineer.department else "Unknown",
            "readiness_score": total_readiness,
            "status": "ready" if total_readiness >= 90 else "needs_training" if total_readiness >= 70 else "not_ready",
            "needs": needs,
            "skills": {
                "technical": total_readiness,
                "process": max(0, total_readiness - 10),
                "tools": max(0, total_readiness - 5)
            },
            "training_progress": {
                "completed_modules": 8 if total_readiness > 80 else 4,
                "total_modules": 12,
                "completion_percentage": round((8 if total_readiness > 80 else 4) / 12 * 100, 1)
            }
        })
    
    # Calculate overall team readiness
    avg_readiness = sum([r["readiness_score"] for r in readiness_data]) / len(readiness_data)
    ready_count = len([r for r in readiness_data if r["status"] == "ready"])
    
    return {
        "team_members": readiness_data,
        "summary": {
            "average_readiness": round(avg_readiness, 1),
            "ready_members": ready_count,
            "total_members": len(readiness_data),
            "readiness_percentage": round(ready_count / len(readiness_data) * 100, 1)
        }
    }


@router.post("/projects/{project_id}/update-progress")
async def update_project_progress(
    project_id: int,
    phase: str,
    progress: int,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_manager)
):
    """
    Update progress for a transition project phase
    """
    # In production, this would update a real database
    # For now, return success message
    
    if progress < 0 or progress > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Progress must be between 0 and 100"
        )
    
    # Log the update (in production, save to database)
    update_log = {
        "project_id": project_id,
        "phase": phase,
        "progress": progress,
        "notes": notes,
        "updated_by": current_user.name,
        "updated_at": datetime.utcnow().isoformat()
    }
    
    return {
        "message": "Progress updated successfully",
        "update": update_log
    }


@router.get("/reports/transition-status")
async def get_transition_status_report(
    project_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_manager)
):
    """
    Generate transition status report
    """
    # Mock report data
    report = {
        "generated_at": datetime.utcnow().isoformat(),
        "generated_by": current_user.name,
        "summary": {
            "total_projects": 2,
            "active_projects": 1,
            "completed_projects": 0,
            "overall_progress": 55
        },
        "projects": [
            {
                "name": "System Alpha Migration",
                "progress": 85,
                "status": "on_track",
                "risks": ["medium", "high"],
                "next_milestone": "Go-Live Ready - Dec 20"
            },
            {
                "name": "Network Infrastructure Handover", 
                "progress": 25,
                "status": "planning",
                "risks": [],
                "next_milestone": "Planning Complete - Dec 15"
            }
        ],
        "knowledge_transfer": {
            "articles_completed": 25,
            "articles_total": 30,
            "completion_rate": 83.3
        },
        "team_readiness": {
            "ready_members": 1,
            "total_members": 3,
            "average_readiness": 80
        },
        "recommendations": [
            "Accelerate training for Tom Support",
            "Complete remaining knowledge articles by Dec 15",
            "Address key team member availability risk"
        ]
    }
    
    return report