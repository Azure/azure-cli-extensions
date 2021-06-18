# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# from knack.util import CLIError
# from requests.api import get
import json
import threading
import sys
import uuid
import time
import re
import textwrap
import numpy     # pylint: disable=unused-import
import wsaccel   # pylint: disable=unused-import
import websocket
import requests
from azure.cli.core.azclierror import UnclassifiedUserFault
from azure.cli.core.azclierror import ResourceNotFoundError
from azure.cli.core.azclierror import AzureConnectionError
from azure.cli.core.azclierror import ForbiddenError
from azure.core.exceptions import ResourceNotFoundError as ComputeClientResourceNotFoundError
from azext_serialconsole._client_factory import _compute_client_factory


# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes
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
        self.OSIsWindows = False


class PrintClass:
    CYAN = 36
    YELLOW = 33
    RED = 91

    def __init__(self):
        self.messageBuffer = ""

    def print(self, message, color=None, buffer=True):
        if color:
            message = "\x1b[" + str(color) + "m" + message + "\x1b[0m"
        if GV.blockPrint and buffer:
            self.messageBuffer += message
        else:
            if not GV.blockPrint:
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
        self.hideCursor(buffer=False)
        _, originalCol = self.getCursorPosition(getch)
        self.setCursorHorizontalPosition(999, buffer=False)
        _, width = self.getCursorPosition(getch)
        self.setCursorHorizontalPosition(originalCol, buffer=False)
        self.showCursor(buffer=False)
        return width

    def hideCursor(self, buffer=True):
        self.print("\x1b[?25l", buffer=buffer)

    def showCursor(self, buffer=True):
        self.print("\x1b[?25h", buffer=buffer)

    @staticmethod
    def _getMaxWidthOfString(s):
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

    def prompt(self, getch, message):
        GV.blockPrint = True
        width = self.getTerminalWidth(getch)
        _, col = self.getCursorPosition(getch)
        # adjust message if it is too wide to fit in console
        if width < self._getMaxWidthOfString(message):
            wrapped = textwrap.wrap(message.replace(
                "\r\n", " ").replace("\n\r", " "), width=width)
            message = "\r\n".join(wrapped)
        lines = message.count("\r\n") + message.count("\n\r") + 1
        self.print("\r\n" + message, color=PrintClass.YELLOW, buffer=False)
        c = getch()
        self.hideCursor(buffer=False)
        for _ in range(lines):
            self.clearLine(buffer=False)
            self.cursorUp(buffer=False)
        self.setCursorHorizontalPosition(col, buffer=False)
        self.showCursor(buffer=False)
        self.emptyMessageBuffer()
        GV.blockPrint = False
        return c


def quitapp(fromWebsocket=False, message="", error_message=None, error_recommendation=None, error_func=None):
    PC.print(message + "\r\n", color=PrintClass.RED)
    GV.terminatingApp = True
    GV.loading = False
    if GV.terminalInstance:
        GV.terminalInstance.revertTerminal()
        GV.terminalInstance = None
    if not fromWebsocket and GV.webSocket:
        GV.webSocket.close()
        GV.webSocket = None
    if error_message and error_func:
        raise error_func(error_message, error_recommendation)
    sys.exit()


GV = GlobalVariables()
PC = PrintClass()


# pylint: disable=too-few-public-methods
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

    @staticmethod
    def _getchUnix():
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
    ERROR_MESSAGE = "Unable to configure terminal."
    RECOMENDATION = ("Make sure that app in running in a terminal on a Windows 10 "
                     "or Unix based machine. Versions earlier than Windows 10 are not supported.")

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
            if (not kernel32.GetConsoleMode(self.winOut, ctypes.byref(dwOriginalOutMode)) or
                    not kernel32.GetConsoleMode(self.winIn, ctypes.byref(dwOriginalInMode))):
                quitapp(error_message=Terminal.ERROR_MESSAGE,
                        error_recommendation=Terminal.RECOMENDATION, error_func=UnclassifiedUserFault)

            self.winOriginalOutMode = dwOriginalOutMode.value
            self.winOriginalInMode = dwOriginalInMode.value

            dwOutMode = self.winOriginalOutMode | ENABLE_VIRTUAL_TERMINAL_PROCESSING
            dwInMode = (self.winOriginalInMode |
                        ENABLE_VIRTUAL_TERMINAL_INPUT) & DISABLE

            if (not kernel32.SetConsoleMode(self.winOut, dwOutMode) or
                    not kernel32.SetConsoleMode(self.winIn, dwInMode)):
                quitapp(error_message=Terminal.ERROR_MESSAGE,
                        error_recommendation=Terminal.RECOMENDATION, error_func=UnclassifiedUserFault)
        else:
            try:
                import tty
                import termios  # pylint: disable=import-error
                fd = sys.stdin.fileno()
            except (ModuleNotFoundError, ValueError):
                quitapp(error_message=Terminal.ERROR_MESSAGE,
                        error_recommendation=Terminal.RECOMENDATION, error_func=UnclassifiedUserFault)

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
            if self.unixOriginalMode:
                import termios  # pylint: disable=import-error
                try:
                    fd = sys.stdin.fileno()
                except ValueError:
                    return
                termios.tcsetattr(fd, termios.TCSADRAIN, self.unixOriginalMode)


