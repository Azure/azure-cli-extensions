# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import sys

from knack.util import CLIError


def _is_wow64_process():
    import ctypes
    from ctypes import wintypes

    if sys.maxsize > 2**32:
        return False

    kernel32 = ctypes.WinDLL("kernel32", winmode=0x00000800, use_last_error=True)
    get_current_process = kernel32.GetCurrentProcess
    get_current_process.argtypes = []
    get_current_process.restype = wintypes.HANDLE

    if hasattr(kernel32, "IsWow64Process2"):
        is_wow64_process = kernel32.IsWow64Process2
        is_wow64_process.argtypes = [
            wintypes.HANDLE,
            ctypes.POINTER(wintypes.WORD),
            ctypes.POINTER(wintypes.WORD),
        ]
        is_wow64_process.restype = wintypes.BOOL
        process_machine = wintypes.WORD()
        native_machine = wintypes.WORD()
        result = is_wow64_process(
            get_current_process(),
            ctypes.byref(process_machine),
            ctypes.byref(native_machine),
        )
        is_wow64 = process_machine.value != 0
    else:
        is_wow64_process = kernel32.IsWow64Process
        is_wow64_process.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.BOOL)]
        is_wow64_process.restype = wintypes.BOOL
        wow64_flag = wintypes.BOOL()
        result = is_wow64_process(get_current_process(), ctypes.byref(wow64_flag))
        is_wow64 = bool(wow64_flag.value)

    if not result:
        raise CLIError(
            "Unable to determine Windows process architecture "
            f"(Windows error {ctypes.get_last_error()})."
        )
    return is_wow64


def _get_native_program_files_path():
    import ntpath

    try:
        import winreg
    except ImportError as error:
        raise CLIError(
            "Windows registry access is unavailable; this operation requires Windows."
        ) from error

    with winreg.OpenKey(
        winreg.HKEY_LOCAL_MACHINE,
        r"SOFTWARE\Microsoft\Windows\CurrentVersion",
        access=winreg.KEY_READ | winreg.KEY_WOW64_64KEY,
    ) as key:
        path, value_type = winreg.QueryValueEx(key, "ProgramFilesDir")

    if (
        value_type != winreg.REG_SZ
        or not isinstance(path, str)
        or not ntpath.splitdrive(path)[0]
        or not ntpath.isabs(path)
    ):
        raise CLIError("Unable to locate the native Windows Program Files directory.")
    return path


def _get_windows_ssh_keygen_paths():
    import ctypes
    from ctypes import wintypes
    import ntpath

    is_wow64 = _is_wow64_process()

    # Query Windows rather than trusting environment variables; load only a system DLL.
    get_folder_path = ctypes.WinDLL("shell32", winmode=0x00000800).SHGetFolderPathW
    get_folder_path.argtypes = [
        wintypes.HWND,
        ctypes.c_int,
        wintypes.HANDLE,
        wintypes.DWORD,
        wintypes.LPWSTR,
    ]
    get_folder_path.restype = ctypes.c_long

    folder_ids = (("Program Files", 0x0026), ("System", 0x0025))
    if is_wow64:
        folder_ids += (("Windows", 0x0024),)

    folders = {}
    for name, folder_id in folder_ids:
        buffer = ctypes.create_unicode_buffer(260)
        result = get_folder_path(None, folder_id, None, 0, buffer)
        if (
            result != 0
            or not ntpath.splitdrive(buffer.value)[0]
            or not ntpath.isabs(buffer.value)
        ):
            raise CLIError(
                f"Unable to locate the Windows {name} directory for OpenSSH "
                f"(HRESULT 0x{result & 0xffffffff:08X})."
            )
        folders[name] = buffer.value

    program_files = [folders["Program Files"]]
    system_directory = folders["System"]
    if is_wow64:
        native_program_files = _get_native_program_files_path()
        if ntpath.normcase(native_program_files) != ntpath.normcase(program_files[0]):
            program_files.insert(0, native_program_files)
        # Sysnative bypasses filesystem redirection for a 32-bit process.
        system_directory = ntpath.join(folders["Windows"], "Sysnative")

    return [
        ntpath.join(directory, installation, "ssh-keygen.exe")
        for directory in program_files
        for installation in ("OpenSSH", "OpenSSH-Win64")
    ] + [
        ntpath.join(system_directory, "OpenSSH", "ssh-keygen.exe"),
    ]


def get_windows_ssh_keygen_path():
    """Resolve ssh-keygen only from supported Windows installation locations."""
    try:
        candidates = _get_windows_ssh_keygen_paths()
    except OSError as error:
        raise CLIError(f"Unable to locate Windows OpenSSH: {error}") from error

    for path in candidates:
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path

    raise CLIError(
        "OpenSSH ssh-keygen was not found in a supported system installation. "
        "Install OpenSSH 9.4 or later. Searched: " + ", ".join(candidates)
    )
