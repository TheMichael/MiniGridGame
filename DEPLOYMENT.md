# Deployment Guide - Neural Navigator

This guide shows you how to deploy Neural Navigator online for free.

## Option 1: Render (Recommended - Easiest)

### Steps:

1. **Push your code to GitHub** (you've already done this!)

2. **Sign up for Render**
   - Go to https://render.com
   - Sign up with your GitHub account

3. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository: `TheMichael/MiniGridGame`
   - Choose the branch (e.g., `main`)

4. **Configure Service**
   - **Name**: `neural-navigator` (or whatever you want)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && python app.py`

5. **Add Environment Variables**
   - Click "Advanced" → "Add Environment Variable"
   - Add these:
     - `FLASK_ENV` = `production`
     - `FLASK_HOST` = `0.0.0.0`
     - `FLASK_PORT` = `10000`
     - `SECRET_KEY` = (click "Generate" for random value)

6. **Deploy!**
   - Click "Create Web Service"
   - Wait 5-10 minutes for deployment
   - Your app will be live at: `https://neural-navigator.onrender.com`

### Important Notes:
- **Free tier limitation**: App sleeps after 15 min of inactivity (takes ~30s to wake up on first request)
- **Database**: SQLite data persists between deploys
- **GIF storage**: GIFs will be stored on the server

---

## Option 2: PythonAnywhere

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

## Option 3: Fly.io (More Advanced)

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
     origins=['http://localhost:5000', 'https://your-app.onrender.com'],
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
```

### Create Admin Account
Visit your deployed app and register - the first user automatically becomes admin!

### Monitor
- **Render**: Check logs in Render dashboard
- **PythonAnywhere**: Check error log and server log

---

## Cost Comparison

| Service | Free Tier | Limitations | Best For |
|---------|-----------|-------------|----------|
| **Render** | ✅ 750 hrs/mo | Sleeps after 15 min | Quick deployment |
| **PythonAnywhere** | ✅ 1 web app | CPU limits, always on | No sleep needed |
| **Fly.io** | ✅ 3 VMs | Requires Docker | Advanced users |

## Need Help?

- Check logs in your hosting dashboard
- Ensure all environment variables are set
- Verify database file has write permissions
- Check that static files are being served correctly
