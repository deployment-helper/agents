#!/bin/bash

# Set your repo and project details
REPO="deployment-helper/agents"
PROJECT_NUMBER="6"  # Use `gh project list` to find this number
LABEL="Blogs"
ORG="deployment-helper"
titles=(
  "Integrating OpenAI GPT with WhatsApp Cloud API for Smart Conversations"
  "Document-Aware GPT with Pinecone or Relevance AI (RAG on WhatsApp)"
  "Per-User Memory in Chatbots: Secure, Contextual, and Deletable"
  "Adding Voice to WhatsApp Bots with Whisper and Neural TTS"
  "Containerizing AI-Powered Bots for Cloud or Serverless Deployment"
  "From Prototype to Production: Testing, Docs & Handoff for AI Assistants"
)

descriptions=(
  "- WhatsApp Cloud API integration basics\n- Connecting user messages to OpenAI GPT\n- Webhook setup, media handling, and replies\n- Creating an intelligent WhatsApp assistant"
  "- Using Pinecone/Relevance AI for vector search\n- Document upload and RAG-based GPT answers\n- Real-time document-aware chat experiences"
  "- Per-user memory architecture\n- Handling GDPR-style 'delete-my-data' features\n- Scoping contextual memory (session, long-term)"
  "- Whisper for transcription\n- Neural TTS for audio replies\n- Integrating with WhatsApp’s audio capabilities"
  "- Dockerizing an AI chatbot app\n- Deployment on AWS Lambda, EC2, or Cloud Run\n- Secure configuration with secrets and HTTPS"
  "- Testing async chatbots\n- Writing handoff documentation\n- Deliverables and deployment readiness checklist"
)


# Loop through titles and create issues 
for i in "${!titles[@]}"; do
  title="${titles[$i]}"
  body="${descriptions[$i]}"
  
  echo "Creating issue: $title"
  # Convert \n to actual newlines by using echo with -e flag
  formatted_body=$(echo -e "$body")
  
  # Create the issue and capture the output URL
  issue_url=$(gh issue create \
    --repo "$REPO" \
    --title "$title" \
    --body "$formatted_body" \
    --label "$LABEL")

  echo "Issue created: $issue_url"
  
  # Add to GitHub Project (beta/projects v2) with owner parameter
  # Assuming it's your personal project; if it's an org project, specify the org name
  echo "Adding to project..."
  gh project item-add "$PROJECT_NUMBER" --owner "$ORG" --url "$issue_url"
done

echo "✅ All issues created and added to the project!"