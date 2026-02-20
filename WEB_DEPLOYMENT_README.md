# Mazingame Web Deployment

Browser-based terminal interface for Mazingame using Flask, Terminado, and xterm.js.

## Quick Start

### Using Docker Compose (Recommended)

1. **Build and start the service:**
   ```bash
   docker-compose up -d
   ```

2. **Access the application:**
   Open your browser and navigate to: `http://localhost:5000`

3. **Stop the service:**
   ```bash
   docker-compose down
   ```

### Using Docker

1. **Build the image:**
   ```bash
   docker build -f Dockerfile.web -t mazingame-web .
   ```

2. **Run the container:**
   ```bash
   docker run -d -p 5000:5000 -v $(pwd)/data:/data --name mazingame-web mazingame-web
   ```

3. **Access the application:**
   Open your browser and navigate to: `http://localhost:5000`

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r web/requirements-web.txt
   pip install -e .
   ```

2. **Run the application:**
   ```bash
   python -m web.app
   ```
   
   Or using Flask CLI:
   ```bash
   export FLASK_APP=web.app
   export FLASK_ENV=development
   flask run --host=0.0.0.0 --port=5000
   ```

3. **Access the application:**
   Open your browser and navigate to: `http://localhost:5000`

## Configuration

### Environment Variables

Configure the application using environment variables:

#### Flask Settings
- `SECRET_KEY`: Flask secret key (default: 'dev-secret-key-change-in-production')
- `FLASK_ENV`: Environment mode - 'development' or 'production' (default: 'production')
- `FLASK_DEBUG`: Enable debug mode - 'true' or 'false' (default: 'false')

#### Session Management
- `MAX_CONCURRENT_SESSIONS`: Maximum total concurrent sessions (default: 50)
- `MAX_SESSIONS_PER_IP`: Maximum sessions per IP address (default: 3)
- `SESSION_TIMEOUT`: Idle timeout in seconds (default: 1800 = 30 minutes)
- `SESSION_ABSOLUTE_TIMEOUT`: Absolute session timeout in seconds (default: 7200 = 2 hours)
- `SESSION_CLEANUP_INTERVAL`: Cleanup task interval in seconds (default: 300 = 5 minutes)

#### Terminal Settings
- `TERMINAL_ROWS`: Terminal height in rows (default: 24)
- `TERMINAL_COLS`: Terminal width in columns (default: 80)
- `TERM_TYPE`: Terminal type (default: 'xterm-256color')

#### Data Storage
- `MAZINGAME_HIGHSCORE_FILE`: Path to SQLite database (default: '/data/mazingame_highscores.sqlite')
- `MAZINGAME_DATA_DIR`: Data directory path (default: '/data')

#### Logging
- `LOG_LEVEL`: Logging level - DEBUG, INFO, WARNING, ERROR (default: 'INFO')

### Example .env File

Create a `.env` file in the project root:

```env
# Production settings
SECRET_KEY=your-super-secret-key-here
FLASK_ENV=production

# Session limits
MAX_CONCURRENT_SESSIONS=100
MAX_SESSIONS_PER_IP=5
SESSION_TIMEOUT=1800

# Terminal size
TERMINAL_ROWS=30
TERMINAL_COLS=100

# Logging
LOG_LEVEL=INFO
```

Then use with docker-compose:
```bash
docker-compose --env-file .env up -d
```

## Architecture

### Components

1. **Flask Web Server**: HTTP routing and session management
2. **Terminado**: WebSocket-based terminal emulation
3. **xterm.js**: Browser-based terminal renderer
4. **Session Manager**: Concurrent user session tracking
5. **Terminal Handler**: PTY process management

### Directory Structure

```
web/
├── __init__.py              # Package initialization
├── app.py                   # Flask application entry point
├── config.py                # Configuration management
├── session_manager.py       # Session lifecycle management
├── terminal_handler.py      # Terminado integration
├── requirements-web.txt     # Python dependencies
├── static/                  # Static assets (CSS, JS)
│   ├── css/
│   └── js/
└── templates/               # Jinja2 HTML templates
    ├── base.html           # Base template
    ├── index.html          # Landing page
    ├── terminal.html       # Terminal interface
    ├── highscores.html     # High scores display
    └── error.html          # Error page
```

## API Endpoints

### Web Pages
- `GET /` - Landing page with game information
- `GET /terminal` - Create new terminal session and display interface
- `GET /highscores` - Display high scores
- `GET /health` - Health check endpoint

### API Routes
- `GET /api/session/<session_id>` - Get session information
- `DELETE /api/session/<session_id>` - Terminate a session
- `GET /api/sessions` - List all active sessions (admin)
- `GET /api/stats` - Get session statistics

### WebSocket
- `WS /terminal/<session_id>` - WebSocket connection for terminal I/O

## Usage

### Playing the Game

