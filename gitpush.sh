#!/bin/bash

# Check if a commit message was provided as an argument
if [ -z "$1" ]; then
  echo "Error: Please provide a commit message as an argument."
  echo "Usage: $0 \"Your commit message\""
  exit 1
fi

# Store the first argument ($1) as the commit message
commitMessage="$1"

# Show git status
git status

# Add, commit, push
git add .
git commit -m "$commitMessage"
git push origin main

