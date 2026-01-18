#!/bin/bash

# Navigate to the picture directory
cd "$(dirname "$0")/../docs/slides/pic" || exit 1

echo "Starting SVG to PNG conversion using macOS QuickLook..."

for file in *.svg; do
    if [ ! -f "$file" ]; then
        echo "No SVG files found in $(pwd)"
        continue
    fi

    # Get filename without extension
    filename=$(basename "$file" .svg)
    
    echo "Processing: $file"
    
    # Use qlmanage to generate a PNG thumbnail (width 1000px)
    # -t: Thumbnail mode
    # -s 1000: Size 1000px
    # -o .: Output to current directory
    qlmanage -t -s 1000 -o . "$file" >/dev/null 2>&1
    
    # Rename the output (qlmanage produces filename.svg.png)
    if [ -f "$file.png" ]; then
        mv "$file.png" "$filename.png"
        echo "✅ Generated: $filename.png"
    else
        echo "❌ Failed to convert $file"
    fi
done

echo "Conversion complete. You can now compile your LaTeX document."
