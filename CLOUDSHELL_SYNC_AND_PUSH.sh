#!/bin/bash
# Sync Cloud Shell repo with GitHub and push

# Pull with merge (non-destructive)
git pull https://SanliData:YOUR_GITHUB_TOKEN@github.com/SanliData/records_ai_v2.git main --no-rebase

# If pull succeeds, push again
if [ $? -eq 0 ]; then
    echo "Pull successful, pushing..."
    git push https://SanliData:YOUR_GITHUB_TOKEN@github.com/SanliData/records_ai_v2.git main
else
    echo "Pull failed. Check for conflicts."
fi