1. Navigate to `http://localhost:5000`
2. Click "Start Playing Now!" or go to `/terminal`
3. A new terminal session will be created
4. Use arrow keys or WASD to navigate the maze
5. Press 'q' to quit the current game
6. Click "Disconnect" to end your session

### Viewing High Scores

1. Navigate to `/highscores`
2. View top scores with filtering options
3. Filter by maze size or generation algorithm

### Session Management

Sessions are automatically managed:
- Maximum 3 sessions per IP address (configurable)
- Sessions expire after 30 minutes of inactivity
- Absolute timeout of 2 hours per session
- Automatic cleanup every 5 minutes

## Monitoring

### Health Check

Check application health:
```bash
curl http://localhost:5000/health
```

Response:
```json
{
  "status": "healthy",
  "active_sessions": 5,
  "max_sessions": 50
}
```

### Session Statistics

Get current session statistics:
```bash
curl http://localhost:5000/api/stats
```

Response:
```json
{
  "total_sessions": 5,
  "unique_ips": 3,
  "max_sessions": 50,
  "max_per_ip": 3,
  "sessions_by_ip": {
    "192.168.1.100": 2,
    "192.168.1.101": 3
  }
}
```

### Logs

View application logs:
```bash
# Docker Compose
docker-compose logs -f mazingame-web

# Docker
docker logs -f mazingame-web

# Local
tail -f logs/mazingame-web.log
```

## Production Deployment

### Using Nginx Reverse Proxy

1. **Install Nginx:**
   ```bash
   sudo apt-get install nginx
   ```

2. **Configure Nginx** (`/etc/nginx/sites-available/mazingame`):
   ```nginx
   upstream mazingame {
       server localhost:5000;
   }

   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://mazingame;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

3. **Enable site and restart Nginx:**
   ```bash
   sudo ln -s /etc/nginx/sites-available/mazingame /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

### SSL/TLS with Let's Encrypt

1. **Install Certbot:**
   ```bash
   sudo apt-get install certbot python3-certbot-nginx
   ```

2. **Obtain certificate:**
   ```bash
   sudo certbot --nginx -d your-domain.com
   ```

3. **Auto-renewal:**
   ```bash
   sudo certbot renew --dry-run
   ```

### Systemd Service

Create `/etc/systemd/system/mazingame-web.service`:

```ini
[Unit]
Description=Mazingame Web Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/mazingame
Environment="FLASK_ENV=production"
Environment="SECRET_KEY=your-secret-key"
ExecStart=/usr/bin/python3 -m web.app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable mazingame-web
sudo systemctl start mazingame-web
sudo systemctl status mazingame-web
```

## Troubleshooting

### Common Issues

1. **WebSocket connection fails:**
   - Check firewall rules allow port 5000
   - Verify WebSocket upgrade headers in proxy configuration
   - Check browser console for errors

2. **Session limit reached:**
   - Increase `MAX_CONCURRENT_SESSIONS` or `MAX_SESSIONS_PER_IP`
   - Check for orphaned sessions: `curl http://localhost:5000/api/sessions`
   - Restart service to clear all sessions

3. **Terminal not rendering:**
   - Verify xterm.js CDN is accessible
   - Check browser console for JavaScript errors
   - Try different browser

4. **High scores not displaying:**
   - Check database file exists and is writable
   - Verify `MAZINGAME_HIGHSCORE_FILE` path
   - Check file permissions

### Debug Mode

Enable debug mode for development:
```bash
export FLASK_ENV=development
export FLASK_DEBUG=true
python -m web.app
```

### Checking Logs

```bash
# Application logs
docker-compose logs -f

# Specific service
docker-compose logs -f mazingame-web

# Last 100 lines
docker-compose logs --tail=100 mazingame-web
```

## Security Considerations

1. **Change default secret key** in production
2. **Use HTTPS/WSS** for production deployment
3. **Implement rate limiting** for session creation
4. **Set appropriate session limits** based on server capacity
5. **Regular security updates** for dependencies
6. **Monitor resource usage** to prevent DoS
7. **Use firewall rules** to restrict access if needed

## Performance Tuning

### Increase Session Limits

For high-traffic deployments:
```yaml
environment:
  - MAX_CONCURRENT_SESSIONS=200
  - MAX_SESSIONS_PER_IP=10
```

### Optimize Terminal Size

Smaller terminals use less resources:
```yaml
environment:
  - TERMINAL_ROWS=20
  - TERMINAL_COLS=60
```

### Adjust Cleanup Interval

More frequent cleanup for busy servers:
```yaml
environment:
  - SESSION_CLEANUP_INTERVAL=120  # 2 minutes
```

## Support

- **GitHub Issues**: https://github.com/samisalkosuo/mazingame/issues
- **Documentation**: See WEB_DEPLOYMENT_PLAN.md for architecture details
- **Original Project**: https://github.com/samisalkosuo/mazingame

## License

MIT License - see LICENSE file for details.