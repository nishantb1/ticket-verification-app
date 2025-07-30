# 🚀 Deployment Guide

## Free Deployment Options

### Option 1: Render (Recommended)
**Free Tier**: 750 hours/month (enough for 24/7 deployment)

1. **Sign up** at [render.com](https://render.com) (no credit card required)
2. **Connect your GitHub** repository
3. **Create a Web Service**
4. **Configure**:
   - **Build Command**: `pip install -r requirements-deploy.txt`
   - **Start Command**: `gunicorn backend.api:app`
   - **Environment**: Python 3
5. **Deploy!**

### Option 2: Railway
**Free Tier**: 500 hours/month

1. **Sign up** at [railway.app](https://railway.app)
2. **Connect your GitHub** repository
3. **Railway auto-detects** and deploys
4. **Done!**

### Option 3: Fly.io
**Free Tier**: 3 shared-cpu VMs, 3GB storage

1. **Sign up** at [fly.io](https://fly.io)
2. **Install Fly CLI**: `curl -L https://fly.io/install.sh | sh`
3. **Deploy**: `fly launch`
4. **Deploy**: `fly deploy`

## Configuration Files

### requirements-deploy.txt
Minimal requirements for deployment (no problematic packages).

### Procfile
Tells deployment platforms how to run your app.

### Environment Variables
Set these in your deployment platform:
- `PORT`: Usually set automatically
- `SECRET_KEY`: Change from default in production

## Testing Your Deployment

After deployment, test these endpoints:

```bash
# Test current wave (public)
curl https://your-app-url/api/waves/current

# Test auth validation (public)
curl https://your-app-url/api/auth/validate

# Test admin login (POST)
curl -X POST https://your-app-url/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

## Troubleshooting

### Build Errors
- Use `requirements-deploy.txt` instead of `requirements.txt`
- Pillow 9.5.0 is more compatible than 10.0.1

### Import Errors
- Make sure all dependencies are in `requirements-deploy.txt`
- Check that `gunicorn` is installed

### Database Issues
- SQLite database will be created automatically
- For production, consider using PostgreSQL

## Next Steps

1. **Deploy to Render** (easiest)
2. **Test all endpoints**
3. **Set up custom domain** (optional)
4. **Configure environment variables**

Your app is ready for deployment! 🎉 