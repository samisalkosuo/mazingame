"""Flask application for Mazingame web deployment."""

import logging
import os
import sys
from threading import Thread
import time

from flask import Flask, render_template, request, jsonify, session as flask_session
from flask_cors import CORS
from tornado.web import Application as TornadoApplication
from tornado.ioloop import IOLoop
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer

# Add parent directory to path for mazingame imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from web.config import get_config
from web.session_manager import SessionManager
from web.terminal_handler import create_terminal_handlers
from mazingame.highscores import getHighScoreFile
from mazingame.utils import utils

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
config = get_config()
app.config.from_object(config)
config.init_app(app)

# Enable CORS
CORS(app)

# Initialize session manager
session_manager = SessionManager(config)

# Initialize terminal manager and WebSocket handler
terminal_manager, term_socket_class = create_terminal_handlers(config, session_manager)

# Background cleanup task
def cleanup_task():
    """Background task to clean up expired sessions."""
    while True:
        try:
            time.sleep(config.SESSION_CLEANUP_INTERVAL)
            cleaned = session_manager.cleanup_expired_sessions()
            if cleaned > 0:
                logger.info(f"Cleanup task removed {cleaned} expired sessions")
        except Exception as e:
            logger.error(f"Error in cleanup task: {e}", exc_info=True)

# Start cleanup thread
cleanup_thread = Thread(target=cleanup_task, daemon=True)
cleanup_thread.start()
logger.info("Session cleanup task started")


@app.route('/')
def index():
    """Landing page."""
    stats = session_manager.get_stats()
    return render_template('index.html', stats=stats)


@app.route('/terminal')
def terminal():
    """Terminal interface page."""
    # Get client IP
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ',' in client_ip:
        client_ip = client_ip.split(',')[0].strip()
    
    user_agent = request.headers.get('User-Agent', '')
    
    # Create session
    session_id = session_manager.create_session(client_ip, user_agent)
    
    if not session_id:
        return render_template(
            'error.html',
            error_title="Session Limit Reached",
            error_message="Maximum number of concurrent sessions reached. Please try again later."
        ), 503
    
    # Create terminal for session
    terminal_name = terminal_manager.create_terminal(session_id)
    
    if not terminal_name:
        session_manager.remove_session(session_id)
        return render_template(
            'error.html',
            error_title="Terminal Creation Failed",
            error_message="Failed to create terminal session. Please try again."
        ), 500
    
    logger.info(f"New terminal session: {session_id} from {client_ip}")
    
    return render_template(
        'terminal.html',
        session_id=session_id,
        terminal_name=terminal_name,
        ws_url=f"/terminal/{session_id}"
    )


@app.route('/highscores')
def highscores():
    """High scores page."""
    try:
        # Get high scores from database
        dbFile = getHighScoreFile()
        
        if dbFile is None or not os.path.exists(dbFile):
            return render_template('highscores.html', scores=[])
        
        (conn, cursor) = utils.openDatabase(dbFile)
        
        sql = ("select gameid,timestamp,score,level,algorithm,player_name,"
               "elapsed_secs as elapsed_time,moves,shortest_path_moves,"
               "cheat,version,braid,replay_of_gameid,"
               "level as maze_rows, level as maze_cols "
               "from highscores where cheat=0 order by score desc limit 50")
        
        scores = []
        for row in cursor.execute(sql):
            scores.append(dict(row))
        
        utils.closeDatabase(conn)
        
        return render_template('highscores.html', scores=scores)
    except Exception as e:
        logger.error(f"Error loading high scores: {e}", exc_info=True)
        return render_template(
            'error.html',
            error_title="Error Loading High Scores",
            error_message=str(e)
        ), 500


@app.route('/api/session/<session_id>', methods=['GET', 'DELETE'])
def api_session(session_id):
    """Session management API."""
    if request.method == 'GET':
        # Get session info
        session_info = session_manager.get_session(session_id)
        if not session_info:
            return jsonify({'error': 'Session not found'}), 404
        
        return jsonify({
            'session_id': session_info.session_id,
            'age_seconds': session_info.age_seconds(),
            'idle_seconds': session_info.idle_seconds(),
            'terminal_name': session_info.terminal_name
        })
    
    elif request.method == 'DELETE':
        # Terminate session
        session_info = session_manager.get_session(session_id)
        if session_info:
            # Kill terminal
            terminal_manager.cleanup_session_terminal(session_id)
            # Remove session
            session_manager.remove_session(session_id)
            return jsonify({'message': 'Session terminated'})
        return jsonify({'error': 'Session not found'}), 404


@app.route('/api/sessions')
def api_sessions():
    """List all active sessions (admin endpoint)."""
    sessions = session_manager.list_sessions()
    stats = session_manager.get_stats()
    return jsonify({
        'sessions': sessions,
        'stats': stats
    })


@app.route('/api/stats')
def api_stats():
    """Get session statistics."""
    stats = session_manager.get_stats()
    return jsonify(stats)


@app.route('/health')
def health():
    """Health check endpoint."""
    stats = session_manager.get_stats()
    return jsonify({
        'status': 'healthy',
        'active_sessions': stats['total_sessions'],
        'max_sessions': stats['max_sessions']
    })


@app.errorhandler(404)
def not_found(error):
    """404 error handler."""
    return render_template(
        'error.html',
        error_title="Page Not Found",
        error_message="The requested page could not be found."
    ), 404


@app.errorhandler(500)
def internal_error(error):
    """500 error handler."""
    logger.error(f"Internal server error: {error}", exc_info=True)
    return render_template(
        'error.html',
        error_title="Internal Server Error",
        error_message="An unexpected error occurred. Please try again later."
    ), 500


def create_tornado_app():
    """Create Tornado application with WebSocket support."""
    import tornado.web
    
    # Create Flask WSGI container
    flask_app = WSGIContainer(app)
    
    # Create Tornado application with WebSocket route
    tornado_app = TornadoApplication([
        (r'/terminal/([^/]+)', term_socket_class, {'term_manager': terminal_manager}),
        (r'.*', tornado.web.FallbackHandler, {'fallback': flask_app}),
    ])
    
    return tornado_app


def run_server(host='0.0.0.0', port=5000):
    """Run the server with Tornado."""
    
    logger.info(f"Starting Mazingame web server on {host}:{port}")
    logger.info(f"Configuration: {config.__class__.__name__}")
    logger.info(f"Max concurrent sessions: {config.MAX_CONCURRENT_SESSIONS}")
    logger.info(f"Session idle timeout: {config.SESSION_IDLE_TIMEOUT}s")
    
    # Create Tornado app
    tornado_app = create_tornado_app()
    
    # Create HTTP server
    http_server = HTTPServer(tornado_app)
    http_server.listen(port, address=host)
    
    logger.info(f"Server ready at http://{host}:{port}")
    logger.info("Press Ctrl+C to stop")
    
    # Start IOLoop
    try:
        IOLoop.current().start()
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        IOLoop.current().stop()


if __name__ == '__main__':
    # Run with Tornado
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    run_server(host, port)

# Made with Bob
