# Deployment Guide - Neural Navigator

This guide shows you how to deploy Neural Navigator online for free.

## Option 1: PythonAnywhere (Recommended)

### Steps:

1. **Sign up**
   - Go to https://www.pythonanywhere.com
   - Create free account

2. **Upload Code**
   - Go to "Files" tab
   - Upload your project or clone from GitHub:
     ```bash
     git clone https://github.com/TheMichael/MiniGridGame.git
     ```

3. **Create Virtual Environment**
   - Go to "Consoles" → Start a Bash console
   ```bash
   cd MiniGridGame
   python3 -m venv venv
   source venv/bin/activate
   pip install -r backend/requirements.txt
   ```

4. **Set up Web App**
   - Go to "Web" tab → "Add a new web app"
   - Choose "Manual configuration" → Python 3.10
   - Set source code directory: `/home/yourusername/MiniGridGame/backend`
   - Set working directory: `/home/yourusername/MiniGridGame/backend`

5. **Configure WSGI**
   - Click on WSGI configuration file
   - Replace contents with:
   ```python
   import sys
   path = '/home/yourusername/MiniGridGame/backend'
   if path not in sys.path:
       sys.path.append(path)

   from app import app as application
   ```

6. **Set Virtual Environment Path**
   - In Web tab, set virtualenv path:
     `/home/yourusername/MiniGridGame/venv`

7. **Reload**
   - Click "Reload" button
   - Your app will be at: `https://yourusername.pythonanywhere.com`

### Important Notes:
- **Always on**: No sleep/wake delays
- **Storage**: 512MB disk space on free tier
- **CPU**: Limited CPU seconds per day

---

## Option 2: Fly.io (More Advanced)

### Requires Docker but offers good free tier:

1. Install flyctl CLI
2. Run `fly launch` in project directory
3. Follow prompts
4. Deploy with `fly deploy`

Free tier: 3 shared VMs, 3GB storage

---

## After Deployment

### Update CORS Settings
After deploying, update `backend/app.py` to allow your production URL:

```python
CORS(app,
     supports_credentials=True,
     origins=['http://localhost:5000', 'https://your-deployed-app.com'],
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
```

### Create Admin Account
Visit your deployed app and register - the first user automatically becomes admin!

### Monitor
- **PythonAnywhere**: Check error log and server log in the dashboard
- **Fly.io**: Use `flyctl logs` to view application logs

---

## Cost Comparison

| Service | Free Tier | Limitations | Best For |
|---------|-----------|-------------|----------|
| **PythonAnywhere** | ✅ 1 web app | CPU limits, always on | Easiest setup, no sleep |
| **Fly.io** | ✅ 3 VMs | Requires Docker | Advanced users |

## Need Help?

- Check logs in your hosting dashboard
- Ensure all environment variables are set
- Verify database file has write permissions
- Check that static files are being served correctly
