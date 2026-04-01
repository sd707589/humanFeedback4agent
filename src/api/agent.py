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