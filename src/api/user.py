from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta, timezone
import secrets

from src.models import get_db, User, TestQuestion, UserAnswer

router = APIRouter()

# 简单的token存储（生产环境应使用JWT）
tokens = {}

# 全局轮询指针
global_question_pointer = 0


# ========== Pydantic 模型 ==========

class UserRegister(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserInfo(BaseModel):
    id: int
    username: str
    points: int
    created_at: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserInfo


class QuestionDisplay(BaseModel):
    question_id: int
    content: str
    options: list
    lock_expires_at: Optional[str] = None  # 锁定过期时间（ISO格式）
    timeout_seconds: Optional[int] = None  # 剩余超时秒数（前端倒计时用）


class AnswerSubmit(BaseModel):
    question_id: int
    answer: str
    time_spent: int  # 花费时间(秒)


class AnswerResponse(BaseModel):
    success: bool
    points_earned: int
    current_points: int


# ========== 工具函数 ==========

import bcrypt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # bcrypt 限制密码最长72字节
    password_bytes = plain_password[:72].encode('utf-8')
    hash_bytes = hashed_password.encode('utf-8') if isinstance(hashed_password, str) else hashed_password
    return bcrypt.checkpw(password_bytes, hash_bytes)


def get_password_hash(password: str) -> str:
    # bcrypt 限制密码最长72字节
    password_bytes = password[:72].encode('utf-8')
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')


def create_token() -> str:
    return secrets.token_urlsafe(32)


def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未授权")

    token = authorization.replace("Bearer ", "")
    user_id = tokens.get(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="无效的token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")

    return user


# ========== API 端点 ==========

@router.post("/users/register", response_model=TokenResponse)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查用户名是否已存在
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")

    # 创建用户
    user = User(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        points=0
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # 生成token
    token = create_token()
    tokens[token] = user.id

    return TokenResponse(
        access_token=token,
        user=UserInfo(
            id=user.id,
            username=user.username,
            points=user.points,
            created_at=user.created_at.isoformat()
        )
    )


@router.post("/users/login", response_model=TokenResponse)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    user = db.query(User).filter(User.username == user_data.username).first()
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    # 生成token
    token = create_token()
    tokens[token] = user.id

    return TokenResponse(
        access_token=token,
        user=UserInfo(
            id=user.id,
            username=user.username,
            points=user.points,
            created_at=user.created_at.isoformat()
        )
    )


@router.get("/users/me", response_model=UserInfo)
def get_me(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    """获取当前用户信息"""
    user = get_current_user(authorization, db)
    return UserInfo(
        id=user.id,
        username=user.username,
        points=user.points,
        created_at=user.created_at.isoformat()
    )


@router.get("/questions/next", response_model=QuestionDisplay)
def get_next_question(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    """获取下一道待回答的题目"""
    user = get_current_user(authorization, db)
    now = datetime.now(timezone.utc)

    # 清理超时的锁定（手动处理时区问题）
    locked_questions = db.query(TestQuestion).filter(
        TestQuestion.locked_by.isnot(None),
        TestQuestion.lock_expires_at.isnot(None)
    ).all()

    for q in locked_questions:
        lock_expires = q.lock_expires_at
        if lock_expires.tzinfo is None:
            lock_expires = lock_expires.replace(tzinfo=timezone.utc)
        if now > lock_expires:
            q.locked_by = None
            q.lock_expires_at = None
    db.commit()

    global global_question_pointer
    last_question_id = global_question_pointer

    # 获取当前UTC时间（带时区信息）
    now = datetime.now(timezone.utc)

    # 查找需要更多答案的题目（未达到required_answers）
    # 注意：不再过滤locked_by，因为允许多个用户同时做同一道题
    questions = db.query(TestQuestion).filter(
        TestQuestion.current_answers_count < TestQuestion.required_answers
    ).order_by(TestQuestion.current_answers_count, TestQuestion.id).all()

    if not questions:
        raise HTTPException(status_code=404, detail="暂无可用题目")

    # 轮询分配：找到用户还未回答的题目
    selected_question = None
    for i in range(len(questions) * 2):  # 多轮循环确保找到
        idx = (last_question_id + i) % len(questions)
        candidate = questions[idx]
        # 检查用户是否已回答过此题
        existing_answer = db.query(UserAnswer).filter(
            UserAnswer.question_id == candidate.id,
            UserAnswer.user_id == user.id
        ).first()
        if not existing_answer:
            selected_question = candidate
            break

    if not selected_question:
        raise HTTPException(status_code=404, detail="暂无可用题目")

    # 锁定题目
    lock_expires = now + timedelta(seconds=selected_question.timeout_seconds)
    selected_question.locked_by = user.id
    selected_question.lock_expires_at = lock_expires
    db.commit()

    # 更新轮询指针
    global_question_pointer = selected_question.id

    return QuestionDisplay(
        question_id=selected_question.id,
        content=selected_question.content,
        options=selected_question.options_json,
        lock_expires_at=lock_expires.isoformat(),
        timeout_seconds=selected_question.timeout_seconds
    )


@router.post("/answers", response_model=AnswerResponse)
def submit_answer(
    answer_data: AnswerSubmit,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """提交答案"""
    user = get_current_user(authorization, db)
    now = datetime.now(timezone.utc)

    # 验证题目存在
    question = db.query(TestQuestion).filter(TestQuestion.id == answer_data.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")

    # 检查用户是否已回答过该题
    existing = db.query(UserAnswer).filter(
        UserAnswer.question_id == answer_data.question_id,
        UserAnswer.user_id == user.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="您已回答过该题目")

    # 检查是否已达到所需回答数
    if question.current_answers_count >= question.required_answers:
        raise HTTPException(status_code=400, detail="该题目已收集足够答案")

    # 清理过期的锁定
    lock_expires = question.lock_expires_at
    if lock_expires and lock_expires.tzinfo is None:
        lock_expires = lock_expires.replace(tzinfo=timezone.utc)
    if lock_expires and now > lock_expires:
        question.locked_by = None
        question.lock_expires_at = None
        db.commit()

    # 记录答案
    answer = UserAnswer(
        question_id=answer_data.question_id,
        user_id=user.id,
        answer=answer_data.answer,
        time_spent=answer_data.time_spent
    )
    db.add(answer)

    # 更新题目回答人数
    question.current_answers_count += 1

    # 解锁题目
    question.locked_by = None
    question.lock_expires_at = None

    # 奖励积分
    points_earned = 10
    user.points += points_earned

    db.commit()

    return AnswerResponse(
        success=True,
        points_earned=points_earned,
        current_points=user.points
    )