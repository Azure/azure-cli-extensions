# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# from knack.util import CLIError
# from requests.api import get
import requests
import json
import websocket
import threading
import sys
import uuid
import time
import re
import textwrap
import numpy
import wsaccel


class GlobalVariables:
    def __init__(self):
        self.webSocket = None
        self.terminalInstance = None
        self.serialConsoleInstance = None
        self.terminatingApp = False
        self.loading = True
        self.firstMessage = True
        self.blockPrint = False
        self.trycount = 0


class PrintClass:
    CYAN = 36
    YELLOW = 33
    RED = 91

    def __init__(self, GV):
        self.messageBuffer = ""
        self.GV = GV

    def print(self, message, color=None, buffer=True):
        if color:
            message = "\x1b[" + str(color) + "m" + message + "\x1b[0m"
        if self.GV.blockPrint and buffer:
            self.messageBuffer += message
        else:
            if not self.GV.blockPrint:
                self.emptyMessageBuffer()
            print(message, end="", flush=True)

    def clearScreen(self, buffer=True):
        self.print("\x1b[2J\x1b[0;0H", buffer=buffer)

    def clearLine(self, buffer=True):
        self.print("\x1b[2K\x1b[1G", buffer=buffer)

    def cursorUp(self, buffer=True):
        self.print("\x1b[A", buffer=buffer)

    def setCursorHorizontalPosition(self, col, buffer=True):
        self.print("\x1b[" + str(col) + "G", buffer=buffer)

    def emptyMessageBuffer(self):
        print(self.messageBuffer, end="", flush=True)
        self.messageBuffer = ""

    def getCursorPosition(self, getch):
        self.print("\x1b[6n", buffer=False)
        buf = ""
        while True:
            c = getch().decode()
            buf += c
            if c == "R":
                break
        try:
            matches = re.match(r"^\x1b\[(\d*);(\d*)R", buf)
            groups = matches.groups()
        except AttributeError:
            return 1, 1
        return int(groups[0]), int(groups[1])

    def getTerminalWidth(self, getch):
        PC.hideCursor(buffer=False)
        _, originalCol = self.getCursorPosition(getch)
        self.setCursorHorizontalPosition(999, buffer=False)
        _, width = self.getCursorPosition(getch)
        self.setCursorHorizontalPosition(originalCol, buffer=False)
        PC.showCursor(buffer=False)
        return width

    def hideCursor(self, buffer=True):
        self.print("\x1b[?25l", buffer=buffer)

    def showCursor(self, buffer=True):
        self.print("\x1b[?25h", buffer=buffer)


GV = GlobalVariables()
PC = PrintClass(GV)


def quitapp(fromWebsocket=False, message=""):
    PC.print(message + "\r\n", color=PrintClass.RED)
    GV.terminatingApp = True
    GV.loading = False
    if GV.terminalInstance:
        GV.terminalInstance.revertTerminal()
        GV.terminalInstance = None
    if not fromWebsocket and GV.webSocket:
        GV.webSocket.close()
        GV.webSocket = None
    sys.exit()


class _Getch:
    def __init__(self):
        if sys.platform.startswith('win'):
            import ctypes
            from ctypes import wintypes
            STD_INPUT_HANDLE = -10
            self.hIn = ctypes.windll.kernel32.GetStdHandle(STD_INPUT_HANDLE)
            self.lpBuffer = ctypes.create_string_buffer(1)
            self.lpNumberOfCharsRead = wintypes.DWORD()
            self.nNumberOfCharsToRead = wintypes.DWORD()
            self.nNumberOfCharsToRead.value = 1
            self.impl = self._getchWindows
        else:
            self.impl = self._getchUnix

    def __call__(self):
        return self.impl()

    def _getchUnix(self):
        return sys.stdin.read(1).encode()

    def _getchWindows(self):
        import ctypes
        status = ctypes.windll.kernel32.ReadConsoleW(self.hIn,
                                                     self.lpBuffer,
                                                     self.nNumberOfCharsToRead,
                                                     ctypes.byref(
                                                         self.lpNumberOfCharsRead),
                                                     None)
        if status == 0:
            quitapp()
        return chr(self.lpBuffer.raw[0]).encode()


