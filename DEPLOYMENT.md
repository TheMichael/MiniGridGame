# Deployment Guide - Neural Navigator

This guide shows you how to deploy Neural Navigator online for free.

## Option 1: Fly.io (Recommended - Best Free Tier)

Fly.io offers **3GB storage** on the free tier, which is perfect for this PyTorch application!

### Prerequisites:
- Git installed
- Docker installed (optional - Fly can build remotely)
- Fly CLI installed

### Step 1: Install Fly CLI

**Mac/Linux:**
```bash
curl -L https://fly.io/install.sh | sh
```

**Windows (PowerShell):**
```powershell
iwr https://fly.io/install.ps1 -useb | iex
```

### Step 2: Create Fly Account & Login

```bash
fly auth signup  # Create new account
# OR
fly auth login   # If you already have an account
```

### Step 3: Deploy Your App

```bash
cd MiniGridGame

# Launch the app (this will create and configure everything)
fly launch

# When prompted:
# - App name: neural-navigator (or your choice)
# - Region: Choose closest to you
# - PostgreSQL: No (we use SQLite)
# - Redis: No
# - Deploy now: Yes
```

The `fly launch` command will:
- Detect the Dockerfile
- Use the existing fly.toml configuration
- Build your Docker image
- Deploy to Fly.io
- Give you a URL like: https://neural-navigator.fly.dev

### Step 4: Set Environment Variables (Optional)

```bash
fly secrets set SECRET_KEY="your-random-secret-key-here"
```

### Step 5: Monitor Your App

```bash
# View logs
fly logs

# Check status
fly status

# Open app in browser
fly open
```

### Subsequent Deployments

After the initial setup, deploy updates with:

```bash
fly deploy
```

### Important Notes:
- **Storage**: 3GB persistent volume (plenty for PyTorch!)
- **Memory**: 256MB shared-cpu-1x (upgradeable if needed)
- **Auto-sleep**: Free tier machines sleep after 10 minutes of inactivity
- **First request**: May take 5-10 seconds to wake up from sleep
- **Database**: SQLite data persists in the persistent volume
- **GIFs**: Will be stored and persist between deployments

### Troubleshooting:

**If deployment fails:**
```bash
# Check detailed logs
fly logs

# SSH into the machine
fly ssh console

# Restart the app
fly restart
```

**If app runs out of memory:**
```bash
# Scale up memory (still free tier)
fly scale memory 512

# Or upgrade to 1GB
fly scale memory 1024
```

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
- **Storage**: 512MB disk space on free tier ⚠️ **NOT ENOUGH for PyTorch (~800MB)**
- **CPU**: Limited CPU seconds per day
- **Recommendation**: Use Fly.io instead due to storage limitations

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
| **Fly.io** | ✅ 3 VMs, 3GB storage | Auto-sleep after inactivity, requires Docker | **Recommended** - Has enough space for PyTorch! |
| **PythonAnywhere** | ✅ 1 web app, 512MB storage | ❌ Not enough space for PyTorch (~800MB) | Small Python apps only |

## Need Help?

- Check logs in your hosting dashboard
- Ensure all environment variables are set
- Verify database file has write permissions
- Check that static files are being served correctly
