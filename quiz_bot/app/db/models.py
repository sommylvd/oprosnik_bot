from sqlalchemy import (CheckConstraint, Integer, String, DateTime, ForeignKey,
                        Boolean, func, Index)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional
from datetime import datetime
from app.db.schemas import (enterprise, question, respondent, 
                     software_category, survey_answer, survey)

class Base(DeclarativeBase):
    pass

class Enterprises(Base):
    """
    Предприятия (компании), участвующие в опросах.

    Attributes:
        id: Уникальный идентификатор предприятия.
        name: Полное название предприятия.
        industry: Отрасль деятельности предприятия.
        inn: ИНН предприятия (уникальный).
        short_name: Сокращенное название.
        is_active: Флаг активности предприятия.
        create_at: Дата создания записи.
    """
    __tablename__ = 'enterprises'

    __table_args__ = (
        Index('idx_enterprises_name', 'name'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    inn: Mapped[str] = mapped_column(String(12), unique=True)
    short_name: Mapped[str] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    create_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
    respondent: Mapped["Respondents"] = relationship(back_populates="enterprise")

    def to_pydantic(self):
        return enterprise.EnterpriseOut(
            id=self.id,
            name=self.name,
            industry_id=self.industry_id,
            inn=self.inn,
            short_name=self.short_name,
            is_active=self.is_active,
            create_at=self.create_at
        )

class Respondents(Base):
    """
    Респонденты (участники опросов).

    Attributes:
        id: Уникальный идентификатор респондента.
        enterprise_id: Ссылка на предприятие респондента.
        full_name: Полное имя респондента.
        position: Должность респондента.
        phone: Контактный телефон.
        email: Электронная почта.
        consent: Флаг согласия на обработку данных.
        create_at: Дата создания записи.
    """
    __tablename__ = 'respondents'
    
    __table_args__ = (
        Index('idx_respondents_enterprise', 'enterprise_id'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    enterprise_id: Mapped[int] = mapped_column(ForeignKey('enterprises.id'))
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    position: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String)
    consent: Mapped[bool] = mapped_column(Boolean, default=False)
    create_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    enterprise: Mapped[list["Enterprises"]] = relationship(back_populates="respondent")
    survey: Mapped["Surveys"] = relationship(back_populates="respondent")

    def to_pydantic(self):
        return respondent.RespondentOut(
            id=self.id,
            enterprise_id=self.enterprise_id,
            full_name=self.full_name,
            position=self.position,
            phone=self.phone,
            email=self.email,
            consent=self.consent,
            create_at=self.create_at
        )

class Surveys(Base):
    """
    Сессии прохождения опросов.

    Attributes:
        id: Уникальный идентификатор сессии опроса.
        respondent_id: Ссылка на респондента.
        started_at: Время начала опроса.
        completed_at: Время завершения опроса (если завершен).
        ip_address: IP-адрес устройства респондента.
        user_agent: Информация о браузере/устройстве респондента.
    """
    __tablename__ = 'surveys'

    __table_args__ = (
        Index('idx_surveys_respondent', 'respondent_id'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    respondent_id: Mapped[int] = mapped_column(ForeignKey('respondents.id'))
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=None)
    ip_address: Mapped[str] = mapped_column(String(45))
    user_agent: Mapped[str] = mapped_column(String)
    
    respondent: Mapped['Respondents'] = relationship(back_populates='survey')
    answers: Mapped[list["SurveyAnswers"]] = relationship(back_populates="survey")

    def to_pydantic(self):
        return survey.SurveyOut(
            id=self.id,
            respondent_id=self.respondent_id,
            started_at=self.started_at,
            completed_at=self.completed_at if self.completed_at else None,
            ip_address=self.ip_address,
            user_agent=self.user_agent
        )

class Questions(Base):
    """
    Вопросы опросника.

    Attributes:
        id: Уникальный идентификатор вопроса.
        number: Номер вопроса в опросе (уникальный).
        text: Текст вопроса.
        answer_type: Тип ожидаемого ответа.
    """
    __tablename__ = 'questions'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    number: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)  # номер вопроса  
    text: Mapped[str] = mapped_column(String, nullable=False)  # текст вопроса
    answer_type: Mapped[str] = mapped_column(String)  # тип ответа 
    
    answers: Mapped[list["SurveyAnswers"]] = relationship(back_populates="question")

    def to_pydantic(self):
        return question.QuestionOut(
            id=self.id,
            number=self.number,
            text=self.text,
            answer_type=self.answer_type
        )

class SurveyAnswers(Base):
    """
    Ответы на вопросы в рамках опросных сессий.

    Attributes:
        id: Уникальный идентификатор ответа.
        survey_id: Ссылка на сессию опроса.
        question_id: Ссылка на вопрос.
        answer: Ответ в формате JSON.
        created_at: Время создания ответа.
    """
    __tablename__ = 'survey_answers'
    
    __table_args__ = (
        CheckConstraint(
            "jsonb_typeof(answer) = 'object'", 
            name="ck_answer_is_json"
        ),
        Index('idx_answer_survey', 'survey_id'),
        Index('idx_answer_question', 'question_id'),
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    survey_id: Mapped[int] = mapped_column(ForeignKey('surveys.id'))
    question_id: Mapped[int] = mapped_column(ForeignKey('questions.id'))
    answer: Mapped[dict] = mapped_column(JSONB(none_as_null=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    question: Mapped["Questions"] = relationship(back_populates="answers")
    survey: Mapped["Surveys"] = relationship(back_populates="answers")

    def to_pydantic(self):
        return survey_answer.SurveyAnswerOut(
            id=self.id,
            survey_id=self.survey_id,
            question_id=self.question_id,
            answer=self.answer,
            created_at=self.created_at
        )
    
class SoftwareCategories(Base):
    """
    Категории программного обеспечения.

    Attributes:
        id: Уникальный идентификатор категории ПО.
        name: Название категории (уникальное).
        description: Описание категории ПО.
    """
    __tablename__ = 'software_categories'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String)

    def to_pydantic(self):
        return software_category.SoftwareCategoryOut(
            id=self.id,
            name=self.name,
            description=self.description
        )