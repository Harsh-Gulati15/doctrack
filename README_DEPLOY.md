# 🚀 DocTrack — Google Cloud Run Deployment Guide

> **A beginner-friendly, step-by-step guide to taking DocTrack from your computer to the cloud!**  
> No deep DevOps knowledge required. Every command is provided with clear explanations and visual UI walkthroughs.

---

## 📋 Table of Contents
1. [Overview & Architecture](#-overview--architecture)
2. [Prerequisites](#-prerequisites)
3. [Step 1: Create a Google Cloud Project](#-step-1-create-a-google-cloud-project)
4. [Step 2: Enable Required Google Cloud APIs](#-step-2-enable-required-google-cloud-apis)
5. [Step 3: Set Up a Cloud MySQL Database](#-step-3-set-up-a-cloud-mysql-database)
   - [Option A: Railway (Recommended — Free Tier)](#option-a-railway-recommended--easiest--free)
   - [Option B: Aiven (Free Tier)](#option-b-aiven-free-tier)
   - [Option C: Google Cloud SQL (Production / Pay-as-you-go)](#option-c-google-cloud-sql-pay-as-you-go)
6. [Step 4: Create a Google Cloud Storage (GCS) Bucket](#-step-4-create-a-google-cloud-storage-gcs-bucket)
7. [Step 5: Configure Environment Variables (`.env.cloud`)](#-step-5-configure-environment-variables-envcloud)
8. [Step 6: Deploy to Cloud Run](#-step-6-deploy-to-cloud-run)
9. [Step 7: Seed the Cloud Database with Sample Data](#-step-7-seed-the-cloud-database-with-sample-data)
10. [Step 8: Verify Your Deployment](#-step-8-verify-your-deployment)
11. [Step 9: Manage Environment Variables via Web Console](#-step-9-manage-environment-variables-via-web-console)
12. [Troubleshooting & FAQs](#-troubleshooting--faqs)
13. [Cost & Free Tier Breakdown](#-cost--free-tier-breakdown)

---

## 🏛 Overview & Architecture

When deployed to Google Cloud, DocTrack runs as a containerized web application:

```
                  ┌──────────────────────────────────────────────┐
                  │                 Users / Web Browser          │
                  └───────────────────────┬──────────────────────┘
                                          │ HTTPS
                                          ▼
                  ┌──────────────────────────────────────────────┐
                  │           Google Cloud Run Service           │
                  │  - Runs DocTrack Docker container            │
                  │  - Built-in Tesseract OCR & WeasyPrint       │
                  │  - Auto-scales to 0 when idle (saves money!) │
                  └──────────────┬───────────────┬───────────────┘
                                 │               │
                 Database queries│               │ File storage
                                 ▼               ▼
        ┌─────────────────────────────┐   ┌─────────────────────────────┐
        │     Managed MySQL DB        │   │  Google Cloud Storage (GCS) │
        │ (Railway, Aiven, Cloud SQL) │   │ (Uploaded PDF / Images)     │
        └─────────────────────────────┘   └─────────────────────────────┘
                                 │
                                 ▼
                    ┌───────────────────────────┐
                    │     Google AI Studio      │
                    │  (Gemini API for Auto-    │
                    │   Categorization & OCR)   │
                    └───────────────────────────┘
```

---

## 🧰 Prerequisites

Before getting started, make sure you have:

1. **A Google Account**: (e.g., your personal `@gmail.com` or Google Workspace account).
2. **Google Cloud CLI (`gcloud`) installed**:
   - **Windows**: Download the [Google Cloud CLI Installer](https://cloud.google.com/sdk/docs/install#windows) and run it. Open PowerShell or Command Prompt and test with:
     ```bash
     gcloud --version
     ```
   - **macOS**: Install via Homebrew `brew install --cask google-cloud-sdk` or the macOS pkg installer.
   - **Linux**: Install via your distribution's package manager (`sudo apt-get install google-cloud-cli`).
   - *(Alternative: You can do everything using the in-browser **Google Cloud Shell** without installing anything locally!)*
3. **Google AI Studio Gemini API Key**:
   - Go to [Google AI Studio](https://aistudio.google.com/app/apikey).
   - Click **"Create API Key"** and copy the generated key string (e.g. `AIzaSy...`). Keep this safe!

---

## 📍 Step 1: Create a Google Cloud Project

Every service in Google Cloud lives inside a **Project**.

1. Open your web browser and navigate to the [Google Cloud Console](https://console.cloud.google.com/).
2. Log in with your Google account.
3. At the top left (next to "Google Cloud"), click the **Project Selector** dropdown.
4. In the dialog that pops up, click **"NEW PROJECT"** in the top-right corner.
   
   ```
   ┌─────────────────────────────────────────────────────────┐
   │ Select a project                       [ NEW PROJECT ]  │
   ├─────────────────────────────────────────────────────────┤
   │ Search projects...                                      │
   └─────────────────────────────────────────────────────────┘
   ```
5. Enter a project name, such as: `doctrack-prod`.
6. Notice the generated **Project ID** underneath the project name (e.g., `doctrack-prod-412308` or similar). **Copy and save this Project ID!** You will use it in multiple commands.
7. Click **"CREATE"**.
8. Make sure your newly created project is selected in the top bar dropdown.
9. **Enable Billing**:
   - Open the navigation menu (≡) on the top left and click **Billing**.
   - Link a credit or debit card.
   - *Don't worry: Google provides a free tier and a \$300 credit for new accounts. DocTrack easily stays inside the free tier.*

---

## 🔌 Step 2: Enable Required Google Cloud APIs

Cloud Run and its supporting services require specific APIs to be turned on.

Open your local terminal (PowerShell on Windows, Terminal on Mac/Linux, or Google Cloud Shell) and run:

```bash
# 1. Log in to Google Cloud
gcloud auth login

# 2. Set your active project (Replace YOUR_PROJECT_ID with your actual project ID)
gcloud config set project YOUR_PROJECT_ID

# 3. Enable Cloud Run, Cloud Build, Artifact Registry, and Cloud Storage APIs
gcloud services enable cloudbuild.googleapis.com run.googleapis.com artifactregistry.googleapis.com storage.googleapis.com
```

> 💡 **What this does**:
> - `cloudbuild.googleapis.com`: Builds your application container inside Google's cloud servers.
> - `run.googleapis.com`: Runs your application container on serverless infrastructure.
> - `artifactregistry.googleapis.com`: Stores your compiled container images securely.
> - `storage.googleapis.com`: Powers file storage for incoming letters and attachments.

---

## 🗄 Step 3: Set Up a Cloud MySQL Database

DocTrack requires a MySQL database. Choose **one** of the following three options based on your preference:

---

### Option A: Railway (Recommended — Easiest & Free)

[Railway.app](https://railway.app) provides a cloud MySQL database with 500 MB storage in minutes with zero database administration.

1. **Sign Up**: Go to [railway.app](https://railway.app) and sign up (using your GitHub account or Email).
2. **Create Project**: Click **"+ New Project"** → select **"Provision MySQL"**.
3. Railway will spin up a MySQL database in approximately 10 seconds.
4. **Get Credentials**:
   - Click on the newly created **MySQL** box in your canvas.
   - Switch to the **"Variables"** tab.
   - Look for the variable named **`MYSQL_URL`**.
   - Click the eye/copy icon to copy the value. It looks like:
     ```text
     mysql://root:AbCdEf123456@viaduct.proxy.rlwy.net:12345/railway
     ```
5. **Convert to SQLAlchemy Format**:
   - Add `+pymysql` right after `mysql`.
   - Your final `DATABASE_URL` looks like:
     ```text
     mysql+pymysql://root:AbCdEf123456@viaduct.proxy.rlwy.net:12345/railway
     ```
6. Save this string! This is your `DATABASE_URL`.

---

### Option B: Aiven (Free Tier)

[Aiven](https://aiven.io) offers a free MySQL plan on Google Cloud infrastructure.

1. Go to [aiven.io](https://aiven.io) and create a free account.
2. Click **"Create Service"** → select **MySQL**.
3. Choose **Google Cloud** as cloud provider and pick a region near you (e.g. `asia-south1` or `us-central1`).
4. Select the **Free Plan**.
5. Give your service a name (e.g., `doctrack-db`) and click **"Create Service"**.
6. Once active (status turns to *Running*):
   - On the service overview page, find **Service URI**.
   - It will look like: `mysql://avnadmin:PASSWORD@HOST:PORT/defaultdb?ssl-mode=REQUIRED`
   - Prepend `+pymysql` to `mysql` so it starts with:
     ```text
     mysql+pymysql://avnadmin:PASSWORD@HOST:PORT/defaultdb?ssl-mode=REQUIRED
     ```
7. Save this as your `DATABASE_URL`.

---

### Option C: Google Cloud SQL (Pay-as-you-go)

If you want everything natively hosted inside your Google Cloud project:

1. Create a Cloud SQL MySQL micro instance:
   ```bash
   gcloud sql instances create doctrack-db \
       --database-version=MYSQL_8_0 \
       --region=asia-south1 \
       --tier=db-f1-micro \
       --root-password="YourStrongPassword123"
   ```
2. Create the application database:
   ```bash
   gcloud sql databases create doctrack_db --instance=doctrack-db
   ```
3. Create an application user:
   ```bash
   gcloud sql users create doctrack_user \
       --instance=doctrack-db \
       --password="UserSecretPassword123"
   ```
4. Configure public IP access or connect via Cloud SQL Auth Proxy:
   - For Cloud Run, you can connect Cloud SQL directly via unix socket:
     ```text
     mysql+pymysql://doctrack_user:UserSecretPassword123@/doctrack_db?unix_socket=/cloudsql/YOUR_PROJECT_ID:asia-south1:doctrack-db
     ```
   - Make sure to add `--add-cloudsql-instances YOUR_PROJECT_ID:asia-south1:doctrack-db` to your Cloud Run deployment command.

---

## 🪣 Step 4: Create a Google Cloud Storage (GCS) Bucket

DocTrack uploads PDF scans and images directly to Google Cloud Storage so files persist permanently (Cloud Run containers are stateless).

1. Pick a unique bucket name. We recommend `doctrack-uploads-` followed by your Project ID:
   ```bash
   # Example: if your Project ID is doctrack-prod-412308
   gsutil mb -l asia-south1 gs://doctrack-uploads-YOUR_PROJECT_ID
   ```
   *(On Windows PowerShell, use the same `gsutil` command).*

2. *(Optional)* **Grant Public Read Access** or rely on the Cloud Run default service account:
   By default, Cloud Run uses the Compute Engine default service account (`PROJECT_NUMBER-compute@developer.gserviceaccount.com`), which already has access to storage buckets in the same project.

3. **CORS Configuration (if needed for direct browser previews)**:
   If document previews fail in browser due to CORS restrictions, create a file named `cors.json`:
   ```json
   [
     {
       "origin": ["*"],
       "method": ["GET", "HEAD"],
       "responseHeader": ["Content-Type", "Content-Disposition"],
       "maxAgeSeconds": 3600
     }
   ]
   ```
   And apply it:
   ```bash
   gsutil cors set cors.json gs://doctrack-uploads-YOUR_PROJECT_ID
   ```

---

## ⚙️ Step 5: Configure Environment Variables (`.env.cloud`)

In your local `doctrack` directory, create a file named **`.env.cloud`** (note the leading dot).

> 🔒 **Security Notice**: Never commit `.env.cloud` or `.env` to Git! It contains your database passwords and API keys. (It is already listed in `.gitignore`).

### 1. Generate a secure random Secret Key
In your terminal, run this Python one-liner to generate a strong 32-character key:
```bash
python -c "import secrets; print(secrets.token_hex(24))"
```
Copy the printed random string.

### 2. Fill in `.env.cloud`
Open or create `.env.cloud` and paste the following, replacing placeholders with your actual values:

```ini
FLASK_SECRET_KEY=9f3b145d2e7a890123456789abcdef0123456789abcdef01
DATABASE_URL=mysql+pymysql://root:PASSWORD@viaduct.proxy.rlwy.net:12345/railway
GEMINI_API_KEY=AIzaSyYourGoogleAIStudioKeyHere
GCS_BUCKET_NAME=doctrack-uploads-YOUR_PROJECT_ID
GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
FLASK_ENV=production
SLA_HOURS=48
AI_CONFIDENCE_THRESHOLD=0.75
```

*(Optional: Add email variables `MAIL_USERNAME` and `MAIL_PASSWORD` if you want automatic email notifications for SLAs).*

---

## 🚢 Step 6: Deploy to Cloud Run

You can deploy using the automated script `deploy.sh` or run the commands manually.

### Method 1: Using the Automated Script (`deploy.sh`)

If you are using **Git Bash**, **macOS Terminal**, **Linux**, or **Cloud Shell**:

```bash
# Make the deployment script executable
chmod +x deploy.sh

# Run the deployment
./deploy.sh
```

The script will:
1. Check your Google Cloud authentication.
2. Enable all required APIs automatically.
3. Create the Artifact Registry Docker repository (`doctrack-repo`) in `asia-south1`.
4. Build your container image using Google Cloud Build.
5. Deploy to Cloud Run with `.env.cloud` variables attached.
6. Display your public live URL!

---

### Method 2: Manual Commands (PowerShell / Windows / Any OS)

If you are on Windows PowerShell or prefer executing each step manually:

```powershell
# 1. Set your Project ID
$PROJECT_ID = "YOUR_PROJECT_ID"
$REGION = "asia-south1"

gcloud config set project $PROJECT_ID

# 2. Create the Artifact Registry repository (only needs to be done once)
gcloud artifacts repositories create doctrack-repo `
    --repository-format=docker `
    --location=$REGION `
    --description="DocTrack Docker images"

# 3. Build and submit the Docker image to Artifact Registry
$IMAGE = "$REGION-docker.pkg.dev/$PROJECT_ID/doctrack-repo/doctrack:latest"
gcloud builds submit --tag $IMAGE

# 4. Deploy the image to Cloud Run
# Notice: Replace with your actual values or load from your environment
gcloud run deploy doctrack `
    --image $IMAGE `
    --platform managed `
    --region $REGION `
    --allow-unauthenticated `
    --memory 512Mi `
    --cpu 1 `
    --min-instances 0 `
    --max-instances 2 `
    --timeout 120 `
    --set-env-vars FLASK_ENV=production,SLA_HOURS=48,AI_CONFIDENCE_THRESHOLD=0.75,GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GCS_BUCKET_NAME="doctrack-uploads-$PROJECT_ID"
```

> 💡 After the first deploy, you can paste the remaining sensitive variables (`DATABASE_URL`, `GEMINI_API_KEY`, `FLASK_SECRET_KEY`) directly into the Cloud Run web console as explained in **Step 9**.

---

## 🌱 Step 7: Seed the Cloud Database with Sample Data

Your cloud database is currently blank. Before logging in, run the database seeder script from your local machine so it creates all tables and populates sample departments, users, and letters.

### On Windows (Command Prompt `cmd.exe`):
```cmd
set DATABASE_URL=mysql+pymysql://root:PASSWORD@HOST:PORT/dbname
python seed_mock_data.py
```

### On Windows (PowerShell):
```powershell
$env:DATABASE_URL="mysql+pymysql://root:PASSWORD@HOST:PORT/dbname"
python seed_mock_data.py
```

### On macOS / Linux:
```bash
export DATABASE_URL="mysql+pymysql://root:PASSWORD@HOST:PORT/dbname"
python seed_mock_data.py
```

### 🔑 Default Seed Login Credentials

Once `seed_mock_data.py` finishes, it will print a confirmation message. The default accounts created are:

| Role | Username | Password | Email | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Super Admin** | `admin` | `Admin@123` | `admin@doctrack.gov.in` | Full system access, audit logs, SLA dashboard |
| **Receptionist 1** | `reception1` | `Admin@123` | `sunita@doctrack.gov.in` | Front desk letter entry, barcode tagging |
| **Receptionist 2** | `reception2` | `Admin@123` | `rafi@doctrack.gov.in` | Front desk letter entry |
| **Finance Head** | `fin_user1` | `Admin@123` | `fin_user1@doctrack.gov.in` | Head of Finance & Accounts |
| **HR Head** | `hr_user1` | `Admin@123` | `hr_user1@doctrack.gov.in` | Head of Human Resources |
| **IT Head** | `it_user1` | `Admin@123` | `it_user1@doctrack.gov.in` | Head of IT Department |
| **Legal Head** | `legal_user1` | `Admin@123` | `legal_user1@doctrack.gov.in` | Head of Legal & RTI |

*(Note: If you ran the minimal `seed.py` instead of `seed_mock_data.py`, the login is `admin` with password `admin123`).*

---

## ✅ Step 8: Verify Your Deployment

1. **Find your Live URL**:
   Look at the terminal output from `deploy.sh` or retrieve it using:
   ```bash
   gcloud run services describe doctrack --region=asia-south1 --format='value(status.url)'
   ```
   It will look like:
   ```
   https://doctrack-xxxxxx-el.a.run.app
   ```
2. **Open the URL in your web browser**. You will see the DocTrack Login screen.
3. Log in with:
   - **Username**: `admin`
   - **Password**: `Admin@123`
4. **Verification Checklist**:
   - [ ] Dashboard displays statistics (Total Inward, Pending, Overdue, Acknowledged).
   - [ ] Navigate to **"Inward Documents"** to view the sample seeded letters.
   - [ ] Try creating a new letter entry and uploading a sample PDF or image.
   - [ ] Verify that Gemini categorizes the letter and extracts sender/subject information.
   - [ ] Click **"Print Barcode"** or **"Export PDF"** to verify that WeasyPrint and barcoding work.

---

## 🎛 Step 9: Manage Environment Variables via Web Console

You can easily adjust settings or update secrets at any time without re-running CLI commands:

```
  Google Cloud Console
  ┌──────────────────────────────────────────────────────────────┐
  │ ≡ Google Cloud    Search: Cloud Run                          │
  ├──────────────────────────────────────────────────────────────┤
  │ Cloud Run Services > [ doctrack ]                            │
  │                                                              │
  │ [ EDIT & DEPLOY NEW REVISION ]   [ RESTART ]   [ DELETE ]    │
  ├──────────────────────────────────────────────────────────────┤
  │ Tabs: [ Metrics ] [ Logs ] [ Revisions ] [ Networking ]      │
  │       [ Container, Variables & Secrets ]                     │
  └──────────────────────────────────────────────────────────────┘
```

1. Go to the [Google Cloud Run Console](https://console.cloud.google.com/run).
2. Click on your service name: **`doctrack`**.
3. Click the **"EDIT & DEPLOY NEW REVISION"** button at the top.
4. Scroll down and click on the **"Container(s)"** tab.
5. Click **"Variables & Secrets"** (or Environment Variables).
6. Click **"+ ADD VARIABLE"** for each of your settings:
   - `DATABASE_URL` = `mysql+pymysql://...`
   - `FLASK_SECRET_KEY` = `your-secret-key`
   - `GEMINI_API_KEY` = `your-api-key`
   - `GCS_BUCKET_NAME` = `doctrack-uploads-YOUR_PROJECT_ID`
   - `GOOGLE_CLOUD_PROJECT` = `YOUR_PROJECT_ID`
   - `FLASK_ENV` = `production`
   - `SLA_HOURS` = `48`
   - `AI_CONFIDENCE_THRESHOLD` = `0.75`
7. Click **"DEPLOY"** at the bottom.
8. Cloud Run will seamlessly start a new revision with zero downtime!

---

## 🛠 Troubleshooting & FAQs

### 1. "Service Unavailable" or 500 / 503 HTTP Error
- **Cause**: The container failed to start or crashed on launch.
- **Solution**:
  1. Open [Cloud Run Console](https://console.cloud.google.com/run).
  2. Click **`doctrack`** → Click the **"LOGS"** tab.
  3. Look for red error lines. The traceback will tell you the exact issue (e.g., syntax error, missing environment variable, or database timeout).

### 2. "Can't connect to MySQL server on ..." or Database Connection Error
- **Cause**: The `DATABASE_URL` is incorrect or the remote database does not accept incoming connections.
- **Solution**:
  - Double-check that your `DATABASE_URL` starts with `mysql+pymysql://` and not plain `mysql://`.
  - In Railway / Aiven, verify that the service is running.
  - If using Google Cloud SQL, ensure that Cloud Run has Cloud SQL Client permissions or that the Cloud SQL instance connection name is registered.

### 3. File Uploads Fail or Give 403 Forbidden
- **Cause**: Cloud Run's service account doesn't have permission to write to your GCS bucket, or `GCS_BUCKET_NAME` has a typo.
- **Solution**:
  - Verify that `GCS_BUCKET_NAME` matches the bucket you created in Step 4.
  - In Cloud Console, go to **Cloud Storage** → click your bucket → **Permissions** tab.
  - Verify that your project's default Compute service account has the role `Storage Object Admin` or `Storage Object User`.

### 4. OCR Not Working on Scanned Documents
- **No configuration needed!** The `Dockerfile` includes `tesseract-ocr` and `poppler-utils` pre-installed.
- Ensure the uploaded file is a legible PDF, PNG, or JPEG.
- Check that `GEMINI_API_KEY` is provided; if Gemini AI is reachable, it will enhance or perform structured information extraction automatically.

### 5. PDF Generation / WeasyPrint Error (`pango not found`)
- **No action needed!** The Docker container automatically installs `libpango-1.0-0`, `libpangocairo-1.0-0`, and Cairo libraries so WeasyPrint PDF reports render cleanly.

---

## 💰 Cost & Free Tier Breakdown

Google Cloud Run and cloud databases provide generous free tiers:

| Service | Free Tier Allowance | DocTrack Consumption (Small/Medium Office) | Estimated Cost |
| :--- | :--- | :--- | :--- |
| **Google Cloud Run** | 2 Million requests/month + 360,000 GB-seconds memory free | ~5,000 – 20,000 requests/month | **$0.00 / month** |
| **Google Cloud Build** | 120 build-minutes per day free | ~3–5 minutes per deployment | **$0.00 / month** |
| **Google Cloud Storage** | 5 GB Standard storage / month free | ~500 MB – 2 GB of scanned PDFs | **$0.00 / month** |
| **Railway MySQL** | $5 monthly credit / 500 MB database free | ~20–50 MB for tens of thousands of records | **$0.00 / month** |
| **Google AI Studio** | Generous free rate limits for Gemini 1.5 Flash | Standard document categorization | **$0.00 / month** |
| **Total Estimated Monthly Cost** | | | **$0.00 (100% Free Tier)** |

> 💡 **Tip**: When nobody is using DocTrack (e.g. nights and weekends), Cloud Run automatically scales down to 0 container instances. You are never billed for idle time!