class SerialConsole:
    def __init__(self, cmd, resource_group_name, vm_vmss_name, vmss_instanceid):
        from azure.cli.core.commands.client_factory import get_subscription_id
        armEndpoint = "https://management.azure.com"
        RP_PROVIDER = "Microsoft.SerialConsole"
        subscriptionId = get_subscription_id(cmd.cli_ctx)
        vmPath = f"virtualMachineScaleSets/{vm_vmss_name}/virtualMachines/{vmss_instanceid}" \
            if vmss_instanceid else f"virtualMachines/{vm_vmss_name}"
        self.connectionUrl = (f"{armEndpoint}/subscriptions/{subscriptionId}/resourcegroups/{resource_group_name}"
                              f"/providers/Microsoft.Compute/{vmPath}"
                              f"/providers/{RP_PROVIDER}/serialPorts/0"
                              f"/connect?api-version=2018-05-01")
        self.websocketURL = None
        self.accessToken = None

    @staticmethod
    def listenForKeys():
        getch = _Getch()
        while True:
            c = getch()
            if GV.webSocket and not GV.firstMessage:
                if c == b'\x1d':
                    if GV.OSIsWindows:
                        message = ("| Press n for NMI | r to Reset VM |\r\n"
                                   "| q to quit Console | CTRL + ] to forward input |")
                    else:
                        message = ("| Press n for NMI | s for SysRq | r to Reset VM |\r\n"
                                   "| q to quit Console | CTRL + ] to forward input |")
                    c = PC.prompt(getch, message)
                    if c == b'n':
                        message = ("Warning: A Non-Maskable Interrupt (NMI) is used in debugging\r\n"
                                   "scenarios and is designed to crash your target Virtual Machine.\r\n"
                                   "Are you sure you want to send an NMI? (Y/n): ")
                        c = PC.prompt(getch, message)
                        if c == b"Y":
                            GV.serialConsoleInstance.sendNMI()
                        continue
                    if c == b'r':
                        message = ("Warning: This results in a hard restart, like powering the computer\r\n"
                                   "down, then back up again. This can result in data loss in the virtual\r\n"
                                   "machine. You should only perform this operation if a graceful restart\r\n"
                                   "is not effective.\r\n"
                                   "Are you sure you want to Hard Reset the VM? (Y/n): ")
                        c = PC.prompt(getch, message)
                        if c == b"Y":
                            GV.serialConsoleInstance.sendReset()
                        continue
                    if not GV.OSIsWindows and c == b's':
                        message = "Which SysRq command would you like to send? Press h for help: "
                        c = PC.prompt(getch, message)
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
                if c == b'\r' and not GV.loading:
                    GV.serialConsoleInstance.connect()
                elif c == b'\x1d':
                    c = PC.prompt(getch, "| Press q to quit Console |")
                    if c == b'q':
                        quitapp()
                        return

    @staticmethod
    def connectLoadingMessageLinux():
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

    @staticmethod
    def connectLoadingMessageWindows():
        PC.clearScreen()
        message1 = ("Windows Serial Console requires Special Administration Console (SAC) to be enabled within "
                   "the Windows VM.\r\nIf you do not see SAC> in the console below after the connection is made, "
                   "SAC is not enabled.\r\n\r\n")
        message2 = ("For more information on the Azure Serial Console and SAC, "
                    "see <https://aka.ms/serialconsolewindows>.\r\n")
        PC.print(message1)
        PC.print(message2, color=PrintClass.YELLOW)
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

    @staticmethod
    def sendLoadingMessage(loadingText):
        indx = 0
        numberOfSquares = 3
        chars = ["\u25A1"] * numberOfSquares
        while GV.loading:
            charsCopy = chars.copy()
            charsCopy[indx] = "\u25A0"
            squares = " ".join(charsCopy)
            print(loadingText + "   " + squares, end="\r")
            indx = (indx + 1) % numberOfSquares
            time.sleep(0.5)

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
                    message = ("\r\nCould not establish connection to VM or VMSS. "
                               "Make sure that it is powered on and press \"Enter\" try again...")
                    PC.print(message, color=PrintClass.RED)
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
                message = ("\r\nCould not establish connection to VM or VMSS. "
                           "Make sure that input parameters are correct or press \"Enter\" to try again...")
                PC.print(message, color=PrintClass.RED)

        GV.loading = True
        GV.firstMessage = True

        if GV.OSIsWindows:
            th1 = threading.Thread(target=self.connectLoadingMessageWindows, args=())
        else:
            th1 = threading.Thread(target=self.connectLoadingMessageLinux, args=())
        th1.daemon = True
        th1.start()

        th2 = threading.Thread(target=connectThread, args=())
        th2.daemon = True
        th2.start()

    def launchConsole(self):
        GV.terminalInstance = Terminal()
        GV.terminalInstance.configureTerminal()
        th = threading.Thread(target=self.listenForKeys, args=())
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
        return False

    def sendNMI(self):
        return self.sendAdminCommand("nmi", {})

    def sendReset(self):
        return self.sendAdminCommand("reset", {})

    def sendSysRq(self, key):
        return self.sendAdminCommand("sysrq", {"SysRqCommand": key})

    def connectAndSendAdminCommand(self, command, arg_characters=None):
        if command == "nmi":
            func = self.sendNMI
            successMessage = "NMI sent successfully    \r\n"
            failureMessage = "Failed to send NMI       \r\n"
            loadingText = "Sending NMI to VM"
        elif command == "reset":
            func = self.sendReset
            successMessage = "Successfully Hard Reset VM      \r\n"
            failureMessage = "Failed to Hard Reset VM         \r\n"
            loadingText = "Forcing VM to Hard Reset"
        elif command == "sysrq" and arg_characters is not None:
            def wrapper():
                return self.sendSysRq(arg_characters)
            func = wrapper
            successMessage = "Successfully sent SysRq command\r\n"
            failureMessage = "Failed to send SysRq command. Make sure the input only contains numbers and letters.\r\n"
            loadingText = "Sending SysRq to VM"
        else:
            return

        GV.loading = True

        th1 = threading.Thread(
            target=self.sendLoadingMessage, args=(loadingText,))
        th1.daemon = True
        th1.start()

        if self.loadWebSocketURL():
            def on_message(ws, _):
                GV.trycount += 1
                if func():
                    GV.loading = False
                    GV.terminatingApp = True
                    print(successMessage, end="")
                    ws.close()
                elif GV.trycount >= 2:
                    GV.loading = False
                    GV.terminatingApp = True
                    print(failureMessage, end="")
                    ws.close()

            wsapp = websocket.WebSocketApp(
                self.websocketURL + "?authorization=" + self.accessToken, on_message=on_message)
            wsapp.run_forever()
            GV.loading = False
            if GV.trycount == 0:
                error_message = "Could not establish connection to VM or VMSS."
                recommendation = 'Try restarting it with "az vm restart".'
                raise AzureConnectionError(
                    error_message, recommendation=recommendation)
        else:
            GV.loading = False
            error_message = "Could not establish connection to VM or VMSS."
            recommendation = "Make sure the parameters name/resource-group/vmss-instance are correct."
            raise ResourceNotFoundError(
                error_message, recommendation=recommendation)


