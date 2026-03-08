#!/bin/bash

# Setup script for bobobot_inst_ddd project

echo "🚀 Setting up bobobot_inst_ddd project..."

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo "🔧 Creating virtual environment..."
python -m venv .venv

# Activate virtual environment
echo "✅ Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -e ".[dev]"

# Copy .env.example to .env
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration"
fi

# Start Docker infrastructure
echo "🐳 Starting Docker infrastructure..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 5

# Run migrations
echo "🔄 Running database migrations..."
alembic upgrade head

# Run tests
echo "🧪 Running tests..."
pytest

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Start development: python -m src.main"
echo "3. Run tests: pytest"
echo ""
echo "Happy coding! 🎉"
