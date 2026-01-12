# Deployment Guide - Firebase Cloud Run

This guide explains how to deploy the YOLO Abnormality Detection application to **Google Cloud Run** via **Firebase**.

## Prerequisites

Before you begin, make sure you have:

1. **Google Cloud Project** - Create one at [Google Cloud Console](https://console.cloud.google.com)
2. **Google Cloud SDK** - Install from [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
3. **Docker** - Install from [Docker](https://www.docker.com/products/docker-desktop)
4. **Firebase Account** - Sign up at [Firebase Console](https://console.firebase.google.com)
5. **Git** - For version control (optional but recommended)

## Step 1: Set Up Google Cloud Project

### 1.1 Create a new project
```bash
# Navigate to Google Cloud Console
# Click "Select a Project" > "New Project"
# Enter a project name (e.g., "abnormality-detection")
# Click "Create"
```

### 1.2 Link Firebase to the project
```bash
# In Firebase Console, click "Add project"
# Select your Google Cloud project from the dropdown
# Follow the setup wizard
```

### 1.3 Enable required APIs
```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

## Step 2: Prepare Your Local Environment

### 2.1 Initialize Google Cloud CLI
```bash
gcloud init

# Follow the prompts to:
# - Log in with your Google account
# - Select your project
# - Set default region (choose the closest to your users)
```

### 2.2 Set your project ID
```bash
export PROJECT_ID=$(gcloud config get-value project)
echo $PROJECT_ID
```

### 2.3 Set up authentication
```bash
gcloud auth configure-docker
```

## Step 3: Build and Push Docker Image

### 3.1 Build the Docker image locally (optional, for testing)
```bash
# Navigate to your project directory
cd "C:\Users\akshi\Downloads\Abnormal-behavior-detection-using-YOLO"

# Build the image
docker build -t abnormality-detection:latest .

# Test locally
docker run -p 8080:8080 abnormality-detection:latest
# Access at http://localhost:8080
```

### 3.2 Build and push to Google Container Registry
```bash
# Navigate to your project directory
cd "C:\Users\akshi\Downloads\Abnormal-behavior-detection-using-YOLO"

# Set image name
IMAGE_NAME="gcr.io/${PROJECT_ID}/abnormality-detection"

# Build and push (Google Cloud Build handles this)
gcloud builds submit --tag ${IMAGE_NAME}
```

**Alternative: Use Cloud Build without local Docker**
```bash
gcloud run deploy abnormality-detection \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Step 4: Deploy to Cloud Run

### 4.1 Deploy the image
```bash
# Set your desired region
REGION="us-central1"  # Change to your preferred region

# Deploy
gcloud run deploy abnormality-detection \
  --image gcr.io/${PROJECT_ID}/abnormality-detection \
  --platform managed \
  --region ${REGION} \
  --memory 2Gi \
  --timeout 600 \
  --allow-unauthenticated \
  --port 8080
```

### 4.2 Configure for better performance
```bash
# If deployment was successful, update configuration:
gcloud run deploy abnormality-detection \
  --image gcr.io/${PROJECT_ID}/abnormality-detection \
  --platform managed \
  --region ${REGION} \
  --memory 4Gi \
  --cpu 2 \
  --timeout 900 \
  --max-instances 10 \
  --allow-unauthenticated
```

### Deployment Options Explained:
- `--memory`: RAM allocation (2Gi-4Gi recommended for video processing)
- `--cpu`: CPU cores (1-4 recommended)
- `--timeout`: Request timeout in seconds (600-900 for video processing)
- `--max-instances`: Maximum concurrent instances for auto-scaling
- `--allow-unauthenticated`: Allows public access (remove for private app)

## Step 5: Access Your Application

After deployment, you'll see output like:
```
Service [abnormality-detection] revision [abnormality-detection-00001-xyz]
has been deployed and is serving 100 percent of traffic at:
https://abnormality-detection-xxxxx.run.app
```

Visit this URL in your browser to access the application.

## Deployment via Firebase Console (Alternative)

### Method 1: Through Firebase Console
1. Go to [Firebase Console](https://console.firebase.google.com)
2. Select your project
3. Navigate to **Build** → **Functions** (or **Extensions**)
4. Click **Manage all Cloud Run services**
5. Click **Create Service** and follow the prompts

### Method 2: Manual Cloud Run Deployment
1. Go to [Cloud Run Console](https://console.cloud.google.com/run)
2. Click **Create Service**
3. Choose **Deploy one revision from an image**
4. Select the image from Container Registry (or build a new one)
5. Configure settings and deploy

## Troubleshooting

### Issue: Image too large or takes too long to build
**Solution**: Optimize the Dockerfile or use Cloud Build cache

### Issue: Out of memory errors
**Solution**: Increase `--memory` flag (try 4Gi or 8Gi)

### Issue: Video processing times out
**Solution**: Increase `--timeout` to 900 seconds (15 minutes)

### Issue: Permission errors
**Solution**: Ensure your service account has necessary permissions:
```bash
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member=serviceAccount:${PROJECT_ID}@appspot.gserviceaccount.com \
  --role=roles/run.admin
```

### Issue: Container fails to start
**Solution**: Check logs:
```bash
gcloud run logs read abnormality-detection --limit 50
```

## Monitoring and Management

### View logs
```bash
gcloud run logs read abnormality-detection --limit 50
```

### View service details
```bash
gcloud run services describe abnormality-detection
```

### Update the application
```bash
# Make changes to your code, then:
gcloud builds submit --tag gcr.io/${PROJECT_ID}/abnormality-detection

# Deploy the new image
gcloud run deploy abnormality-detection \
  --image gcr.io/${PROJECT_ID}/abnormality-detection \
  --platform managed \
  --region us-central1
```

### Stop the service
```bash
gcloud run services delete abnormality-detection
```

## Costs

Google Cloud Run pricing:
- **Compute**: $0.00002400 per CPU/second (approx)
- **Memory**: $0.00000
250 per GB/second (approx)
- **Requests**: $0.40 per 1 million requests
- **Free tier**: 2 million requests/month, 360,000 GB/seconds/month

**Example costs for moderate usage**:
- 1000 requests/day × 30 days = 30,000 requests = ~$0.01/month
- Light processing (< 1 minute per video) = ~$0.10/month

## Next Steps

### 1. Set up custom domain (optional)
```bash
# In Cloud Run console, click the service
# Click "Manage Custom Domains"
# Add your domain and follow DNS setup
```

### 2. Enable authentication (recommended)
```bash
# Modify Cloud Run to require authentication:
gcloud run deploy abnormality-detection \
  --no-allow-unauthenticated
```

### 3. Set up CI/CD pipeline
Create a `.github/workflows/deploy.yml` for automatic deployment on code push:
```yaml
name: Deploy to Cloud Run
on:
  push:
    branches:
      - main
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Cloud Run
        uses: google-github-actions/deploy-cloudrun@v0
        with:
          service: abnormality-detection
          image: gcr.io/${{ secrets.GCP_PROJECT_ID }}/abnormality-detection
          region: us-central1
```

### 4. Monitor with Firebase Analytics
Enable monitoring in Firebase Console to track usage and performance.

## Quick Reference Commands

```bash
# List all Cloud Run services
gcloud run services list

# Get service URL
gcloud run services describe abnormality-detection --format 'value(status.url)'

# Deploy with all recommended settings
gcloud run deploy abnormality-detection \
  --source . \
  --platform managed \
  --region us-central1 \
  --memory 4Gi \
  --cpu 2 \
  --timeout 900 \
  --allow-unauthenticated

# View live logs
gcloud run logs read abnormality-detection --follow

# Delete service
gcloud run services delete abnormality-detection
```

## Support

For more information:
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Firebase Hosting](https://firebase.google.com/docs/hosting)
- [Cloud Run Pricing](https://cloud.google.com/run/pricing)
