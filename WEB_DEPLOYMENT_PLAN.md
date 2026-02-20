# Mazingame Web Deployment Plan

## Overview
Transform the terminal-based Mazingame into a browser-accessible application using Flask, Terminado, and xterm.js, supporting multiple concurrent users with session management.

## Architecture Design

### Technology Stack

#### Backend
- **Flask**: Lightweight web framework for HTTP routing and session management
- **Terminado**: Tornado-based library providing terminal emulation via WebSockets
- **ptyprocess**: Process management for terminal sessions (dependency of terminado)

#### Frontend
- **xterm.js**: JavaScript terminal emulator for rendering in browser
- **xterm-addon-fit**: Auto-resize terminal to fit container
- **xterm-addon-web-links**: Optional - clickable links in terminal
- **Plain HTML/CSS/JavaScript**: No heavy frameworks needed

#### Infrastructure
- **Docker**: Containerized deployment
- **Nginx** (optional): Reverse proxy for production
- **Redis** (future): Session storage for multi-tenant scaling

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Browser Client                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  HTML/CSS/JavaScript Frontend                          │ │
│  │  - xterm.js terminal renderer                          │ │
│  │  - WebSocket connection manager                        │ │
│  │  - Session UI controls                                 │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ WebSocket (ws://)
                            │
┌─────────────────────────────────────────────────────────────┐
│                      Flask Web Server                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Flask Routes                                          │ │
│  │  - / (index page)                                      │ │
│  │  - /terminal (WebSocket endpoint via Terminado)       │ │
│  │  - /highscores (view scores)                          │ │
│  │  - /api/session (session management)                  │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Terminado Terminal Manager                            │ │
│  │  - Creates PTY for each session                        │ │
│  │  - Manages WebSocket connections                       │ │
│  │  - Handles terminal I/O                                │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Session Manager                                       │ │
│  │  - Track active sessions                               │ │
│  │  - Cleanup idle/disconnected sessions                  │ │
│  │  - Resource limits per user                            │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ PTY
                            │
┌─────────────────────────────────────────────────────────────┐
│              Mazingame Terminal Processes                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ Session 1│  │ Session 2│  │ Session N│  ...             │
│  │ python   │  │ python   │  │ python   │                  │
│  │ mazingame│  │ mazingame│  │ mazingame│                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
mazingame/
├── web/                          # New web application directory
│   ├── __init__.py
│   ├── app.py                    # Flask application entry point
│   ├── config.py                 # Configuration management
│   ├── session_manager.py        # Session lifecycle management
│   ├── terminal_handler.py       # Terminado integration
│   ├── static/                   # Static assets
│   │   ├── css/
│   │   │   └── style.css         # Terminal styling
│   │   ├── js/
│   │   │   ├── xterm.min.js      # xterm.js library
│   │   │   ├── xterm-addon-fit.min.js
│   │   │   └── terminal.js       # WebSocket & terminal logic
│   │   └── favicon.ico
│   ├── templates/                # Jinja2 templates
│   │   ├── base.html             # Base template
│   │   ├── index.html            # Landing page
│   │   ├── terminal.html         # Terminal interface
│   │   └── highscores.html       # High scores display
│   └── requirements-web.txt      # Web-specific dependencies
├── Dockerfile.web                # Web deployment Dockerfile
├── docker-compose.yml            # Multi-container orchestration
└── WEB_DEPLOYMENT_PLAN.md        # This document
```

## Key Implementation Details

### 1. Flask Application Setup

**Dependencies** (`web/requirements-web.txt`):
```
Flask>=3.0.0
terminado>=0.18.0
tornado>=6.4
ptyprocess>=0.7.0
```

**Core Flask App** (`web/app.py`):
- Initialize Flask with session support
- Configure Terminado terminal manager
- Set up WebSocket routes
- Implement session cleanup background task
- Add health check endpoint

### 2. Terminado Integration

**Terminal Handler** (`web/terminal_handler.py`):
- Create custom terminal manager extending `terminado.TerminalManager`
- Configure shell command to launch mazingame: `["python", "-m", "mazingame"]`
- Set terminal size (rows=24, cols=80 or configurable)
- Handle terminal lifecycle (create, connect, disconnect, cleanup)
- Implement timeout for idle sessions (e.g., 30 minutes)

**WebSocket Endpoint**:
- Route: `/terminal/<session_id>`
- Upgrade HTTP to WebSocket
- Bind terminal I/O to WebSocket messages
- Handle connection errors gracefully

### 3. Session Management

**Session Manager** (`web/session_manager.py`):
- Generate unique session IDs (UUID4)
- Track active sessions with metadata:
  - Session ID
  - Creation timestamp
  - Last activity timestamp
  - Terminal PID
  - User identifier (IP or future auth token)
- Implement session limits:
  - Max concurrent sessions per IP (e.g., 3)
  - Max total concurrent sessions (e.g., 50)
  - Idle timeout (30 minutes)
  - Absolute timeout (2 hours)
- Background cleanup task (runs every 5 minutes)
- Graceful session termination

### 4. Frontend Implementation

**Terminal Interface** (`templates/terminal.html`):
```html
<!DOCTYPE html>
<html>
<head>
    <title>Mazingame - Terminal</title>
    <link rel="stylesheet" href="/static/css/xterm.css">
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <div id="terminal-container">
        <div id="terminal"></div>
    </div>
    <div id="controls">
        <button id="new-game">New Game</button>
        <button id="disconnect">Disconnect</button>
    </div>
    <script src="/static/js/xterm.min.js"></script>
    <script src="/static/js/xterm-addon-fit.min.js"></script>
    <script src="/static/js/terminal.js"></script>
</body>
</html>
```

**Terminal JavaScript** (`static/js/terminal.js`):
- Initialize xterm.js terminal
- Establish WebSocket connection to `/terminal/<session_id>`
- Handle terminal input/output
- Implement auto-reconnect logic
- Handle window resize events
- Send keepalive pings

### 5. High Scores Integration

**High Scores Endpoint** (`/highscores`):
- Read from shared SQLite database
- Display top scores in HTML table
- Support filtering by maze size/algorithm
- Real-time updates (optional: WebSocket or polling)

**Database Considerations**:
- Mount shared volume for `/data` directory
- Handle concurrent access (SQLite WAL mode)
- Consider read-only access for web display

### 6. Docker Configuration

**Web Dockerfile** (`Dockerfile.web`):
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libncurses5-dev \
    libncursesw5-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy application
COPY mazingame/ ./mazingame/
COPY web/ ./web/
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir -e . && \
    pip install --no-cache-dir -r web/requirements-web.txt

# Create data directory
RUN mkdir -p /data

VOLUME ["/data"]

EXPOSE 5000

ENV FLASK_APP=web.app
ENV MAZINGAME_HIGHSCORE_FILE=/data/mazingame_highscores.sqlite

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
```

**Docker Compose** (`docker-compose.yml`):
```yaml
version: '3.8'

services:
  mazingame-web:
    build:
      context: .
      dockerfile: Dockerfile.web
    ports:
      - "5000:5000"
    volumes:
      - ./data:/data
    environment:
      - FLASK_ENV=production
      - MAZINGAME_HIGHSCORE_FILE=/data/mazingame_highscores.sqlite
      - MAX_CONCURRENT_SESSIONS=50
      - SESSION_TIMEOUT=1800
    restart: unless-stopped
```

## Key Considerations & Recommendations

### Security

1. **Rate Limiting**
   - Limit session creation per IP (e.g., 3 sessions per IP)
   - Implement request rate limiting (Flask-Limiter)
   - Add CAPTCHA for production (optional)

2. **Input Validation**
   - Sanitize all user inputs
   - Validate session IDs (UUID format)
   - Prevent command injection in terminal

3. **Resource Limits**
   - Set memory limits per container
   - Limit CPU usage per terminal process
   - Implement max concurrent sessions

4. **HTTPS/WSS**
   - Use Nginx reverse proxy with SSL in production
   - Upgrade WebSocket to WSS (secure WebSocket)
   - Implement CORS policies

### Performance

1. **Connection Management**
   - Use connection pooling
   - Implement WebSocket keepalive
   - Handle reconnection gracefully

2. **Resource Cleanup**
   - Automatic cleanup of orphaned processes
   - Monitor memory usage
   - Log session metrics

3. **Scaling Considerations**
   - Stateless Flask app (session data in Redis for future)
   - Load balancer support (sticky sessions)
   - Horizontal scaling with shared storage

### User Experience

1. **Terminal Rendering**
   - Proper TERM environment variable (xterm-256color)
   - Handle terminal resize events
   - Smooth scrolling and rendering

2. **Session Persistence**
   - Save session state on disconnect (future)
   - Allow reconnection to existing session
   - Display session timeout warnings

3. **Error Handling**
   - Graceful degradation on connection loss
   - Clear error messages
   - Automatic retry logic

### Monitoring & Logging

1. **Metrics to Track**
   - Active sessions count
   - Session duration statistics
   - Connection errors
   - Resource usage per session

2. **Logging**
   - Structured logging (JSON format)
   - Log levels: DEBUG, INFO, WARNING, ERROR
   - Separate logs for access and application

3. **Health Checks**
   - `/health` endpoint for monitoring
   - Check terminal manager status
   - Database connectivity check

## Future Enhancements (Multi-Tenant Path)

### Phase 2: Authentication & User Accounts
- User registration and login
- OAuth integration (Google, GitHub)
- Personal high score tracking
- Game history per user

### Phase 3: Advanced Features
- Multiplayer/spectator mode
- Tournament system
- Leaderboards with filters
- Game replay viewer in browser
- Custom maze configurations per user

### Phase 4: Scaling
- Redis for session storage
- PostgreSQL for user data
- Kubernetes deployment
- CDN for static assets
- WebSocket load balancing

## Testing Strategy

1. **Unit Tests**
   - Session manager logic
   - Terminal handler
   - Configuration management

2. **Integration Tests**
   - WebSocket connection flow
   - Terminal I/O handling
   - Database operations

3. **Load Tests**
   - Concurrent session handling
   - Memory leak detection
   - Connection stability under load

4. **Manual Testing**
   - Cross-browser compatibility (Chrome, Firefox, Safari, Edge)
   - Mobile browser support
   - Network interruption handling

## Deployment Checklist

- [ ] Set up production environment variables
- [ ] Configure SSL certificates (Let's Encrypt)
- [ ] Set up Nginx reverse proxy
- [ ] Configure firewall rules
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Configure log aggregation
- [ ] Set up automated backups for high scores
- [ ] Create deployment documentation
- [ ] Test disaster recovery procedures
- [ ] Set up CI/CD pipeline

## Estimated Timeline

- **Phase 1: Basic Implementation** (1-2 weeks)
  - Flask app skeleton
  - Terminado integration
  - Basic frontend with xterm.js
  - Session management

- **Phase 2: Polish & Testing** (1 week)
  - Error handling
  - UI improvements
  - Load testing
  - Documentation

- **Phase 3: Deployment** (3-5 days)
  - Docker configuration
  - Production setup
  - Monitoring
  - Documentation

**Total: 3-4 weeks for production-ready web deployment**

## Resources & References

### Documentation
- [Terminado GitHub](https://github.com/jupyter/terminado)
- [xterm.js Documentation](https://xtermjs.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [WebSocket Protocol](https://datatracker.ietf.org/doc/html/rfc6455)

### Example Projects
- Jupyter Terminal (uses terminado)
- Wetty (web terminal)
- ttyd (terminal over HTTP)

### Libraries
- `flask-cors`: CORS handling
- `flask-limiter`: Rate limiting
- `python-dotenv`: Environment management
- `gunicorn`: Production WSGI server

## Conclusion

This plan provides a solid foundation for deploying Mazingame as a web service with support for multiple concurrent users. The architecture is designed to be:

1. **Scalable**: Easy to add more capacity
2. **Maintainable**: Clear separation of concerns
3. **Extensible**: Ready for multi-tenant features
4. **Secure**: Built-in security considerations
5. **User-friendly**: Smooth browser experience

The Flask + Terminado + xterm.js stack is proven, well-documented, and suitable for both demo purposes and production deployment.