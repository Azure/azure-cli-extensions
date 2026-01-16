# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import platform
import signal
import struct
import sys
import threading
import time
from typing import List, Optional, Tuple

from azext_aks_agent._consts import AGENT_NAMESPACE, HEARTBEAT_INTERVAL, RESIZE_CHANNEL
from knack.log import get_logger
from kubernetes import client, config
from kubernetes.stream import stream

# Platform-specific imports
IS_WINDOWS = platform.system() == 'Windows'

if not IS_WINDOWS:
    import fcntl
    import select
    import termios
else:
    # Windows doesn't have fcntl, select, or termios
    fcntl = None
    select = None
    termios = None

logger = get_logger(__name__)

# WebSocket buffer size - matches Kubernetes client-go implementation
# Reference: https://github.com/kubernetes/client-go/blob/master/transport/websocket/roundtripper.go#L67
WEBSOCKET_BUFFER_SIZE = 32 * 1024  # 32 KiB


def _get_terminal_size() -> Tuple[int, int]:
    """
    Get current terminal size.

    Returns:
        Tuple of (rows, cols)
    """
    try:
        if IS_WINDOWS:
            # Windows-specific terminal size detection
            import shutil
            size = shutil.get_terminal_size(fallback=(80, 24))
            return size.lines, size.columns

        # Unix/Linux terminal size detection
        size_struct = struct.pack('HHHH', 0, 0, 0, 0)
        result = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, size_struct)
        rows, cols, _, _ = struct.unpack('HHHH', result)
        return rows, cols
    except (OSError, IOError, ImportError, AttributeError):
        # Fallback to environment variables or defaults
        return int(os.environ.get('LINES', 24)), int(os.environ.get('COLUMNS', 80))


def _send_terminal_size(exec_stream, rows, cols):
    """
    Send terminal size to pod via WebSocket channel.

    Args:
        exec_stream: The WebSocket stream object
        rows: Terminal height
        cols: Terminal width
    """
    try:
        resize_message = json.dumps({
            "Width": cols,
            "Height": rows
        })
        exec_stream.write_channel(RESIZE_CHANNEL, resize_message)
        logger.debug("Terminal resized to %dx%d", cols, rows)
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.debug("Failed to send terminal size: %s", e)


def _monitor_resize_events_windows(exec_stream, stop_event):
    """
    Monitor terminal resize events on Windows by polling.
    Implementation based on Kubernetes kubectl.
    Reference: https://github.com/kubernetes/kubernetes/blob/master/staging/src/k8s.io/kubectl/pkg/util/term/resizeevents_windows.go  # pylint: disable=line-too-long

    Args:
        exec_stream: The WebSocket stream object
        stop_event: Threading event to stop monitoring
    """
    last_size = _get_terminal_size()

    while not stop_event.is_set() and exec_stream.is_open():
        try:
            current_size = _get_terminal_size()
            if current_size != last_size:
                _send_terminal_size(exec_stream, current_size[0], current_size[1])
                last_size = current_size
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.debug("Error monitoring terminal size: %s", e)
            break

        # Sleep to avoid hot looping (same interval as kubectl)
        stop_event.wait(0.25)


