from pathlib import Path

from fastapi import Body, Depends, FastAPI, Query
import uvicorn
from dotenv import load_dotenv
import os

from dto.hello_request_dto import HelloRequestDto
from dto.hello_response_dto import HelloResponseDto
from dto.mail_request_dto import MailRequestDto
from services.mailer import Mailer

load_dotenv()

# créer une instance de FastAPI
app = FastAPI()

@app.get('/hello')
def hello(
    # name: str = Query(default='Khun', description='Permet de définir qui sera saluer'), 
    # nb: int = Query(default=1, description='Permet de définir combien de fois')
    dto: HelloRequestDto = Query()
) -> HelloResponseDto:
    """
    Fonction test qui permet de dire bonjour !
    """
    return HelloResponseDto(
        result=f'Hello {dto.name * dto.nb}',
        square=dto.nb**2
    )
    # return { 'result': f'Hello {dto.name * dto.nb}', 'square': dto.nb**2 }


@app.post('/mail', status_code=201)
async def mail(
    dto: MailRequestDto = Body(),
    mailer: Mailer = Depends(Mailer)
) -> None:
    
    await mailer.send_message(
        dto.subject,
        dest=['lykhun@gmail.com'],
        template_body=dict(dto),
        template_name='mail_template.html'
    )

if __name__ == '__main__':
    # exposer FastAPI sur le port 8000
    uvicorn.run(
        'server:app', 
        host='127.0.0.1',
        port=8000,
        reload=True
    )


assert mail() == None