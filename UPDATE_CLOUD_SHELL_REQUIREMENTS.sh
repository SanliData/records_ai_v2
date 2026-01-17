#!/bin/bash
# Update requirements.txt in Cloud Shell

echo "Updating requirements.txt to add rapidfuzz..."

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "ERROR: requirements.txt not found!"
    exit 1
fi

# Check if rapidfuzz already exists
if grep -q "rapidfuzz" requirements.txt; then
    echo "rapidfuzz already in requirements.txt"
else
    echo "Adding rapidfuzz to requirements.txt..."
    echo "rapidfuzz>=3.0.0" >> requirements.txt
    echo "Done. Updated requirements.txt:"
    cat requirements.txt
fi



