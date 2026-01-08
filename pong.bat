@echo off
title Pong - Console
color 03

py game.py

if %errorlevel% NEQ 0 (
    pause >nul
)
exit /b 0