from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Industry(Base):
    __tablename__ = 'industries'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    is_custom = Column(Boolean, default=False)

class KiiSubject(Base):
    __tablename__ = 'kii_subjects'
    id = Column(Integer, primary_key=True)
    organization_name = Column(String, nullable=False)
    contact_person = Column(String)
    contact_email = Column(String)
    contact_phone = Column(String)
    industry_id = Column(Integer, ForeignKey('industries.id'))
    industry = relationship("Industry")

class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    question_text = Column(Text, nullable=False)
    question_type = Column(String, nullable=False)  # single_choice, multiple_choice, text
    is_active = Column(Boolean, default=True)

class AnswerOption(Base):
    __tablename__ = 'answer_options'
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey('questions.id', ondelete="CASCADE"))
    option_text = Column(Text, nullable=False)
    is_custom = Column(Boolean, default=False)

class Response(Base):
    __tablename__ = 'responses'
    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey('kii_subjects.id', ondelete="CASCADE"))
    question_id = Column(Integer, ForeignKey('questions.id', ondelete="CASCADE"))
    answer_option_id = Column(Integer, ForeignKey('answer_options.id'))
    custom_answer = Column(Text)

class TextResponse(Base):
    __tablename__ = 'text_responses'
    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey('kii_subjects.id', ondelete="CASCADE"))
    question_id = Column(Integer, ForeignKey('questions.id', ondelete="CASCADE"))
    response_text = Column(Text)
