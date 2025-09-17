from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.database import get_db
from app.api.dependencies import get_current_user, require_roles
from app.models.user import User
from app.models.knowledge import KnowledgeArticle, KnowledgeCategory, KnowledgeTag, ArticleTag
from app.schemas.knowledge import (
    KnowledgeArticleCreate,
    KnowledgeArticleUpdate,
    KnowledgeArticleResponse,
    KnowledgeCategoryCreate,
    KnowledgeCategoryResponse,
    KnowledgeSearchResponse,
    KnowledgeTagResponse
)
from app.services.ai_service import AIService
from app.services.file_service import FileService
from sqlalchemy.orm import joinedload

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

# @router.get("/articles", response_model=List[KnowledgeArticleResponse])
# async def get_articles(
#     skip: int = Query(0, ge=0),
#     limit: int = Query(100, ge=1, le=100),
#     category_id: Optional[int] = Query(None),
#     status: Optional[str] = Query(None),
#     search: Optional[str] = Query(None),
#     tags: Optional[List[str]] = Query(None),
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """Get knowledge articles with filtering and search"""
#     query = db.query(KnowledgeArticle)
    
#     # Apply filters
#     if category_id:
#         query = query.filter(KnowledgeArticle.category_id == category_id)
    
#     if status:
#         query = query.filter(KnowledgeArticle.status == status)
    
#     if search:
#         search_filter = or_(
#             KnowledgeArticle.title.ilike(f"%{search}%"),
#             KnowledgeArticle.content.ilike(f"%{search}%"),
#             KnowledgeArticle.summary.ilike(f"%{search}%")
#         )
#         query = query.filter(search_filter)
    
#     if tags:
#         # Filter by tags
#         query = query.join(ArticleTag).join(KnowledgeTag).filter(
#             KnowledgeTag.name.in_(tags)
#         )
    
#     # Apply role-based filtering
#     if current_user.role == "end_user":
#         query = query.filter(KnowledgeArticle.status == "published")
    
#     articles = query.offset(skip).limit(limit).all()
#     return articles

@router.get("/articles")  # Remove response_model
async def get_articles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    tags: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get knowledge articles with filtering and search"""
    query = db.query(KnowledgeArticle)
    
    # Your existing filters...
    if category_id:
        query = query.filter(KnowledgeArticle.category_id == category_id)
    
    if status:
        query = query.filter(KnowledgeArticle.status == status)
    
    if search:
        search_filter = or_(
            KnowledgeArticle.title.ilike(f"%{search}%"),
            KnowledgeArticle.content.ilike(f"%{search}%"),
            KnowledgeArticle.summary.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    if tags:
        query = query.join(ArticleTag).join(KnowledgeTag).filter(
            KnowledgeTag.name.in_(tags)
        )
    
    if current_user.role == "end_user":
        query = query.filter(KnowledgeArticle.status == "published")
    
    # Add eager loading and get results
    articles = query.options(
        joinedload(KnowledgeArticle.author),
        joinedload(KnowledgeArticle.category),
        joinedload(KnowledgeArticle.tags).joinedload(ArticleTag.tag)
    ).offset(skip).limit(limit).all()
    articles = []
    for article in articles:
        articles.append(article.title)
    print(articles)
    
    return [
    {
        "id": article.id,
        "title": article.title,
        "content": article.content,
        "summary": article.summary,
        "article_type": article.article_type.value,  # .value for enum
        "status": article.status.value,
        "difficulty_level": article.difficulty_level.value,
        "estimated_read_time": article.estimated_read_time,
        "author_id": article.author_id,
        "category_id": article.category_id,
        "view_count": article.view_count,
        "helpful_count": article.helpful_count,
        "not_helpful_count": article.not_helpful_count,
        "average_rating": article.average_rating,
        "rating_count": article.rating_count,
        "is_featured": article.is_featured,
        "attachments": article.attachments,
        "created_at": article.created_at.isoformat(),
        "updated_at": article.updated_at.isoformat() if article.updated_at else None,
        "published_at": article.published_at.isoformat() if article.published_at else None,
        "author": {
            "id": article.author.id,
            "username": article.author.username,
            "email": article.author.email,
        },
        "category": {
            "id": article.category.id,
            "name": article.category.name,
            "description": article.category.description,
            "color": article.category.color,
            "parent_id": article.category.parent_id,
            "created_at": article.category.created_at.isoformat(),
        },
        "tags": [
            {
                "id": tag.id,
                "tag": {
                    "id": tag.tag.id,
                    "name": tag.tag.name,
                    "description": tag.tag.description,
                    "color": tag.tag.color,
                }
            }
            for tag in article.tags
        ]
    }
    for article in articles
]

@router.get("/articles/{article_id}", response_model=KnowledgeArticleResponse)
async def get_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific knowledge article"""
    article = db.query(KnowledgeArticle).filter(
        KnowledgeArticle.id == article_id
    ).first()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Check permissions
    if current_user.role == "end_user" and article.status != "published":
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Increment view count
    article.view_count += 1
    db.commit()
    
    return article

