# app/routers/auth.py
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import os
import logging

router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserCredentials(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    user: str = None
    debug_info: dict = None

# Path to the users file
USERS_FILE_PATH = "app/users.txt"

def verify_user(username: str, password: str) -> tuple[bool, str, dict]:
    """
    Verify user credentials against the users.txt file
    Returns a tuple of (is_valid, error_type, debug_info)
    error_type can be: "success", "user_not_found", "incorrect_password"
    """
    debug_info = {
        "attempted_user": username,
        "users_file_path": USERS_FILE_PATH,
        "file_exists": os.path.exists(USERS_FILE_PATH),
        "users_found": []
    }
    
    if not os.path.exists(USERS_FILE_PATH):
        debug_info["error"] = "Users file not found"
        logger.error(f"Users file not found at {USERS_FILE_PATH}")
        return False, "server_error", debug_info
    
    user_found = False
    
    try:
        with open(USERS_FILE_PATH, "r") as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                if line:  # Skip empty lines
                    try:
                        stored_username, stored_password = line.split(";")
                        debug_info["users_found"].append({
                            "line": line_num,
                            "username": stored_username
                        })
                        
                        if stored_username == username:
                            user_found = True
                            if stored_password == password:
                                debug_info["matched_line"] = line_num
                                logger.info(f"User {username} authenticated successfully")
                                return True, "success", debug_info
                            else:
                                debug_info["matched_line"] = line_num
                                logger.info(f"User {username} found but password incorrect")
                                return False, "incorrect_password", debug_info
                    except ValueError:
                        logger.warning(f"Invalid format in users file at line {line_num}: {line}")
                        continue
                        
    except Exception as e:
        debug_info["error"] = f"Error reading users file: {str(e)}"
        logger.error(f"Error reading users file: {str(e)}")
        return False, "server_error", debug_info
    
    if not user_found:
        logger.info(f"User {username} not found")
    else:
        logger.info(f"Authentication failed for user {username}")
        
    return False, "user_not_found" if not user_found else "incorrect_password", debug_info

@router.post("/login", response_model=LoginResponse)
async def login(credentials: UserCredentials):
    """
    Authenticate user by checking credentials against users.txt file
    Returns detailed debug information
    """
    is_valid, error_type, debug_info = verify_user(credentials.username, credentials.password)
    
    if is_valid:
        return LoginResponse(
            success=True,
            message="Authentication successful",
            user=credentials.username,
            debug_info=debug_info
        )
    else:
        # Create specific error messages based on error type
        if error_type == "user_not_found":
            message = "User not found"
        elif error_type == "incorrect_password":
            message = "Incorrect password"
        else:
            message = "Authentication failed"
            
        return LoginResponse(
            success=False,
            message=message,
            user=None,
            debug_info=debug_info
        )