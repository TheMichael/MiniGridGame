# Paid Hosting Deployment Guide - Neural Navigator

This guide covers the **most reliable paid hosting options** for your application.

---

## 🥇 Option 1: Render.com (RECOMMENDED)

**Cost:** $25/month (Standard tier with 2GB RAM)
**Reliability:** ⭐⭐⭐⭐⭐ (99.99% uptime SLA)
**Ease:** ⭐⭐⭐⭐⭐ (Easiest deployment)

### Why Render?
- ✅ No cold starts - always running
- ✅ Auto-deploy from GitHub on every push
- ✅ Automatic HTTPS certificates
- ✅ Built-in persistent disk storage
- ✅ Easy environment variable management
- ✅ Great logs and monitoring dashboard
- ✅ Zero config - detects Dockerfile automatically

### Prerequisites
- GitHub account with your repository
- Credit card (for paid plan)

### Step-by-Step Deployment

#### 1. Create Render Account
1. Go to https://render.com
2. Sign up with GitHub (easiest option)
3. Add payment method in Settings

#### 2. Create Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository: `TheMichael/MiniGridGame`
3. Click **"Connect"** next to your repository

#### 3. Configure Service
Fill in these settings:

- **Name:** `neural-navigator` (or your choice)
- **Region:** Choose closest to your users (e.g., Oregon, Frankfurt)
- **Branch:** `main` (or your default branch)
- **Runtime:** `Docker`
- **Instance Type:** **Standard** ($25/month, 2GB RAM) - needed for PyTorch
- **Dockerfile Path:** `./Dockerfile` (auto-detected)

#### 4. Add Environment Variables
Click **"Advanced"** and add these:

```
SECRET_KEY=<generate-a-random-secret-key-here>
FLASK_ENV=production
FLASK_HOST=0.0.0.0
PORT=8080
```

To generate a secure SECRET_KEY:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

#### 5. Configure Persistent Disk (Important!)
1. Scroll down to **"Disk"**
2. Click **"Add Disk"**
3. Settings:
   - **Name:** `data`
   - **Mount Path:** `/app/backend/static`
   - **Size:** 1 GB (or more if you expect many videos)

This ensures your database and generated videos persist across deployments!

#### 6. Deploy
1. Click **"Create Web Service"**
2. Render will:
   - Clone your repository
   - Build the Docker image
   - Deploy your app
   - Provide a URL like: `https://neural-navigator.onrender.com`

First deployment takes 5-10 minutes.

#### 7. Update CORS Settings
After deployment, update your CORS configuration in `backend/app.py`:

```python
CORS(app,
     supports_credentials=True,
     origins=[
         'http://localhost:5000',
         'http://127.0.0.1:5000',
         'https://neural-navigator.onrender.com'  # Add your Render URL
     ],
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
```

Commit and push - Render will auto-deploy!

#### 8. Monitor Your App
- **Dashboard:** View logs, metrics, and deployment history
- **Logs:** Real-time logs in the dashboard
- **Health:** Auto-restart if app crashes
- **Metrics:** CPU, memory, and request metrics

### Troubleshooting Render

**App shows 502 Bad Gateway:**
- Check logs in the Render dashboard
- Ensure PORT=8080 matches your Dockerfile EXPOSE port
- Verify app is binding to 0.0.0.0, not localhost

**App crashes on startup:**
- Check logs for Python errors
- Ensure all dependencies are in requirements.txt
- Verify PyTorch is installed correctly

**Database not persisting:**
- Ensure persistent disk is mounted to `/app/backend/static`
- Check disk usage in dashboard

### Render CLI (Optional)
```bash
# Install Render CLI
brew install render  # Mac
scoop install render # Windows

# View logs
render logs

# Restart service
render restart
```

---

## 🥈 Option 2: Railway.app

**Cost:** $5 base + ~$10 usage = **~$15/month**
**Reliability:** ⭐⭐⭐⭐⭐
**Ease:** ⭐⭐⭐⭐⭐

### Why Railway?
- ✅ Pay-per-use pricing (cheaper than fixed plans)
- ✅ Beautiful dashboard
- ✅ GitHub integration with auto-deploy
- ✅ Very fast deployments
- ✅ Great developer experience

