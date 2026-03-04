#!/bin/bash
# Installation script for Autonomous Agent Orchestration Skill System

set -e

echo "================================"
echo "Installing Agent Skill System"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Paths
SKILLS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ORCHESTRATOR_DIR="$HOME/composio-orchestrator"
MEMORY_DIR="$HOME/persistent-agent-memory"

echo "Skills directory: $SKILLS_DIR"

# Check prerequisites
echo -e "\n${YELLOW}Checking prerequisites...${NC}"

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ Python found: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}✗ Python 3 not found. Please install Python 3.10+${NC}"
    exit 1
fi

# Check Git
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version)
    echo -e "${GREEN}✓ Git found: $GIT_VERSION${NC}"
else
    echo -e "${RED}✗ Git not found. Please install Git 2.25+${NC}"
    exit 1
fi

# Check Ollama
if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✓ Ollama found${NC}"
else
    echo -e "${YELLOW}! Ollama not found. Install from https://ollama.ai${NC}"
fi

# Check for required Ollama models
echo -e "\n${YELLOW}Checking Ollama models...${NC}"
REQUIRED_MODELS=("qwen2.5:14b" "qwen2.5-coder:14b")
for model in "${REQUIRED_MODELS[@]}"; do
    if ollama list 2>/dev/null | grep -q "$model"; then
        echo -e "${GREEN}✓ Model found: $model${NC}"
    else
        echo -e "${YELLOW}! Model not found: $model. Pull with: ollama pull $model${NC}"
    fi
done

# Install Python dependencies
echo -e "\n${YELLOW}Installing Python dependencies...${NC}"
pip3 install --user requests 2>/dev/null || pip install --user requests 2>/dev/null || echo "Note: requests package may need manual installation"

# Setup Persistent Memory
echo -e "\n${YELLOW}Setting up Persistent Memory...${NC}"
if [ -d "$MEMORY_DIR" ]; then
    cd "$MEMORY_DIR"
    if [ -f "scripts/init_databases.py" ]; then
        python3 scripts/init_databases.py
        echo -e "${GREEN}✓ Persistent memory databases initialized${NC}"
    else
        echo -e "${YELLOW}! init_databases.py not found. Skipping database init.${NC}"
    fi
else
    echo -e "${YELLOW}! persistent-agent-memory not found at $MEMORY_DIR${NC}"
fi

# Create symlinks for easy access
echo -e "\n${YELLOW}Creating convenience symlinks...${NC}"
mkdir -p "$HOME/.local/bin"

# Strategic autonomy CLI
if [ -f "$SKILLS_DIR/strategic-autonomy/scripts/strategic_autonomy.py" ]; then
    chmod +x "$SKILLS_DIR/strategic-autonomy/scripts/strategic_autonomy.py"
    ln -sf "$SKILLS_DIR/strategic-autonomy/scripts/strategic_autonomy.py" "$HOME/.local/bin/strategic-autonomy" 2>/dev/null || true
    echo -e "${GREEN}✓ Created symlink: strategic-autonomy${NC}"
fi

# Memory bridge CLI
if [ -f "$SKILLS_DIR/agent-memory-bridge/scripts/memory_bridge.py" ]; then
    chmod +x "$SKILLS_DIR/agent-memory-bridge/scripts/memory_bridge.py"
    ln -sf "$SKILLS_DIR/agent-memory-bridge/scripts/memory_bridge.py" "$HOME/.local/bin/memory-bridge" 2>/dev/null || true
    echo -e "${GREEN}✓ Created symlink: memory-bridge${NC}"
fi

# Create orchestrator config if it doesn't exist
echo -e "\n${YELLOW}Setting up Orchestrator configuration...${NC}"
ORCHESTRATOR_CONFIG="$HOME/agent-orchestrator.yaml"
if [ ! -f "$ORCHESTRATOR_CONFIG" ]; then
    cat > "$ORCHESTRATOR_CONFIG" << 'EOF'
# Agent Orchestrator Configuration
port: 3000

defaults:
  runtime: tmux
  agent: claude-code
  workspace: worktree
  notifiers: [desktop]

# Example project (modify for your repos)
projects:
  example:
    repo: owner/example
    path: ~/example
    defaultBranch: main
    sessionPrefix: ex

reactions:
  ci-failed:
    auto: true
    action: send-to-agent
    retries: 2
  changes-requested:
    auto: true
    action: send-to-agent
    escalateAfter: 30m
