# 🚀 AWS Amplify Deployment Guide - TaxWise

Deploy your **entire full-stack application** to AWS Amplify in minutes - **100% FREE**!

## ✨ Why AWS Amplify?

- ✅ **Completely Free** for your use case
- ✅ **Automatic CI/CD** from GitHub
- ✅ **Built-in SSL/HTTPS** certificate (free)
- ✅ **Global CDN** included
- ✅ **Auto-scaling** and high availability
- ✅ **Easy environment variables** management
- ✅ **Preview deployments** for pull requests
- ✅ **Custom domains** support

### Free Tier Includes:
- 1,000 build minutes/month
- 15 GB data transfer/month
- 5 GB storage/month
- Unlimited hosting for static sites

---

## 🎯 Deployment Methods

### **Method 1: One-Click Deploy (Easiest - 5 Minutes)**

#### Step 1: Push to GitHub
```powershell
# If not already on GitHub
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/SudanJerald/BitNBuild-25_Nova.git
git push -u origin clone
```

#### Step 2: Deploy to Amplify
1. Go to [AWS Amplify Console](https://console.aws.amazon.com/amplify/)
2. Click **"New app"** → **"Host web app"**
3. Choose **GitHub** as source
4. Authorize AWS Amplify to access your GitHub
5. Select repository: **BitNBuild-25_Nova**
6. Select branch: **clone**
7. Click **"Next"**

#### Step 3: Configure Build Settings
The `amplify.yml` file is already configured! Amplify will auto-detect it.

Just add your **environment variables**:
- Click **"Advanced settings"**
- Add environment variables:
  ```
  SUPABASE_URL = your_supabase_url
  SUPABASE_KEY = your_supabase_key
  SUPABASE_SERVICE_KEY = your_service_key
  ```

#### Step 4: Deploy!
- Click **"Save and deploy"**
- ⏳ Wait 5-10 minutes for first build
- 🎉 Your app will be live at: `https://clone.xxxxxx.amplifyapp.com`

---

### **Method 2: Using Amplify CLI (More Control)**

#### Install Amplify CLI
```powershell
npm install -g @aws-amplify/cli
amplify configure
```

#### Initialize Amplify
```powershell
cd c:\Desktop\PROJECTS\BitNBuild'25_Nova\BitNBuild-25_Nova

amplify init
# Choose:
# - App name: taxwise
# - Environment: prod
# - Default editor: Visual Studio Code
# - App type: javascript
# - Framework: react
# - Source directory: frontend/temp/src
# - Build directory: frontend/temp/build
# - Build command: npm run build
# - Start command: npm start
```

#### Add Hosting
```powershell
amplify add hosting
# Choose: Hosting with Amplify Console (Managed hosting with custom domains, CI/CD)
```

#### Deploy
```powershell
amplify publish
```

---

## 🔧 For Full-Stack (Frontend + Backend API)

Since your backend is Flask (Python), you have two options:

### **Option A: Amplify Frontend + Lambda Backend (Recommended)**

1. **Deploy Frontend to Amplify** (as above)
2. **Deploy Backend to AWS Lambda** using Serverless Framework

Create `backend/serverless.yml`:
```yaml
service: taxwise-api

provider:
  name: aws
  runtime: python3.11
  region: us-east-1
  environment:
    SUPABASE_URL: ${env:SUPABASE_URL}
    SUPABASE_KEY: ${env:SUPABASE_KEY}
    SUPABASE_SERVICE_KEY: ${env:SUPABASE_SERVICE_KEY}

functions:
  api:
    handler: wsgi_handler.handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
          cors:
            origin: '*'
            headers:
              - Content-Type
              - Authorization

plugins:
  - serverless-wsgi
  - serverless-python-requirements

custom:
  wsgi:
    app: app.app
```

Install serverless:
```powershell
npm install -g serverless
cd backend
serverless plugin install -n serverless-wsgi
serverless plugin install -n serverless-python-requirements
serverless deploy
```

Then update frontend API URL to your Lambda endpoint.

---

### **Option B: Amplify Frontend + Elastic Beanstalk Backend**

1. Deploy frontend to Amplify (frontend only)
2. Deploy backend to Elastic Beanstalk (use `deploy-to-aws.ps1` script)
3. Update frontend environment variables in Amplify Console

---

## 📝 Environment Variables in Amplify

### Set in Amplify Console:
1. Go to your app in Amplify Console
2. Click **"App settings"** → **"Environment variables"**
3. Add:
   ```
   REACT_APP_API_URL = your-backend-url
   REACT_APP_SUPABASE_URL = your_supabase_url
   REACT_APP_SUPABASE_KEY = your_supabase_key
   ```

### Or set via CLI:
```powershell
amplify env add prod
amplify push
```

---

## 🌐 Custom Domain Setup

### Add Custom Domain (FREE SSL included!):
1. In Amplify Console → **"Domain management"**
2. Click **"Add domain"**
3. Enter your domain (e.g., `taxwise.com`)
4. Amplify automatically provisions **FREE SSL certificate**
5. Update DNS records as shown
6. ✅ Your app is now at `https://taxwise.com`

**Cost:** $0 (SSL certificate is FREE with Amplify!)

---

## 🔄 Auto-Deploy on Git Push

Once connected to GitHub, every push triggers automatic deployment:

```powershell
# Make changes to your code
git add .
git commit -m "Updated feature"
git push

# 🎉 Amplify automatically builds and deploys!
```

You can watch build progress in Amplify Console.

---

## 🚀 Quick Deploy Script

I've created an automated script for you:

```powershell
.\deploy-to-amplify.ps1
```

---

## 📊 Monitoring & Logs

### View in Amplify Console:
- **Build logs**: See build progress and errors
- **Access logs**: Monitor traffic
- **Metrics**: View bandwidth, requests, errors
- **Custom headers**: Add security headers
- **Redirects**: Configure URL redirects

### Useful Commands:
```powershell
amplify status              # Check app status
amplify console            # Open Amplify Console
amplify env list           # List environments
amplify delete             # Delete app (stop hosting)
```

---

## 💰 Cost Breakdown

| Feature | Free Tier | After Free Tier |
|---------|-----------|-----------------|
| Build minutes | 1,000/month | $0.01/minute |
| Hosting | 15GB transfer | $0.15/GB |
| Storage | 5GB | $0.023/GB |
| SSL Certificate | ✅ FREE | ✅ FREE |
| Custom Domain | ✅ FREE | ✅ FREE |

**Expected cost for TaxWise: $0/month** (well within free tier)

---

## 🎨 Preview Deployments

Amplify creates preview URLs for pull requests automatically!

1. Create a new branch: `git checkout -b feature-new-ui`
2. Make changes and push
3. Create pull request on GitHub
4. 🎉 Amplify creates preview URL: `https://feature-new-ui.xxxxxx.amplifyapp.com`

---

## 🔒 Security Best Practices

### Environment Variables:
- ✅ Store in Amplify Console (encrypted)
- ❌ Never commit to Git

### Headers:
Add in Amplify Console → **App settings** → **Custom headers**:
```yaml
customHeaders:
  - pattern: '**/*'
    headers:
      - key: 'Strict-Transport-Security'
        value: 'max-age=31536000; includeSubDomains'
      - key: 'X-Frame-Options'
        value: 'SAMEORIGIN'
      - key: 'X-Content-Type-Options'
        value: 'nosniff'
```

---

## 🆘 Troubleshooting

### Build Fails:
1. Check build logs in Amplify Console
2. Verify `amplify.yml` is correct
3. Check Node version: Add to `amplify.yml`:
   ```yaml
   frontend:
     phases:
       preBuild:
         commands:
           - nvm install 18
           - nvm use 18
   ```

### API Not Working:
1. Check CORS settings on backend
2. Verify environment variables are set
3. Check API URL in frontend code

### Custom Domain Issues:
1. Wait for DNS propagation (up to 48 hours)
2. Verify DNS records match Amplify instructions
3. Check SSL certificate status

---

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Connected Amplify to GitHub repo
- [ ] Environment variables configured
- [ ] First deployment successful
- [ ] Frontend accessible via Amplify URL
- [ ] Backend API configured (Lambda or EB)
- [ ] Frontend connected to backend API
- [ ] Custom domain added (optional)
- [ ] SSL certificate active
- [ ] Auto-deploy working on git push

---

## 🎯 Comparison: Amplify vs Other Options

| Feature | Amplify | Vercel | Netlify | AWS EB |
|---------|---------|--------|---------|--------|
| **Setup Time** | 5 min | 3 min | 3 min | 15 min |
| **Free SSL** | ✅ | ✅ | ✅ | ❌ |
| **Auto Deploy** | ✅ | ✅ | ✅ | ❌ |
| **Backend Support** | Lambda | Edge Fns | Edge Fns | ✅ Full |
| **Free Tier** | Generous | Good | Good | Limited |
| **Best For** | Full AWS | Next.js | JAMstack | Full Control |

---

## 🎉 Success!

Your TaxWise app is now:
- ✅ Hosted on AWS Amplify
- ✅ Accessible via HTTPS
- ✅ Auto-deploying on every push
- ✅ Globally distributed via CDN
- ✅ Costing $0/month

**Live URL**: Check Amplify Console for your app URL!

---

## 📱 Mobile App (Bonus)

Want to convert to mobile app? Amplify supports:
- React Native
- Flutter
- iOS/Android native

Just run:
```powershell
amplify add api
amplify add storage
amplify push
```

---

## 🔗 Useful Links

- [Amplify Console](https://console.aws.amazon.com/amplify/)
- [Amplify Documentation](https://docs.amplify.aws/)
- [Pricing Calculator](https://aws.amazon.com/amplify/pricing/)
- [Community Forum](https://github.com/aws-amplify/amplify-js/discussions)

---

**Need help?** Check the [Amplify Discord](https://discord.gg/amplify) or AWS Support!
