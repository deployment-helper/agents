#!/bin/bash

# Set your repo and project details
REPO="deployment-helper/agents"
PROJECT_NUMBER="6"  # Use `gh project list` to find this number
LABEL="Blogs"
ORG="deployment-helper"
titles=(  
  "Memory Pruning in AI Agents: How to Keep the Important Stuff"
  "How to Chain LLMs for Smarter Decision-Making and Suggestion Generation"
  "RAG Systems with LangChain: Connecting Vector Search to Language Models"
  "Optimizing Context Windows with RAG and Memory Graph Techniques"
  "Using Embeddings to Build Semantic Recall in AI Agents"
  "Advanced Prompt Engineering for Multi-Agent Orchestration"
  "From Prompt to Action: Designing Language-Driven Workflows"
  "Context Prioritization Strategies in LLM Chains"
)

descriptions=(
  "- Techniques for pruning stale memory\n- Priority scoring and summarization\n- Keeping memory efficient for low-latency"
  "- Combining agents with shared memory\n- Steps to build reasoning chains\n- Examples of summarization + synthesis"
  "- Setting up vector stores\n- LangChain retrievers and pipelines\n- End-to-end RAG architecture"
  "- Working with limited context window\n- Sliding window + chunking + vector compression\n- RAG optimization techniques"
  "- What are embeddings?\n- How they power semantic memory\n- Use cases in real-time AI assistants"
  "- Prompt templates for multi-agent use\n- Dynamic variable handling\n- Reflection & recursive improvement"
  "- LLM as a flow controller\n- Triggering actions based on structured prompts\n- Examples from productivity AI"
  "- Deciding what matters in large input data\n- Scoring, relevance, and fallback strategies\n- Reducing prompt overload"
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