# Cloudflare R2 Storage Setup Guide

This guide will help you set up Cloudflare R2 storage for persistent file storage in your ticket verification application.

## Prerequisites

- A Cloudflare account
- Access to Cloudflare Dashboard
- Your application deployed on Render (or another hosting platform)

## Step-by-Step Setup

### 1. Log in to your Cloudflare dashboard
Go to [https://dash.cloudflare.com](https://dash.cloudflare.com) and sign in with your account.

### 2. Find your Account ID

* From the left-hand sidebar, click **"Home"** (the Cloudflare icon).
* Under **"Account Home"**, you'll see **"Account ID"**. Copy that; you'll use it for your R2 endpoint.

### 3. Enable R2 for your account (if you haven't yet)

* In the sidebar, scroll to **"Storage"** and click **"R2"**.
* If it prompts "Enable R2," just click **"Enable"**.

### 4. Create an R2 bucket

* Still under **Storage → R2**, click **"Create bucket"**.
* Give it a name (e.g. `my-app-storage` or `depsi-ticket-storage`).
* Leave public/private as default (private).
* Click **"Create"**.

### 5. Generate access keys

* In the R2 dashboard, click the **"Access keys"** tab.
* Click **"Create access key"**.
* Choose the policy you need (for full read/write, select **"Read/Write"**).
* Click **"Create"**.
* Copy the **Access Key ID** and **Secret Access Key**—you won't be able to see the secret again after you close the dialog.

### 6. Determine your endpoint URL
The endpoint is always:

```
https://<ACCOUNT_ID>.r2.cloudflarestorage.com
```

Replace `<ACCOUNT_ID>` with the value you copied in Step 2.

### 7. Configure your app's environment variables

#### For Render Deployment:

1. Go to your Render dashboard
2. Navigate to your web service
3. Click on "Environment" in the left sidebar
4. Add these environment variables:

```
R2_ACCOUNT_ID=<your account ID>
R2_BUCKET_NAME=<your bucket name>
R2_ACCESS_KEY_ID=<the access key ID>
R2_SECRET_ACCESS_KEY=<the secret you copied>
R2_ENDPOINT=https://<your account ID>.r2.cloudflarestorage.com
```

#### For Local Development:

Create a `.env` file in your project root:

```bash
# Cloudflare R2 Configuration
R2_ACCOUNT_ID=your_account_id_here
R2_BUCKET_NAME=your_bucket_name_here
R2_ACCESS_KEY_ID=your_access_key_id_here
R2_SECRET_ACCESS_KEY=your_secret_access_key_here
R2_ENDPOINT=https://your_account_id_here.r2.cloudflarestorage.com
```

**Note:** Make sure `.env` is in your `.gitignore` file to avoid committing secrets.

### 8. Test the connection

After setting up the environment variables, you can test the R2 connection:

```bash
# For local testing
python test_r2_connection.py

# Or if using environment variables from .env file
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
exec(open('test_r2_connection.py').read())
"
```

### 9. Deploy and verify

1. **Deploy your service** with the new environment variables.
2. **Check the logs** to ensure R2 initialization is successful. You should see:
   ```
   R2 storage initialized successfully. Bucket: your-bucket-name
   ```
3. **Test file uploads** by submitting a ticket with a receipt image.
4. **Verify persistence** by restarting your service and checking that uploaded files are still accessible.

## Troubleshooting

### Common Issues

1. **"Missing R2 environment variables" warning**
   - Ensure all 5 environment variables are set correctly
   - Check for typos in variable names
   - Verify values don't have extra spaces

2. **"Failed to initialize R2 client" error**
   - Verify your access keys are correct
   - Check that your account ID matches the endpoint URL
   - Ensure your bucket name is correct

3. **"Access Denied" errors**
   - Verify your access key has read/write permissions
   - Check that your bucket exists and is accessible

4. **Files not accessible after restart**
   - This indicates R2 is not properly configured
   - Check that environment variables persist after deployment
   - Run the connection test script

### Fallback Behavior

If R2 is not configured or fails to initialize, the application will automatically fall back to local file storage. You'll see this message in the logs:

```
R2 not available, using local storage for receipt
```

This ensures your application continues to work even without R2 configured.

### Monitoring R2 Usage

You can monitor your R2 usage in the Cloudflare dashboard:

1. Go to **Storage → R2**
2. Click on your bucket name
3. View storage usage, request metrics, and costs

## Security Best Practices

1. **Use least-privilege access keys**: Only grant the permissions your application needs
2. **Rotate access keys regularly**: Generate new keys periodically and update your environment variables
3. **Monitor access logs**: Keep an eye on unusual access patterns
4. **Keep secrets secure**: Never commit access keys to version control

## Cost Considerations

Cloudflare R2 pricing (as of 2024):
- **Storage**: $0.015 per GB per month
- **Class A operations** (writes): $4.50 per million requests
- **Class B operations** (reads): $0.36 per million requests
- **Egress**: Free (no data transfer costs)

For a typical ticket verification application, costs should be minimal.

## Support

If you encounter issues:

1. Check the application logs for error messages
2. Run the connection test script
3. Verify your Cloudflare R2 configuration
4. Consult the [Cloudflare R2 documentation](https://developers.cloudflare.com/r2/)

## Migration from Local Storage

If you're migrating from local storage to R2:

1. Set up R2 as described above
2. Deploy the updated application
3. New files will automatically use R2
4. Existing local files will continue to work
5. Optionally, migrate existing files to R2 using a custom script

The application handles both storage types seamlessly, so migration can be gradual.