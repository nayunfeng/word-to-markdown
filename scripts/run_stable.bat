@echo off
setlocal

if "%~1"=="" goto usage
if "%~2"=="" goto usage

set INPUT_PATH=%~1
set OUTPUT_PATH=%~2

python main_stable.py convert --input "%INPUT_PATH%" --output "%OUTPUT_PATH%" --split-by-heading --extract-image --recursive
goto end

:usage
echo Usage: run_stable.bat ^<input_file_or_dir^> ^<output_dir^>
echo Example: run_stable.bat examples output

:end
endlocal