EOF
    echo -e "${GREEN}✓ Created example orchestrator config: $ORCHESTRATOR_CONFIG${NC}"
    echo -e "${YELLOW}  Edit this file to add your projects${NC}"
else
    echo -e "${GREEN}✓ Orchestrator config already exists${NC}"
fi

# Build Qwen tentacle plugin if Node.js is available
echo -e "\n${YELLOW}Checking for Node.js (for plugin build)...${NC}"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓ Node.js found: $NODE_VERSION${NC}"
    
    if [ -d "$ORCHESTRATOR_DIR" ]; then
        echo "Building Agent Orchestrator (this may take a while)..."
        cd "$ORCHESTRATOR_DIR"
        
        # Check if pnpm is available
        if command -v pnpm &> /dev/null; then
            pnpm install 2>/dev/null || echo "Note: pnpm install may need to be run manually"
            pnpm build 2>/dev/null || echo "Note: Build may need to be run manually"
            echo -e "${GREEN}✓ Agent Orchestrator built${NC}"
        else
            echo -e "${YELLOW}! pnpm not found. Install with: npm install -g pnpm${NC}"
        fi
    else
        echo -e "${YELLOW}! composio-orchestrator not found at $ORCHESTRATOR_DIR${NC}"
    fi
else
    echo -e "${YELLOW}! Node.js not found. Install Node.js 20+ to build the orchestrator${NC}"
fi

# Create wrapper script
echo -e "\n${YELLOW}Creating integration wrapper...${NC}"
WRAPPER_SCRIPT="$HOME/.local/bin/agent-skill"
cat > "$WRAPPER_SCRIPT" << EOF
#!/bin/bash
# Agent Skill System Wrapper

SKILLS_DIR="$SKILLS_DIR"

show_help() {
    cat << 'HELP'
Agent Skill System - Available Commands:

  strategic-autonomy <command> [options]
    analyze    - Comprehensive strategic analysis
    execute    - Fully autonomous execution
    improve    - Recall and improve past work
    learn      - Learn from feedback
    boot       - Boot with memory context

  memory-bridge <command> [options]
    boot       - Generate boot context
    writeback  - Write back results
    spawn      - Spawn orchestrated agent
    swarm      - Deploy agent swarm
    recall     - Recall similar work

  Python API:
    from skills.integrated_autonomous_skill import get_integrated_skill
    skill = get_integrated_skill()
    result = skill.strategic_analyze("Your objective")

Examples:
  strategic-autonomy analyze -o "Refactor auth system" -d comprehensive
  strategic-autonomy execute -o "Add OAuth2 login" -c "Use JWT" -c "Support Google"
  memory-bridge spawn --project myapp --role coder
  memory-bridge swarm --objective "Implement payment system" --project myapp

For more help: cat $SKILLS_DIR/SKILL.md
HELP
}

case "\$1" in
    help|--help|-h)
        show_help
        ;;
    status)
        echo "=== Agent Skill System Status ==="
        echo "Skills directory: \$SKILLS_DIR"
        echo "Memory base: ~/persistent-agent-memory"
        
        # Check Ollama
        if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            echo "Ollama: Running"
        else
            echo "Ollama: Not running (start with: ollama serve)"
        fi
        
        # Check memory
        if [ -d ~/persistent-agent-memory/data ]; then
            echo "Memory databases: Initialized"
        else
            echo "Memory databases: Not initialized (run install.sh)"
        fi
        ;;
    *)
        show_help
        ;;
esac
EOF
chmod +x "$WRAPPER_SCRIPT"
echo -e "${GREEN}✓ Created wrapper: agent-skill${NC}"

# Final instructions
echo -e "\n${GREEN}================================"
echo "Installation Complete!"
echo "================================${NC}"

echo -e "\nNext steps:"
echo "1. Ensure Ollama is running: ollama serve"
echo "2. Pull required models: ollama pull qwen2.5:14b"
echo "3. Edit ~/agent-orchestrator.yaml to add your projects"
echo "4. Run: strategic-autonomy analyze -o 'Your objective'"

echo -e "\nAvailable commands:"
echo "  strategic-autonomy  - Main autonomous skill CLI"
echo "  memory-bridge       - Memory and orchestration bridge"
echo "  agent-skill         - System status and help"

echo -e "\nDocumentation: cat $SKILLS_DIR/SKILL.md"

# Check PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo -e "\n${YELLOW}Note: Add ~/.local/bin to your PATH:${NC}"
    echo '  export PATH="$HOME/.local/bin:$PATH"'
    echo "  Add this to your ~/.bashrc or ~/.zshrc"
fi
