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


def _resize_terminal_handler(_signum, _frame, exec_stream):
    """
    Handle terminal resize signal and send new size to pod via WebSocket channel.

    Args:
        signum: Signal number
        frame: Current stack frame
        exec_stream: The WebSocket stream object
    """
    try:
        rows, cols = _get_terminal_size()
        # Create resize message as JSON
        resize_message = json.dumps({
            "Width": cols,
            "Height": rows
        })
        # Send resize message through WebSocket channel 4 (RESIZE_CHANNEL)
        exec_stream.write_channel(RESIZE_CHANNEL, resize_message)
        logger.debug("Terminal resized to %dx%d", cols, rows)
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.debug("Failed to resize terminal: %s", e)


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


def exec_command_in_pod(pod_name: str, command: List[str],  # pylint: disable=too-many-branches
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

    try:
        # Initialize Kubernetes client
        if kubeconfig_path:
            config.load_kube_config(config_file=kubeconfig_path)
        else:
            config.load_kube_config()

        core_v1 = client.CoreV1Api()

        # Create the exec session
        resp = stream(
            core_v1.connect_get_namespaced_pod_exec,
            pod_name,
            namespace,
            command=command,
            stdin=interactive,
            stdout=True,
            stderr=True,
            tty=tty,
            _preload_content=False
        )

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
        original_sigwinch = None
        heartbeat_stop_event = None
        heartbeat_thread = None
        fd = None
        fl = None

        try:
            # Set up terminal resize handler (Unix/Linux only)
            if not IS_WINDOWS and hasattr(signal, 'SIGWINCH'):
                def resize_handler(signum, frame):
                    _resize_terminal_handler(signum, frame, resp)

                # Register signal handler for terminal resize
                original_sigwinch = signal.signal(signal.SIGWINCH, resize_handler)

            # Set up heartbeat mechanism
            heartbeat_stop_event = threading.Event()
            heartbeat_thread = threading.Thread(
                target=_heartbeat_worker,
                args=(resp, heartbeat_stop_event),
                daemon=True
            )
            heartbeat_thread.start()

            # Make stdin non-blocking (Unix/Linux only)
            if not IS_WINDOWS:
                fd = sys.stdin.fileno()
                fl = fcntl.fcntl(fd, fcntl.F_GETFL)
                fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

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
            while resp.is_open():
                resp.update(timeout=0.1)

                # Handle stdout
                if resp.peek_stdout():
                    stdout_data = resp.read_stdout()
                    sys.stdout.write(stdout_data)
                    sys.stdout.flush()

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
                                resp.write_stdin(data)
                    else:
                        # Unix/Linux: Use select for non-blocking input
                        if select.select([sys.stdin], [], [], 0)[0]:
                            data = sys.stdin.read()
                            if data:
                                resp.write_stdin(data)
                except (OSError, IOError, ImportError):
                    # No input available or import failed
                    pass

            logger.info("Pod exec session completed successfully")
            return True

        except KeyboardInterrupt:
            logger.info("Pod exec session interrupted by user")
            return True
        finally:
            # Cleanup
            if heartbeat_stop_event:
                heartbeat_stop_event.set()
            if heartbeat_thread and heartbeat_thread.is_alive():
                heartbeat_thread.join(timeout=2.0)

            if original_sigwinch and not IS_WINDOWS:
                signal.signal(signal.SIGWINCH, original_sigwinch)

            # Restore stdin to blocking mode (Unix/Linux only)
            if not IS_WINDOWS and fd is not None and fl is not None:
                try:
                    fcntl.fcntl(fd, fcntl.F_SETFL, fl)
                except (NameError, OSError, IOError):
                    pass

            resp.close()

    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Failed to execute command in pod '%s': %s", pod_name, e)
        return False