def _set_terminal_raw_mode():
    """
    Set terminal to raw mode and return state for restoration.
    Implementation based on moby/term.

    Returns:
        Tuple of (fd, old_settings) for Unix/Linux or (stdin_handle, old_mode) for Windows
    """
    if IS_WINDOWS:
        # Windows raw mode implementation
        # Reference: https://github.com/moby/term/blob/main/termios_windows.go
        import ctypes
        from ctypes import wintypes

        kernel32 = ctypes.windll.kernel32

        # Get stdin handle
        STD_INPUT_HANDLE = -10
        stdin_handle = kernel32.GetStdHandle(STD_INPUT_HANDLE)

        # Save current console mode
        old_mode = wintypes.DWORD()
        kernel32.GetConsoleMode(stdin_handle, ctypes.byref(old_mode))

        # Console mode flags
        ENABLE_ECHO_INPUT = 0x0004
        ENABLE_LINE_INPUT = 0x0002
        ENABLE_MOUSE_INPUT = 0x0010
        ENABLE_WINDOW_INPUT = 0x0008
        ENABLE_PROCESSED_INPUT = 0x0001
        ENABLE_EXTENDED_FLAGS = 0x0080
        ENABLE_INSERT_MODE = 0x0020
        ENABLE_QUICK_EDIT_MODE = 0x0040
        ENABLE_VIRTUAL_TERMINAL_INPUT = 0x0200

        # Disable these modes
        new_mode = old_mode.value
        new_mode &= ~ENABLE_ECHO_INPUT
        new_mode &= ~ENABLE_LINE_INPUT
        new_mode &= ~ENABLE_MOUSE_INPUT
        new_mode &= ~ENABLE_WINDOW_INPUT
        new_mode &= ~ENABLE_PROCESSED_INPUT

        # Enable these modes
        new_mode |= ENABLE_EXTENDED_FLAGS
        new_mode |= ENABLE_INSERT_MODE
        new_mode |= ENABLE_QUICK_EDIT_MODE
        new_mode |= ENABLE_VIRTUAL_TERMINAL_INPUT

        kernel32.SetConsoleMode(stdin_handle, new_mode)

        return stdin_handle, old_mode.value

    # Unix/Linux raw mode implementation
    # Reference: https://github.com/moby/term/blob/main/termios_unix.go
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    new_settings = list(old_settings)

    # Input modes - clear IGNBRK, BRKINT, PARMRK, ISTRIP, INLCR, IGNCR, ICRNL, IXON
    new_settings[0] &= ~(termios.IGNBRK | termios.BRKINT | termios.PARMRK |
                         termios.ISTRIP | termios.INLCR | termios.IGNCR |
                         termios.ICRNL | termios.IXON)

    # Output modes - clear OPOST
    new_settings[1] &= ~termios.OPOST

    # Local modes - clear ECHO, ECHONL, ICANON, ISIG, IEXTEN
    new_settings[3] &= ~(termios.ECHO | termios.ECHONL | termios.ICANON |
                         termios.ISIG | termios.IEXTEN)

    # Control modes - clear CSIZE, PARENB; set CS8
    new_settings[2] &= ~(termios.CSIZE | termios.PARENB)
    new_settings[2] |= termios.CS8

    # Control characters - set VMIN = 1, VTIME = 0
    new_settings[6][termios.VMIN] = 1
    new_settings[6][termios.VTIME] = 0

    termios.tcsetattr(fd, termios.TCSADRAIN, new_settings)

    return fd, old_settings


def _restore_terminal_mode(fd_or_handle, old_settings, windows_console_state=None):
    """
    Restore terminal to original mode.

    Args:
        fd_or_handle: File descriptor (Unix) or handle (Windows)
        old_settings: Original terminal settings to restore
        windows_console_state: Windows console state tuple (output_cp, input_cp, stdout_mode, stdout_handle)
    """
    try:
        if IS_WINDOWS:
            import ctypes
            kernel32 = ctypes.windll.kernel32

            # Restore terminal raw mode
            kernel32.SetConsoleMode(fd_or_handle, old_settings)

            # Restore Windows console settings (code pages and VT100 mode)
            if windows_console_state is not None:
                output_cp, input_cp, stdout_mode, stdout_handle = windows_console_state
                kernel32.SetConsoleOutputCP(output_cp)
                kernel32.SetConsoleCP(input_cp)
                kernel32.SetConsoleMode(stdout_handle, stdout_mode)
        else:
            termios.tcsetattr(fd_or_handle, termios.TCSADRAIN, old_settings)
    except (NameError, OSError, IOError) as e:
        logger.debug("Failed to restore terminal mode: %s", e)


def _is_blocking_error(error):
    """
    Check if an error is a blocking I/O error (resource temporarily unavailable).

    Args:
        error: The exception to check

    Returns:
        True if it's a blocking error (EAGAIN/EWOULDBLOCK)
    """
    import errno
    err_code = getattr(error, 'errno', None) or getattr(error, 'winerror', None)
    return err_code in (errno.EAGAIN, errno.EWOULDBLOCK) if err_code else False


def _is_connection_reset_error(error):
    """
    Check if an error is a connection reset error.
    Handles both Unix (ECONNRESET, EPIPE) and Windows (WSAECONNRESET) errors.

    Args:
        error: The exception to check

    Returns:
        True if connection was reset by remote
    """
    import errno
    err_code = getattr(error, 'errno', None) or getattr(error, 'winerror', None)
    # Unix: ECONNRESET, EPIPE
    # Windows: WinError 10054 (WSAECONNRESET)
    return err_code in (errno.ECONNRESET, errno.EPIPE, 10054) if err_code else False


