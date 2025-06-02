from sqlalchemy import (JSON, CheckConstraint, Integer, String, Numeric, DateTime, ForeignKey,
                        BigInteger, Boolean, func, Index)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional
from datetime import datetime
# 
# TODO: импортировать pydantic схемы 
# 

class Base(DeclarativeBase):
    pass

class Enterprises(Base):
    __tablename__ = 'enterprises'

    __table_args__ = (
        Index('idx_Enterprises_name', 'name')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    industry: Mapped[str] = mapped_column(String(100), nullable=False)
    inn: Mapped[str] = mapped_column(String(12), unique=True)
    short_name: Mapped[str] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    create_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
    respondent: Mapped["Respondents"] = relationship(back_populates="enterprise_id")

    # метод для pydantic

class Respondents(Base):
    __tablename__ = 'respondents'
    
    __table_args__ = (
        Index('idx_Respondents_enterprise', 'enterprise_id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    enterprise_id: Mapped[int] = mapped_column(ForeignKey('Enterprises.id'))
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    position: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String)
    consent: Mapped[bool] = mapped_column(Boolean, default=False)
    create_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    survey: Mapped["Surveys"] = relationship(back_populates="respondent_id")

    # метод для pydantic

class Surveys(Base):
    __tablename__ = 'surveys'

    __table_args__ = (
        Index('idx_Surveys_respondent', 'enterprise_id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    respondent_id: Mapped[int] = mapped_column(ForeignKey('Respondents.id'))
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=None)
    ip_address: Mapped[str] = mapped_column(String(45))
    user_agent: Mapped[str] = mapped_column(String)
    
    answers: Mapped[list["SurveyAnswers"]] = relationship(back_populates="survey_id")

    # метод для pydantic

class Question(Base):
    __tablename__ = 'questions'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    number: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)  # номер вопроса  
    text: Mapped[str] = mapped_column(String, nullable=False)  # текст вопроса
    answer_type: Mapped[str] = mapped_column(String)  # тип ответа 
    
    answers: Mapped[list["SurveyAnswers"]] = relationship(back_populates="question")

class SurveyAnswers(Base):
    __tablename__ = 'survey_answers'
    
    __table_args__ = (
        CheckConstraint(
            "jsonb_typeof(answer) = 'object'", 
            name="ck_answer_is_json"
        ),
        Index('idx_answer_survey', 'survey_id'),
        Index('idx_answer_question', 'question_id')
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    survey_id: Mapped[int] = mapped_column(ForeignKey('surveys.id'))
    question_id: Mapped[int] = mapped_column(ForeignKey('questions.id'))
    answer: Mapped[dict] = mapped_column(JSON(none_as_null=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    question: Mapped["Question"] = relationship(back_populates="answers")
    survey: Mapped["Surveys"] = relationship(back_populates="answers")

    # метод для pydantic
    
class Industries(Base):
    __tablename__ = 'industries'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String)

    # метод для pydantic

class SoftwareCategories(Base):
    __tablename__ = 'software_categories'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String)

    # метод для pydantic