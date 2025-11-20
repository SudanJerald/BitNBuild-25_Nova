# 🚀 AWS Free Tier Deployment Guide for TaxWise

This guide will help you deploy the TaxWise application on AWS using **100% free tier** services.

## 📋 Prerequisites

1. **AWS Account** (Free Tier eligible)
   - Sign up at: https://aws.amazon.com/free/
   - Free tier includes:
     - 750 hours/month of EC2 t2.micro instance
     - 5GB of S3 storage
     - 750 hours/month of RDS db.t2.micro
     - 1 million free Lambda requests/month

2. **AWS CLI** installed on your computer
   ```powershell
   # Download from: https://aws.amazon.com/cli/
   # Or install via chocolatey:
   choco install awscli
   ```

3. **Git** installed
4. **Your AWS credentials configured**

## 🎯 Deployment Options (All Free Tier)

### **Option 1: AWS Elastic Beanstalk (Recommended - Easiest)**

#### Benefits:
- ✅ Easy deployment and management
- ✅ Auto-scaling (stays in free tier)
- ✅ Load balancing included
- ✅ Free for 750 hours/month

#### Steps:

1. **Install EB CLI**
   ```powershell
   pip install awsebcli
   ```

2. **Initialize Elastic Beanstalk (Backend)**
   ```powershell
   cd backend
   eb init -p python-3.11 taxwise-backend --region us-east-1
   ```

3. **Create environment**
   ```powershell
   eb create taxwise-backend-env --instance-type t2.micro
   ```

4. **Set environment variables**
   ```powershell
   eb setenv SUPABASE_URL=your_supabase_url SUPABASE_KEY=your_key SUPABASE_SERVICE_KEY=your_service_key
   ```

5. **Deploy**
   ```powershell
   eb deploy
   ```

6. **Get URL**
   ```powershell
   eb status
   # Your backend will be at: http://taxwise-backend-env.xxxxx.us-east-1.elasticbeanstalk.com
   ```

---

### **Option 2: AWS EC2 + S3 (More Control)**

#### Backend on EC2:

1. **Launch EC2 Instance**
   - Go to AWS Console → EC2
   - Click "Launch Instance"
   - Choose: **Ubuntu Server 22.04 LTS (Free tier eligible)**
   - Instance type: **t2.micro** (Free tier)
   - Create new key pair (download .pem file)
   - Security group: Allow SSH (22), HTTP (80), HTTPS (443), Custom TCP (5000)
   - Launch instance

2. **Connect to EC2**
   ```powershell
   # Convert .pem to .ppk if using PuTTY, or use:
   ssh -i your-key.pem ubuntu@your-ec2-public-ip
   ```

3. **Setup Backend on EC2**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Python and dependencies
   sudo apt install python3-pip python3-venv nginx -y
   
   # Clone your repository
   git clone https://github.com/SudanJerald/BitNBuild-25_Nova.git
   cd BitNBuild-25_Nova/backend
   
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   pip install gunicorn
   
   # Create .env file
   nano .env
   # Add your Supabase credentials
   
   # Run with gunicorn
   gunicorn app:app --bind 0.0.0.0:5000 --workers 2 --daemon
   ```

4. **Setup Nginx as reverse proxy**
   ```bash
   sudo nano /etc/nginx/sites-available/taxwise
   ```
   
   Add:
   ```nginx
   server {
       listen 80;
       server_name your-ec2-public-ip;
   
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```
   
   ```bash
   sudo ln -s /etc/nginx/sites-available/taxwise /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

#### Frontend on S3 + CloudFront:

1. **Build Frontend**
   ```powershell
   cd frontend/temp
   npm run build
   ```

2. **Create S3 Bucket**
   - Go to AWS Console → S3
   - Create bucket: `taxwise-frontend`
   - Uncheck "Block all public access"
   - Enable static website hosting
   - Index document: `index.html`

3. **Upload Build Files**
   ```powershell
   aws s3 sync build/ s3://taxwise-frontend --acl public-read
   ```

4. **Configure Bucket Policy**
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [{
       "Sid": "PublicReadGetObject",
       "Effect": "Allow",
       "Principal": "*",
       "Action": "s3:GetObject",
       "Resource": "arn:aws:s3:::taxwise-frontend/*"
     }]
   }
   ```

5. **Setup CloudFront (Optional - for HTTPS)**
   - Create CloudFront distribution
   - Origin: Your S3 bucket website endpoint
   - Free tier: 50GB data transfer/month

---

### **Option 3: AWS Lambda + API Gateway (Serverless - Most Cost Effective)**

Perfect for low-traffic applications.

#### Benefits:
- ✅ 1 million requests/month FREE
- ✅ No server management
- ✅ Auto-scaling
- ✅ Pay only for what you use

#### Steps:

1. **Install Serverless Framework**
   ```powershell
   npm install -g serverless
   ```

2. **Create serverless.yml in backend folder**
   ```yaml
   service: taxwise-backend
   
   provider:
     name: aws
     runtime: python3.11
     region: us-east-1
     stage: prod
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
             cors: true
   
   plugins:
     - serverless-wsgi
     - serverless-python-requirements
   ```

3. **Deploy**
   ```powershell
   cd backend
   serverless deploy
   ```

---

## 🔧 Configuration Updates

### Update Frontend API URL

After deploying backend, update the frontend to use your AWS backend URL:

**File: `frontend/temp/src/utils/supabase/client.tsx`**
```typescript
const API_BASE_URL = 'http://your-backend-url.elasticbeanstalk.com'
// or your EC2 IP/domain
// or your API Gateway URL
```

### Update CORS in Backend

**File: `backend/app.py`**
```python
CORS(app, origins=[
    'http://localhost:3000',
    'http://taxwise-frontend.s3-website-us-east-1.amazonaws.com',
    'https://your-cloudfront-domain.cloudfront.net',
    # Add your actual frontend URL
])
```

---

## 💰 Cost Breakdown (Free Tier)

| Service | Free Tier Limit | After Free Tier |
|---------|----------------|-----------------|
| EC2 t2.micro | 750 hrs/month (1 instance 24/7) | ~$8/month |
| S3 | 5GB storage, 20K GET, 2K PUT | $0.023/GB |
| RDS db.t2.micro | 750 hrs/month | ~$15/month |
| Lambda | 1M requests, 400K GB-seconds | Very cheap |
| CloudFront | 50GB transfer/month | $0.085/GB |
| Data Transfer | 1GB out/month | $0.09/GB |

**Total for this project in Free Tier: $0/month** ✅

---

## 🚀 Quick Start (Fastest Method)

### Using Elastic Beanstalk (Backend) + S3 (Frontend)

```powershell
# 1. Backend
cd backend
pip install awsebcli gunicorn
eb init -p python-3.11 taxwise-backend --region us-east-1
eb create taxwise-backend-env --instance-type t2.micro
eb setenv SUPABASE_URL=your_url SUPABASE_KEY=your_key SUPABASE_SERVICE_KEY=your_service_key
eb deploy

