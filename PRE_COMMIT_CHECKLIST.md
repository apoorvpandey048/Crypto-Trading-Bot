# Pre-Commit Checklist

Before pushing to GitHub, verify:

## ✅ Security Checks

- [ ] No API keys in code (check all test files)
- [ ] No passwords or secrets in code
- [ ] `.env` file is in `.gitignore`
- [ ] `.env.example` contains only placeholder values
- [ ] Database files (*.db) are in `.gitignore`
- [ ] Log files (*.log) are in `.gitignore`
- [ ] `venv/` and `node_modules/` are in `.gitignore`

## ✅ Code Quality

- [ ] All test files have placeholder API keys
- [ ] No personal information (names, emails, IPs) in code
- [ ] All imports work correctly
- [ ] No absolute paths (use relative paths)
- [ ] Requirements.txt is up to date

## ✅ Documentation

- [ ] README.md is complete and accurate
- [ ] SETUP_GUIDE.md is clear for new users
- [ ] All .md files are properly formatted
- [ ] Links in documentation work
- [ ] API endpoints are documented

## ✅ Functionality

- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Can register new user
- [ ] Can login successfully
- [ ] API documentation loads at /docs

## ✅ Git

- [ ] All changes are committed
- [ ] Commit messages are descriptive
- [ ] `.gitignore` is comprehensive
- [ ] No sensitive files in staging area

## Commands to Run Before Push

```bash
# Check for sensitive data
git grep -i "password\|secret\|api_key" -- ':!*.md' ':!.gitignore'

# Check what will be committed
git status

# Verify .gitignore is working
git check-ignore backend/.env backend/crypto_trading.db backend/*.log

# Review all changes
git diff

# Stage all files
git add .

# Commit
git commit -m "Initial commit - Crypto Trading Bot"

# Push to GitHub
git push origin main
```

## Final Verification

After pushing:
- [ ] Clone repository in a new location
- [ ] Follow SETUP_GUIDE.md
- [ ] Verify application runs correctly
- [ ] Check GitHub repository - no sensitive data visible