@router.post("/articles", response_model=KnowledgeArticleResponse)
async def create_article(
    article: KnowledgeArticleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["l2_engineer", "ops_manager", "transition_manager"]))
):
    """Create a new knowledge article"""
    
    # Check if category exists
    category = db.query(KnowledgeCategory).filter(
        KnowledgeCategory.id == article.category_id
    ).first()
    if not category:
        raise HTTPException(status_code=400, detail="Invalid category")
    
    # Create article
    db_article = KnowledgeArticle(
        title=article.title,
        content=article.content,
        summary=article.summary,
        article_type=article.article_type,
        category_id=article.category_id,
        author_id=current_user.id,
        status=article.status or "draft",
        difficulty_level=article.difficulty_level,
        estimated_read_time=article.estimated_read_time
    )
    
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    
    # Add tags if provided
    if article.tags:
        for tag_name in article.tags:
            # Get or create tag
            tag = db.query(KnowledgeTag).filter(
                KnowledgeTag.name == tag_name
            ).first()
            if not tag:
                tag = KnowledgeTag(name=tag_name)
                db.add(tag)
                db.commit()
                db.refresh(tag)
            
            # Create article-tag relationship
            article_tag = ArticleTag(
                article_id=db_article.id,
                tag_id=tag.id
            )
            db.add(article_tag)
    
    db.commit()
    return db_article

@router.put("/articles/{article_id}", response_model=KnowledgeArticleResponse)
async def update_article(
    article_id: int,
    article_update: KnowledgeArticleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["l2_engineer", "ops_manager", "transition_manager"]))
):
    """Update a knowledge article"""
    
    db_article = db.query(KnowledgeArticle).filter(
        KnowledgeArticle.id == article_id
    ).first()
    
    if not db_article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Check permissions (author or manager can edit)
    if (current_user.id != db_article.author_id and 
        current_user.role not in ["ops_manager", "transition_manager"]):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update fields
    update_data = article_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field != "tags":
            setattr(db_article, field, value)
    
    # Update tags if provided
    if "tags" in update_data:
        # Remove existing tags
        db.query(ArticleTag).filter(
            ArticleTag.article_id == article_id
        ).delete()
        
        # Add new tags
        for tag_name in update_data["tags"]:
            tag = db.query(KnowledgeTag).filter(
                KnowledgeTag.name == tag_name
            ).first()
            if not tag:
                tag = KnowledgeTag(name=tag_name)
                db.add(tag)
                db.commit()
                db.refresh(tag)
            
            article_tag = ArticleTag(
                article_id=article_id,
                tag_id=tag.id
            )
            db.add(article_tag)
    
    db.commit()
    db.refresh(db_article)
    return db_article

@router.delete("/articles/{article_id}")
async def delete_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ops_manager", "transition_manager"]))
):
    """Delete a knowledge article"""
    
    article = db.query(KnowledgeArticle).filter(
        KnowledgeArticle.id == article_id
    ).first()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Remove tags first
    db.query(ArticleTag).filter(ArticleTag.article_id == article_id).delete()
    
    # Delete article
    db.delete(article)
    db.commit()
    
    return {"message": "Article deleted successfully"}

