"""Terminal handler integrating Terminado with Mazingame."""

import logging
import os
import sys
from typing import Optional

from terminado import TermSocket, NamedTermManager
from terminado.management import PtyWithClients
import ptyprocess

logger = logging.getLogger(__name__)


class MazingameTerminalManager(NamedTermManager):
    """Custom terminal manager for Mazingame sessions."""
    
    def __init__(self, config, session_manager, **kwargs):
        """
        Initialize terminal manager.
        
        Args:
            config: Application configuration
            session_manager: SessionManager instance
            **kwargs: Additional arguments for UniqueTermManager
        """
        self.config = config
        self.session_manager = session_manager
        
        # Get the path to mazingame module
        mazingame_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..')
        )
        
        # Prepare shell command to run mazingame
        shell_command = [
            sys.executable,  # Python interpreter
            '-m',
            'mazingame'
        ]
        
        # Store environment for later use
        self.env = os.environ.copy()
        self.env['TERM'] = config.TERM_TYPE
        self.env['MAZINGAME_HIGHSCORE_FILE'] = config.MAZINGAME_HIGHSCORE_FILE
        self.env['PYTHONPATH'] = mazingame_path + os.pathsep + self.env.get('PYTHONPATH', '')
        
        # Initialize parent with configuration
        super().__init__(
            shell_command=shell_command,
            max_terminals=config.MAX_CONCURRENT_SESSIONS,
            **kwargs
        )
        
        logger.info(
            f"MazingameTerminalManager initialized: "
            f"command={' '.join(shell_command)}, "
            f"max_terminals={config.MAX_CONCURRENT_SESSIONS}, "
            f"default_size={config.TERMINAL_ROWS}x{config.TERMINAL_COLS}"
        )
    
    def new_terminal(self, **kwargs):
        """Override to create terminal with correct dimensions."""
        # Extract dimensions
        if 'dimensions' in kwargs:
            dimensions = kwargs.pop('dimensions')
        else:
            rows = kwargs.pop('rows', self.config.TERMINAL_ROWS)
            cols = kwargs.pop('cols', self.config.TERMINAL_COLS)
            dimensions = (rows, cols)
        
        logger.info(f"new_terminal: Creating PTY with dimensions: {dimensions}")
        
        # Get environment
        env = kwargs.pop('env', None) or self.env
        
        # Create PTY process directly with correct dimensions
        from terminado.management import PtyProcessUnicode
        ptyproc = PtyProcessUnicode.spawn(
            self.shell_command,
            dimensions=dimensions,
            env=env
        )
        
        logger.info(f"PTY created with PID {ptyproc.pid}, verifying size...")
        actual_size = ptyproc.getwinsize()
        logger.info(f"Verified PTY size: {actual_size}")
        
        # Create PtyWithClients and set all required attributes
        from collections import deque
        term = PtyWithClients.__new__(PtyWithClients)
        term.ptyproc = ptyproc
        term.clients = []
        term.read_buffer = deque([], maxlen=10)
        logger.info(f"PtyWithClients created successfully with all attributes")
        return term
    
    def new_named_terminal(self, name=None, **kwargs):
        """Override to set default terminal dimensions for named terminals."""
        # Terminado expects 'dimensions' as a tuple (rows, cols)
        if 'dimensions' not in kwargs:
            rows = kwargs.pop('rows', self.config.TERMINAL_ROWS)
            cols = kwargs.pop('cols', self.config.TERMINAL_COLS)
            kwargs['dimensions'] = (rows, cols)
        logger.info(f"new_named_terminal called with name={name}, dimensions={kwargs.get('dimensions')}")
        return super().new_named_terminal(name=name, **kwargs)
    
    def create_terminal(self, session_id: str, **kwargs) -> Optional[str]:
        """
        Create a new terminal for a session.
        
        Args:
            session_id: Session ID from session manager
            **kwargs: Additional terminal creation arguments
            
        Returns:
            Terminal name if created, None otherwise
        """
        try:
            # Check if session exists
            session = self.session_manager.get_session(session_id)
            if not session:
                logger.error(f"Cannot create terminal: session {session_id} not found")
                return None
            
            # Set terminal size from config
            kwargs.setdefault('rows', self.config.TERMINAL_ROWS)
            kwargs.setdefault('cols', self.config.TERMINAL_COLS)
            
            logger.info(f"Creating terminal with command: {self.shell_command}")
            logger.info(f"Environment PYTHONPATH: {self.env.get('PYTHONPATH')}")
            logger.info(f"Terminal size: {kwargs.get('rows')}x{kwargs.get('cols')}")
            
            # Create a named terminal with session_id as the name
            # new_named_terminal returns (name, PtyWithClients)
            result = self.new_named_terminal(name=session_id, env=self.env, **kwargs)
            
            logger.info(f"Terminal creation result: {result}")
            
            # Unpack the result
            if isinstance(result, tuple):
                term_name, term = result
                logger.info(f"Terminal name: {term_name}, Terminal object: {term}")
            else:
                term = result
                logger.warning(f"Unexpected result type from new_named_terminal: {type(result)}")
            
            # Verify actual PTY size
            if hasattr(term, 'ptyproc'):
                logger.info(f"Terminal PID: {term.ptyproc.pid}")
                if hasattr(term.ptyproc, 'getwinsize'):
                    actual_size = term.ptyproc.getwinsize()
                    logger.info(f"Actual PTY size after creation: {actual_size}")
                else:
                    logger.warning("ptyproc exists but getwinsize not available")
            else:
                logger.warning("Terminal object has no ptyproc attribute")
            
            # Store terminal name in session
            self.session_manager.set_terminal_name(session_id, session_id)
            
            logger.info(
                f"Terminal created for session {session_id} "
                f"(size: {kwargs.get('rows')}x{kwargs.get('cols')})"
            )
            
            return session_id
            
        except Exception as e:
            logger.error(f"Error creating terminal for session {session_id}: {e}", exc_info=True)
            return None
    
    def kill_terminal(self, session_id: str):
        """Kill a terminal and clean up."""
        try:
            if session_id in self.terminals:
                term = self.terminals[session_id]
                term.kill()
                self.kill(session_id)  # Use parent's kill method
                logger.info(f"Terminal killed for session: {session_id}")
        except Exception as e:
            logger.error(f"Error killing terminal for session {session_id}: {e}", exc_info=True)
    
    def cleanup_session_terminal(self, session_id: str):
        """Clean up terminal associated with a session."""
        self.kill_terminal(session_id)


