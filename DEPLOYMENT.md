# Medical Voice Recognition PC - Deployment Structure

This repository follows the deployment structure from the origin/fix branch for `/var/www/webApp/` deployment.

## Structure:
- `webApp/` - Main Flask application package containing:
  - `__init__.py` - Flask app factory with SQLAlchemy context management
  - `models.py` - Database models with Flask-Login User model
  - `views.py` - Blueprint routes and view functions
  - `templates/` - Jinja2 templates
  - `static/` - CSS and static files
  - `instance/` - Instance-specific files and database
- `webapp.wsgi` - WSGI configuration file for Apache mod_wsgi
- `test.py` - Local development server entry point

## Key Features:
1. **Proper Flask-SQLAlchemy Context**: Database operations are performed within app context
2. **Flexible Instance Path**: Automatically uses `/var/www/webApp/webApp/instance` in production, local path in development
3. **Package Structure**: Clean Python package with proper imports
4. **WSGI Compatibility**: Ready for Apache mod_wsgi deployment

## Local Development:
```bash
python3 test.py
```

## Apache Deployment:
1. Copy entire repository to `/var/www/webApp/`
2. Configure Apache to use `webapp.wsgi`
3. Ensure `/var/www/webApp/webApp/instance/` directory exists with proper permissions

## Database Migration:
See `# Migration erstellen.txt` for Flask-Migrate commands.

This structure resolves the Flask-SQLAlchemy context errors when deploying with Apache mod_wsgi.