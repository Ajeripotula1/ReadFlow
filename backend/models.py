from pydantic import BaseModel
from typing import Optional

## Registration Models ##
class RegisterUser(BaseModel):
    username: str
    password: str
    name: str
    
class RegisterUserResponse(BaseModel):
    username: str
    name:str
    
## Login Models ## 
class User(BaseModel): # Base User model
    id: int
    username: str
    name: str
    
class LoginUser(BaseModel): # Input model for login
    username: str
    password: str
    
class AuthenticatedUser(User): # Output model when user is authenticated
    access_token : str
    token_type: str

class UserList(BaseModel): # Admin view of multiple users
    users: list[User]
    
## Book Models ##
class Book(BaseModel):
    id: Optional[int] = None  # <-- optional
    external_id: str
    title: str
    author: str | None = None
    description: str | None = None
    image_url: str | None = None

class Books(BaseModel):
    books: list[Book]

class TitleSearch(BaseModel):
    title: str
    
class AddBookToList(BaseModel):
    external_id: str
    title: str
    author: str | None = None
    description: str | None = None
    image_url: str | None = None
