#!/bin/bash
#
# Test Script: I-Series Comparison Variants (Phase 3)
#
# Tests 8 slides total:
# - 2 variants (comparison_2col, comparison_3col)
# - 4 layouts (I1, I2, I3, I4)
#
# Uses: POST /v1.2/iseries/{I1|I2|I3|I4} endpoint
# Generates content + image via Text Service -> Creates ONE presentation
#

# Service URLs
TEXT_SERVICE="https://web-production-5daf.up.railway.app"
LAYOUT_SERVICE="https://web-production-f0d13.up.railway.app"

# Output directory for responses
OUTPUT_DIR="./test_outputs/iseries_comparison_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"

# Test configurations: layout|variant|layout_name|title|narrative|topics|image_hint
declare -a TESTS=(
  # I1: Wide Image Left (2 slides)
  "I1|comparison_2col_i1|I1-image-left|Before vs After Analysis|Compare the dramatic transformation achieved through our digital initiative|Before Implementation,After Implementation|transformation comparison before after"
  "I1|comparison_3col_i1|I1-image-left|Service Tier Comparison|Compare our three service tiers to find the best fit for your needs|Starter,Professional,Enterprise|pricing tiers comparison plans"

  # I2: Wide Image Right (2 slides)
  "I2|comparison_2col_i1|I2-image-right|Cloud vs On-Premise|Detailed comparison of cloud and on-premise deployment options|Cloud Solution,On-Premise Solution|cloud versus on premise servers"
  "I2|comparison_3col_i1|I2-image-right|Platform Options|Three platform options designed for different organizational needs|Basic,Advanced,Premium|platform options technology comparison"

  # I3: Narrow Image Left (2 slides)
  "I3|comparison_2col_i3|I3-image-left-narrow|Traditional vs Modern|Comparing traditional approaches with modern methodologies|Traditional Approach,Modern Approach|traditional modern comparison innovation"
  "I3|comparison_3col_i3|I3-image-left-narrow|Deployment Models|Three deployment models for flexible infrastructure choices|Public Cloud,Private Cloud,Hybrid Cloud|cloud deployment models infrastructure"

  # I4: Narrow Image Right (2 slides)
  "I4|comparison_2col_i3|I4-image-right-narrow|Manual vs Automated|Comparing manual processes with automated solutions|Manual Process,Automated Solution|automation comparison manual robot"
  "I4|comparison_3col_i3|I4-image-right-narrow|Team Structure Options|Three organizational models for modern teams|Centralized,Distributed,Hybrid|team organization structure modern"
)

echo "=============================================="
echo "  I-Series Comparison Variants Test"
echo "  Phase 3: 8 Slides (2 variants x 4 layouts)"
echo "=============================================="
echo ""
echo "Text Service:   $TEXT_SERVICE"
echo "Layout Service: $LAYOUT_SERVICE"
echo "Output Dir:     $OUTPUT_DIR"
echo ""

# Array to collect slides JSON
SLIDES_JSON="["
FIRST_SLIDE=true
SUCCESS_COUNT=0
FAIL_COUNT=0
SLIDE_NUM=0

