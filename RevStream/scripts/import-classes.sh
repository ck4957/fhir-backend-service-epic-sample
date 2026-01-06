#!/bin/bash
#
# Import Classes Script
# Imports ObjectScript classes into IRIS via REST API
#

set -e

IRIS_HOST=${IRIS_HOST:-localhost}
IRIS_PORT=${IRIS_PORT:-52773}
NAMESPACE=${NAMESPACE:-USER}
USERNAME=${USERNAME:-SuperUser}
PASSWORD=${PASSWORD:-SYS}

SRC_DIR="./src"

echo "=============================================="
echo "  Import RevStream Classes to IRIS"
echo "=============================================="
echo "Target: $IRIS_HOST:$IRIS_PORT"
echo "Namespace: $NAMESPACE"
echo ""

# Function to import a single file
import_file() {
    local file=$1
    local filename=$(basename "$file")
    
    echo "Importing: $filename"
    
    # Read file content
    content=$(cat "$file")
    
    # Import via IRIS REST API
    curl -s -X POST \
        -u "$USERNAME:$PASSWORD" \
        -H "Content-Type: text/plain" \
        --data-binary "@$file" \
        "http://$IRIS_HOST:$IRIS_PORT/api/atelier/v1/$NAMESPACE/doc/$filename" \
        > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        echo "  ✓ Imported"
    else
        echo "  ✗ Failed"
    fi
}

# Find and import all .cls files
echo "Searching for classes in $SRC_DIR..."
echo ""

find "$SRC_DIR" -name "*.cls" | while read file; do
    import_file "$file"
done

echo ""
echo "=============================================="
echo "  Import Complete"
echo "=============================================="
echo ""
echo "Next: Compile classes in IRIS Studio or Management Portal"