class Terminal:
    def __init__(self):
        self.winOriginalOutMode = None
        self.winOriginalInMode = None
        self.winOut = None
        self.winIn = None
        self.unixOriginalMode = None

    def configureTerminal(self):
        if sys.platform.startswith('win'):
            import ctypes
            from ctypes import wintypes
            ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
            ENABLE_VIRTUAL_TERMINAL_INPUT = 0x0200
            ENABLE_ECHO_INPUT = 0x0004
            ENABLE_LINE_INPUT = 0x0002
            ENABLE_PROCESSED_INPUT = 0x0001
            STD_OUTPUT_HANDLE = -11
            STD_INPUT_HANDLE = -10
            DISABLE = ~(ENABLE_ECHO_INPUT | ENABLE_LINE_INPUT |
                        ENABLE_PROCESSED_INPUT)

            kernel32 = ctypes.windll.kernel32
            dwOriginalOutMode = wintypes.DWORD()
            dwOriginalInMode = wintypes.DWORD()
            self.winOut = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
            self.winIn = kernel32.GetStdHandle(STD_INPUT_HANDLE)
            errorMessage = "Error configuring terminal: Make sure that app in running in a Windows 10 console."

            if not kernel32.GetConsoleMode(self.winOut, ctypes.byref(dwOriginalOutMode)):
                quitapp(message=errorMessage)
            if not kernel32.GetConsoleMode(self.winIn, ctypes.byref(dwOriginalInMode)):
                quitapp(message=errorMessage)

            self.winOriginalOutMode = dwOriginalOutMode.value
            self.winOriginalInMode = dwOriginalInMode.value

            dwOutMode = self.winOriginalOutMode | ENABLE_VIRTUAL_TERMINAL_PROCESSING
            dwInMode = (self.winOriginalInMode |
                        ENABLE_VIRTUAL_TERMINAL_INPUT) & DISABLE

            if not kernel32.SetConsoleMode(self.winOut, dwOutMode):
                quitapp(message=errorMessage)
            if not kernel32.SetConsoleMode(self.winIn, dwInMode):
                quitapp(message=errorMessage)
        else:
            import tty
            import termios
            errorMessage = "Error configuring terminal: Make sure that app in running in a terminal."
            try:
                fd = sys.stdin.fileno()
            except ValueError:
                quitapp(message=errorMessage)
            self.unixOriginalMode = termios.tcgetattr(fd)
            tty.setraw(fd)

    def revertTerminal(self):
        if sys.platform.startswith('win'):
            import ctypes
            kernel32 = ctypes.windll.kernel32
            if self.winOriginalOutMode:
                kernel32.SetConsoleMode(self.winOut, self.winOriginalOutMode)
            if self.winOriginalInMode:
                kernel32.SetConsoleMode(self.winIn, self.winOriginalInMode)
        else:
            import termios
            if self.unixOriginalMode:
                try:
                    fd = sys.stdin.fileno()
                except ValueError:
                    return
                termios.tcsetattr(fd, termios.TCSADRAIN, self.unixOriginalMode)


def getMaxWidthOfString(s):
    maxWidth = -1
    currWidth = 0
    i = 0
    while i < len(s):
        if s[i] == '\r' or s[i] == '\n':
            i += 2
            maxWidth = max(currWidth, maxWidth)
            currWidth = 0
        else:
            i += 1
            currWidth += 1
    return max(maxWidth, currWidth)


def prompt(getch, message, lines=1):
    GV.blockPrint = True
    width = PC.getTerminalWidth(getch)
    _, col = PC.getCursorPosition(getch)
    # adjust string if it is too wide to fit in console
    if width < getMaxWidthOfString(message):
        wrapped = textwrap.wrap(message.replace(
            "\r\n", " ").replace("\n\r", " "), width=width)
        message = "\r\n".join(wrapped)
        lines = len(wrapped)
    PC.print("\r\n" + message, color=PrintClass.YELLOW, buffer=False)
    c = getch()
    PC.hideCursor(buffer=False)
    for _ in range(lines):
        PC.clearLine(buffer=False)
        PC.cursorUp(buffer=False)
    PC.setCursorHorizontalPosition(col, buffer=False)
    PC.showCursor(buffer=False)
    PC.emptyMessageBuffer()
    GV.blockPrint = False
    return c


