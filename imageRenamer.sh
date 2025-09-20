#!/bin/bash

# Check if exiftool exists
if command -v exiftool >/dev/null 2>&1; then
    echo "exiftool is already installed."
else
    echo " exiftool is not installed."

    # Check if Homebrew exists
    if command -v brew >/dev/null 2>&1; then
        echo "Installing exiftool using Homebrew..."
        brew install exiftool
    else
        echo "Homebrew is not installed."
        echo "Install Homebrew first with:"
        echo '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
        exit 1
    fi
fi

# Check if folder was provided
if [ -z "$1" ]; then
    echo "Usage: $0 <folder_path>"
    exit 1
fi

FOLDER="$1"

# Check if folder exists
if [ ! -d "$FOLDER" ]; then
    echo "Not a valid folder: $FOLDER"
    exit 1
fi

echo "Reading images from: $FOLDER"

invalid=0

for IMAGE in "$FOLDER"/*.{jpg,jpeg,png,JPG,JPEG,PNG}; do
    if [ -f "$IMAGE" ]; then
        echo "----------------------------------------"
        echo "Processing: $IMAGE"

        # Extract EXIF Date
        DATE_RAW=$(exiftool -s -s -s -DateTimeOriginal "$IMAGE" 2>/dev/null || echo "")

        if [ -n "$DATE_RAW" ]; then
            # Convert to DD-MM-YYYY
            DATE_FORMATTED=$(echo "$DATE_RAW" | awk -F'[: ]' '{printf "%02d-%02d-%04d", $3,$2,$1}')

            EXT="${IMAGE##*.}"
            EXT_LC=$(echo "$EXT" | tr '[:upper:]' '[:lower:]')

            NEW_NAME="$FOLDER/$DATE_FORMATTED.$EXT_LC"

            # If file exists, add counter
            COUNTER=1
            while [ -f "$NEW_NAME" ]; do
                NEW_NAME="$FOLDER/${DATE_FORMATTED}_$COUNTER.$EXT_LC"
                COUNTER=$((COUNTER+1))
            done

            mv "$IMAGE" "$NEW_NAME"
            echo "Renamed to: $NEW_NAME"
        else
            echo " No EXIF date found, skipping..."
	    invalid=$((invalid+1))	
        fi
    fi
done

echo "Done renaming images."
echo "Invalid Images count $invalid"
