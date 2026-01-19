# 401 Authentication Error Fix

## Problem Analysis

**Error:** `401 {"status":"error","error_type":"http_exception","detail":"User not found. Please sign in again."}`

**Root Cause:**
The error occurs in `backend/api/v1/auth_middleware.py` line 34-36:
```python
user = auth_service.get_user_by_id(str(user_id))
if not user:
    raise HTTPException(status_code=401, detail="User not found. Please sign in again.")
```

**Possible Causes:**
1. **UUID Type Mismatch**: Token contains UUID string, but database query needs UUID object
2. **User Doesn't Exist**: Token was created for a user that no longer exists in database
3. **Database Not Initialized**: Users table is empty (no users created yet)
4. **Token from Different Environment**: Token created in dev, but production database is empty

## Solution

### Fix 1: UUID Type Conversion in get_user_by_id

The `User.id` is a UUID type, but we're querying with a string. Need to convert:

**File:** `backend/services/auth_service.py`

**Current Code:**
```python
def get_user_by_id(self, user_id: str) -> Optional[User]:
    try:
        return self.db.query(User).filter(User.id == user_id).first()
    except Exception:
        return None
```

**Fixed Code:**
```python
def get_user_by_id(self, user_id: str) -> Optional[User]:
    try:
        from uuid import UUID
        # Convert string to UUID if needed
        user_uuid = UUID(user_id) if isinstance(user_id, str) else user_id
        return self.db.query(User).filter(User.id == user_uuid).first()
    except (ValueError, TypeError) as e:
        logger.warning(f"Invalid user_id format: {user_id}, error: {e}")
        return None
    except Exception as e:
        logger.error(f"Error fetching user by id: {e}", exc_info=True)
        return None
```

### Fix 2: Better Error Messages in Middleware

**File:** `backend/api/v1/auth_middleware.py`

Add logging to help debug:

```python
def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    if not authorization:
        raise HTTPException(status_code=401, detail="Authentication required. Please sign in.")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format. Use 'Bearer <token>'")
    
    token = authorization.replace("Bearer ", "").strip()
    
    auth_service = get_auth_service(db)
    payload = auth_service.decode_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token. Please sign in again.")
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload. Please sign in again.")
    
    # Add logging for debugging
    import logging
    logger = logging.getLogger(__name__)
    logger.debug(f"Looking up user with id: {user_id} (type: {type(user_id)})")
    
    user = auth_service.get_user_by_id(str(user_id))
    if not user:
        logger.warning(f"User not found in database for user_id: {user_id}")
        raise HTTPException(status_code=401, detail="User not found. Please sign in again.")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is inactive.")
    
    return user
```

### Fix 3: Frontend Token Check

**File:** `frontend/upload.html`

Add token validation before upload:

```javascript
async function uploadRecord() {
    // Check if token exists
    const authToken = getStorage('authToken');
    if (!authToken) {
        showError('Please sign in first');
        window.location.href = 'login.html';
        return;
    }
    
    // ... rest of upload code
}
```

## Immediate Fix Steps

### Step 1: Fix UUID Query

Update `backend/services/auth_service.py`:

```python
def get_user_by_id(self, user_id: str) -> Optional[User]:
    try:
        from uuid import UUID
        user_uuid = UUID(user_id) if isinstance(user_id, str) else user_id
        return self.db.query(User).filter(User.id == user_uuid).first()
    except (ValueError, TypeError):
        logger.warning(f"Invalid user_id format: {user_id}")
        return None
    except Exception as e:
        logger.error(f"Error fetching user: {e}", exc_info=True)
        return None
```

### Step 2: Verify User Exists

Check if user exists in database:

```python
# In Python shell or debug endpoint
from backend.db import SessionLocal
from backend.models.user import User

db = SessionLocal()
users = db.query(User).all()
print(f"Total users: {len(users)}")
for user in users:
    print(f"User: {user.email}, ID: {user.id}, Active: {user.is_active}")
```

### Step 3: Re-authenticate

If user doesn't exist:
1. Go to `/login.html`
2. Sign in again (creates new user if needed)
3. Get new token
4. Try upload again

## Testing

After fix, test:

1. **Sign in** → Should get token
2. **Check token** → Should decode correctly
3. **Upload** → Should work with valid token
4. **Invalid token** → Should get 401 with clear message

## Debugging Commands

```bash
# Check if users exist
python -c "from backend.db import SessionLocal; from backend.models.user import User; db = SessionLocal(); print(f'Users: {db.query(User).count()}')"

# Decode token manually
python -c "from jose import jwt; import os; token='YOUR_TOKEN'; print(jwt.decode(token, os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production'), algorithms=['HS256']))"
```
