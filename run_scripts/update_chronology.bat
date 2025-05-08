@echo off
setlocal enabledelayedexpansion

REM --- Configuration ---
set "csv_file=\\V0050\05_CTP_chronology\00_courtbooks_to_get.csv"
set "log_file=\\V0050\05_CTP_chronology\watcher.log"
set "script_log_file=\\V0050\05_CTP_chronology\07_main.log"
set "progress_log=\\V0050\05_CTP_chronology\run_scripts\progress.log"
set "trigger_phrase=Script started successfully"
set "max_wait=3600"  REM Max total wait time in seconds
set "folder_to_poll=\\V0050\05_CTP_chronology\run_scripts\processed" REM Folder to monitor for new files

color 1F
title CHRONOLOGY UPDATE TOOL

:menu
cls
echo ==================================================
echo               CHRONOLOGY UPDATE TOOL
echo ==================================================
echo.
echo ** Make sure Windows task 'CTP Watcher' is running **
echo.
echo 0. Exit
echo 1. Help - what does this tool do?
echo 2. Update the chronology for a book
echo.
set /p choice=Choose an option: 

if "%choice%"=="1" goto help
if "%choice%"=="2" goto single
if "%choice%"=="0" exit
goto menu

:help
cls
echo ==================== HELP ========================
echo.
echo The Chronology Update Tool is an automated workflow designed to process book documents 
echo from our internal CTP web app and generate detailed medical chronologies using the Brew 
echo platform LLM. Once a new entry is detected, the tool launches a series of Python scripts 
echo that systematically extract, analyse, and reformat relevant content from each document.
echo.
echo The process starts with data extraction from the firm's internal web application, followed 
echo by the generation of medical chronologies in manageable chunks. These chunks are then 
echo merged into a complete chronology document. 
echo.
echo The tool proceeds to post-process the data, cleaning and refining the output for consistency 
echo and clarity. Next, it builds a structured payload for writeback to the target system. 
echo Before this final step is executed, the user is prompted to confirm whether they wish to proceed 
echo with the writeback. If approved, the tool completes the writeback and performs final cleanup 
echo tasks to reset the environment, ensuring the system is ready for the next round of processing.
echo.
pause
goto menu

:single
cls
echo ========== PROCESSING A BOOK ===============
echo.

REM Read last submitted ID from the CSV (second line of the file)
set "last_id="
for /f "skip=1 delims=" %%i in ('type "%csv_file%"') do (
    set "last_id=%%i"
    goto :show_input_prompt
)

:show_input_prompt
if defined last_id (
    echo Last submitted Courtbook ID was: %last_id%
    echo.
)

set /p user_input=Enter the courtbook ID you want to process: 

REM Check if the entered ID is the same as the previous one
if "%user_input%"=="%last_id%" (
    echo.
    echo ERROR: You entered the same ID as last time. Please enter a different Courtbook ID.
    pause
    goto single
)

REM Truncate the CSV and write new job
attrib -R "%csv_file%" >nul 2>&1
(
    echo ID
    echo %user_input%
) > "%csv_file%"

REM Confirm the file was written
if exist "%csv_file%" (
    echo.
    echo SUCCESS: ID %user_input% submitted for processing.
) else (
    echo.
    echo ERROR: Failed to write to %csv_file%
    echo Please check that the file path exists and is writable.
    pause
    goto menu
)


REM Clear progress log
type nul > "%progress_log%"

REM Poll the folder for new content (new files)
echo.
echo Waiting for the process to complete by checking for new content...
set /a wait_time=0

:wait_for_completion
set /a wait_time+=1
set /a total_seconds=wait_time * 5
cls
echo ================================== LIVE PROGRESS ====================================
echo NOTE: waiting for process to start - max 90sec... [Elapsed: !total_seconds! seconds]
echo -------------------------------------------------------------------------------------
powershell -Command "Get-Content -Path '%progress_log%' -Tail 20"
echo -------------------------------------------------------------------------------------

REM Check if any new file exists in the folder
for %%F in (%folder_to_poll%\*) do (
    echo New file found: %%F

    REM Create archive folder if it doesn't exist
    if not exist "%folder_to_poll%\archived" (
        mkdir "%folder_to_poll%\archived"
        
    )

    REM Move the .zip file to the archived folder
    move "%folder_to_poll%\*.zip" "%folder_to_poll%\archived\" >nul 2>&1

    echo.
    echo Process completed successfully.
    echo Archive complete: ZIP file moved to 'processed/archived'.

    pause
    goto menu
)

timeout /t 5 >nul
goto wait_for_completion

