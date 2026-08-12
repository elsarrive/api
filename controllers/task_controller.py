
from fastapi import APIRouter, Body, Depends, BackgroundTasks, Path, Query, HTTPException
from starlette.status import *
from sqlalchemy import select

from dto.task_filter_request_dto import TaskFilterRequestDto
from dto.task_request_dto import TaskRequestDto
from sqlalchemy.orm import Session

from dto.task_response_dto import TaskResponseDto
from models.base import get_session
from models import Employe
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
    empl = (session.scalar(
        statement=select(Employe).
        where(Employe.email.ilike(dto.attribution_email)))
        .one_or_none())

    if not empl: 
        raise HTTPException(HTTP_422_UNPROCESSABLE_CONTENT, 'Employé introuvable')
    if empl.titre != Employe.Titre.DEV:
        raise HTTPException(HTTP_422_UNPROCESSABLE_CONTENT, 'On ne peut attribuer de tâches qu\'à un développeur')

    task = Task()
    task.name = dto.name
    task.end_date = datetime.now() + timedelta(days=dto.duration)
    task.assign_to_id = dto.assign_to_id
    task.attribution_email = dto.attribution_email

    session.add(task)
    # sauver en db sans commit
    session.flush()

    # envoyer l'email en arrière plan à toute la hiérarchie au dessus de l'employé (superviseurs en chaine)
    # emails = [empl.email]
    # e = empl
    # while e.supervisor:
    #     emails.append(e.supervisor.email)
    #     e = e.supervisor
    # 2e solution récurisve (moins de requêtes que le moyen pythonique)
    cte_r = (
        select(Employe)
        .where(Employe.employee_id == empl.id)
        .cte(recursive=True)
    )
    recursive_stmt = (
        select(Employe)
        .join(cte_r, cte_r.c.supervisor_id == Employe.employee_id)
    )
    stmt = cte_r.union_all(recursive_stmt)
    # ça va donner un tuple contenant des infos concernant l'employé. si on veut etre sur que tout soit convertis en employé; 
    # on rajoute le from_statement (en passant par les CTE, le système perd l'info que ce sont des Employe)
    result: list[Employe] = list(session.scalars(select(Employe).from_statement(stmt)).all())
    print(result) # c'est un modèle employé qu'on obtient
    emails = [e.email for e in result]

    background_tasks.add_task(
        mailer.send_message,
        'Nouvelle tâche', emails,
        task.__dict__,
        'new_task.html'
    )
    return task.id



@router.get('/', status_code=201)
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


@router.patch('/{id}', status_code=201)
def update_status(
    id: int = Path(), status: Task.Status = Body(),
    session: Session = Depends(get_session)
):
    try:
        task = session.get_one(Task, id)
    except:
        raise HTTPException(HTTP_404_NOT_FOUND)
    
    if task.end_date < datetime.now():
        raise HTTPException(HTTP_422_UNPROCESSABLE_CONTENT, {
            'message': 'Il n\'est plus possible de modifier cet enregistrement'
        }) 
    
    task.status = status
    session.flush([task])
    return task.id




@router.delete('/{id}', status_code=201)
def delete(
    background_tasks: BackgroundTasks,
    id: int = Path(), 
    session: Session = Depends(get_session),
    mailer: Mailer = Depends(Mailer)
):
    try:
        task: Task = session.get_one(Task, id)
    except:
        raise HTTPException(HTTP_404_NOT_FOUND)

    if task.status == Task.Status.done:
        raise HTTPException(HTTP_422_UNPROCESSABLE_CONTENT, {
            'message': 'Impossible de supprimer une tâche terminée'
        })

    background_tasks.add_task(
        mailer.send_message,
        'Tâche supprimée',
        [task.attribution_email],
        task.__dict__,
        'task_removed.html'
    )
    session.delete(task)
    session.flush()
    return task.id