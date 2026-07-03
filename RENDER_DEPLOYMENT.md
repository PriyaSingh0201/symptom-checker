# Render Deployment Guide

This guide explains how to deploy the AI Symptom Checker app to **Render**.

## Prerequisites
- GitHub account with the repository pushed
- Render account (https://render.com)
- GEMINI_API_KEY from Google (optional but recommended)

## Deployment Steps

### 1. Connect GitHub Repository
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Select **"Connect a repository"**
4. Authorize Render to access your GitHub account
5. Select this repository

### 2. Configure Service
- **Name:** `ai-symptom-checker` (or your preferred name)
- **Environment:** Python
- **Region:** Choose closest to your users
- **Branch:** `main` (or your default branch)
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** Will auto-detect from `render.yaml` or `Procfile`
- **Plan:** Free (or upgrade as needed)

### 3. Set Environment Variables
In the Render dashboard, go to **Environment** section and add:

```
SECRET_KEY=<generate-random-32-char-string>
JWT_SECRET_KEY=<generate-random-32-char-string>
GEMINI_API_KEY=<your-google-gemini-api-key>
FLASK_ENV=production
PYTHONUNBUFFERED=1
```

**To generate secure keys:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Configure Database
By default, the app uses SQLite (`instance/database.db`), which **won't persist** across Render restarts.

**Recommended: Use PostgreSQL**

1. In Render dashboard, click **"New +"** → **"PostgreSQL"**
2. Configure the database:
   - **Name:** `ai-symptom-checker-db`
   - **Database:** `symptom_checker`
   - **User:** (auto-generated)
3. Copy the **Internal Database URL**
4. In your web service environment variables, add:
   ```
   DATABASE_URL=<paste-the-url-from-postgresql>
   ```

If using SQLite (free tier), understand that:
- Database persists on the same instance but resets if the service is restarted
- Consider exporting data regularly or upgrading to PostgreSQL

### 5. Deploy
1. Click **"Create Web Service"**
2. Render will automatically:
   - Pull your code
   - Install dependencies from `requirements.txt`
   - Start the service using the command in `render.yaml` or `Procfile`

### 6. Monitor Deployment
- Watch the build logs in the Render dashboard
- Once deployed, your app will be live at: `https://<service-name>.onrender.com`
- Check health endpoint: `https://<service-name>.onrender.com/health`

## Troubleshooting

### Build Fails
- Check that `requirements.txt` is correct
- Ensure all dependencies are listed
- Check build logs in Render dashboard

### App Crashes on Start
- Check application logs in Render dashboard
- Verify all environment variables are set correctly
- Ensure `SECRET_KEY` and `JWT_SECRET_KEY` are set

### Database Issues
- If using PostgreSQL, verify `DATABASE_URL` format starts with `postgresql://`
- The app automatically converts old `postgres://` URLs to `postgresql://`

### Uploads Not Persisting
- Free Render instances use ephemeral storage
- Uploads in the `uploads/` folder are deleted on restart
- **Solution:** Use cloud storage (AWS S3, Cloudinary, etc.)

## Production Best Practices

1. **Use a Production Database:** PostgreSQL > SQLite
2. **Enable HTTPS:** Render provides free SSL/TLS
3. **Set Strong Secrets:** Use `secrets.token_urlsafe(32)`
4. **Monitor Logs:** Regularly check application logs
5. **Set Up Health Checks:** The app includes `/health` endpoint
6. **Environment Variables:** Never commit `.env` file to Git

## Monitoring & Maintenance

- **Logs:** View in Render dashboard → Service → Logs
- **Metrics:** Check CPU, Memory usage in dashboard
- **Auto-Deploy:** Set GitHub branch to auto-deploy on push

## Rolling Back
If deployment fails, use Render's dashboard to:
1. View previous deployment logs
2. Redeploy a previous version
3. Manually restart the service

---

**Questions?** Check the [Render Documentation](https://render.com/docs) or app logs for details.
