#!/bin/bash

# Show git status
git status

# Ask for commit message
echo "Enter commit message:"
read commitMessage

# Add, commit, push
git add .
git commit -m "$commitMessage"
git push origin main