# Get backend URL
eb status

# 2. Frontend
cd ../frontend/temp

# Update API URL in src/utils/supabase/client.tsx
# Replace localhost:5000 with your EB URL

npm run build

# Upload to S3
aws s3 mb s3://taxwise-app-frontend
aws s3 website s3://taxwise-app-frontend --index-document index.html
aws s3 sync build/ s3://taxwise-app-frontend --acl public-read

# Get frontend URL
echo "http://taxwise-app-frontend.s3-website-us-east-1.amazonaws.com"
```

---

## 📊 Monitoring & Management

### Elastic Beanstalk Commands:
```powershell
eb status              # Check environment status
eb health              # Check health
eb logs                # View logs
eb ssh                 # SSH into instance
eb terminate           # Delete environment (stop costs)
```

### EC2 Management:
- **Stop instance when not in use** (free tier hours still count)
- **Monitor usage** in AWS Billing Dashboard
- **Set up billing alerts** at $1 threshold

---

## 🔒 Security Best Practices

1. **Never commit .env files** to Git
2. **Use AWS Secrets Manager** for sensitive data (free tier: 30-day trial)
3. **Enable HTTPS** with AWS Certificate Manager (FREE)
4. **Restrict Security Groups** to only necessary ports
5. **Use IAM roles** instead of access keys when possible

---

## 🆘 Troubleshooting

### Backend won't start:
```bash
# Check logs
eb logs

# Or SSH and check manually
eb ssh
sudo cat /var/log/eb-engine.log
```

### Frontend 403 errors:
- Check S3 bucket policy
- Verify public access settings
- Check CloudFront distribution settings

### Database connection issues:
- Verify Supabase credentials in environment variables
- Check security group allows outbound HTTPS

---

## 📱 Alternative: Deploy to Railway (Even Easier)

If you want the absolute simplest deployment:

1. Go to https://railway.app
2. Sign in with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Add environment variables
6. Deploy!

**Railway Free Tier:** $5 credit/month, 500 hours

---

## ✅ Checklist

- [ ] AWS Account created
- [ ] AWS CLI installed and configured
- [ ] Backend deployed to EB/EC2/Lambda
- [ ] Frontend built and uploaded to S3
- [ ] Environment variables set
- [ ] CORS configured
- [ ] API URL updated in frontend
- [ ] SSL certificate added (optional)
- [ ] Billing alerts configured
- [ ] Application tested and working

---

## 🎉 Success!

Your TaxWise application should now be live on AWS! 

**Important:** Monitor your AWS Free Tier usage at:
https://console.aws.amazon.com/billing/home#/freetier

---

For questions or issues, refer to:
- [AWS Free Tier FAQ](https://aws.amazon.com/free/free-tier-faqs/)
- [Elastic Beanstalk Documentation](https://docs.aws.amazon.com/elasticbeanstalk/)
- [AWS Support](https://console.aws.amazon.com/support/home)
