# Deploying Budget Planner Chatbot on Render

This guide explains how to deploy your Budget Planner Chatbot on Render.

## Prerequisites

- A Render account (sign up at https://render.com if you don't have one)
- Your Google API key for Gemini AI

## Deployment Steps

1. **Create a new Web Service on Render**

   - Log in to your Render account
   - Click on "New" and select "Web Service"
   - Connect your GitHub repository or use the "Deploy from existing repository" option

2. **Configure your Web Service**

   - **Name**: Choose a name for your service (e.g., "budget-planner-chatbot")
   - **Runtime**: Choose "Python 3"
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: Choose the Free tier to start

3. **Add Environment Variables**

   - Click on "Environment" tab
   - Add the following environment variable:
     - Key: `GOOGLE_API_KEY`
     - Value: Your Google Gemini API key

4. **Deploy**

   - Click "Create Web Service"
   - Render will automatically build and deploy your application

5. **Access Your Chatbot**

   - Once deployment is complete, Render will provide you with a URL
   - Your chatbot will be accessible at this URL

## Troubleshooting

- If you encounter any issues, check the logs in the Render dashboard
- Make sure your environment variables are set correctly
- Verify that all required dependencies are listed in requirements.txt

## Additional Notes

- The free tier on Render may have some limitations, including spinning down after periods of inactivity
- For production use, consider upgrading to a paid plan
