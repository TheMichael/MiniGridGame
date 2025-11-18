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

## Option 3: Vercel (Experimental - Serverless)

### ⚠️ Important Limitations

Vercel uses **serverless functions** which have constraints for this app:
- **PyTorch size** (~800MB) may exceed serverless limits - deployment might fail
- **Ephemeral filesystem** - generated GIFs and SQLite data won't persist between requests
- **Cold starts** - first request after inactivity will be slow
- **Not recommended** for production use with this app's architecture

### Steps (if you want to try anyway):

1. **Sign up for Vercel**
   - Go to https://vercel.com
   - Sign up with your GitHub account

2. **Install Vercel CLI** (optional)
   ```bash
   npm install -g vercel
   ```

3. **Deploy from GitHub**
   - Click "New Project" in Vercel dashboard
   - Import your GitHub repository: `TheMichael/MiniGridGame`
   - Vercel will auto-detect the `vercel.json` configuration
   - Click "Deploy"

4. **Or Deploy via CLI**
   ```bash
   cd MiniGridGame
   vercel
   ```

5. **Configure Environment Variables** (in Vercel dashboard)
   - `FLASK_ENV` = `production`
   - `SECRET_KEY` = (generate a random secret key)

### Expected Issues:
- ❌ Deployment may fail due to PyTorch package size
- ❌ SQLite database will reset on each deployment
- ❌ Generated GIFs will be lost between function invocations
- ❌ Game functionality may not work as expected

### Recommendation:
**Use PythonAnywhere or Fly.io instead** - they're better suited for this Flask + PyTorch application.

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
| **PythonAnywhere** | ✅ 1 web app | CPU limits, always on | **Recommended** - Easiest setup |
| **Fly.io** | ✅ 3 VMs | Requires Docker | Advanced users |
| **Vercel** | ✅ Serverless | PyTorch too large, no persistence | ❌ Not recommended |

## Need Help?

- Check logs in your hosting dashboard
- Ensure all environment variables are set
- Verify database file has write permissions
- Check that static files are being served correctly
