# Quick Start: Deploy to Render.com in 10 Minutes

**Cost:** $25/month (Standard tier - 2GB RAM needed for PyTorch)

---

## Step 1: Sign Up (2 minutes)

1. Go to https://render.com
2. Click **"Get Started"**
3. Sign up with GitHub (easiest)
4. Add payment method in **Account Settings**

---

## Step 2: Create Web Service (3 minutes)

1. Click **"New +"** in top right
2. Select **"Web Service"**
3. Click **"Connect GitHub"** (if first time)
4. Find and click **"Connect"** next to `MiniGridGame`

---

## Step 3: Configure (3 minutes)

### Basic Settings:
- **Name:** `neural-navigator` (or anything you want)
- **Region:** Oregon (US West) or Frankfurt (Europe)
- **Branch:** `main`
- **Runtime:** Docker ✓ (auto-detected)
- **Instance Type:** **Standard ($25/mo)** ⚠️ Required for PyTorch!

### Environment Variables:
Click **"Advanced"** and add:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | Generate with: `python3 -c "import secrets; print(secrets.token_hex(32))"` |
| `FLASK_ENV` | `production` |
| `FLASK_HOST` | `0.0.0.0` |
| `PORT` | `8080` |

### Persistent Disk (IMPORTANT!):
Scroll to **"Disk"** section:
- Click **"Add Disk"**
- **Name:** `data`
- **Mount Path:** `/app/backend/static`
- **Size:** 1 GB (increase if needed later)

---

## Step 4: Deploy (5 minutes)

1. Click **"Create Web Service"** at bottom
2. Wait for build (5-10 minutes first time)
3. Watch logs in real-time
4. When complete, you'll see: ✅ **Live**

Your app will be at: `https://neural-navigator.onrender.com`

---

## Step 5: Update CORS (2 minutes)

1. Open `backend/app.py` in your code editor
2. Find the CORS section (around line 24)
3. Add your Render URL:

```python
CORS(app,
     supports_credentials=True,
     origins=[
         'http://localhost:5000',
         'http://127.0.0.1:5000',
         'https://neural-navigator.onrender.com'  # ← Add this
     ],
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
```

4. Commit and push to GitHub:
```bash
git add backend/app.py
git commit -m "Add Render CORS origin"
git push
```

5. Render will auto-deploy (watch in dashboard)

---

## Done! 🎉

Visit your app at: `https://neural-navigator.onrender.com`

---

## Monitoring

### View Logs:
1. Go to your service in Render dashboard
2. Click **"Logs"** tab
3. See real-time application logs

### View Metrics:
1. Click **"Metrics"** tab
2. See CPU, memory, disk usage

### Check Health:
- Green **"Live"** indicator = healthy
- Red indicator = check logs for errors

---

## Auto-Deploy on Git Push

Render automatically deploys when you push to GitHub:

```bash
# Make changes to your code
git add .
git commit -m "Add new feature"
git push

# Render will:
# 1. Detect the push
# 2. Build new Docker image
# 3. Deploy automatically
# 4. Keep old version running until new one is ready (zero downtime!)
```

---

## Troubleshooting

### App won't start:
```
1. Check Render logs for errors
2. Verify Dockerfile builds locally: docker build -t test .
3. Ensure PORT=8080 matches Dockerfile EXPOSE port
```

### 502 Bad Gateway:
```
- App must bind to 0.0.0.0, not localhost
- Check FLASK_HOST=0.0.0.0 in env vars
- Verify app is listening on PORT 8080
```

### Database not persisting:
```
- Check disk is mounted to /app/backend/static
- Verify mount path in Render dashboard
- Check disk usage isn't full
```

### Out of memory:
```
- Upgrade to larger instance:
  - Settings → Instance Type → Professional (4GB RAM)
- Or optimize PyTorch model loading
```

---

## Useful Render Features

### Shell Access:
1. Go to your service
2. Click **"Shell"** tab
3. Run commands directly in your container:
```bash
ls -la /app/backend
python manage.py db migrate
```

### Manual Deploy:
1. Click **"Manual Deploy"**
2. Choose **"Deploy latest commit"**
3. Or select specific commit/branch

### Environment Variables:
1. **"Environment"** tab
2. Add/edit variables
3. Click **"Save Changes"** → auto-redeploys

### Custom Domain:
1. **"Settings"** → **"Custom Domains"**
2. Add your domain: `app.yourdomain.com`
3. Update DNS: Add CNAME → `neural-navigator.onrender.com`
4. Free SSL certificate auto-generated!

---

## Pricing Breakdown

**Standard Instance: $25/month includes:**
- 2 GB RAM (needed for PyTorch)
- 1 vCPU
- Always running (no cold starts)
- Automatic scaling
- HTTPS/SSL certificate
- Free bandwidth (100 GB outbound)
- Auto-deploy from GitHub
- Zero-downtime deployments

**Disk Storage:**
- 1 GB: Free
- Additional: $0.25/GB/month

**Estimated total: $25-27/month**

---

## Next Steps

1. ✅ Test your deployed app
2. ✅ Register first user (auto-admin)
3. ✅ Test game functionality
4. ✅ Set up monitoring alerts (optional)
5. ✅ Add custom domain (optional)
6. ✅ Enable automatic backups

---

## Support

- **Documentation:** https://render.com/docs
- **Community:** https://community.render.com
- **Email Support:** support@render.com (usually responds in < 24 hours)
- **Status:** https://status.render.com

---

## Cost Optimization

**If $25/month is too much:**
- Try **Railway.app** instead (~$15/month, pay-per-use)
- Or start with **Fly.io free tier** for testing (has cold starts)

**If you need more resources:**
- **Professional:** $85/month (4GB RAM, 2 vCPU)
- **Pro Plus:** $185/month (8GB RAM, 4 vCPU)

---

## Comparison: Render vs Others

| Feature | Render | Railway | DigitalOcean | Fly.io (Free) |
|---------|--------|---------|--------------|---------------|
| **Price** | $25/mo | ~$15/mo | $24/mo | $0 |
| **RAM** | 2GB | 2GB | 2GB | 256MB |
| **Cold Starts** | ❌ No | ❌ No | ❌ No | ✅ Yes (10min) |
| **Auto-deploy** | ✅ Yes | ✅ Yes | ✅ Yes | Manual |
| **Ease of use** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Reliability** | 99.99% | 99.99% | 99.99% | 99.5% |

**Verdict:** Render is the best balance of price, features, and reliability.
