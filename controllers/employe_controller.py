from datetime import datetime, timedelta

from fastapi import APIRouter, BackgroundTasks, Body, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from dto.employe_request_dto import EmployeRequestDto
from models.base import get_session
from models.employe import Employe
from models.task import Task
from services.mailer import Mailer


router = APIRouter(prefix='/employes', tags=['employes'])

@router.post('/', status_code=201)
async def create(
    dto: EmployeRequestDto = Body(), 
    session: Session = Depends(get_session)
    ):
    employe = Employe()
    employe.first_name = dto.first_name
    employe.last_name = dto.last_name
    employe.email = dto.email
    employe.salary = dto.salary
    employe.titre = dto.titre
    employe.supervisor_id = dto.supervisor_id

    adresse_mail_stmt = select(Employe).where(Employe.email == dto.email)
    adresse_mail = session.execute(adresse_mail_stmt).scalars().one_or_none()

    if adresse_mail:
        raise HTTPException(status_code=409, detail='Cette adresse email est déjà utilisée')

    superviseur = None
    if dto.supervisor_id:
        superviseur_stmt = select(Employe).where(Employe.employee_id == dto.supervisor_id)
        superviseur = session.execute(superviseur_stmt).scalars().one_or_none()
        
    if dto.titre == Employe.Titre.DEV and not superviseur: 
        raise HTTPException(status_code=422, detail='Un developpeur nécessite un superviseur')
    if dto.titre == Employe.Titre.PM and superviseur and superviseur.titre == Employe.Titre.DEV:
        raise HTTPException(status_code=422, detail='Un développeur ne peut pas superviser un PM')
    
    session.add(employe)
    # sauver en db sans commit
    session.flush()
    return employe.employee_id


@router.get('/e/{employee_id}')
async def get_employee(
    employee_id : int, 
    session : Session = Depends(get_session)):
    e = session.get(Employe, employee_id)
    return e, e.superviseur

    # stmt = select(Employe).options(joinedload(Employe.superviseur)).where(Employe.employee_id == employee_id)
    # e = session.execute(stmt).scalars().one()
    # print(e.employee_id)
    # print(e.supervisor_id)
    # print(e.superviseur.last_name)# -> on va directement pouvoir chainer grace à la recursion dans la hierarchie
    #return {e, e.superviseur}


@router.delete('/e/{employee_id}')
async def delete_employee(
        employee_id : int, 
        session : Session = Depends(get_session)
        ):
    employee = session.get(Employe, employee_id)
    
    if employee is None: 
        raise HTTPException(status_code=404, detail='Cet employé n\'existe pas')
    elif employee.supervisor_id is None:
        raise HTTPException(status_code=418, detail='Suppression impossible : cet employé n\'a pas de superviseur') 
    else: 
        for t in employee.tasks:
            print(t)
            t.assign_to = employee.superviseur.employee
        session.delete(employee)
        session.flush()


def superviseur_checking(employee_id: int, new_sup_id: int, session : Session = Depends(get_session), result : list[int]|None=None):
    if result is None: 
        result = []

    if new_sup_id in result or new_sup_id == employee_id: 
        return False

    result.append(new_sup_id)
    print(result)

    new_sup = session.get(Employe, new_sup_id)
    if not new_sup:
        return True
    if new_sup.superviseur is None:
        return True

    # new_sup = new_sup.superviseur
    return superviseur_checking(employee_id, new_sup.superviseur.employee_id, session, result)
        

@router.patch('/e/{employee_id}')
def superviseur_modification(
        background_tasks: BackgroundTasks,
        employee_id : int, 
        new_sup_id : int,
        session : Session = Depends(get_session),
        mailer : Mailer = Depends(Mailer)
        ):

    employee = session.get(Employe, employee_id)
    if employee is None: 
        raise HTTPException(status_code=422, detail='Cet employé n\'existe pas')
    
    # garder en memoire le supérieur de base de l'employé
    sup_originel = employee.superviseur or None

    # avoir le nouveau superviseur
    new_sup = session.get(Employe, new_sup_id)
    if new_sup is None:
        raise HTTPException(status_code=422, detail='Cet nouveau superviseur n\'existe pas') 
    
    if superviseur_checking(employee_id, new_sup_id, session) is False:
        raise HTTPException(status_code=409, detail='Ce changement créerait un cycle dans la hiérarchie')
    if employee.titre == Employe.Titre.PM and new_sup.titre == Employe.Titre.DEV:
        raise HTTPException(status_code=422, detail='Un développeur ne peut pas superviser un PM')

    employee.superviseur = new_sup
    session.flush([employee])

    # envoi du mail à la hierarchie (NB: j'utilise le contexte de cte recursive, cf.task controller pr obtenir result ><  recursion pythonique: result dans superviseur_checking pas récupéré)
    cte_r = (
    select(Employe)
    .where(Employe.employee_id == employee.employee_id)
    .cte(recursive=True)
    )
    recursive_stmt = (
        select(Employe)
        .join(cte_r, cte_r.c.supervisor_id == Employe.employee_id)
    )
    hierarchie_stmt = cte_r.union_all(recursive_stmt)
    stmt = select(Employe).from_statement(select(hierarchie_stmt))
    result: list[Employe] = session.scalars(stmt).all()
    emails: list[str] = [e.email for e in result]

    mail_context = {
        "employee_first_name": employee.first_name,
        "employee_last_name": employee.last_name,
        "old_sup_last_name": sup_originel.last_name if sup_originel else "Aucun",
        "new_sup_last_name": new_sup.last_name,
    }
    background_tasks.add_task(mailer.send_message, subject='Changement de superviseur', dest=emails, template_body=mail_context, template_name='supervisor_modified.html')

    return employee.employee_id





