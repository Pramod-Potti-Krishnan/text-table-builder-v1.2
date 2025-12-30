#!/bin/bash
#
# Quick Test: Single I-Series Slide
#
# Tests skip_image_generation flag with a single slide.
# Usage:
#   ./test_single_slide.sh                    # With images (default)
#   SKIP_IMAGES=true ./test_single_slide.sh   # Without images (fast, no quota)
#

# Service URLs
TEXT_SERVICE="https://web-production-5daf.up.railway.app"
LAYOUT_SERVICE="https://web-production-f0d13.up.railway.app"

# Skip image flag (default: false)
SKIP_IMAGES=${SKIP_IMAGES:-false}

echo "=============================================="
echo "  Single I-Series Slide Test"
echo "=============================================="
echo ""
echo "Text Service:   $TEXT_SERVICE"
echo "Layout Service: $LAYOUT_SERVICE"
echo "Skip Images:    $SKIP_IMAGES"
echo ""

# Test parameters
LAYOUT="I1"
VARIANT="single_column_3section_i1"
LAYOUT_NAME="I1-image-left"
TITLE="Digital Strategy Overview"
NARRATIVE="Our digital strategy focuses on three key pillars for transformation"
TOPICS='["Innovation","Efficiency","Growth"]'
IMAGE_HINT="digital transformation technology abstract"

echo ">>> Generating slide: $LAYOUT + $VARIANT"
echo "    Title: $TITLE"
echo ""

# Call Text Service
TEXT_RESPONSE=$(curl -s -X POST "$TEXT_SERVICE/v1.2/iseries/$LAYOUT" \
  -H "Content-Type: application/json" \
  -d "{
    \"slide_number\": 1,
    \"layout_type\": \"$LAYOUT\",
    \"title\": \"$TITLE\",
    \"subtitle\": \"Skip Image Test\",
    \"narrative\": \"$NARRATIVE\",
    \"topics\": $TOPICS,
    \"visual_style\": \"illustrated\",
    \"image_prompt_hint\": \"$IMAGE_HINT\",
    \"content_style\": \"bullets\",
    \"max_bullets\": 6,
    \"content_variant\": \"$VARIANT\",
    \"skip_image_generation\": $SKIP_IMAGES,
    \"context\": {
      \"content_context\": {
        \"audience\": {
          \"audience_type\": \"executives\",
          \"complexity_level\": \"moderate\"
        },
        \"purpose\": {
          \"purpose_type\": \"inform\",
          \"emotional_tone\": \"professional\"
        }
      },
      \"image_style_agreement\": {
        \"archetype\": \"photorealistic\",
        \"mood\": \"professional\",
        \"color_scheme\": \"neutral\",
        \"lighting\": \"professional\",
        \"avoid_elements\": [\"anime\", \"cartoon\"],
        \"quality_tier\": \"smart\"
      },
      \"styling_mode\": \"inline_styles\"
    }
  }")

# Extract fields
CONTENT_HTML=$(echo "$TEXT_RESPONSE" | jq -r '.content_html')
IMAGE_URL=$(echo "$TEXT_RESPONSE" | jq -r '.image_url')
IMAGE_FALLBACK=$(echo "$TEXT_RESPONSE" | jq -r '.image_fallback')

if [ "$CONTENT_HTML" == "null" ] || [ -z "$CONTENT_HTML" ]; then
  echo "ERROR: Text Service failed"
  echo "$TEXT_RESPONSE" | jq . 2>/dev/null || echo "$TEXT_RESPONSE"
  exit 1
fi

echo "Text Service Response:"
echo "  - Content: ${#CONTENT_HTML} chars"
echo "  - Image URL: ${IMAGE_URL:0:50}..."
echo "  - Fallback: $IMAGE_FALLBACK"
echo ""

# Escape content for JSON
BODY_ESCAPED=$(echo "$CONTENT_HTML" | jq -Rs .)
IMAGE_ESCAPED=$(echo "$IMAGE_URL" | jq -Rs . | sed 's/^"//;s/"$//')

# Build slide JSON
SLIDE_JSON="{
  \"layout\": \"$LAYOUT_NAME\",
  \"content\": {
    \"slide_title\": \"$TITLE\",
    \"subtitle\": \"Skip Images: $SKIP_IMAGES\",
    \"image_url\": \"$IMAGE_ESCAPED\",
    \"body\": $BODY_ESCAPED,
    \"logo\": \" \",
    \"presentation_name\": \"Single Slide Test\"
  }
}"

# Create presentation via Layout Service
LAYOUT_REQUEST="{
  \"title\": \"Single Slide Test (skip_images=$SKIP_IMAGES)\",
  \"slides\": [$SLIDE_JSON]
}"

echo ">>> Creating presentation..."

LAYOUT_RESPONSE=$(curl -s -X POST "$LAYOUT_SERVICE/api/presentations" \
  -H "Content-Type: application/json" \
  -d "$LAYOUT_REQUEST")

PRES_ID=$(echo "$LAYOUT_RESPONSE" | jq -r '.id')

if [ "$PRES_ID" == "null" ] || [ -z "$PRES_ID" ]; then
  echo "ERROR: Layout Service failed"
  echo "$LAYOUT_RESPONSE" | jq . 2>/dev/null || echo "$LAYOUT_RESPONSE"
  exit 1
fi

URL="$LAYOUT_SERVICE/p/$PRES_ID"

echo ""
echo "=============================================="
echo "  SUCCESS!"
echo "=============================================="
echo ""
echo "Presentation: $URL"
echo ""
echo "Verification:"
if [ "$SKIP_IMAGES" == "true" ]; then
  echo "  - SKIP_IMAGES=true was sent"
  if [ "$IMAGE_FALLBACK" == "true" ]; then
    echo "  - image_fallback=true (CORRECT - image was skipped)"
  else
    echo "  - image_fallback=false (UNEXPECTED - image was generated)"
    echo "    Check if deployment completed!"
  fi
else
  echo "  - SKIP_IMAGES=false (default)"
  echo "  - Image generation attempted normally"
fi
echo ""

# Open in browser
echo "Opening in browser..."
open "$URL"

echo "=============================================="