for item in "${TESTS[@]}"; do
  IFS='|' read -r layout variant layout_name title narrative topics image_hint <<< "$item"
  ((SLIDE_NUM++))

  echo "----------------------------------------------"
  echo ">>> Test $SLIDE_NUM: $layout + $variant"
  echo "    Title: $title"

  # Convert comma-separated topics to JSON array
  TOPICS_JSON=$(echo "$topics" | sed 's/,/","/g' | sed 's/^/["/' | sed 's/$/"]/')

  # Generate content from Text Service I-series endpoint
  TEXT_RESPONSE=$(curl -s -X POST "$TEXT_SERVICE/v1.2/iseries/$layout" \
    -H "Content-Type: application/json" \
    -d "{
      \"slide_number\": $SLIDE_NUM,
      \"layout_type\": \"$layout\",
      \"title\": \"$title\",
      \"subtitle\": \"Phase 3 Test\",
      \"narrative\": \"$narrative\",
      \"topics\": $TOPICS_JSON,
      \"visual_style\": \"illustrated\",
      \"image_prompt_hint\": \"$image_hint\",
      \"content_style\": \"bullets\",
      \"max_bullets\": 5,
      \"content_variant\": \"$variant\",
      \"context\": {\"audience\": \"executives\", \"tone\": \"professional\"}
    }")

  # Save raw response
  echo "$TEXT_RESPONSE" > "$OUTPUT_DIR/${SLIDE_NUM}_${layout}_${variant}_response.json"

  # Extract fields from response
  CONTENT_HTML=$(echo "$TEXT_RESPONSE" | jq -r '.content_html')
  IMAGE_URL=$(echo "$TEXT_RESPONSE" | jq -r '.image_url')
  IMAGE_FALLBACK=$(echo "$TEXT_RESPONSE" | jq -r '.image_fallback')

  if [ "$CONTENT_HTML" == "null" ] || [ -z "$CONTENT_HTML" ]; then
    echo "    ERROR: Text Service failed to generate content"
    echo "$TEXT_RESPONSE" | jq . 2>/dev/null || echo "$TEXT_RESPONSE"
    ((FAIL_COUNT++))
    continue
  fi

  echo "    Text Service: OK"
  echo "    Image: ${IMAGE_URL:0:50}..."
  echo "    Fallback: $IMAGE_FALLBACK"
  echo "    Content: ${#CONTENT_HTML} chars"
  ((SUCCESS_COUNT++))

  # Save HTML for inspection
  echo "$CONTENT_HTML" > "$OUTPUT_DIR/${SLIDE_NUM}_${layout}_${variant}_body.html"

  # Escape for JSON
  BODY_ESCAPED=$(echo "$CONTENT_HTML" | jq -Rs .)
  IMAGE_ESCAPED=$(echo "$IMAGE_URL" | jq -Rs . | sed 's/^"//;s/"$//')

  # Build slide JSON for Layout Service
  SLIDE_JSON="{
    \"layout\": \"$layout_name\",
    \"content\": {
      \"slide_title\": \"$title\",
      \"subtitle\": \"$variant\",
      \"image_url\": \"$IMAGE_ESCAPED\",
      \"body\": $BODY_ESCAPED,
      \"presentation_name\": \"I-Series Phase 3\"
    }
  }"

  # Add to slides array
  if [ "$FIRST_SLIDE" = true ]; then
    SLIDES_JSON="$SLIDES_JSON$SLIDE_JSON"
    FIRST_SLIDE=false
  else
    SLIDES_JSON="$SLIDES_JSON,$SLIDE_JSON"
  fi
done

# Close slides array
SLIDES_JSON="$SLIDES_JSON]"

echo ""
echo "=============================================="
echo "  Creating Single Presentation"
echo "=============================================="
echo ""
echo "Slides generated: $SUCCESS_COUNT success, $FAIL_COUNT failed"

# Save slides JSON for debugging
echo "$SLIDES_JSON" > "$OUTPUT_DIR/all_slides.json"

# Create single presentation with all slides
LAYOUT_REQUEST="{
  \"title\": \"I-Series Phase 3: Comparison (8 slides)\",
  \"slides\": $SLIDES_JSON
}"

echo "$LAYOUT_REQUEST" > "$OUTPUT_DIR/layout_request.json"

LAYOUT_RESPONSE=$(curl -s -X POST "$LAYOUT_SERVICE/api/presentations" \
  -H "Content-Type: application/json" \
  -d "$LAYOUT_REQUEST")

echo "$LAYOUT_RESPONSE" > "$OUTPUT_DIR/layout_response.json"

PRES_ID=$(echo "$LAYOUT_RESPONSE" | jq -r '.id')

if [ "$PRES_ID" == "null" ] || [ -z "$PRES_ID" ]; then
  echo "ERROR: Layout Service failed to create presentation"
  echo "$LAYOUT_RESPONSE" | jq . 2>/dev/null || echo "$LAYOUT_RESPONSE"
  exit 1
fi

URL="$LAYOUT_SERVICE/p/$PRES_ID"

echo ""
echo "=============================================="
echo "  SUCCESS! Phase 3 Complete"
echo "=============================================="
echo ""
echo "Presentation ID: $PRES_ID"
echo "URL: $URL"
echo ""
echo "Slides: $SUCCESS_COUNT / 8"
echo "Output: $OUTPUT_DIR"
echo ""
echo "Review Checklist:"
echo "  [ ] Content fits within layout bounds"
echo "  [ ] Image + content balance looks correct"
echo "  [ ] Character counts are appropriate"
echo "  [ ] No overflow or truncation"
echo "  [ ] Visual consistency across I1-I4"
echo ""

# Open in browser
echo "Opening presentation in browser..."
open "$URL"

echo "=============================================="
