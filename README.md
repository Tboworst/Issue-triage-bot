# Issue-Triage

A Flask application that automatically triages GitHub issues using webhooks, including automatic labeling, owner assignment, and stale issue management.

## Features

- 🔄 **Automatic Issue Labeling**: Labels issues based on keywords in title/body
- 👥 **Owner Assignment**: Assigns owners based on file paths mentioned
- 📝 **Checklist Comments**: Adds helpful checklists for issues with short descriptions
- 💬 **Slash Commands**: Process commands like `/close`, `/area`, `/priority` in comments
- ⏰ **Stale Issue Management**: Automatically marks and closes stale issues
- 🔐 **Secure Webhooks**: Validates GitHub webhook signatures

## Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment (no script needed)

Create a `.env` file in the project root. This file is loaded automatically by the app at startup.

```bash
# Create .env with a template (macOS/zsh)
cat > .env << 'EOF'
# GitHub Configuration
# Provide ONE of the following tokens
GITHUB_TOKEN=your_github_personal_access_token_here
# GITHUB_APP_TOKEN=your_github_app_token_here

# Webhook Configuration
GH_WEBHOOK_SECRET=your_webhook_secret_here

# Flask Configuration
SESSION_SECRET=your_session_secret_here
FLASK_ENV=development

# Database Configuration (optional)
# Defaults to SQLite at ./triage_bot.db if not set
# DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/dbname

# Stale Issue Configuration (optional)
STALE_DAYS=14
STALE_CLOSE_DAYS=30
EOF
```

Required variables:
- `GITHUB_TOKEN` (or `GITHUB_APP_TOKEN`): token with repo/issues permissions
- `GH_WEBHOOK_SECRET`: must match your GitHub webhook secret
- `SESSION_SECRET`: any random string (keep it secret)

### 3. GitHub Token Setup

1. Go to [GitHub Settings > Personal Access Tokens](https://github.com/settings/tokens)
2. Generate a new token with these permissions:
   - `repo`
   - `issues`
   - `pull_requests`

### 4. GitHub Webhook Setup

1. Go to your repository settings
2. Navigate to Webhooks
3. Add a new webhook:
   - Payload URL: `http://your-domain/webhook` (or `http://localhost:5000/webhook` for local tests)
   - Content type: `application/json`
   - Secret: same value as `GH_WEBHOOK_SECRET`
   - Events: select "Issues" and "Issue comments"

### 5. Run the Application

```bash
python main.py
```

The application will start on `http://localhost:5000`

## Usage

### Automatic Features

- **Issue Creation**: Automatically labels and assigns owners based on content
- **Short Issues**: Adds helpful checklist comments for issues with < 40 characters
- **Activity Tracking**: Updates last activity when issues are modified

### Slash Commands

Users can use these commands in issue comments:

| Command | Description | Example |
|---------|-------------|---------|
| `/close` | Close the issue | `/close` |
| `/area <area>` | Add area label | `/area frontend` |
| `/priority <level>` | Add priority label | `/priority high` |
| `/size <size>` | Add size label | `/size m` |
| `/assign <user>` | Assign user | `/assign @username` |

### Stale Issue Management

- Issues are marked as stale after `STALE_DAYS` (default: 14 days)
- Stale issues are closed after `STALE_CLOSE_DAYS` (default: 30 days)
- Add `pinned` label to prevent stale marking

## Configuration

### Label Rules

Edit `rules/labels.json` to customize automatic labeling:

```json
{
  "bug": ["error", "exception", "crash", "fail"],
  "feature": ["feature", "enhancement", "request"],
  "documentation": ["docs", "documentation", "readme"]
}
```

### Owner Rules

Edit `rules/owners.json` to customize owner assignment:

```json
{
  "src/api/": ["api-team", "backend-team"],
  "src/web/": ["frontend-team", "ui-team"],
  "docs/": ["docs-team", "technical-writers"]
}
```

## Development

### Project Structure

```
Issue-Triage/
├── app.py              # Flask application setup
├── main.py             # Application entry point
├── models.py           # Database models
├── github_client.py    # GitHub API client
├── rules_manager.py    # Label and owner rules
├── security.py         # Webhook signature verification
├── handlers/           # Event handlers
│   ├── issues.py       # Issue event handling
│   ├── comments.py     # Comment event handling
│   └── stale.py        # Stale issue management
├── routes/             # Flask routes
│   └── webhook.py      # Webhook endpoint
└── rules/              # Configuration files
    ├── labels.json     # Label rules
    └── owners.json     # Owner rules
```

### Running in Development

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment (create .env as shown above)

# Run with debug mode
python main.py
```

## Troubleshooting

### Common Issues

1. "Invalid webhook signature": Ensure `GH_WEBHOOK_SECRET` matches your GitHub webhook secret
2. "GitHub client not initialized": Check that `GITHUB_TOKEN` is set correctly
3. Database errors: Ensure the application has write permissions in the current directory

### Logs

The application logs to stdout. Check for:
- Webhook events received
- GitHub API calls
- Database operations
- Error messages

## License

This project is open source and available under the MIT License.
