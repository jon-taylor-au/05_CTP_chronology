@echo off
REM Run the first Python script
echo Running 01_webapp_extract.py...
python 01_webapp_extract.py
IF %ERRORLEVEL% NEQ 0 (
    echo 01_webapp_extract.py encountered an error. Exiting.
    exit /b %ERRORLEVEL%
)
echo 01_webapp_extract.py completed.

REM Run the second Python script
echo Running 02_chronology_create.py...
python 02_chronology_create.py
IF %ERRORLEVEL% NEQ 0 (
    echo 02_chronology_create.py encountered an error.
    exit /b %ERRORLEVEL%
)
echo 02_chronology_create.py completed.

echo Both scripts ran successfully.
exit /b 0
