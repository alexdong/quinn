#!/bin/bash

# Platform-Independent Development Tools Installer
# Works on macOS (brew) and Ubuntu/Debian (apt)
# Uses uv for Python package management (following coding standards)
# Author: Alex Dong <me@alexdong.com>
#
# Troubleshooting:
# - If you get "rustup could not choose a version of cargo": Run `rustup default stable`
# - If cargo commands fail: Run `source ~/.cargo/env` and try again
# - If missing tools after install: Restart your shell or source your profile

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Detect platform
detect_platform() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt &> /dev/null; then
            echo "ubuntu"
        else
            log_error "Unsupported Linux distribution. This script requires apt."
            exit 1
        fi
    else
        log_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
}

# Check if command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Install Homebrew on macOS
install_homebrew() {
    if ! command_exists brew; then
        log_info "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # Add brew to PATH for Apple Silicon Macs
        if [[ -f /opt/homebrew/bin/brew ]]; then
            echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
            eval "$(/opt/homebrew/bin/brew shellenv)"
        fi
    else
        log_info "Homebrew already installed"
    fi
}

# Install Rust and Cargo
install_rust() {
    if ! command_exists cargo; then
        log_info "Installing Rust and Cargo..."
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable
        
        # Source cargo environment
        source "$HOME/.cargo/env"
        
        # Verify installation and set default toolchain if needed
        if ! rustup default stable 2>/dev/null; then
            log_info "Setting up default Rust toolchain..."
            rustup toolchain install stable
            rustup default stable
        fi
        
        # Add to shell profile
        local shell_file
        if [[ "$PLATFORM" == "macos" ]]; then
            shell_file="$HOME/.zshrc"
        else
            shell_file="$HOME/.bashrc"
        fi
        
        if ! grep -q 'source "$HOME/.cargo/env"' "$shell_file" 2>/dev/null; then
            echo 'source "$HOME/.cargo/env"' >> "$shell_file"
        fi
        
        # Verify cargo is working
        if ! command_exists cargo; then
            log_error "Cargo installation failed"
            exit 1
        fi
        
        log_success "Rust and Cargo installed successfully"
    else
        log_info "Rust already installed"
        
        # Ensure we have a default toolchain even if Rust was previously installed
        if ! rustup show 2>/dev/null | grep -q "default"; then
            log_info "Setting up default Rust toolchain..."
            rustup default stable 2>/dev/null || {
                rustup toolchain install stable
                rustup default stable
            }
        fi
    fi
}

# Install uv (Python package manager)
install_uv() {
    if command_exists uv; then
        log_info "uv already installed"
        return
    fi
    
    log_info "Installing uv..."
    if [[ "$PLATFORM" == "macos" ]]; then
        brew install uv
    else
        # Install uv via official installer (works on all platforms)
        curl -LsSf https://astral.sh/uv/install.sh | sh
        
        # Add uv to PATH for current session
        export PATH="$HOME/.cargo/bin:$PATH"
        
        # Add to shell profile
        local shell_file="$HOME/.bashrc"
        if ! grep -q 'export PATH="$HOME/.cargo/bin:$PATH"' "$shell_file" 2>/dev/null; then
            echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> "$shell_file"
        fi
    fi
}

# Install tools via package manager
install_package_manager_tools() {
    log_info "Installing package manager tools..."
    
    if [[ "$PLATFORM" == "macos" ]]; then
        # macOS with Homebrew
        local tools=(
            "curl"
            "jq" 
            "ripgrep"           # rg
            "hyperfine"
            "fd"
            "imagemagick"
            "ffmpeg"
            "sox"
            "audacity"
            "yt-dlp"
            "pandoc"
        )
        
        for tool in "${tools[@]}"; do
            if brew list "$tool" &>/dev/null; then
                log_warn "$tool already installed via brew"
            else
                log_info "Installing $tool via brew..."
                brew install "$tool"
            fi
        done
        
    else
        # Ubuntu/Debian with apt
        log_info "Updating package lists..."
        sudo apt update
        
        # Install basic tools
        local apt_tools=(
            "curl"
            "jq"
            "ripgrep"           # rg
            "hyperfine"
            "fd-find"           # creates fdfind binary
            "imagemagick" 
            "ffmpeg"
            "sox"
            "libsox-fmt-all"    # SoX format support
            "audacity"
            "pandoc"
        )
        
        for tool in "${apt_tools[@]}"; do
            if dpkg -l | grep -q "^ii  $tool "; then
                log_warn "$tool already installed via apt"
            else
                log_info "Installing $tool via apt..."
                sudo apt install -y "$tool"
            fi
        done
        
        # Create fd symlink if fdfind exists but fd doesn't
        if command_exists fdfind && ! command_exists fd; then
            mkdir -p ~/.local/bin
            ln -sf "$(which fdfind)" ~/.local/bin/fd
            log_success "Created fd symlink for fdfind"
        fi
        
        # Install yt-dlp via PPA
        if ! command_exists yt-dlp; then
            log_info "Installing yt-dlp via PPA..."
            sudo add-apt-repository ppa:tomtomtom/yt-dlp -y
            sudo apt update
            sudo apt install -y yt-dlp
        fi
    fi
}

