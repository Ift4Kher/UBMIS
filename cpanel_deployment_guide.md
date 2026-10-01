# cPanel Deployment Guide - University Bus Management System

This guide provides step-by-step instructions to get your Django project live on a cPanel hosting environment using the **"Setup Python App"** tool.

## Prerequisites
1. A registered Domain Name.
2. cPanel Hosting with Python support.
3. MySQL Database access in cPanel.

---

## Step 1: Prepare Your Files
1. **Compress your project files**: Select all files in your project folder (except `venv`, `.git`, and `__pycache__`) and create a `.zip` archive.
2. **Note**: Ensure `passenger_wsgi.py` and `requirements.txt` are included in the root of your zip.

## Step 2: Upload Files to cPanel
1. Log in to **cPanel** and open **File Manager**.
2. Create a new folder for your project (e.g., `/home/username/ubmis_app`). 
   > [!IMPORTANT]
   > Do NOT upload directly into `public_html` yet. Put the project files in a separate folder for security.
3. Upload and extract your `.zip` file into this folder.

## Step 3: Create a Database
1. Go to **cPanel > MySQL Database Wizard**.
2. Create a database (e.g., `username_ubmis`).
3. Create a user (e.g., `username_admin`) and set a strong password.
4. Add the user to the database with **All Privileges**.

## Step 4: Configure Settings for Production
1. In cPanel File Manager, edit `ubmis_project/settings.py`:
   - Set `DEBUG = False`.
   - Update `ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']`.
   - Update `DATABASES` with your new cPanel database name, username, and password:
     ```python
     DATABASES = {
         'default': {
             'ENGINE': 'django.db.backends.mysql',
             'NAME': 'username_ubmis',
             'USER': 'username_admin',
             'PASSWORD': 'your_password',
             'HOST': 'localhost',
             'PORT': '3306',
         }
     }
     ```
   - Add `STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')` at the bottom of the file.

## Step 5: Setup Python App
1. Go to **cPanel > Setup Python App**.
2. Click **Create Application**.
3. **Python Version**: Select `3.10` or higher.
4. **Application root**: Enter your folder name (e.g., `ubmis_app`).
5. **Application URL**: Select your domain.
6. **Application startup file**: Enter `passenger_wsgi.py`.
7. **Application Entry point**: Leave it as `application`.
8. Click **Create**.

## Step 6: Install Dependencies
1. After creating the app, look for the section **"Run Pip Install"**. 
2. Choose `requirements.txt` and click **Install**.
   - Wait for it to complete.

## Step 7: Run Migrations and Collect Static
1. Copy the command shown at the top of the Python App page (it looks like `source /home/username/nodevenv/ubmis_app/.../bin/activate`).
2. Open **cPanel > Terminal**.
3. Paste the command and press Enter to activate the virtual environment.
4. Run the following commands:
   ```bash
   cd ~/ubmis_app
   python manage.py migrate
   python manage.py collectstatic --noinput
   python manage.py create_superuser
   ```

## Step 8: Final Touches
1. Go back to **cPanel > Setup Python App** and click **Restart Application**.
2. Visit your domain to see the live project!

---

> [!TIP]
> **Static Files Fix**: If images/CSS don't load, ensure your cPanel Python app settings point to the `staticfiles` folder for static content, or use a Symbolic Link in File Manager:
> `ln -s /home/username/ubmis_app/staticfiles /home/username/public_html/static`
