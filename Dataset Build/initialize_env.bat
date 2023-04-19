@echo off
conda info --envs | find "MedicalDesertEnv" > nul

if %errorlevel% equ 1 (
    echo Creating MedicalDesertEnv environment...
    conda env create -f MedicalDesertEnv.yml
)

echo Activating MedicalDesertEnv environment...
conda activate MedicalDesertEnv