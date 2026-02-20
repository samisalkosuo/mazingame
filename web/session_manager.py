"""Session management for concurrent Mazingame users."""

import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional, Set
from threading import Lock

logger = logging.getLogger(__name__)


@dataclass
class SessionInfo:
    """Information about an active session."""
    session_id: str
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    client_ip: str = ""
    terminal_name: Optional[str] = None
    user_agent: str = ""
    
    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = time.time()
    
    def is_idle(self, timeout: int) -> bool:
        """Check if session has been idle for longer than timeout seconds."""
        return (time.time() - self.last_activity) > timeout
    
    def is_expired(self, timeout: int) -> bool:
        """Check if session has existed longer than absolute timeout seconds."""
        return (time.time() - self.created_at) > timeout
    
    def age_seconds(self) -> float:
        """Get session age in seconds."""
        return time.time() - self.created_at
    
    def idle_seconds(self) -> float:
        """Get idle time in seconds."""
        return time.time() - self.last_activity


class SessionManager:
    """Manages terminal sessions for multiple concurrent users."""
    
    def __init__(self, config):
        """Initialize session manager with configuration."""
        self.config = config
        self.sessions: Dict[str, SessionInfo] = {}
        self.ip_sessions: Dict[str, Set[str]] = {}  # IP -> set of session IDs
        self.lock = Lock()
        
        logger.info(
            f"SessionManager initialized: "
            f"max_sessions={config.MAX_CONCURRENT_SESSIONS}, "
            f"max_per_ip={config.MAX_SESSIONS_PER_IP}, "
            f"idle_timeout={config.SESSION_IDLE_TIMEOUT}s"
        )
    
    def create_session(self, client_ip: str, user_agent: str = "") -> Optional[str]:
        """
        Create a new session if limits allow.
        
        Returns:
            Session ID if created, None if limits exceeded
        """
        with self.lock:
            # Check global session limit
            if len(self.sessions) >= self.config.MAX_CONCURRENT_SESSIONS:
                logger.warning(
                    f"Global session limit reached: {len(self.sessions)}/{self.config.MAX_CONCURRENT_SESSIONS}"
                )
                return None
            
            # Check per-IP session limit
            ip_session_count = len(self.ip_sessions.get(client_ip, set()))
            if ip_session_count >= self.config.MAX_SESSIONS_PER_IP:
                logger.warning(
                    f"Per-IP session limit reached for {client_ip}: "
                    f"{ip_session_count}/{self.config.MAX_SESSIONS_PER_IP}"
                )
                return None
            
            # Create new session
            session_id = str(uuid.uuid4())
            session_info = SessionInfo(
                session_id=session_id,
                client_ip=client_ip,
                user_agent=user_agent
            )
            
            self.sessions[session_id] = session_info
            
            # Track by IP
            if client_ip not in self.ip_sessions:
                self.ip_sessions[client_ip] = set()
            self.ip_sessions[client_ip].add(session_id)
            
            logger.info(
                f"Session created: {session_id} for {client_ip} "
                f"(total: {len(self.sessions)}, ip_sessions: {ip_session_count + 1})"
            )
            
            return session_id
    
    def get_session(self, session_id: str) -> Optional[SessionInfo]:
        """Get session information."""
        with self.lock:
            return self.sessions.get(session_id)
    
    def update_activity(self, session_id: str) -> bool:
        """
        Update session activity timestamp.
        
        Returns:
            True if session exists, False otherwise
        """
        with self.lock:
            session = self.sessions.get(session_id)
            if session:
                session.update_activity()
                return True
            return False
    
    def set_terminal_name(self, session_id: str, terminal_name: str):
        """Associate terminal name with session."""
        with self.lock:
            session = self.sessions.get(session_id)
            if session:
                session.terminal_name = terminal_name
                logger.debug(f"Terminal {terminal_name} associated with session {session_id}")
    
    def remove_session(self, session_id: str) -> bool:
        """
        Remove a session.
        
        Returns:
            True if session was removed, False if not found
        """
        with self.lock:
            session = self.sessions.get(session_id)
            if not session:
                return False
            
            # Remove from IP tracking
            if session.client_ip in self.ip_sessions:
                self.ip_sessions[session.client_ip].discard(session_id)
                if not self.ip_sessions[session.client_ip]:
                    del self.ip_sessions[session.client_ip]
            
            # Remove session
            del self.sessions[session_id]
            
            logger.info(
                f"Session removed: {session_id} "
                f"(age: {session.age_seconds():.1f}s, total: {len(self.sessions)})"
            )
            
            return True
    
    def cleanup_expired_sessions(self) -> int:
        """
        Remove idle and expired sessions.
        
        Returns:
            Number of sessions cleaned up
        """
        with self.lock:
            expired_sessions = []
            
            for session_id, session in self.sessions.items():
                # Check absolute timeout
                if session.is_expired(self.config.SESSION_ABSOLUTE_TIMEOUT):
                    expired_sessions.append((session_id, 'absolute_timeout'))
                    continue
                
                # Check idle timeout
                if session.is_idle(self.config.SESSION_IDLE_TIMEOUT):
                    expired_sessions.append((session_id, 'idle_timeout'))
            
            # Remove expired sessions
            for session_id, reason in expired_sessions:
                session = self.sessions.get(session_id)
                if session:
                    logger.info(
                        f"Cleaning up session {session_id} due to {reason} "
                        f"(age: {session.age_seconds():.1f}s, idle: {session.idle_seconds():.1f}s)"
                    )
                    self.remove_session(session_id)
            
            if expired_sessions:
                logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
            
            return len(expired_sessions)
    
    def get_stats(self) -> Dict:
        """Get session statistics."""
        with self.lock:
            return {
                'total_sessions': len(self.sessions),
                'unique_ips': len(self.ip_sessions),
                'max_sessions': self.config.MAX_CONCURRENT_SESSIONS,
                'max_per_ip': self.config.MAX_SESSIONS_PER_IP,
                'sessions_by_ip': {ip: len(sessions) for ip, sessions in self.ip_sessions.items()},
            }
    
    def list_sessions(self) -> list:
        """Get list of all active sessions with details."""
        with self.lock:
            return [
                {
                    'session_id': session.session_id,
                    'client_ip': session.client_ip,
                    'created_at': datetime.fromtimestamp(session.created_at).isoformat(),
                    'age_seconds': session.age_seconds(),
                    'idle_seconds': session.idle_seconds(),
                    'terminal_name': session.terminal_name,
                }
                for session in self.sessions.values()
            ]

# Made with Bob
