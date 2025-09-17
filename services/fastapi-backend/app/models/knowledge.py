"""
Knowledge base models
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Boolean, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class ArticleType(str, enum.Enum):
    PROCEDURE = "procedure"
    TROUBLESHOOTING = "troubleshooting"
    FAQ = "faq"
    RUNBOOK = "runbook"
    POLICY = "policy"
    TRAINING = "training"


class ArticleStatus(str, enum.Enum):
    DRAFT = "draft"
    REVIEW = "review"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class DifficultyLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class KnowledgeCategory(Base):
    __tablename__ = "knowledge_categories"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String, nullable=True)  # Hex color code for UI
    parent_id = Column(Integer, ForeignKey("knowledge_categories.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    parent = relationship("KnowledgeCategory", remote_side=[id])
    articles = relationship("KnowledgeArticle", back_populates="category")


class KnowledgeTag(Base):
    __tablename__ = "knowledge_tags"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String, nullable=True)  # Hex color code for UI
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    articles = relationship("ArticleTag", back_populates="tag")


class KnowledgeArticle(Base):
    __tablename__ = "knowledge_articles"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    article_type = Column(Enum(ArticleType), nullable=False)
    status = Column(Enum(ArticleStatus), default=ArticleStatus.DRAFT)
    difficulty_level = Column(Enum(DifficultyLevel), default=DifficultyLevel.BEGINNER)
    estimated_read_time = Column(Integer, nullable=True)  # in minutes
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("knowledge_categories.id"), nullable=False)
    view_count = Column(Integer, default=0)
    helpful_count = Column(Integer, default=0)
    not_helpful_count = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)
    is_featured = Column(Boolean, default=False)
    attachments = Column(Text, nullable=True)  # JSON string of attachment info
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    author = relationship("User", back_populates="knowledge_articles")
    category = relationship("KnowledgeCategory", back_populates="articles")
    tags = relationship("ArticleTag", back_populates="article")


class ArticleTag(Base):
    __tablename__ = "article_tags"

    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey("knowledge_articles.id"), nullable=False)
    tag_id = Column(Integer, ForeignKey("knowledge_tags.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    article = relationship("KnowledgeArticle", back_populates="tags")
    tag = relationship("KnowledgeTag", back_populates="articles")

    # Ensure unique article-tag combinations
    __table_args__ = (
        {"extend_existing": True}
    )


class KnowledgeArticleVersion(Base):
    __tablename__ = "knowledge_article_versions"

    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey("knowledge_articles.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    change_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    article = relationship("KnowledgeArticle")
    editor = relationship("User")


class KnowledgeArticleRating(Base):
    __tablename__ = "knowledge_article_ratings"

    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey("knowledge_articles.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    article = relationship("KnowledgeArticle")
    user = relationship("User")

    # Ensure one rating per user per article
    __table_args__ = (
        {"extend_existing": True}
    )