def checkResource(cmd, resource_group_name, vm_vmss_name, vmss_instanceid):
    client = _compute_client_factory(cmd.cli_ctx)
    if vmss_instanceid:
        result = client.virtual_machine_scale_set_vms.get_instance_view(
            resource_group_name, vm_vmss_name, vmss_instanceid)
        print(result)
        if "windows" in result.additional_properties['osName'].lower():
            GV.OSIsWindows = True

        power_state = ','.join(
            [s.display_status for s in result.statuses if s.code.startswith('PowerState/')]).lower()
        if "deallocating" in power_state or "deallocated" in power_state:
            error_message = "Azure Serial Console requires a virtual machine to be running."
            recommendation = 'Use "az vmss start" to start the Virtual Machine.'
            raise AzureConnectionError(
                error_message, recommendation=recommendation)

        result = client.virtual_machine_scale_sets.get(
            resource_group_name, vm_vmss_name)
        recommendation = ('Use "az vmss update --name MyScaleSet --resource-group MyResourceGroup --set '
                          'virtualMachineProfile.diagnosticsProfile="{\"bootDiagnostics\": {\"Enabled\" : \"True\",'
                          '\"StorageUri\":\"https://mystorageacct.blob.core.windows.net/\"}}""'
                          'to enable boot diagnostics.')
        if not result.virtual_machine_profile.diagnostics_profile.boot_diagnostics.enabled:
            error_message = ("Azure Serial Console requires boot diagnostics to be enabled. Additionally, "
                             "Serial Console requires a custom boot diagnostics storage account to be "
                             "used, and is not yet fully compatible with managed boot diagnostics storage accounts.")
            raise AzureConnectionError(
                error_message, recommendation=recommendation)
        if result.virtual_machine_profile.diagnostics_profile.boot_diagnostics.storage_uri is None:
            error_message = ("Serial Console requires a custom boot diagnostics storage account to be used, "
                             "and is not yet fully compatible with managed boot diagnostics storage accounts.")
            raise AzureConnectionError(
                error_message, recommendation=recommendation)
    else:
        try:
            result = client.virtual_machines.get(
                resource_group_name, vm_vmss_name, expand='instanceView')
        except ComputeClientResourceNotFoundError as e:
            try:
                client.virtual_machine_scale_sets.get(
                    resource_group_name, vm_vmss_name)
            except ComputeClientResourceNotFoundError:
                raise e from e
            error_message = e.message
            recommendation = ("We found that you specified a Virtual Machine Scale Set and not a VM. "
                              "Use the --instance-id parameter to select the VMSS instance you want to connect to.")
            raise ResourceNotFoundError(
                error_message, recommendation=recommendation) from e

        if "windows" in result.instance_view.os_name.lower():
            GV.OSIsWindows = True

        power_state = ','.join(
            [s.display_status for s in result.instance_view.statuses if s.code.startswith('PowerState/')])
        if "deallocating" in power_state or "deallocated" in power_state:
            error_message = "Azure Serial Console requires a virtual machine to be running."
            recommendation = 'Use "az vm start" to start the Virtual Machine.'
            raise AzureConnectionError(
                error_message, recommendation=recommendation)

        recommendation = ('Use "az vm boot-diagnostics enable --name MyVM --resource-group MyResourceGroup '
                          '--storage https://mystor.blob.core.windows.net/" to enable boot diagnostics and '
                          'make sure to specify a storage account with the --storage parameter.')
        if not result.diagnostics_profile.boot_diagnostics.enabled:
            error_message = ("Azure Serial Console requires boot diagnostics to be enabled. Additionally, "
                             "Serial Console requires a custom boot diagnostics storage account to be "
                             "used, and is not yet fully compatible with managed boot diagnostics storage accounts.")
            raise AzureConnectionError(
                error_message, recommendation=recommendation)
        if result.diagnostics_profile.boot_diagnostics.storage_uri is None:
            error_message = ("Serial Console requires a custom boot diagnostics storage account to be used, "
                             "and is not yet fully compatible with managed boot diagnostics storage accounts.")
            raise AzureConnectionError(
                error_message, recommendation=recommendation)


