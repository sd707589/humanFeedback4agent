from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    points = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    answers = relationship("UserAnswer", back_populates="user")


class TestTask(Base):
    __tablename__ = "test_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_type = Column(String(50), nullable=False)  # ui评估, 内容审核, 功能验证, 多模态
    content = Column(Text, nullable=False)  # 任务描述
    answer_key = Column(String(50), nullable=True)  # 标准答案(如果有)
    status = Column(String(20), default="pending")  # pending, running, completed
    created_at = Column(DateTime, default=datetime.utcnow)

    questions = relationship("TestQuestion", back_populates="task")


class TestQuestion(Base):
    __tablename__ = "test_questions"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("test_tasks.id"), nullable=False)
    content = Column(Text, nullable=False)  # 题目内容
    options_json = Column(JSON, nullable=False)  # 选项列表
    required_answers = Column(Integer, default=5)  # 需要多少人回答
    current_answers_count = Column(Integer, default=0)  # 当前回答人数
    locked_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # 当前锁定用户ID
    lock_expires_at = Column(DateTime, nullable=True)  # 锁定过期时间
    timeout_seconds = Column(Integer, default=60)  # 超时时间(秒)

    task = relationship("TestTask", back_populates="questions")
    answers = relationship("UserAnswer", back_populates="question")
    locker = relationship("User", foreign_keys=[locked_by])


class UserAnswer(Base):
    __tablename__ = "user_answers"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("test_questions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    answer = Column(String(255), nullable=False)  # 用户选择的答案
    time_spent = Column(Integer, default=0)  # 花费时间(秒)
    created_at = Column(DateTime, default=datetime.utcnow)

    question = relationship("TestQuestion", back_populates="answers")
    user = relationship("User", back_populates="answers")


# 数据库引擎
engine = create_engine("sqlite:///./crowd_test.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()