def _heartbeat_worker(exec_stream, stop_event):
    """
    Heartbeat worker thread to maintain WebSocket connection alive.
    Sends periodic ping frames to prevent connection timeout.

    Args:
        exec_stream: The WebSocket stream object
        stop_event: Threading event to stop the heartbeat
    """
    last_heartbeat = time.time()

    while not stop_event.is_set() and exec_stream.is_open():
        current_time = time.time()

        # Send heartbeat if interval has passed
        if current_time - last_heartbeat >= HEARTBEAT_INTERVAL:
            try:
                # Send ping frame through WebSocket
                if hasattr(exec_stream, 'ping'):
                    exec_stream.ping()
                else:
                    # Fallback: send empty data to keep connection alive
                    exec_stream.write_stdin('')

                last_heartbeat = current_time
                logger.debug("Heartbeat sent to maintain WebSocket connection")
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.debug("Heartbeat failed: %s", e)
                break

        # Sleep for a short interval to avoid busy waiting
        stop_event.wait(min(1.0, HEARTBEAT_INTERVAL / 5))


def exec_command_in_pod(pod_name: str, command: List[str],  # pylint: disable=too-many-branches,too-many-locals
                        namespace: str = AGENT_NAMESPACE,
                        kubeconfig_path: Optional[str] = None,
                        interactive: bool = True,
                        tty: bool = True) -> bool:
    """
    Execute a command in a specific pod with interactive session.

    Args:
        pod_name: Name of the pod to exec into
        command: Command to execute as a list of strings
        namespace: Namespace of the pod (default: AGENT_NAMESPACE)
        kubeconfig_path: Path to kubeconfig file (default: None - use default config)
        interactive: Whether to enable interactive mode
        tty: Whether to allocate a TTY

    Returns:
        True if execution was successful
    """
    logger.info("Executing command in pod '%s' in namespace '%s'", pod_name, namespace)
    logger.debug("Command: %s", ' '.join(command))

    # Variables for resource cleanup - initialized to None for safe cleanup in exception handlers
    resp = None  # WebSocket connection to pod exec API
    terminal_state = None  # Original terminal settings (termios structure on Unix, console mode on Windows)
    original_sigwinch = None  # Original SIGWINCH signal handler (Unix/Linux only)

    # File descriptor and flags for restoring blocking mode
    stdin_fd = None  # stdin file descriptor number
    original_stdin_flags = None  # Original stdin flags (before setting O_NONBLOCK)

    cleanup_done = False  # Flag to prevent duplicate cleanup execution
    windows_console_state = None  # Saved Windows console settings (code pages and VT100 mode)
    resize_stop_event = None  # Event to signal resize monitoring thread to stop (Windows only)
    resize_thread = None  # Background thread for monitoring terminal resize events (Windows only)

    def cleanup():
        """Cleanup function to ensure proper resource cleanup."""
        nonlocal cleanup_done

        # Prevent duplicate cleanup
        if cleanup_done:
            return
        cleanup_done = True

        # Restore signal handler (Unix/Linux). Windows does not use signal handlers for resize.
        if original_sigwinch and not IS_WINDOWS:
            try:
                signal.signal(signal.SIGWINCH, original_sigwinch)
            except (ValueError, OSError):
                pass

        # Restore terminal mode and Windows console settings
        if terminal_state is not None:
            _restore_terminal_mode(terminal_state[0], terminal_state[1], windows_console_state)

        # Restore stdin to blocking mode
        if not IS_WINDOWS:
            if stdin_fd is not None and original_stdin_flags is not None:
                try:
                    fcntl.fcntl(stdin_fd, fcntl.F_SETFL, original_stdin_flags)
                except (NameError, OSError, IOError):
                    pass

        # Close WebSocket connection
        if resp is not None:
            try:
                resp.close()
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.debug("Error closing WebSocket connection: %s", e)

    # Register cleanup for SIGTERM
    def signal_handler(signum, _frame):
        logger.info("Received signal %d, cleaning up...", signum)
        # Raise SystemExit to trigger finally block and normal cleanup
        raise SystemExit(0)

    original_sigterm = None
    if hasattr(signal, 'SIGTERM'):
        original_sigterm = signal.signal(signal.SIGTERM, signal_handler)
    try:
        # Initialize Kubernetes client
        if kubeconfig_path:
            config.load_kube_config(config_file=kubeconfig_path)
        else:
            config.load_kube_config()

        core_v1 = client.CoreV1Api()

        # Create the exec session
        # Reference: https://github.com/kubernetes/client-go/blob/master/transport/websocket/roundtripper.go#L113
        # client-go uses DataBufferSize + 1024 for both read and write buffers
        # The +1024 accounts for the protocol byte indicating which channel the data is for
        websocket_buffer_size = WEBSOCKET_BUFFER_SIZE + 1024

        resp = stream(
            core_v1.connect_get_namespaced_pod_exec,
            pod_name,
            namespace,
            command=command,
            stdin=interactive,
            stdout=True,
            stderr=True,
            tty=tty,
            _preload_content=False,
            _request_timeout=None
        )

        # Set WebSocket buffer sizes directly on the underlying socket
        # The kubernetes-client library doesn't support sockopt parameter natively,
        # so we configure the socket after creation
        try:
            import socket
            resp.sock.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, websocket_buffer_size)
            resp.sock.sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, websocket_buffer_size)
        except (AttributeError, OSError):
            # If setting socket options fails, continue anyway
            # The connection will still work with default buffer sizes
            pass

        if not interactive:
            # Non-interactive mode - just capture output
            while resp.is_open():
                resp.update(timeout=1)
                if resp.peek_stdout():
                    print(resp.read_stdout(), end='')
                if resp.peek_stderr():
                    print(resp.read_stderr(), end='', file=sys.stderr)
            resp.close()
            return True

        # Interactive mode setup
        heartbeat_stop_event = None
        heartbeat_thread = None

        try:
            # Configure Windows console for UTF-8 output
            if IS_WINDOWS:
                import ctypes
                kernel32 = ctypes.windll.kernel32

                # Save original console settings
                original_output_cp = kernel32.GetConsoleOutputCP()
                original_input_cp = kernel32.GetConsoleCP()
                STD_OUTPUT_HANDLE = -11
                stdout_handle = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
                original_mode = ctypes.c_uint32()
                kernel32.GetConsoleMode(stdout_handle, ctypes.byref(original_mode))
                windows_console_state = (original_output_cp, original_input_cp,
                                         original_mode.value, stdout_handle)

                # Set console output code page to UTF-8 (65001)
                kernel32.SetConsoleOutputCP(65001)
                # Set console input code page to UTF-8
                kernel32.SetConsoleCP(65001)
                # Enable VT100 processing for ANSI escape sequences
                ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
                kernel32.SetConsoleMode(stdout_handle, original_mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING)

            # Put terminal in raw mode to disable local echo
            if tty:
                terminal_state = _set_terminal_raw_mode()

            # Set up terminal resize monitoring
            # Reference: https://github.com/kubernetes/kubernetes/blob/master/staging/src/k8s.io/kubectl/pkg/util/term/
            if IS_WINDOWS:
                # Windows: Poll for size changes in background thread
                resize_stop_event = threading.Event()
                resize_thread = threading.Thread(
                    target=_monitor_resize_events_windows,
                    args=(resp, resize_stop_event),
                    daemon=True
                )
                resize_thread.start()
            elif hasattr(signal, 'SIGWINCH'):
                # Unix/Linux: Use SIGWINCH signal handler (must be in main thread)
                def sigwinch_handler(_signum, _frame):
                    try:
                        rows, cols = _get_terminal_size()
                        _send_terminal_size(resp, rows, cols)
                    except Exception as e:  # pylint: disable=broad-exception-caught
                        logger.debug("Error handling terminal resize: %s", e)

                original_sigwinch = signal.signal(signal.SIGWINCH, sigwinch_handler)

            # Set up heartbeat mechanism
            heartbeat_stop_event = threading.Event()
            heartbeat_thread = threading.Thread(
                target=_heartbeat_worker,
                args=(resp, heartbeat_stop_event),
                daemon=True
            )
            heartbeat_thread.start()

            # Configure file descriptor blocking modes (Unix/Linux only)
            if not IS_WINDOWS:
                # stdin - set non-blocking for non-blocking reads
                stdin_fd = sys.stdin.fileno()
                original_stdin_flags = fcntl.fcntl(stdin_fd, fcntl.F_GETFL)
                fcntl.fcntl(stdin_fd, fcntl.F_SETFL, original_stdin_flags | os.O_NONBLOCK)

                # stdout - explicitly set to blocking mode for reliable writes
                stdout_fd = sys.stdout.fileno()
                stdout_flags = fcntl.fcntl(stdout_fd, fcntl.F_GETFL)
                fcntl.fcntl(stdout_fd, fcntl.F_SETFL, stdout_flags & ~os.O_NONBLOCK)

                # stderr - explicitly set to blocking mode for reliable writes
                stderr_fd = sys.stderr.fileno()
                stderr_flags = fcntl.fcntl(stderr_fd, fcntl.F_GETFL)
                fcntl.fcntl(stderr_fd, fcntl.F_SETFL, stderr_flags & ~os.O_NONBLOCK)

            # Send initial terminal size if TTY is enabled
            if tty:
                try:
                    rows, cols = _get_terminal_size()
                    resize_message = json.dumps({
                        "Width": cols,
                        "Height": rows
                    })
                    resp.write_channel(RESIZE_CHANNEL, resize_message)
                except Exception as e:  # pylint: disable=broad-exception-caught
                    logger.debug("Failed to send initial terminal size: %s", e)

            # Main interaction loop
            import errno
            while resp.is_open():
                try:
                    resp.update(timeout=0.1)
                except (OSError, IOError) as e:
                    if _is_connection_reset_error(e):
                        logger.debug("Connection closed by remote: %s", e)
                        break
                    raise

                # Handle stdout
                if resp.peek_stdout():
                    stdout_data = resp.read_stdout()
                    data = stdout_data.encode()

                    # Write in chunks to avoid blocking on full pipe buffer
                    # This prevents "BlockingIOError: [Errno 35] write could not complete without blocking"
                    # which is easily reproducible on macOS (default pipe buffer: 64 KiB)
                    for start in range(0, len(data), WEBSOCKET_BUFFER_SIZE):
                        chunk = data[start: start + WEBSOCKET_BUFFER_SIZE]

                        while True:
                            try:
                                os.write(sys.stdout.fileno(), chunk)
                                break                                  # success → next chunk
                            except BlockingIOError as exc:
                                if exc.errno not in (errno.EAGAIN, errno.EWOULDBLOCK):
                                    raise                              # unexpected error
                                time.sleep(0)                          # yield to let the system drain the pipe buffer

                # Handle stderr
                if resp.peek_stderr():
                    stderr_data = resp.read_stderr()
                    sys.stderr.write(stderr_data)
                    sys.stderr.flush()

                # Handle stdin
                try:
                    if IS_WINDOWS:
                        # Windows: Use msvcrt for non-blocking input
                        import msvcrt
                        if msvcrt.kbhit():
                            data = msvcrt.getwch()
                            if data:
                                try:
                                    resp.write_stdin(data)
                                except OSError as e:
                                    if _is_blocking_error(e):
                                        logger.debug("stdin write blocked: %s", e)
                                    elif _is_connection_reset_error(e):
                                        logger.debug("Connection closed while writing stdin: %s", e)
                                        break
                                    else:
                                        raise
                    else:
                        # Unix/Linux/macOS: Use select for non-blocking input
                        if select.select([sys.stdin], [], [], 0)[0]:
                            # Read in chunks matching WebSocket buffer size
                            # Reference: https://github.com/kubernetes/client-go/blob/master/transport/websocket/roundtripper.go#L113  # pylint: disable=line-too-long
                            # Even with O_NONBLOCK set, stdin.read() without args can block
                            try:
                                data = os.read(sys.stdin.fileno(), WEBSOCKET_BUFFER_SIZE).decode(
                                    'utf-8', errors='replace')
                            except BlockingIOError:
                                data = None
                            if data:
                                try:
                                    resp.write_stdin(data)
                                except OSError as e:
                                    if _is_blocking_error(e):
                                        logger.debug("stdin write blocked: %s", e)
                                    elif _is_connection_reset_error(e):
                                        logger.debug("Connection closed while writing stdin: %s", e)
                                        break
                                    else:
                                        raise
                except (OSError, IOError, ImportError):
                    # No input available or import failed
                    pass

            logger.info("Pod exec session completed successfully")
            return True

        except KeyboardInterrupt:
            logger.info("Pod exec session interrupted by user")
            return True
        finally:
            # Stop resize monitoring
            if resize_stop_event:
                resize_stop_event.set()
            if resize_thread and resize_thread.is_alive():
                resize_thread.join(timeout=2.0)

            # Stop heartbeat
            if heartbeat_stop_event:
                heartbeat_stop_event.set()
            if heartbeat_thread and heartbeat_thread.is_alive():
                heartbeat_thread.join(timeout=2.0)

    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Failed to execute command in pod '%s': %s", pod_name, e)
        return False
    finally:
        # Always cleanup resources
        cleanup()

        # Restore original SIGTERM handler
        if original_sigterm and hasattr(signal, 'SIGTERM'):
            try:
                signal.signal(signal.SIGTERM, original_sigterm)
            except (ValueError, OSError):
                pass
