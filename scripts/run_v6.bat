@echo off
setlocal

if "%~1"=="" goto usage
if "%~2"=="" goto usage

set INPUT_PATH=%~1
set OUTPUT_PATH=%~2

python main_v6.py convert --input "%INPUT_PATH%" --output "%OUTPUT_PATH%" --split-by-heading --extract-image --recursive
goto end

:usage
echo Usage: run_v6.bat ^<input_file_or_dir^> ^<output_dir^>
echo Example: run_v6.bat examples output

:end
endlocal
