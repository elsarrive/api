from fastapi import FastAPI
import uvicorn
from controllers import default_controller, employe_controller, task_controller

# créer une instance de FastAPI
app = FastAPI()

# pour ne pas devoir inclure chaque router, on peut créer une fonction (Khun l'a fait dans son dossier 'utils')
app.include_router(default_controller.router)
app.include_router(task_controller.router)
app.include_router(employe_controller.router)


if __name__ == '__main__':
    # exposer FastAPI sur le port 8000
    uvicorn.run(
        'server:app', 
        host='127.0.0.1',
        port=8000,
        reload=True
    )