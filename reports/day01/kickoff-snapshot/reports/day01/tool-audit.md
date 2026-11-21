# Day 1 tool audit

Check date: **2026-11-12, Asia/Calcutta** (project/client date). Checks ran in host PowerShell with working directory `D:\good_projects\shiftwatch`.

This records actual observations from the initial read-only audit. The folder inventory below predates creation of project instructions, state, the canonical plan, and this report; it is not a claim about the current inventory. Setup availability does not establish Day 1 completion. No packages were installed, Git initialized, code trained, or other projects changed during the audit.

## Initial project inventory

Commands:

```powershell
Get-ChildItem -LiteralPath 'D:\good_projects\shiftwatch' -Force | Select-Object Mode, Length, Name
rg --files --hidden -g AGENTS.md -g PROJECT_STATE.md -g pyproject.toml -g requirements*.txt -g uv.lock -g poetry.lock -g Pipfile* -g Dockerfile* -g compose*.yml -g docker-compose*.yml -g .python-version -g pyvenv.cfg -g '!node_modules' -g '!.git' -g '!.venv/Lib/**' -g '!venv/Lib/**'
```

Observed inventory:

```text
Mode  Length Name
----  ------ ----
-a---  57158 ShiftWatch-14-Day-Plan-shiftwatch
```

The `rg` search returned no matching configuration files (exit code 1).

Additional checks:

```powershell
git -C 'D:\good_projects\shiftwatch' rev-parse --is-inside-work-tree
@('.venv','venv','env','.git','AGENTS.md','PROJECT_STATE.md','ShiftWatch-14-Day-Plan.md') | ForEach-Object { [PSCustomObject]@{ ProjectEntry = $_; Exists = Test-Path -LiteralPath (Join-Path 'D:\good_projects\shiftwatch' $_) } }
```

Git output:

```text
fatal: not a git repository (or any of the parent directories): .git
```

All seven `Test-Path` results were `False`. The PowerShell table inherited columns from preceding output and did not display the individual entry labels; the tested entries are recorded explicitly in the command above.

## Executable discovery

Command:

```powershell
$toolNames = @('python','python3','py','pip','git','docker','bash'); foreach ($toolName in $toolNames) { $toolCommands = Get-Command $toolName -ErrorAction SilentlyContinue; if ($toolCommands) { $toolCommands | Select-Object Name, CommandType, Source } else { Write-Output "MISSING: $toolName" } }
```

Observed results:

| Name | Type | Source/result |
| --- | --- | --- |
| python.exe | Application | `C:\Python313\python.exe` |
| python3.exe | Application | `C:\Users\ADITYA CHHIMWAL\AppData\Local\Microsoft\WindowsApps\python3.exe` |
| py.exe | Application | `C:\Windows\py.exe` |
| pip.exe | Application | `C:\Python313\Scripts\pip.exe` |
| git.exe | Application | `C:\Program Files\Git\cmd\git.exe` |
| docker.exe | Application | `C:\Users\ADITYA CHHIMWAL\AppData\Local\Programs\DockerDesktop\resources\bin\docker.exe` |
| bash | Not resolved | `MISSING: bash` |

`python3.exe` was discovered but was not executed; the WindowsApps entry alone does not verify a working interpreter.

## Python, pip, and Git versions

Commands:

```powershell
python --version
python -m pip --version
py -0p
git --version
```

Observed outputs, in order:

```text
Python 3.13.3
pip 25.0.1 from C:\Python313\Lib\site-packages\pip (python 3.13)
 -V:3.13 *        C:\Python313\python.exe
git version 2.47.1.windows.2
```

The Python launcher listed only Python 3.13. Compatibility of future project dependencies with this interpreter was not tested.

## Docker CLI and daemon

Commands (daemon probe bounded by a 15-second job wait):

```powershell
docker --version
$dockerCheck = Start-Job -ScriptBlock { & 'C:\Users\ADITYA CHHIMWAL\AppData\Local\Programs\DockerDesktop\resources\bin\docker.exe' version --format '{{json .}}' }
$dockerFinished = Wait-Job -Job $dockerCheck -Timeout 15
if ($dockerFinished) { Receive-Job -Job $dockerCheck } else { Stop-Job -Job $dockerCheck; Write-Output 'DOCKER_DAEMON_CHECK_TIMEOUT_AFTER_15_SECONDS' }
Remove-Job -Job $dockerCheck
```

Observed outputs:

```text
Docker version 29.7.2, build a7dcaa6
{"Client":{"Version":"29.7.2","ApiVersion":"1.55","DefaultAPIVersion":"1.55","GitCommit":"a7dcaa6","GoVersion":"go1.26.5","Os":"windows","Arch":"amd64","BuildTime":"Wed Aug  5 18:31:33 2026","Context":"desktop-linux"},"Server":null}
failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine; check if the path is correct and if the daemon is running: open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.
```

The CLI is installed and responds. A usable Docker daemon was **not** verified: the selected `desktop-linux` endpoint was unavailable. The probe returned before the timeout; no timeout marker appeared. The outer PowerShell command finished with exit code 0 after job cleanup, which must not be interpreted as successful daemon connectivity.

## Git Bash availability

Commands:

```powershell
$bashPaths = @('C:\Program Files\Git\bin\bash.exe','C:\Program Files\Git\usr\bin\bash.exe','C:\Program Files\Git\git-bash.exe'); foreach ($bashPath in $bashPaths) { [PSCustomObject]@{ Path = $bashPath; Exists = Test-Path -LiteralPath $bashPath -PathType Leaf } }
if (Test-Path -LiteralPath 'C:\Program Files\Git\bin\bash.exe' -PathType Leaf) { & 'C:\Program Files\Git\bin\bash.exe' --version | Select-Object -First 1 }
```

All three executable paths existed. Explicit Bash invocation produced this error instead of a version:

```text
      0 [main] bash (18472) C:\Program Files\Git\bin\..\usr\bin\bash.exe: *** fatal error - NtCreateDirectoryObject(\BaseNamedObjects\msys-2.0S5-1888ae32e00d56aa): 0xC0000022
```

Bash was not resolved from this tool session's PATH, despite installed Git Bash executables. The explicit invocation encountered access denial in this execution environment. This does not establish that the user's interactive Git Bash terminal is broken; its usability and the user's preferred terminal remain unverified.

## Limits of this evidence

- No dependency import, installation, service, container build, or project test was run.
- No credentials or complete environment-variable dumps were requested or recorded.
- Docker daemon access and Bash execution require follow-up before either can be claimed operational.
- Creating this report and subsequent project documentation changes the initial inventory; preserve the observation as historical evidence.