def listenForKeys():
    getch = _Getch()
    while True:
        c = getch()
        if GV.webSocket and not GV.firstMessage:
            if c == b'\x1d':
                c = prompt(
                    getch, "| Press n for NMI | s for SysRq | r to Reset VM |\r\n| q to quit Console | CTRL + ] to forward input |", lines=2)
                if c == b'n':
                    c = prompt(getch, "Warning: A Non-Maskable Interrupt (NMI) is used in debugging\r\nscenarios and is designed to crash your target Virtual Machine.\r\nAre you sure you want to send an NMI? (Y/n): ", lines=3)
                    if c == b"Y":
                        GV.serialConsoleInstance.sendNMI()
                    continue
                if c == b'r':
                    c = prompt(getch, "Warning: This results in a hard restart, like powering the computer\r\ndown, then back up again. This can result in data loss in the virtual\r\nmachine. You should only perform this operation if a graceful restart\r\nis not effective.\r\nAre you sure you want to Hard Reset the VM? (Y/n): ", lines=5)
                    if c == b"Y":
                        GV.serialConsoleInstance.sendReset()
                    continue
                if c == b's':
                    c = prompt(
                        getch, "Which SysRq command would you like to send? Press h for help: ")
                    GV.serialConsoleInstance.sendSysRq(c.decode())
                    continue
                if c == b'q':
                    quitapp()
                    return
                if c != b'\x1d':
                    continue
            try:
                if GV.webSocket:
                    GV.webSocket.send(c)
            except (AttributeError, websocket.WebSocketConnectionClosedException):
                pass
        else:
            if c == b'\r':
                GV.serialConsoleInstance.connect()
            elif c == b'\x1d':
                c = prompt(getch, "| Press q to quit Console |")
                if c == b'q':
                    quitapp()
                    return


def loadingMessage(clearScreen=True):
    if clearScreen:
        PC.clearScreen()
    PC.print("For more information on the Azure Serial Console, see <https://aka.ms/serialconsolelinux>.\r\n",
             color=PrintClass.YELLOW)
    indx = 0
    numberOfSquares = 3
    chars = ["\u25A1"] * numberOfSquares
    while GV.loading:
        PC.hideCursor()
        charsCopy = chars.copy()
        charsCopy[indx] = "\u25A0"
        squares = " ".join(charsCopy)
        PC.clearLine()
        PC.print("Connecting to console of VM   " +
                 squares, color=PrintClass.CYAN)
        PC.showCursor()
        indx = (indx + 1) % numberOfSquares
        time.sleep(0.5)