class MazingameTermSocket(TermSocket):
    """Custom WebSocket handler for Mazingame terminals."""
    
    def __init__(self, *args, **kwargs):
        """Initialize terminal WebSocket."""
        self.session_manager = kwargs.pop('session_manager', None)
        super().__init__(*args, **kwargs)
    
    def open(self, url_component=None):
        """Handle WebSocket connection open."""
        # Extract session ID from URL
        session_id = url_component
        
        if not session_id:
            logger.error("No session ID provided in WebSocket connection")
            self.close()
            return
        
        # Verify session exists
        if self.session_manager:
            session = self.session_manager.get_session(session_id)
            if not session:
                logger.error(f"Invalid session ID: {session_id}")
                self.close()
                return
            
            # Update session activity
            self.session_manager.update_activity(session_id)
        
        # Store session_id for later use
        self.session_id = session_id
        
        logger.info(f"WebSocket opened for session: {session_id}")
        
        # Call parent's open with session_id as the terminal name
        # This will properly connect to the terminal
        super().open(session_id)
    
    def on_message(self, message):
        """Handle incoming WebSocket message."""
        # Update session activity on each message
        if self.session_manager and hasattr(self, 'term_name'):
            # Find session by terminal name
            for session_id, session in self.session_manager.sessions.items():
                if session.terminal_name == self.term_name:
                    self.session_manager.update_activity(session_id)
                    break
        
        # Pass message to parent handler
        super().on_message(message)
    
    def on_close(self):
        """Handle WebSocket connection close."""
        logger.info(f"WebSocket closed for terminal: {getattr(self, 'term_name', 'unknown')}")
        super().on_close()


def create_terminal_handlers(config, session_manager):
    """
    Create terminal manager and WebSocket handler.
    
    Args:
        config: Application configuration
        session_manager: SessionManager instance
        
    Returns:
        Tuple of (terminal_manager, websocket_handler_class)
    """
    # Create terminal manager
    terminal_manager = MazingameTerminalManager(config, session_manager)
    
    # Create WebSocket handler class with injected dependencies
    class ConfiguredTermSocket(MazingameTermSocket):
        def __init__(self, *args, **kwargs):
            kwargs['session_manager'] = session_manager
            super().__init__(*args, **kwargs)
    
    return terminal_manager, ConfiguredTermSocket

# Made with Bob
