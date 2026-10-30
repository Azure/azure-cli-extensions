# Azure CLI nexusidentity Extension #

This is an extension to Azure CLI to manage nexusidentity resources.

## How to use ##

Install the extension:

```
az extension add --name nexusidentity
```

Validate that the extension is installed correctly:

```
az nexusidentity --help
```

## OpenSSH prerequisites ##

Key generation requires OpenSSH 9.4 or later with FIDO2 security-key support
and a connected security key. On Windows, run the command without administrator
privileges.

On Windows, `ssh-keygen.exe` is selected from the following locations, in order:

- `OpenSSH` under the Windows Program Files directory.
- `OpenSSH-Win64` under the Windows Program Files directory.
- `OpenSSH` under the Windows system directory (normally `C:\Windows\System32`).

The directories are obtained from Windows, not environment variables. Install
OpenSSH with administrator-managed permissions so ordinary users cannot replace
its binaries.

When 32-bit Azure CLI runs on 64-bit Windows (WOW64), native Program Files
installations are checked first, followed by the 32-bit Program Files
installations. The native Program Files directory is read from the 64-bit
machine registry view. The system candidate uses the Windows-provided
`Sysnative\OpenSSH` alias to bypass System32 filesystem redirection.
Architecture or directory lookup failures stop the command without falling back
to the current directory or `PATH`.

On Windows, the command uses the first executable found in that order; it does
not probe the OpenSSH version or search the current directory or `PATH`.
Installations in other locations are not automatically discovered. If no
executable is found in a supported location, the command reports an error.

On Linux, the existing `ssh-keygen` lookup through `PATH` is unchanged.
On either platform, key-generation failure stops the command before a public
key is uploaded.

## Included Features ##

Below is a high-level overview of nexusidentity commands.

| Commands                  | Description            |
|---------------------------|------------------------|
| az nexusidentity gen-keys | Manage key generation. |