class SerialConsole:
    def __init__(self, cmd, resource_group_name, vm_vmss_name, vmss_instanceid):
        from azure.cli.core.commands.client_factory import get_subscription_id
        armEndpoint = "https://management.azure.com"
        RP_PROVIDER = "Microsoft.SerialConsole"
        subscriptionId = get_subscription_id(cmd.cli_ctx)
        vmPath = f"virtualMachineScaleSets/{vm_vmss_name}/virtualMachines/{vmss_instanceid}" if vmss_instanceid else f"virtualMachines/{vm_vmss_name}"
        self.connectionUrl = (f"{armEndpoint}/subscriptions/{subscriptionId}/resourcegroups/{resource_group_name}"
                              f"/providers/Microsoft.Compute/{vmPath}"
                              f"/providers/{RP_PROVIDER}/serialPorts/0"
                              f"/connect?api-version=2018-05-01")
        self.websocketURL = None
        self.accessToken = None

    # Returns True if successful, False otherwise
    def loadWebSocketURL(self):
        from azure.cli.core._profile import Profile
        tokenInfo, _, _ = Profile().get_raw_token()
        self.accessToken = tokenInfo[1]
        applicationJsonFormat = "application/json"
        headers = {'authorization': "Bearer " + self.accessToken,
                   'accept': applicationJsonFormat,
                   'content-type': applicationJsonFormat}
        result = requests.post(self.connectionUrl, headers=headers)
        jsonResults = json.loads(result.text)
        if result.status_code == 200 and "connectionString" in jsonResults:
            self.websocketURL = jsonResults["connectionString"]
            return True

        return False

    def connect(self):
        def on_open(_):
            pass

        def on_message(_, message):
            if GV.firstMessage:
                PC.clearScreen()
            GV.firstMessage = False
            GV.loading = False
            PC.print(message)

        def on_error(*_):
            pass

        def on_close(_):
            GV.loading = False
            if not GV.terminatingApp:
                if GV.firstMessage:
                    PC.print(
                        "\r\nCould not establish connection to VM or VMSS. Make sure that it is powered on and press \"Enter\" try again...", color=PrintClass.RED)
                else:
                    PC.print(
                        "\r\nConnection Closed: Press Enter to reconnect...", color=PrintClass.RED)
                GV.webSocket = None

        def connectThread():
            if self.loadWebSocketURL():
                GV.webSocket = websocket.WebSocketApp(self.websocketURL + "?authorization=" + self.accessToken,
                                                      on_open=on_open,
                                                      on_message=on_message,
                                                      on_error=on_error,
                                                      on_close=on_close)
                GV.webSocket.run_forever(skip_utf8_validation=True)
            else:
                GV.loading = False
                PC.print(
                    "\r\nCould not establish connection to VM or VMSS. Make sure that input parameters are correct or press \"Enter\" to try again...", color=PrintClass.RED)

        GV.loading = True
        GV.firstMessage = True

        th1 = threading.Thread(target=loadingMessage, args=())
        th1.daemon = True
        th1.start()

        th2 = threading.Thread(target=connectThread, args=())
        th2.daemon = True
        th2.start()

    def launchConsole(self):
        GV.terminalInstance = Terminal()
        GV.terminalInstance.configureTerminal()
        th = threading.Thread(target=listenForKeys, args=())
        th.daemon = True
        th.start()
        self.connect()
        th.join()

    def sendAdminCommand(self, command, commandParameters):
        if self.websocketURL and self.accessToken:
            url = self.websocketURL.replace("wss", "https").replace(
                "ws", "http").replace("/client", "/adminCommand/" + command)
            headers = {'accept': "application/json",
                       'authorization': "Bearer " + self.accessToken,
                       'accept-language': "en",
                       'content-type': "application/json"}
            data = {'command': command,
                    'requestId': str(uuid.uuid4()),
                    'commandParameters': commandParameters}
            result = requests.post(url, headers=headers, data=json.dumps(data))
            return result.status_code == 200

    def sendNMI(self):
        return self.sendAdminCommand("nmi", {})

    def sendReset(self):
        return self.sendAdminCommand("reset", {})

    def sendSysRq(self, key):
        return self.sendAdminCommand("sysrq", {"SysRqCommand": key})

    def connectAndSendAdminCommand(self, command, arg_character=None):
        if command == "nmi":
            func = self.sendNMI
            successMessage = "NMI sent successfully\r\n"
            failureMessage = "Failed to send NMI\r\n"
        elif command == "reset":
            func = self.sendReset
            successMessage = "Successfully Hard Reset VM\r\n"
            failureMessage = "Failed to Hard Reset VM\r\n"
        elif command == "sysrq" and arg_character is not None and len(arg_character) == 1:
            def wrapper():
                return self.sendSysRq(arg_character)
            func = wrapper
            successMessage = "Successfully sent SysRq command\r\n"
            failureMessage = "Failed to send SysRq command\r\n"
        else:
            return

        GV.terminalInstance = Terminal()
        GV.terminalInstance.configureTerminal()
        GV.loading = True

        th1 = threading.Thread(target=loadingMessage, args=(False,))
        th1.daemon = True
        th1.start()

        if self.loadWebSocketURL():
            def on_message(ws, _):
                GV.trycount += 1
                if func():
                    GV.loading = False
                    GV.terminatingApp = True
                    PC.clearLine()
                    PC.print(successMessage)
                    ws.close()
                    return
                if GV.trycount >= 2:
                    GV.loading = False
                    GV.terminatingApp = True
                    PC.clearLine()
                    PC.print(failureMessage, color=PrintClass.RED)
                    ws.close()

            def on_close(_):
                if not GV.terminatingApp:
                    PC.clearLine()
                    PC.print(
                        "Could not establish connection to VM or VMSS. Make sure that it is powered on and try again.\r\n", color=PrintClass.RED)

            wsapp = websocket.WebSocketApp(
                self.websocketURL + "?authorization=" + self.accessToken, on_message=on_message, on_close=on_close)
            wsapp.run_forever()
        else:
            GV.loading = False
            PC.print("\r\nCould not establish connection to VM or VMSS. Make sure that input parameters are correct and try again.\r\n", color=PrintClass.RED)

        GV.loading = False
        GV.terminalInstance.revertTerminal()


def connect_serialconsole(cmd, resource_group_name, vm_vmss_name, vmss_instanceid=None):
    GV.serialConsoleInstance = SerialConsole(
        cmd, resource_group_name, vm_vmss_name, vmss_instanceid)
    GV.serialConsoleInstance.launchConsole()


def send_nmi_serialconsole(cmd, resource_group_name, vm_vmss_name, vmss_instanceid=None):
    GV.serialConsoleInstance = SerialConsole(
        cmd, resource_group_name, vm_vmss_name, vmss_instanceid)
    GV.serialConsoleInstance.connectAndSendAdminCommand("nmi")


def send_reset_serialconsole(cmd, resource_group_name, vm_vmss_name, vmss_instanceid=None):
    GV.serialConsoleInstance = SerialConsole(
        cmd, resource_group_name, vm_vmss_name, vmss_instanceid)
    GV.serialConsoleInstance.connectAndSendAdminCommand("reset")


def send_sysrq_serialconsole(cmd, resource_group_name, vm_vmss_name, sysrqinput, vmss_instanceid=None):
    GV.serialConsoleInstance = SerialConsole(
        cmd, resource_group_name, vm_vmss_name, vmss_instanceid)
    GV.serialConsoleInstance.connectAndSendAdminCommand(
        "sysrq", arg_character=sysrqinput)