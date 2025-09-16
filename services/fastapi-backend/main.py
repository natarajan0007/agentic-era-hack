from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from the FastAPI backend"}

@app.get("'/api/data'")
def get_data():
    return {"data": [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]}
