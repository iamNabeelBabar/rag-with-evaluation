from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router.upload_router import router as upload_router
from router.retrieve_router import router as retrieve_router
import uvicorn



app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Streamlit default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(retrieve_router)

@app.get("/")
async def root():
    return {"message": "FastAPI is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=4545, reload=True)
