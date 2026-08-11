from datetime import datetime, timedelta

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from dto.employe_request_dto import EmployeRequestDto
from models.base import get_session
from models.employe import Employe
from models.task import Task


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

    adresse_mail = session.query(Employe).filter(Employe.email == dto.email).first()
    superviseur = session.query(Employe).filter(Employe.employee_id == dto.supervisor_id).first()
    if adresse_mail:
        raise HTTPException(status_code=422, detail='Cette adresse email est déjà utilisée')
    elif dto.titre == Employe.Titre.DEV and not superviseur: 
        raise HTTPException(status_code=422, detail='Un developpeur nécessite un superviseur')
    elif dto.titre == Employe.Titre.PM and superviseur.titre == Employe.Titre.DEV:
        raise HTTPException(status_code=422, detail='Un développeur ne peut pas superviser un PM')
    else:
        session.add(employe)
        # sauver en db sans commit
        session.flush()
        return employe.employee_id


@router.get('/e/{employee_id}')
def get_employee(
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
def delete_employee(
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


# @router.patch
def superviseur_modification(
        employee_id : int, 
        new_sup_id : int,
        session : Session = Depends(get_session)
        ):
    employee = session.get(Employe, employee_id)
    new_sup = session.get(Employe, new_sup_id)
    if employee is None: 
        raise HTTPException(status_code=404, detail='Cet employé n\'existe pas')
    elif new_sup is None:
        raise HTTPException(status_code=418, detail='Cet nouveau superviseur n\'existe pas') 
    else: 
        #superviseur_checking(employee_id, new_sup_id)

# c'est le NOUVEAU SUPERVISEUR que je dois vérfier
# def superviseur_checking(employee_id: int, session : Session = Depends(get_session), result:list=[]):
#     employee = session.get(Employe, employee_id)
#     result = []
#     while employee.superviseur:
#         result.append(employee_id)
#         if employee_id in result: 
#             return False
#         else: 

#             superviseur_checking(employee.superviseur.supervisor_id, Depends(get_session), result)
#             print(result)