### Step-by-Step Deployment

#### 1. Create Account
1. Go to https://railway.app
2. Sign up with GitHub
3. Upgrade to Developer plan ($5/month)

#### 2. Create New Project
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your repository: `TheMichael/MiniGridGame`
4. Click **"Deploy Now"**

#### 3. Configure Service
Railway auto-detects your Dockerfile and deploys automatically!

#### 4. Add Environment Variables
1. Click on your service
2. Go to **"Variables"** tab
3. Add:
```
SECRET_KEY=<your-random-secret-key>
FLASK_ENV=production
FLASK_HOST=0.0.0.0
PORT=8080
```

#### 5. Add Persistent Volume
1. In your service, click **"Settings"**
2. Scroll to **"Volumes"**
3. Click **"+ New Volume"**
4. Mount path: `/app/backend/static`
5. Click **"Add"**

#### 6. Generate Domain
1. Go to **"Settings"** tab
2. Click **"Generate Domain"**
3. You'll get a URL like: `neural-navigator.up.railway.app`

#### 7. Update CORS (same as Render)
Update `backend/app.py` with your Railway domain.

### Monitoring Railway
- **Metrics:** View CPU, memory, and network usage
- **Logs:** Real-time logs in dashboard
- **Deployments:** View deployment history
- **Cost:** See usage and estimated monthly cost

---

## 🥉 Option 3: DigitalOcean App Platform

**Cost:** $24/month (Professional tier, 2GB RAM)
**Reliability:** ⭐⭐⭐⭐⭐
**Ease:** ⭐⭐⭐⭐

### Why DigitalOcean?
- ✅ Enterprise-grade infrastructure
- ✅ Very stable and predictable
- ✅ Managed databases available
- ✅ Great documentation

### Step-by-Step Deployment

#### 1. Create Account
1. Go to https://www.digitalocean.com
2. Sign up and add payment method
3. Go to **"Apps"** section

#### 2. Create New App
1. Click **"Create App"**
2. Connect GitHub repository
3. Choose `TheMichael/MiniGridGame`
4. Select branch: `main`

#### 3. Configure App
- **Resource Type:** Docker
- **Dockerfile Location:** `/Dockerfile`
- **HTTP Port:** 8080
- **Instance Size:** Professional (2GB RAM) - $24/month

#### 4. Environment Variables
Add in the "Environment Variables" section:
```
SECRET_KEY=<your-secret>
FLASK_ENV=production
FLASK_HOST=0.0.0.0
PORT=8080
```

#### 5. Add Persistent Storage (Important!)
This requires upgrading to Professional tier:
1. In app settings, enable **"Persistent Storage"**
2. Mount path: `/app/backend/static`
3. Size: 5GB

#### 6. Deploy
Click **"Create Resources"** and wait for deployment (5-10 minutes).

You'll get a URL like: `https://neural-navigator-xxxxx.ondigitalocean.app`

### Monitoring DigitalOcean
- **Insights:** CPU, memory, bandwidth metrics
- **Logs:** View application logs
- **Alerts:** Set up email/Slack alerts
- **Activity:** Deployment history

---

## ❌ Why NOT Vercel, Netlify, or Cloudflare Pages?

**Important:** These platforms are **NOT suitable** for your application!

### Vercel / Netlify / Cloudflare Pages
**Why they don't work:**
- ❌ **Designed for static sites + serverless functions only**
- ❌ **Serverless functions have 10-60 second timeout limits**
- ❌ **Cannot run long-running Flask servers**
- ❌ **No support for WebSockets or persistent connections**
- ❌ **PyTorch is too large for serverless cold starts (5+ seconds)**
- ❌ **No persistent storage for SQLite database**
- ❌ **Not designed for stateful applications**

### What They're Good For:
- ✅ Static websites (HTML/CSS/JS)
- ✅ React/Next.js/Vue.js frontend apps
- ✅ API routes (short, stateless functions)
- ✅ JAMstack applications

### Your Application Needs:
- Long-running Flask backend server ✓
- PyTorch model inference ✓
- Persistent SQLite database ✓
- Video/GIF generation and storage ✓
- Stateful sessions ✓

