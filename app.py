import uvicorn
import httpx

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import all_routers  # all_routers is a list of routers imported from routers module
from config import origins


app = FastAPI(
    title="VM Allocater",
    description="A VM Allocater for supporting both OSPC and Flex environments",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in all_routers:
    app.include_router(r)


@app.get("/")
def home():
    return {"message": "Welcome to the FastAPI application!"}

#####################################################################
# TODO: This code will move into new service in NGPC codebase as VM Service
# Calling this will info complete functionality like add security groups then those will also attach to ports from here itself
# Should represent all the functionality of VM Service in NGPC codebase

@app.post("/create-vm")
def home():
    return {"message": "Welcome to the FastAPI application!"}

@app.delete("/delete-vm")
def home():
    return {"message": "Welcome to the FastAPI application!"}

@app.get("/get-full-vm-info")
def home():
    return {"message": "Welcome to the FastAPI application!"}

######################################################################

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)