def connect_serialconsole(cmd, resource_group_name, vm_vmss_name, vmss_instanceid=None):
    checkResource(cmd, resource_group_name, vm_vmss_name, vmss_instanceid)
    GV.serialConsoleInstance = SerialConsole(
        cmd, resource_group_name, vm_vmss_name, vmss_instanceid)
    GV.serialConsoleInstance.launchConsole()


def send_nmi_serialconsole(cmd, resource_group_name, vm_vmss_name, vmss_instanceid=None):
    checkResource(cmd, resource_group_name, vm_vmss_name, vmss_instanceid)
    GV.serialConsoleInstance = SerialConsole(
        cmd, resource_group_name, vm_vmss_name, vmss_instanceid)
    GV.serialConsoleInstance.connectAndSendAdminCommand("nmi")


def send_reset_serialconsole(cmd, resource_group_name, vm_vmss_name, vmss_instanceid=None):
    checkResource(cmd, resource_group_name, vm_vmss_name, vmss_instanceid)
    GV.serialConsoleInstance = SerialConsole(
        cmd, resource_group_name, vm_vmss_name, vmss_instanceid)
    GV.serialConsoleInstance.connectAndSendAdminCommand("reset")


def send_sysrq_serialconsole(cmd, resource_group_name, vm_vmss_name, sysrqinput, vmss_instanceid=None):
    checkResource(cmd, resource_group_name, vm_vmss_name, vmss_instanceid)
    if GV.OSIsWindows:
        error_message = "You can only send a SysRq to a Linux VM."
        raise ForbiddenError(error_message)
    GV.serialConsoleInstance = SerialConsole(
        cmd, resource_group_name, vm_vmss_name, vmss_instanceid)
    GV.serialConsoleInstance.connectAndSendAdminCommand(
        "sysrq", arg_characters=sysrqinput)