@router.get("/search", response_model=KnowledgeSearchResponse)
async def search_knowledge(
    q: str = Query(..., min_length=1),
    category_id: Optional[int] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    ai_service: AIService = Depends()
):
    """Advanced knowledge search with AI enhancement"""
    
    # Basic text search
    query = db.query(KnowledgeArticle)
    
    if current_user.role == "end_user":
        query = query.filter(KnowledgeArticle.status == "published")
    
    if category_id:
        query = query.filter(KnowledgeArticle.category_id == category_id)
    
    # Text search
    search_filter = or_(
        KnowledgeArticle.title.ilike(f"%{q}%"),
        KnowledgeArticle.content.ilike(f"%{q}%"),
        KnowledgeArticle.summary.ilike(f"%{q}%")
    )
    
    articles = query.filter(search_filter).limit(limit).all()
    
    # AI-enhanced search suggestions
    try:
        ai_suggestions = await ai_service.get_knowledge_suggestions(q, [
            {"title": a.title, "summary": a.summary} for a in articles
        ])
    except Exception:
        ai_suggestions = []
    
    return KnowledgeSearchResponse(
        query=q,
        articles=articles,
        total_results=len(articles),
        ai_suggestions=ai_suggestions
    )

@router.get("/categories", response_model=List[KnowledgeCategoryResponse])
async def get_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all knowledge categories"""
    categories = db.query(KnowledgeCategory).all()
    return categories

@router.post("/categories", response_model=KnowledgeCategoryResponse)
async def create_category(
    category: KnowledgeCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ops_manager", "transition_manager"]))
):
    """Create a new knowledge category"""
    
    # Check if category already exists
    existing = db.query(KnowledgeCategory).filter(
        KnowledgeCategory.name == category.name
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")
    
    db_category = KnowledgeCategory(
        name=category.name,
        description=category.description,
        color=category.color
    )
    
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    
    return db_category

@router.get("/tags", response_model=List[KnowledgeTagResponse])
async def get_tags(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all knowledge tags"""
    tags = db.query(KnowledgeTag).all()
    return tags

@router.post("/articles/{article_id}/rate")
async def rate_article(
    article_id: int,
    rating: int = Query(..., ge=1, le=5),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Rate a knowledge article"""
    
    article = db.query(KnowledgeArticle).filter(
        KnowledgeArticle.id == article_id
    ).first()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Update rating (simplified - in production, you'd track individual ratings)
    if article.rating_count == 0:
        article.average_rating = rating
        article.rating_count = 1
    else:
        total_rating = article.average_rating * article.rating_count
        article.rating_count += 1
        article.average_rating = (total_rating + rating) / article.rating_count
    
    db.commit()
    
    return {"message": "Rating submitted successfully"}

@router.post("/articles/{article_id}/attachments")
async def upload_attachment(
    article_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["l2_engineer", "ops_manager", "transition_manager"])),
    file_service: FileService = Depends()
):
    """Upload attachment to knowledge article"""
    
    article = db.query(KnowledgeArticle).filter(
        KnowledgeArticle.id == article_id
    ).first()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Check permissions
    if (current_user.id != article.author_id and 
        current_user.role not in ["ops_manager", "transition_manager"]):
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        file_url = await file_service.upload_file(
            file, 
            folder="knowledge_attachments"
        )
        
        # Update article attachments (assuming JSON field)
        if not article.attachments:
            article.attachments = []
        
        article.attachments.append({
            "filename": file.filename,
            "url": file_url,
            "uploaded_by": current_user.id,
            "uploaded_at": "now"  # Use proper datetime in production
        })
        
        db.commit()
        
        return {"message": "File uploaded successfully", "url": file_url}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/analytics/popular")
async def get_popular_articles(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ops_manager", "transition_manager"]))
):
    """Get most popular knowledge articles"""
    
    articles = db.query(KnowledgeArticle).filter(
        KnowledgeArticle.status == "published"
    ).order_by(
        KnowledgeArticle.view_count.desc()
    ).limit(limit).all()
    
    return {
        "popular_articles": [
            {
                "id": a.id,
                "title": a.title,
                "view_count": a.view_count,
                "average_rating": a.average_rating,
                "category": a.category.name if a.category else None
            }
            for a in articles
        ]
    }

@router.get("/analytics/gaps")
async def identify_knowledge_gaps(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["ops_manager", "transition_manager"])),
    ai_service: AIService = Depends()
):
    """Identify knowledge gaps based on ticket patterns"""
    
    try:
        # This would analyze tickets without resolutions or with long resolution times
        # and suggest knowledge articles that should be created
        gaps = await ai_service.identify_knowledge_gaps(db)
        
        return {
            "knowledge_gaps": gaps,
            "recommendations": [
                "Create article on common login issues",
                "Document network troubleshooting procedures",
                "Add hardware replacement guides"
            ]
        }
        
    except Exception as e:
        return {
            "knowledge_gaps": [],
            "recommendations": [],
            "error": "Analysis temporarily unavailable"
        }