**Verdict:** Use Render, Railway, or DigitalOcean instead!

---

## Other Options (If Budget is Higher)

### AWS Elastic Beanstalk
**Cost:** ~$30-50/month
**Best for:** Large-scale applications, enterprise requirements
**Setup complexity:** Medium

### Google Cloud Run
**Cost:** ~$20-40/month
**Best for:** Containerized apps, automatic scaling
**Note:** Can work but has some cold start issues with PyTorch

### Heroku
**Cost:** $25-50/month (deprecated free tier)
**Note:** Used to be the go-to, but Render/Railway are now better value
**Status:** Still reliable but less popular now

### Azure App Service
**Cost:** ~$50+/month
**Best for:** Microsoft ecosystem integration, enterprise
**Setup complexity:** High

### AWS EC2 (Self-Managed)
**Cost:** ~$10-40/month (depending on instance)
**Best for:** Full control, custom configurations
**Setup complexity:** High (requires DevOps knowledge)
**Note:** You manage everything (OS updates, security, scaling)

---

## Recommendation Summary

### For Most Users: **Render.com** ($25/month)
- Best balance of price, reliability, and ease of use
- No cold starts
- Great dashboard and logs
- Easy auto-deploy from GitHub
- Persistent storage included

### For Budget-Conscious: **Railway.app** (~$15/month)
- Pay only for what you use
- Great developer experience
- Slightly more variable pricing

### For Enterprise: **DigitalOcean** ($24/month)
- Very stable infrastructure
- Predictable pricing
- Enterprise support available

---

## Post-Deployment Checklist

After deploying to any platform:

- [ ] Update CORS in `backend/app.py` with production URL
- [ ] Test user registration and login
- [ ] Test game functionality
- [ ] Verify videos/GIFs are being generated
- [ ] Check database persistence (register, logout, login again)
- [ ] Set up monitoring/alerts
- [ ] Add custom domain (optional)
- [ ] Enable automatic backups
- [ ] Document your deployment URL for team

---

## Custom Domain Setup

All platforms support custom domains:

### Render / Railway / DigitalOcean
1. Go to settings → Custom Domains
2. Add your domain (e.g., `app.yourdomain.com`)
3. Update DNS records at your registrar:
   - Add CNAME record pointing to provided URL
4. Wait for DNS propagation (5-60 minutes)
5. SSL certificate auto-generated

---

## Backup Strategy

### Database Backups
Since you're using SQLite:

**Option 1: Render/Railway/DO Disk Snapshots**
- Most platforms offer automatic disk snapshots
- Enable in settings (usually $1-2/month extra)

**Option 2: Automated Database Export**
Add a cron job or scheduled task to:
```bash
# Export database to external storage (S3, Dropbox, etc.)
python export_db.py
```

**Option 3: GitHub Backup**
Regularly commit database to a private GitHub repo (not ideal for large DBs)

---

## Cost Optimization Tips

1. **Start with Railway** (~$15/month) for testing
2. **Upgrade to Render** ($25/month) when you need more reliability
3. **Monitor usage** regularly to avoid surprises
4. **Use disk wisely** - set up video cleanup for old files
5. **Consider CDN** for static assets if traffic grows

---

## Need Help?

### Render Support
- Docs: https://render.com/docs
- Community: https://community.render.com
- Support: Email support (fast response)

### Railway Support
- Docs: https://docs.railway.app
- Discord: Very active community
- Twitter: @Railway

### DigitalOcean Support
- Docs: https://docs.digitalocean.com
- Community: https://www.digitalocean.com/community
- Support: Ticket system

---

## Conclusion

**My recommendation:** Start with **Render.com Standard tier ($25/month)**

It's the sweet spot of:
- ✅ Reliability (99.99% uptime)
- ✅ Ease of use (5-minute setup)
- ✅ Performance (no cold starts)
- ✅ Features (auto-deploy, HTTPS, monitoring)
- ✅ Price (very reasonable for what you get)

Your PyTorch app will run smoothly, and you won't have to worry about downtime or complicated configurations.
