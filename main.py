from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pymongo import MongoClient
from bson import ObjectId
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
import secrets
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

client = MongoClient('mongodb://localhost:27017/')
db = client['local']
collection = db['submission']

try:
    client.admin.command('ping')
    logger.info("Successfully connected to MongoDB!")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")

app = FastAPI()
security = HTTPBasic()
class User(BaseModel):
    username: str
    password: str
    is_admin: bool = False

class Assignment(BaseModel):
    userId: str
    task: str
    admin: str
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)

def get_user(username: str):
    logger.debug(f"Attempting to retrieve user: {username}")
    user = collection.find_one({"username": username})
    if user:
        logger.debug(f"User found: {username}")
    else:
        logger.debug(f"User not found: {username}")
    return user

def authenticate_user(credentials: HTTPBasicCredentials):
    logger.debug(f"Attempting to authenticate user: {credentials.username}")
    user = get_user(credentials.username)
    if user and secrets.compare_digest(user['password'], credentials.password):
        logger.debug(f"User authenticated successfully: {credentials.username}")
        return user
    logger.debug(f"Authentication failed for user: {credentials.username}")
    return None

async def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    user = authenticate_user(credentials)
    if not user:
        logger.warning(f"Invalid authentication attempt for user: {credentials.username}")
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return user
@app.post("/register")
async def register_user(user: User):
    logger.info(f"Received registration request for user: {user.username}")
    if get_user(user.username):
        logger.warning(f"Attempted to register existing username: {user.username}")
        raise HTTPException(status_code=400, detail="Username already registered")
    user_dict = user.model_dump()
    logger.debug(f"Inserting user into database: {user_dict}")
    collection.insert_one(user_dict)
    logger.info(f"User registered successfully: {user.username}")
    return {"message": "User registered successfully"}

@app.post("/upload")
async def upload_assignment(assignment: Assignment, current_user: dict = Depends(get_current_user)):
    logger.info(f"Received assignment upload request from user: {current_user['username']}")
    if current_user.get("is_admin"):
        logger.warning(f"Admin user attempted to upload assignment: {current_user['username']}")
        raise HTTPException(status_code=403, detail="Admins cannot upload assignments")
    assignment_dict = assignment.model_dump()
    assignment_dict["userId"] = current_user["username"]
    logger.debug(f"Inserting assignment into database: {assignment_dict}")
    result = collection.insert_one(assignment_dict)
    logger.info(f"Assignment uploaded successfully. ID: {result.inserted_id}")
    return {"message": "Assignment uploaded successfully", "id": str(result.inserted_id)}

@app.get("/admins")
async def get_admins(current_user: dict = Depends(get_current_user)):
    logger.info(f"Received request to get admins from user: {current_user['username']}")
    admins = collection.find({"is_admin": True}, {"username": 1, "_id": 0})
    admin_list = list(admins)
    logger.debug(f"Retrieved {len(admin_list)} admins")
    return admin_list

@app.get("/assignments")
async def get_assignments(current_user: dict = Depends(get_current_user)):
    logger.info(f"Received request to get assignments from user: {current_user['username']}")
    if not current_user.get("is_admin"):
        logger.warning(f"Non-admin user attempted to view assignments: {current_user['username']}")
        raise HTTPException(status_code=403, detail="Only admins can view assignments")
    assignments = collection.find({"admin": current_user["username"]})
    assignment_list = list(assignments)
    logger.debug(f"Retrieved {len(assignment_list)} assignments for admin: {current_user['username']}")
    return assignment_list

@app.post("/assignments/{assignment_id}/accept")
async def accept_assignment(assignment_id: str, current_user: dict = Depends(get_current_user)):
    logger.info(f"Received request to accept assignment {assignment_id} from user: {current_user['username']}")
    if not current_user.get("is_admin"):
        logger.warning(f"Non-admin user attempted to accept assignment: {current_user['username']}")
        raise HTTPException(status_code=403, detail="Only admins can accept assignments")
    result = collection.update_one(
        {"_id": ObjectId(assignment_id), "admin": current_user["username"]},
        {"$set": {"status": "accepted"}}
    )
    if result.modified_count == 0:
        logger.warning(f"Assignment not found or not assigned to admin: {assignment_id}")
        raise HTTPException(status_code=404, detail="Assignment not found or not assigned to you")
    logger.info(f"Assignment {assignment_id} accepted successfully")
    return {"message": "Assignment accepted successfully"}

@app.post("/assignments/{assignment_id}/reject")
async def reject_assignment(assignment_id: str, current_user: dict = Depends(get_current_user)):
    logger.info(f"Received request to reject assignment {assignment_id} from user: {current_user['username']}")
    if not current_user.get("is_admin"):
        logger.warning(f"Non-admin user attempted to reject assignment: {current_user['username']}")
        raise HTTPException(status_code=403, detail="Only admins can reject assignments")
    result = collection.update_one(
        {"_id": ObjectId(assignment_id), "admin": current_user["username"]},
        {"$set": {"status": "rejected"}}
    )
    if result.modified_count == 0:
        logger.warning(f"Assignment not found or not assigned to admin: {assignment_id}")
        raise HTTPException(status_code=404, detail="Assignment not found or not assigned to you")
    logger.info(f"Assignment {assignment_id} rejected successfully")
    return {"message": "Assignment rejected successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8009)
