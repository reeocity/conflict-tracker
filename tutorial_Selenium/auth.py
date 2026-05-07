import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict
import bcrypt
import jwt
from dotenv import load_dotenv
from db import connect_db


load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY or len(SECRET_KEY.strip()) < 32:
    raise RuntimeError(
        "JWT_SECRET_KEY must be set and at least 32 characters long"
    )
ALGORITHM = "HS256"
TOKEN_EXPIRE_DAYS = 7


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_user(email: str, password: str) -> Optional[Dict]:
    """Create a new user in the database"""
    conn = None
    try:
        conn = connect_db()
        with conn.cursor() as cur:
            password_hash = hash_password(password)
            cur.execute(
                """
                INSERT INTO users (email, password_hash)
                VALUES (%s, %s)
                RETURNING id, email, created_at;
                """,
                (email, password_hash),
            )
            result = cur.fetchone()
            conn.commit()
            if result:
                return {
                    "id": result[0],
                    "email": result[1],
                    "created_at": result[2].isoformat() if result[2] else None,
                }
    except Exception as e:
        print(f"Error creating user: {e}")
    finally:
        if conn:
            conn.close()
    return None


def get_user_by_email(email: str) -> Optional[Dict]:
    """Get user by email"""
    conn = None
    try:
        conn = connect_db()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, email, password_hash, created_at FROM users WHERE email = %s;",
                (email,),
            )
            result = cur.fetchone()
            if result:
                return {
                    "id": result[0],
                    "email": result[1],
                    "password_hash": result[2],
                    "created_at": result[3],
                }
    except Exception as e:
        print(f"Error getting user: {e}")
    finally:
        if conn:
            conn.close()
    return None


def get_user_by_id(user_id: int) -> Optional[Dict]:
    """Get user by ID"""
    conn = None
    try:
        conn = connect_db()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, email, created_at FROM users WHERE id = %s;",
                (user_id,),
            )
            result = cur.fetchone()
            if result:
                return {
                    "id": result[0],
                    "email": result[1],
                    "created_at": result[2],
                }
    except Exception as e:
        print(f"Error getting user by ID: {e}")
    finally:
        if conn:
            conn.close()
    return None


def create_access_token(user_id: int, email: str) -> str:
    """Create JWT access token"""
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(days=TOKEN_EXPIRE_DAYS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> Optional[Dict]:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def save_user_subscription(user_id: int, country: Optional[str] = None, category: Optional[str] = None) -> Optional[Dict]:
    """Save user alert subscription"""
    conn = None
    try:
        conn = connect_db()
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO user_alert_subscriptions (user_id, country, category)
                VALUES (%s, %s, %s)
                RETURNING id, user_id, country, category, created_at;
                """,
                (user_id, country, category),
            )
            result = cur.fetchone()
            conn.commit()
            if result:
                return {
                    "id": result[0],
                    "user_id": result[1],
                    "country": result[2],
                    "category": result[3],
                    "created_at": result[4].isoformat() if result[4] else None,
                }
    except Exception as e:
        print(f"Error saving subscription: {e}")
    finally:
        if conn:
            conn.close()
    return None


def get_user_subscriptions(user_id: int) -> list:
    """Get all subscriptions for a user"""
    conn = None
    try:
        conn = connect_db()
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, user_id, country, category, created_at
                FROM user_alert_subscriptions
                WHERE user_id = %s
                ORDER BY created_at DESC;
                """,
                (user_id,),
            )
            results = cur.fetchall()
            subscriptions = []
            for row in results:
                subscriptions.append({
                    "id": row[0],
                    "user_id": row[1],
                    "country": row[2],
                    "category": row[3],
                    "created_at": row[4].isoformat() if row[4] else None,
                })
            return subscriptions
    except Exception as e:
        print(f"Error getting subscriptions: {e}")
    finally:
        if conn:
            conn.close()
    return []


def delete_user_subscription(subscription_id: int, user_id: int) -> bool:
    """Delete a user subscription"""
    conn = None
    try:
        conn = connect_db()
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM user_alert_subscriptions WHERE id = %s AND user_id = %s;",
                (subscription_id, user_id),
            )
            conn.commit()
            return cur.rowcount > 0
    except Exception as e:
        print(f"Error deleting subscription: {e}")
    finally:
        if conn:
            conn.close()
    return False
