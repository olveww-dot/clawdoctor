#!/bin/bash
# ClawDoctor Installation Script

echo "🦞 Installing ClawDoctor..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Install psutil
echo "📦 Installing psutil..."
pip3 install psutil --user

# Create symlink for easy access
echo "🔗 Creating shortcuts..."
mkdir -p ~/.local/bin
ln -sf "$(pwd)/clawdoctor_simple.py" ~/.local/bin/clawdoctor
ln -sf "$(pwd)/server_simple.py" ~/.local/bin/clawdoctor-server

# Add to PATH if not already
echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> ~/.zshrc
echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> ~/.bashrc

echo ""
echo "✅ ClawDoctor installed successfully!"
echo ""
echo "Usage:"
echo "  clawdoctor --status    # Check status"
echo "  clawdoctor --fix       # One-click fix"
echo "  clawdoctor --scan      # Security scan"
echo "  clawdoctor-server      # Start web dashboard"
echo ""
echo "Then open: http://127.0.0.1:8080/dashboard.html"
