"""
Knowledge base Pydantic schemas
"""
from pydantic import BaseModel, Field,ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Import enums from models
class ArticleType(str, Enum):
    PROCEDURE = "procedure"
    TROUBLESHOOTING = "troubleshooting"
    FAQ = "faq"
    GUIDE = "guide"
    REFERENCE = "reference"

class ArticleStatus(str, Enum):
    DRAFT = "draft"
    REVIEW = "review"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

# Base schemas
class KnowledgeCategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")

class KnowledgeCategoryCreate(KnowledgeCategoryBase):
    pass

class KnowledgeCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")

class KnowledgeCategoryResponse(KnowledgeCategoryBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True
    }


# Tag schemas
class KnowledgeTagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")

class KnowledgeTagCreate(KnowledgeTagBase):
    pass

class KnowledgeTagResponse(KnowledgeTagBase):
    id: int
    created_at: datetime

    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True
    }


# Article schemas
class KnowledgeArticleBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    content: str = Field(..., min_length=50)
    summary: Optional[str] = Field(None, max_length=500)
    article_type: ArticleType 
    category_id: int
    difficulty_level: Optional[DifficultyLevel] = DifficultyLevel.BEGINNER
    estimated_read_time: Optional[int] = Field(None, ge=1, le=120)  # minutes

class KnowledgeArticleCreate(KnowledgeArticleBase):
    status: Optional[ArticleStatus] = ArticleStatus.DRAFT
    tags: Optional[List[str]] = []

class KnowledgeArticleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    content: Optional[str] = Field(None, min_length=50)
    summary: Optional[str] = Field(None, max_length=500)
    category_id: Optional[int] = None
    status: Optional[ArticleStatus] = None
    difficulty_level: Optional[DifficultyLevel] = None
    estimated_read_time: Optional[int] = Field(None, ge=1, le=120)
    tags: Optional[List[str]] = None

class KnowledgeArticleResponse(KnowledgeArticleBase):
    id: int
    status: ArticleStatus
    author_id: int
    view_count: int = 0
    average_rating: Optional[float] = None
    rating_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    article_type: ArticleType
    
    
    # Related data
    author: Optional[Dict[str, Any]] = None
    category: Optional[KnowledgeCategoryResponse] = None
    tags: Optional[List[KnowledgeTagResponse]] = []
    attachments: Optional[List[Dict[str, Any]]] = []
    
    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True
    }


# Search schemas
class KnowledgeSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    category_id: Optional[int] = None
    tags: Optional[List[str]] = []
    difficulty_level: Optional[DifficultyLevel] = None
    status: Optional[ArticleStatus] = None

class KnowledgeSearchResponse(BaseModel):
    query: str
    articles: List[KnowledgeArticleResponse]
    total_results: int
    ai_suggestions: Optional[List[str]] = []
    related_tags: Optional[List[str]] = []

# Rating schemas
class KnowledgeArticleRatingCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=500)

class KnowledgeArticleRatingResponse(BaseModel):
    id: int
    article_id: int
    user_id: int
    rating: int
    comment: Optional[str] = None
    created_at: datetime
    
    
    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True
    }


# Version schemas
class KnowledgeArticleVersionResponse(BaseModel):
    id: int
    article_id: int
    version_number: int
    title: str
    content: str
    summary: Optional[str] = None
    created_by: int
    created_at: datetime
    change_summary: Optional[str] = None

    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True
    }


# Analytics schemas
class KnowledgeAnalytics(BaseModel):
    total_articles: int
    published_articles: int
    draft_articles: int
    total_categories: int
    total_views: int
    average_rating: Optional[float] = None
    most_viewed_articles: List[Dict[str, Any]] = []
    recent_articles: List[KnowledgeArticleResponse] = []
    popular_tags: List[Dict[str, Any]] = []

# Bulk operations
class BulkArticleUpdate(BaseModel):
    article_ids: List[int]
    updates: KnowledgeArticleUpdate

class BulkOperationResponse(BaseModel):
    success_count: int
    failed_count: int
    errors: List[str] = []

# Export schemas
class ExportRequest(BaseModel):
    format: str = Field(..., pattern="^(pdf|docx|html)$")
    article_ids: Optional[List[int]] = None
    category_id: Optional[int] = None
    include_attachments: bool = False

class ExportResponse(BaseModel):
    download_url: str
    expires_at: datetime
    file_size: Optional[int] = None
