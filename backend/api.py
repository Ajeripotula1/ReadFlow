from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt, JWTError
from passlib.context import CryptContext # Helper for hashing and verifying passwords
from datetime import datetime, timedelta
from database import get_connection
from psycopg2.extras import RealDictCursor
import os, requests, psycopg2
from datetime import date
from dotenv import load_dotenv
from models import RegisterUser, RegisterUserResponse, AuthenticatedUser, UserList, Books, TitleSearch, AddBookToList
load_dotenv()
app = FastAPI()

# Declare that you will receive the JWT token from the user when they try to access a protected route
# this a reusable dependency (Bearer Token) which is obtained at the token endpoint
# When a route DEPENDS on this schema, FastAPI looks for an Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# CORS Control: Cross-Origin Resource Sharing: webserver relaxes the same-origin policy and allow brower to communicate with server
origins = [
    "http://localhost:3000" # Frontend Port (Can add domain to production server also)
]
app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

# Helper to hash pasword
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# JWT Authetication stff
SECRET_KEY = "my-secret-key"
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRES_MINUTES = 30

    
# Register User
@app.post("/register", response_model=RegisterUserResponse, status_code=status.HTTP_201_CREATED)
def register(user: RegisterUser):
    cursor, conn = None, None
    try:
        # Establish db connection and create cursor for sql commands
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if username alr exists
        query = """
            SELECT username FROM users
            WHERE username = (%s)
        """
        values = (user.username,)
        cursor.execute(query, values)
        fetched_user = cursor.fetchone()
        
        if fetched_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists. Pleae pick another")
        
        # If not hash pasword and save user info in DB
        hashed_password = pwd_context.hash(user.password)
        query = """
            INSERT INTO users (username, password, name)
            VALUES (%s, %s, %s)
        """
        values = (user.username, hashed_password, user.name)
        cursor.execute(query, values)
        # commit changes to DB
        conn.commit()
        
        return {
            "username": user.username, 
            "name": user.name
        }
    
    # Let FastAPI handle any HTTPExceptions you raised yourself
    except HTTPException as e:
        raise e
    
    except psycopg2.Error as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e.pgerror}")
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error." + str(e))
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Generate Token for authenticated user
def generate_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    
    # If we are given a time_delta, add it to now and set expiary date
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # else compute times based on default (30 mins)
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
    # add epiration time to input dict
    to_encode.update({"exp": expire})
    # take dictionary and turn it into securly signed token and return token str
    # JWT has three parts: 
        # Header: describes type and algo used, 
        # Payload: the data you want to encode (input dict)
        # Signature: signature formed to ensure no tampering by adding header, payload, and secret key
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Login and issue token
#OAuth2PasswordRequestForm: FastAPI class that parses form data sent to login or token route
    # assumes body contains form data 
# Depends(): FastAPI dependency injection tool ()
    # tells fastpai to run some code before function is called
@app.post("/token", response_model=AuthenticatedUser, status_code=status.HTTP_200_OK)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    connection,cursor = None, None
    try:
        # Get hashed password for username if it exists
        connection = get_connection()
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * from users WHERE username = %s",(form_data.username,))
        db_user = cursor.fetchone()
        
        # Throw error if user doesn't exist or password is incorrect
        if not db_user or not pwd_context.verify(form_data.password, db_user["password"]):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invlaid credentials.")
    
        # If password matches, generate a JWT Token
        access_token = generate_token({ "sub":form_data.username,"id": db_user["id"] }) 
        return {
            "id": db_user["id"],
            "username": db_user["username"],
            "name": db_user["name"],
            "access_token": access_token,
            "token_type" : "bearer"
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error." + str(e))
        
    finally:
        cursor.close()
        connection.close()

# extract and validate JWT token from the request
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token or credentials",
        headers={"WWW-Authenticate":"Bearer"},
    )
    try:
        # is the token present
        # is the token valid (not expired, signed correctly)
        # who is the user
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        id:int = payload.get("id")
        if username is None:
            raise credentials_exception
        return {"username":username, "id":id}
    
    except JWTError:
        raise credentials_exception

@app.get("/users", response_model=UserList, status_code=status.HTTP_200_OK)
def get_users(curr_user: dict = Depends(get_current_user)):
    conn, cursor = None, None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT id, username, name FROM users")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        return {"users":users}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not get users")
    finally:
        if conn:
            conn.close()
        if cursor:
            cursor.close()
