# Deployment Instructions for Medical Voice Recognition PC

## Files for Apache/mod_wsgi Deployment

### Key Files:
- `webApp.py` - Main Flask application file 
- `webApp.wsgi` - WSGI configuration file for Apache
- `models.py` - Database models
- `views.py` - Application routes and views
- `requirements.txt` - Python dependencies

### Deployment Steps:

1. **Setup Server and Install Dependencies:**
   ```bash
   sudo apt update
   sudo apt install apache2 libapache2-mod-wsgi-py3 python3-pip
   sudo pip3 install -r requirements.txt
   ```

2. **Copy Files to Server:**
   Copy all application files to `/var/www/webApp/`

3. **Configure Apache Virtual Host:**
   Create `/etc/apache2/sites-available/webApp.conf`:
   ```apache
   <VirtualHost *:80>
       ServerName your-domain.com
       DocumentRoot /var/www/webApp
       WSGIDaemonProcess webapp python-path=/var/www/webApp
       WSGIProcessGroup webapp
       WSGIScriptAlias / /var/www/webApp/webApp.wsgi
       <Directory /var/www/webApp>
           WSGIApplicationGroup %{GLOBAL}
           Require all granted
       </Directory>
   </VirtualHost>
   ```

4. **Enable Site and Restart Apache:**
   ```bash
   sudo a2ensite webApp
   sudo systemctl reload apache2
   ```

### Fixed Issues:
- Flask-SQLAlchemy context initialization
- Proper WSGI application factory pattern
- Database table creation within app context
- Blueprint registration

### Database:
The application uses SQLite by default (`database.db`). The database and tables are automatically created when the application starts.