@echo off
REM Vercel Deployment Script for Windows
REM Run this from your project root to deploy to Vercel

echo.
echo 🚀 Ingredient Scanner - Vercel Deployment Script
echo ==================================================
echo.

REM Check if Git is initialized
if not exist ".git" (
    echo ❌ Git repository not initialized.
    echo 🔧 Initializing git...
    git init
    git add .
    git commit -m "Initial commit - ready for Vercel deployment"
    if errorlevel 1 (
        echo ❌ Git initialization failed. Make sure git is installed and configured.
        pause
        exit /b 1
    )
)

echo 📋 Pre-deployment Checklist:
echo   ✓ Git repository ready
echo.

REM Check if Vercel CLI is installed
where vercel >nul 2>nul
if errorlevel 1 (
    echo ❌ Vercel CLI not found.
    echo 🔧 Installing Vercel CLI globally...
    npm install -g vercel
    if errorlevel 1 (
        echo ❌ Failed to install Vercel CLI.
        echo   Make sure Node.js and npm are installed.
        echo   Download from: https://nodejs.org/
        pause
        exit /b 1
    )
)

echo   ✓ Vercel CLI installed
echo.

REM Get environment variables from user
echo 🔐 Environment Variables Setup
echo ================================
echo.
REM We'll let Vercel dashboard handle this for simplicity
echo ℹ️  You can set environment variables in two ways:
echo    1. Vercel Dashboard (Recommended for production)
echo    2. Command line with --env flags
echo.

REM Offer to deploy now
echo 📤 Ready to Deploy to Vercel!
echo ================================
echo.
echo Press any key to continue with deployment...
pause >nul

echo.
echo Starting Vercel deployment...
echo.

REM Deploy to Vercel
vercel deploy

if errorlevel 1 (
    echo.
    echo ❌ Deployment failed. Check the output above for errors.
    pause
    exit /b 1
)

echo.
echo ✅ Deployment complete!
echo.
echo 🌐 Your app is now live!
echo.
echo 📝 Next steps:
echo   1. Visit your Vercel dashboard to see the URL
echo   2. Set environment variables in Vercel Dashboard:
echo      - FLASK_ENV=production
echo      - SECRET_KEY=your-secure-key
echo   3. Test your app
echo   4. Check logs: vercel logs --tail
echo.
pause