# All books in Database 
@app.get("/books", response_model=Books, status_code=status.HTTP_200_OK)
def get_books(curr_user: dict = Depends(get_current_user)): # Requires Login 
    try:
        conn = get_connection()
        # auto convert rows into dictionaries 
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM books;")
        books = cursor.fetchall()
        cursor.close()
        conn.close()
        return {"books": books}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error." + str(e))
        
    
# Get all books for all the Best Sellers lists for specified print date.
@app.get("/trending", response_model=Books, status_code=status.HTTP_200_OK)
def get_trending():
    try:
        api_url = "https://api.nytimes.com/svc/books/v3/lists/overview.json"
        api_key = os.getenv("BOOKS_API")
        # "2025-05-19"
        today = date.today()
        api_date = today.strftime("%Y-%m-%d")
        print("sending request for: ", api_date)
        response = requests.get(
            url = api_url, 
            params = {
                "published_date": api_date,
                "api-key": api_key
            }
        )
        # convert JSON to python dict
        trending = response.json()        
        # get top 10 lists
        lists = trending["results"]["lists"][:10]
        
        # store one book from each list 
        books = []
        for list in lists:
            # print(list["list_name"], list["books"][0]["title"])
            books.append(list["books"][0])
        
        # extract only relevant info 
        trending = []
        for book in books:
            # print(book)
            # option 1. create new list of books with only relevant info and then add whole list to db? will this add individually?
            trending.append({
                "external_id": book["primary_isbn13"] or book["primary_isbn10"],
                "title": book["title"],
                "author": book["author"],
                "description": book["description"],
                "image_url": book["book_image"]
            })
        return {"books": trending}
                  
    except Exception as e:
        # Add print to see the actual error in your terminal
        print("Error fetching trending books:", str(e))
        raise HTTPException(status_code=500, detail="Something went wrong: " + str(e))
# Search for book by title, return top 5 results
@app.post("/search", response_model=Books, status_code=status.HTTP_200_OK)
def search(book_title:TitleSearch):
    try:
        api_url = "https://www.googleapis.com/books/v1/volumes"
        request = requests.get(
            api_url,
            params= {
                "q": book_title.title,
                "maxResults": 5,
                "printType" : "books",
                "projection" : "lite"
            }    
        )
        # convert data to python
        data = request.json()
        books = []
        for item in data["items"]:
            volume_info = item["volumeInfo"]
            industry_ids = volume_info.get("industryIdentifiers", [])
            
            isbn13 = next((id["identifier"] for id in industry_ids if id["type"] == "ISBN_13"), None)
            external_id = isbn13 or item["id"]

            title = volume_info.get("title", "Unknown Title")
            author = ", ".join(volume_info.get("authors", ["Unknown Author"]))
            description = volume_info.get("description", "")
            image_url = volume_info.get("imageLinks", {}).get("thumbnail", "")

            books.append(
                {
                    "external_id":external_id, 
                    "title":title, 
                    "author":author, 
                    "description":description, 
                    "image_url":image_url
                }
            )
        return {"books":books}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error." + str(e))
    
# get the logged in user, and look up their books
@app.get("/reading_list", response_model=Books, status_code=status.HTTP_200_OK)
def get_reading_list(curr_user: dict = Depends(get_current_user)):
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        query = """
        SELECT b.id, b.external_id, b.title, b.author, b.description, b.image_url
        FROM user_books ub
        JOIN books b ON ub.book_id = b.id
        WHERE ub.user_id = %s
        """
        cursor.execute(query, (curr_user["id"],))
        books = cursor.fetchall()

        cursor.close()
        conn.close()
        return {"books": books}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error." + str(e))

@app.post("/reading_list")
def add_to_list(book:AddBookToList,curr_user:dict=Depends(get_current_user)):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 1. Check if book already exists in books table
        cursor.execute("SELECT id FROM books WHERE external_id = %s", (book.external_id,))
        result = cursor.fetchone()
        
        # 2. If not exists, insert it
        if not result:
            cursor.execute(
                """
                INSERT INTO books (external_id, title, author, description, image_url)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """,
                (book.external_id, book.title, book.author, book.description, book.image_url)
            )
            book_id = cursor.fetchone()[0]
        else:
            book_id = result[0]
         # 3. Insert into user_books
        cursor.execute(
            """
            INSERT INTO user_books (user_id, book_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
            """,
            (curr_user["id"], book_id)
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"message": f"'{book.title}' added to your reading list!"}
    except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Internal Server Error." + str(e))    