# Install Rust-based tools via cargo
install_cargo_tools() {
    log_info "Installing Rust-based tools via cargo..."
    
    # Ensure cargo is in PATH and working
    if [[ -f "$HOME/.cargo/env" ]]; then
        source "$HOME/.cargo/env"
    fi
    
    # Verify cargo is working
    if ! command_exists cargo; then
        log_error "Cargo not found. Please ensure Rust is properly installed."
        return 1
    fi
    
    # Verify default toolchain
    if ! rustup show 2>/dev/null | grep -q "default"; then
        log_info "Setting up default Rust toolchain..."
        rustup default stable
    fi
    
    local cargo_tools=(
        "broot"
        "htmlq"
        "monolith"
        "rnr"
        "tailspin"          # tspin command
    )
    
    for tool in "${cargo_tools[@]}"; do
        if cargo install --list 2>/dev/null | grep -q "^$tool "; then
            log_warn "$tool already installed via cargo"
        else
            log_info "Installing $tool via cargo..."
            if cargo install --locked "$tool"; then
                log_success "$tool installed successfully"
            else
                log_error "Failed to install $tool"
            fi
        fi
    done
    
    # Special setup for broot
    if command_exists broot; then
        if [[ ! -f ~/.local/share/broot/launcher/bash/br ]]; then
            log_info "Setting up broot shell integration..."
            broot --install
        fi
    fi
}

# Install mise (development environment manager)
install_mise() {
    if command_exists mise; then
        log_warn "mise already installed"
        return
    fi
    
    log_info "Installing mise..."
    if [[ "$PLATFORM" == "macos" ]]; then
        brew install mise
    else
        # Ubuntu - use official installer
        curl https://mise.run | sh
        echo 'eval "$(~/.local/bin/mise activate bash)"' >> ~/.bashrc
    fi
    
    # Activate mise for current session
    if [[ -f ~/.local/bin/mise ]]; then
        eval "$(~/.local/bin/mise activate bash)"
    elif command_exists mise; then
        eval "$(mise activate bash)"
    fi
}

# Install llm (Python-based)
install_llm() {
    if command_exists llm; then
        log_warn "llm already installed"
        return
    fi
    
    log_info "Installing llm via uv..."
    uv tool install llm
    
    log_info "llm installed. Configure API keys with: llm keys set openai"
}

# Setup shell environment
setup_shell_environment() {
    log_info "Setting up shell environment..."
    
    local shell_file
    if [[ "$PLATFORM" == "macos" ]]; then
        shell_file="$HOME/.zshrc"
    else
        shell_file="$HOME/.bashrc"
    fi
    
    # Ensure ~/.local/bin is in PATH
    if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' "$shell_file" 2>/dev/null; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$shell_file"
        export PATH="$HOME/.local/bin:$PATH"
    fi
    
    # Ensure cargo bin is in PATH
    if ! grep -q 'source "$HOME/.cargo/env"' "$shell_file" 2>/dev/null; then
        echo 'source "$HOME/.cargo/env"' >> "$shell_file"
    fi
    
    log_success "Shell environment configured in $shell_file"
}

# Verify installations
verify_installations() {
    log_info "Verifying installations..."
    
    local tools=(
        "curl" "jq" "rg" "hyperfine" "fd" "broot" "htmlq" 
        "mise" "llm" "monolith" "rnr" "tspin" "convert" 
        "ffmpeg" "sox" "yt-dlp" "pandoc"
    )
    
    local missing=()
    
    for tool in "${tools[@]}"; do
        if command_exists "$tool"; then
            log_success "✓ $tool"
        else
            log_error "✗ $tool"
            missing+=("$tool")
        fi
    done
    
    # Special check for audacity (GUI app)
    if [[ "$PLATFORM" == "macos" ]]; then
        if [[ -d "/Applications/Audacity.app" ]]; then
            log_success "✓ audacity"
        else
            log_error "✗ audacity"
            missing+=("audacity")
        fi
    else
        if command_exists audacity; then
            log_success "✓ audacity"
        else
            log_error "✗ audacity"
            missing+=("audacity")
        fi
    fi
    
    if [[ ${#missing[@]} -eq 0 ]]; then
        log_success "All tools installed successfully!"
    else
        log_error "Missing tools: ${missing[*]}"
        log_info "You may need to restart your shell or run: source ~/.bashrc (or ~/.zshrc)"
        return 1
    fi
}

# Main installation function
main() {
    log_info "Starting development tools installation..."
    
    # Detect platform
    PLATFORM=$(detect_platform)
    log_info "Detected platform: $PLATFORM"
    
    # Install package managers
    if [[ "$PLATFORM" == "macos" ]]; then
        install_homebrew
    fi
    
    # Install core dependencies
    install_rust
    install_uv
    
    # Install tools
    install_package_manager_tools
    install_cargo_tools
    install_mise
    install_llm
    
    # Setup environment
    setup_shell_environment
    
    # Verify everything worked
    verify_installations
    
    log_success "Installation complete!"
    log_info "Please restart your shell or run:"
    if [[ "$PLATFORM" == "macos" ]]; then
        log_info "  source ~/.zshrc"
    else
        log_info "  source ~/.bashrc"
    fi
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
