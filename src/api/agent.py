from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from collections import Counter

from src.models import get_db, TestTask, TestQuestion, UserAnswer

router = APIRouter()


# ========== Pydantic 模型 ==========

class QuestionCreate(BaseModel):
    content: str
    options: List[str]
    required_answers: int = 5
    timeout_seconds: int = 60  # 超时时间(秒)


class TaskCreate(BaseModel):
    task_type: str  # ui评估, 内容审核, 功能验证, 多模态
    content: str  # 任务描述
    answer_key: Optional[str] = None  # 标准答案(如果有)
    questions: List[QuestionCreate]


class TaskResponse(BaseModel):
    id: int
    task_type: str
    content: str
    status: str
    created_at: str

    class Config:
        from_attributes = True


class QuestionResult(BaseModel):
    question_id: int
    content: str
    options: List[str]
    required_answers: int
    current_answers_count: int
    answer_distribution: dict
    correct_answer: Optional[str] = None
    avg_time_spent: Optional[float] = None


class TaskResult(BaseModel):
    task_id: int
    task_type: str
    content: str
    status: str
    total_questions: int
    completed_questions: int
    questions: List[QuestionResult]


# ========== API 端点 ==========

@router.post("/tasks", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """创建测试任务"""
    db_task = TestTask(
        task_type=task.task_type,
        content=task.content,
        answer_key=task.answer_key,
        status="running"
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    # 创建题目
    for q in task.questions:
        db_question = TestQuestion(
            task_id=db_task.id,
            content=q.content,
            options_json=q.options,
            required_answers=q.required_answers,
            current_answers_count=0,
            timeout_seconds=q.timeout_seconds
        )
        db.add(db_question)

    db.commit()

    return TaskResponse(
        id=db_task.id,
        task_type=db_task.task_type,
        content=db_task.content,
        status=db_task.status,
        created_at=db_task.created_at.isoformat()
    )


@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """查询任务状态"""
    task = db.query(TestTask).filter(TestTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    return TaskResponse(
        id=task.id,
        task_type=task.task_type,
        content=task.content,
        status=task.status,
        created_at=task.created_at.isoformat()
    )


@router.get("/tasks/{task_id}/results", response_model=TaskResult)
def get_task_results(task_id: int, db: Session = Depends(get_db)):
    """获取测试结果"""
    task = db.query(TestTask).filter(TestTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    questions = db.query(TestQuestion).filter(TestQuestion.task_id == task_id).all()

    results = []
    completed_count = 0

    for q in questions:
        # 获取该题目的所有答案
        answers = db.query(UserAnswer).filter(UserAnswer.question_id == q.id).all()

        # 统计答案分布
        answer_list = [a.answer for a in answers]
        distribution = dict(Counter(answer_list))

        # 计算平均耗时
        avg_time = sum(a.time_spent for a in answers) / len(answers) if answers else None

        # 确定正确答案（多数投票）
        correct = max(distribution, key=distribution.get) if distribution else None

        # 检查是否完成
        is_completed = q.current_answers_count >= q.required_answers
        if is_completed:
            completed_count += 1

        results.append(QuestionResult(
            question_id=q.id,
            content=q.content,
            options=q.options_json,
            required_answers=q.required_answers,
            current_answers_count=q.current_answers_count,
            answer_distribution=distribution,
            correct_answer=correct if is_completed else None,
            avg_time_spent=avg_time
        ))

    # 更新任务状态
    if completed_count == len(questions) and len(questions) > 0:
        task.status = "completed"
        db.commit()

    return TaskResult(
        task_id=task.id,
        task_type=task.task_type,
        content=task.content,
        status=task.status,
        total_questions=len(questions),
        completed_questions=completed_count,
        questions=results
    )


from fastapi import UploadFile, File
from fastapi.responses import FileResponse
import os
import time
import uuid
from pathlib import Path

IMAGE_DIR = Path("/tmp/crowd_test_images")
EXPIRE_DAYS = 2

IMAGE_DIR.mkdir(parents=True, exist_ok=True)


def clean_expired_images():
    """清理过期图片（超过 EXPIRE_DAYS 天）"""
    now = time.time()
    for file in IMAGE_DIR.glob("*"):
        if file.is_file():
            mtime = file.stat().st_mtime
            if (now - mtime) > (EXPIRE_DAYS * 24 * 60 * 60):
                try:
                    file.unlink()
                except Exception:
                    pass


class ImageUploadResponse(BaseModel):
    success: bool
    image_url: str
    image_id: str


@router.post("/images", response_model=ImageUploadResponse)
def upload_image(file: UploadFile = File(...)):
    """上传图片，返回可访问的 URL

    图片会保存在 /tmp/crowd_test_images，超过 2 天自动清理
    """
    clean_expired_images()

    ext = file.filename.split(".")[-1] if "." in file.filename else "png"
    if ext.lower() not in ["jpg", "jpeg", "png", "gif", "webp"]:
        raise HTTPException(status_code=400, detail="不支持的图片格式，仅支持: jpg, png, gif, webp")

    image_id = f"{uuid.uuid4().hex[:16]}.{ext.lower()}"
    image_path = IMAGE_DIR / image_id

    content = file.file.read()
    with open(image_path, "wb") as f:
        f.write(content)

    image_url = f"/api/images/{image_id}"
    return ImageUploadResponse(
        success=True,
        image_url=image_url,
        image_id=image_id
    )


@router.get("/images/{image_id}")
def get_image(image_id: str):
    """获取图片"""
    image_path = IMAGE_DIR / image_id
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="图片不存在或已过期")

    ext = image_id.split(".")[-1].lower()
    content_type_map = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "webp": "image/webp"
    }
    content_type = content_type_map.get(ext, "image/png")

    return FileResponse(image_path, media_type=content_type)


class BatchQuestionsRequest(BaseModel):
    """批量获取问题结果请求"""
    question_ids: Optional[List[int]] = None
    task_id_min: Optional[int] = None
    task_id_max: Optional[int] = None
    created_after: Optional[str] = None
    created_before: Optional[str] = None


class BatchQuestionsResponse(BaseModel):
    """批量获取问题结果响应"""
    total: int
    questions: List[QuestionResult]


@router.post("/questions/results", response_model=BatchQuestionsResponse)
def get_questions_results(
    request: BatchQuestionsRequest,
    db: Session = Depends(get_db)
):
    """批量获取多个问题的结果

    支持多种筛选方式：
    - question_ids: 直接指定问题ID列表
    - task_id_min / task_id_max: 指定任务ID范围
    - created_after / created_before: 指定创建时间范围 (ISO格式字符串，如 2026-04-01)

    返回所有符合条件的问题结果，包含每个问题的答案分布统计
    """
    query = db.query(TestQuestion)

    if request.question_ids:
        query = query.filter(TestQuestion.id.in_(request.question_ids))

    if request.task_id_min is not None:
        query = query.filter(TestQuestion.task_id >= request.task_id_min)
    if request.task_id_max is not None:
        query = query.filter(TestQuestion.task_id <= request.task_id_max)

    from datetime import datetime
    if request.created_after:
        try:
            dt = datetime.fromisoformat(request.created_after)
            query = query.filter(TestQuestion.created_at >= dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="created_after 格式错误，需要 ISO 格式如 2026-04-01")
    if request.created_before:
        try:
            dt = datetime.fromisoformat(request.created_before)
            query = query.filter(TestQuestion.created_at <= dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="created_before 格式错误，需要 ISO 格式如 2026-04-01")

    questions = query.all()
    results = []

    for q in questions:
        answers = db.query(UserAnswer).filter(UserAnswer.question_id == q.id).all()
        answer_list = [a.answer for a in answers]
        distribution = dict(Counter(answer_list))

        avg_time = sum(a.time_spent for a in answers) / len(answers) if answers else None

        correct = max(distribution, key=distribution.get) if distribution else None
        is_completed = q.current_answers_count >= q.required_answers

        results.append(QuestionResult(
            question_id=q.id,
            content=q.content,
            options=q.options_json,
            required_answers=q.required_answers,
            current_answers_count=q.current_answers_count,
            answer_distribution=distribution,
            correct_answer=correct if is_completed else None,
            avg_time_spent=avg_time
        ))

    return BatchQuestionsResponse(
        total=len(results),
        questions=results
    )


class ListTasksRequest(BaseModel):
    """列出任务请求"""
    task_id_min: Optional[int] = None
    task_id_max: Optional[int] = None
    created_after: Optional[str] = None
    created_before: Optional[str] = None
    status: Optional[str] = None


class TaskListItem(BaseModel):
    """任务列表项"""
    id: int
    task_type: str
    content: str
    status: str
    created_at: str
    total_questions: int
    completed_questions: int

    class Config:
        from_attributes = True


class ListTasksResponse(BaseModel):
    """列出任务响应"""
    total: int
    tasks: List[TaskListItem]


@router.post("/tasks/list", response_model=ListTasksResponse)
def list_tasks(
    request: ListTasksRequest,
    db: Session = Depends(get_db)
):
    """按条件筛选列出多个任务

    支持筛选：
    - task_id_min / task_id_max: 任务ID范围
    - created_after / created_before: 创建时间范围
    - status: 任务状态 (running / completed)
    """
    query = db.query(TestTask)

    if request.task_id_min is not None:
        query = query.filter(TestTask.id >= request.task_id_min)
    if request.task_id_max is not None:
        query = query.filter(TestTask.id <= request.task_id_max)

    from datetime import datetime
    if request.created_after:
        try:
            dt = datetime.fromisoformat(request.created_after)
            query = query.filter(TestTask.created_at >= dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="created_after 格式错误，需要 ISO 格式如 2026-04-01")
    if request.created_before:
        try:
            dt = datetime.fromisoformat(request.created_before);
            query = query.filter(TestTask.created_at <= dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="created_before 格式错误，需要 ISO 格式如 2026-04-01")

    if request.status:
        query = query.filter(TestTask.status == request.status)

    tasks = query.order_by(TestTask.id.desc()).all()
    results = []

    for task in tasks:
        total_questions = db.query(TestQuestion).filter(TestQuestion.task_id == task.id).count()
        completed_questions = db.query(TestQuestion).filter(
            TestQuestion.task_id == task.id,
            TestQuestion.current_answers_count >= TestQuestion.required_answers
        ).count()

        results.append(TaskListItem(
            id=task.id,
            task_type=task.task_type,
            content=task.content,
            status=task.status,
            created_at=task.created_at.isoformat(),
            total_questions=total_questions,
            completed_questions=completed_questions
        ))

    return ListTasksResponse(
        total=len(results),
        tasks=results
    )