# Frontend Deployment Guide

**Date:** April 7, 2025  
**Author:** Kern Resources Team

## Overview

This guide provides step-by-step instructions for deploying the Kern Resources frontend static website to Render.com. The frontend is a simple static site that serves as the user interface for the Kern Resources application.

## Prerequisites

Before deploying the frontend, ensure you have:

1. A GitHub account with access to the Kern Resources repository
2. A Render.com account
3. The domain name you want to use (e.g., kernresources.com)

## Deployment Steps

### 1. Prepare the Repository

The frontend code is located in the `frontend/` directory of the main Kern Resources repository. Make sure all changes are committed and pushed to GitHub.

### 2. Create a New Static Site on Render

1. Log in to your Render.com account
2. Click on "New" and select "Static Site"
3. Connect your GitHub account if you haven't already
4. Select the Kern Resources repository
5. Configure the static site:
   - **Name:** kern-resources-frontend (or your preferred name)
   - **Root Directory:** frontend
   - **Build Command:** Leave empty (no build step required for this simple static site)
   - **Publish Directory:** . (the root of the frontend directory)
6. Click "Create Static Site"

Render will automatically deploy your static site. This process usually takes less than a minute.

### 3. Configure Custom Domain

1. In the Render dashboard, select your static site
2. Go to the "Settings" tab
3. Scroll down to the "Custom Domain" section
4. Click "Add Custom Domain"
5. Enter your domain name (e.g., kernresources.com)
6. Follow Render's instructions to update your DNS settings:
   - Add a CNAME record for www.kernresources.com pointing to your Render URL
   - Add an ANAME or ALIAS record for kernresources.com pointing to your Render URL
   - If your DNS provider doesn't support ANAME/ALIAS, use Render's provided IP addresses for A records

### 4. Verify SSL Configuration

Render automatically provisions SSL certificates for your custom domains. Verify that SSL is properly configured:

1. In the Render dashboard, select your static site
2. Go to the "Settings" tab
3. Scroll down to the "SSL" section
4. Ensure that the status is "Active"

### 5. Test the Deployment

1. Visit your custom domain (e.g., https://kernresources.com)
2. Verify that the site loads correctly
3. Test basic functionality:
   - Navigation links
   - Responsive design (test on mobile and desktop)
   - Search box (should show an alert in this test version)
   - Contact form (should show an alert in this test version)

### 6. Configure Backend Integration

For the frontend to communicate with the backend API:

1. Deploy the backend API on Render (see the Backend Deployment Guide)
2. Configure the API URL in the frontend:
   - In the Render dashboard, select your static site
   - Go to the "Environment" tab
   - Add an environment variable:
     - **Key:** API_URL
     - **Value:** https://api.kernresources.com (or your actual API URL)
3. Redeploy the static site to apply the environment variable

### 7. Set Up Monitoring

1. In the Render dashboard, select your static site
2. Go to the "Monitoring" tab
3. Enable "Uptime Monitoring"
4. Configure notification settings for downtime alerts

## Troubleshooting

### Site Not Loading

1. Check the Render dashboard for deployment errors
2. Verify that the DNS settings are correct
3. Check that SSL is properly configured

### CORS Issues

If the frontend cannot communicate with the backend API:

1. Verify that the API URL is correctly configured
2. Check that CORS is properly configured on the backend
3. Verify that the backend is running and accessible

### Custom Domain Not Working

1. Verify that the DNS settings are correct
2. Check that the DNS changes have propagated (can take up to 48 hours)
3. Verify that SSL is properly configured

## Maintenance

### Updating the Frontend

To update the frontend:

1. Make changes to the frontend code
2. Commit and push the changes to GitHub
3. Render will automatically deploy the changes

### Monitoring Performance

1. Use Render's built-in monitoring tools
2. Consider adding Google Analytics or similar for user behavior tracking
3. Regularly check for 404 errors or other issues

## Conclusion

The Kern Resources frontend is now deployed on Render.com and accessible via your custom domain. The static site provides a clean, responsive user interface for the Kern Resources application.

For any issues or questions, please contact the Kern Resources team.
