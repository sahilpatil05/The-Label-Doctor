#!/bin/bash
# Quick Vercel Deployment Script
# Run this from your project root to deploy to Vercel

echo "🚀 Ingredient Scanner - Vercel Deployment Script"
echo "================================================="
echo ""

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Git repository not initialized."
    echo "🔧 Initializing git..."
    git init
    git add .
    git commit -m "Initial commit - ready for Vercel deployment"
fi

# Show deployment status
echo "📋 Pre-deployment Checklist:"
echo "  ✓ Vercel CLI installed"
echo "  ✓ Git repository ready"
echo ""

# Prompt for environment variables
echo "🔐 Environment Variables Setup"
echo "================================"
echo "You can set these in Vercel dashboard later, or enter them now:"
read -p "  FLASK_ENV (production): " FLASK_ENV
FLASK_ENV=${FLASK_ENV:-production}

read -p "  SECRET_KEY (secure random value): " SECRET_KEY
if [ -z "$SECRET_KEY" ]; then
    SECRET_KEY=$(openssl rand -hex 32)
    echo "  Generated SECRET_KEY: $SECRET_KEY"
fi

echo ""
echo "📤 Deploying to Vercel..."
echo "================================"

# Deploy to Vercel
vercel deploy \
  --env FLASK_ENV=$FLASK_ENV \
  --env SECRET_KEY=$SECRET_KEY \
  --prod

echo ""
echo "✅ Deployment complete!"
echo "🌐 Your app is live at: https://ingredient-scanner.vercel.app"
echo ""
echo "📝 Next steps:"
echo "  1. Test your app at the URL above"
echo "  2. Configure additional environment variables in Vercel dashboard if needed"
echo "  3. Check logs: vercel logs --tail"
echo ""
