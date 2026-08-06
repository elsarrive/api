from fastapi import FastAPI
import uvicorn
from controllers import default_controller

# créer une instance de FastAPI
app = FastAPI()

app.include_router(default_controller.router)

if __name__ == '__main__':
    # exposer FastAPI sur le port 8000
    uvicorn.run(
        'server:app', 
        host='127.0.0.1',
        port=8000,
        reload=True
    )