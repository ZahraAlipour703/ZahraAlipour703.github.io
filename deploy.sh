#!/bin/bash

echo "=========================================="
echo "  Personal Website Deployment"
echo "  Ali Torabi - GitHub Pages"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo -e "${BLUE}→${NC} Initializing Git repository..."
    git init
    echo -e "${GREEN}✓${NC} Git initialized"
else
    echo -e "${GREEN}✓${NC} Git repository already exists"
fi

# Check if remote exists
if ! git remote get-url origin &>/dev/null; then
    echo ""
    echo -e "${YELLOW}⚠️  Important:${NC} Have you created the repository on GitHub?"
    echo -e "   Repository name must be: ${BLUE}selfishout.github.io${NC}"
    echo -e "   Create it at: https://github.com/new"
    echo ""
    read -p "Have you created the repository? (y/n) " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo -e "${YELLOW}Please create the repository first:${NC}"
        echo "  1. Go to: https://github.com/new"
        echo "  2. Repository name: selfishout.github.io"
        echo "  3. Make it Public"
        echo "  4. Don't initialize with README"
        echo "  5. Create repository"
        echo ""
        echo "Then run this script again!"
        exit 1
    fi
    
    echo ""
    echo -e "${BLUE}→${NC} Adding GitHub remote..."
    git remote add origin https://github.com/selfishout/selfishout.github.io.git
    echo -e "${GREEN}✓${NC} Remote added"
fi

# Stage all files
echo ""
echo -e "${BLUE}→${NC} Staging files..."
git add .
echo -e "${GREEN}✓${NC} Files staged"

# Commit
echo ""
echo -e "${BLUE}→${NC} Creating commit..."
git commit -m "Deploy personal website: Professional portfolio for Ali Torabi

Features:
- Modern, responsive design
- Research interests and publications
- 12 Computer Vision & ML projects showcase
- Professional experience timeline
- Contact information and social links
- Smooth animations and interactive UI

Technologies: HTML5, CSS3, JavaScript, AOS, Font Awesome"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Commit created"
else
    echo -e "${YELLOW}!${NC} No changes to commit (or already committed)"
fi

# Rename branch to main
echo ""
echo -e "${BLUE}→${NC} Ensuring main branch..."
git branch -M main
echo -e "${GREEN}✓${NC} Branch set to main"

# Push to GitHub
echo ""
echo -e "${BLUE}→${NC} Pushing to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo -e "  ${GREEN}Deployment Successful!${NC}"
    echo "=========================================="
    echo ""
    echo -e "Your website will be live at:"
    echo -e "  ${BLUE}https://selfishout.github.io${NC}"
    echo ""
    echo -e "⏰ Please wait 1-2 minutes for GitHub to build your site."
    echo ""
    echo "Next steps:"
    echo "  1. Check deployment status:"
    echo "     https://github.com/selfishout/selfishout.github.io/actions"
    echo ""
    echo "  2. Verify GitHub Pages settings:"
    echo "     https://github.com/selfishout/selfishout.github.io/settings/pages"
    echo ""
    echo "  3. Visit your website:"
    echo "     https://selfishout.github.io"
    echo ""
    echo "  4. Share on LinkedIn and add to your resume!"
    echo ""
    echo "=========================================="
else
    echo ""
    echo -e "${RED}✗${NC} Push failed. Please check:"
    echo "  1. Repository exists: selfishout.github.io"
    echo "  2. You have correct permissions"
    echo "  3. Authentication is set up (gh auth login)"
    echo ""
    echo "For help with authentication:"
    echo "  Run: gh auth login"
    echo "  Or: git push -u origin main (and enter credentials)"
fi

