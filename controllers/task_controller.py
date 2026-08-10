
from fastapi import APIRouter, Body, Depends, BackgroundTasks, Query
from sqlalchemy import select

from dto.task_filter_request_dto import TaskFilterRequestDto
from dto.task_request_dto import TaskRequestDto
from sqlalchemy.orm import Session

from dto.task_response_dto import TaskResponseDto
from models.base import get_session
from models.task import Task
from datetime import datetime, timedelta

from services.mailer import Mailer


router = APIRouter(prefix='/tasks', tags=['Tasks'])

@router.post('/', status_code=201)
async def create(
    background_tasks: BackgroundTasks,
    dto: TaskRequestDto = Body(), 
    session: Session = Depends(get_session),
    mailer: Mailer = Depends(Mailer)
):
    task = Task()
    task.name = dto.name
    task.attribution_email = dto.attribution_email
    task.end_date = datetime.now() + timedelta(days=dto.duration)
    session.add(task)
    # sauver en db sans commit
    session.flush()
    # envoyer l'email en arrière plan
    background_tasks.add_task(
        mailer.send_message,
        'Nouvelle tâche', [task.attribution_email],
        task.__dict__,
        'new_task.html'
    )
    return task.id

@router.get('/')
def get(
    dto: TaskFilterRequestDto = Query(),
    session: Session = Depends(get_session)
) -> list[TaskResponseDto]:
    stmt = (select(Task)
        .where(not dto.email or Task.attribution_email == dto.email)
        .where(not dto.status or Task.status == dto.status)
        .offset((dto.page - 1) * dto.limit)
        .limit(dto.limit)
    )
    tasks = session.execute(stmt).scalars().all()
    # transforme chaque model db en dto
    return map(TaskResponseDto.from_entity, tasks)
    # return [TaskResponseDto.from_entity(t) for t in tasks]

    

    
