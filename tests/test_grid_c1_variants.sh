#!/bin/bash
#
# Test Script: All Grid C1 Variants (Single Presentation)
#
# Uses: POST /v1.2/generate endpoint
# Generates content via Text Service → Creates ONE presentation with 9 slides
#
# Grid C1 Variants (9 total):
#   - grid_2x2_centered_c1
#   - grid_2x2_left_c1
#   - grid_2x2_numbered_c1
#   - grid_2x3_c1
#   - grid_2x3_left_c1
#   - grid_2x3_numbered_c1
#   - grid_3x2_c1
#   - grid_3x2_left_c1
#   - grid_3x2_numbered_c1
#

# Service URLs
TEXT_SERVICE="https://web-production-5daf.up.railway.app"
LAYOUT_SERVICE="https://web-production-f0d13.up.railway.app"

# Output directory for responses
OUTPUT_DIR="./test_outputs/grid_c1_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"

# All 9 Grid C1 Variants with appropriate content specs
declare -a VARIANTS=(
  "grid_2x2_centered_c1|Digital Transformation Pillars|Four key technology areas driving business innovation"
  "grid_2x2_left_c1|Core Business Capabilities|Essential competencies for competitive advantage"
  "grid_2x2_numbered_c1|Implementation Phases|Four-step deployment methodology"
  "grid_2x3_c1|Product Feature Overview|Six key features of our enterprise platform"
  "grid_2x3_left_c1|Service Offerings|Comprehensive suite of professional services"
  "grid_2x3_numbered_c1|Project Milestones|Six critical milestones for successful delivery"
  "grid_3x2_c1|Technology Stack|Modern architecture components"
  "grid_3x2_left_c1|Department Functions|Organizational capabilities overview"
  "grid_3x2_numbered_c1|Onboarding Steps|Six-step employee onboarding process"
)

echo "=============================================="
echo "  Grid C1 Variants Test Script"
echo "  Single Presentation with 9 Slides"
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

for item in "${VARIANTS[@]}"; do
  IFS='|' read -r variant title purpose <<< "$item"

  echo "----------------------------------------------"
  echo ">>> Generating: $variant"
  echo "    Title: $title"

  # Generate content from Text Service
  TEXT_RESPONSE=$(curl -s -X POST "$TEXT_SERVICE/v1.2/generate" \
    -H "Content-Type: application/json" \
    -d "{
      \"variant_id\": \"$variant\",
      \"slide_spec\": {
        \"slide_title\": \"$title\",
        \"slide_purpose\": \"$purpose\",
        \"key_message\": \"Demonstrate $variant template capabilities\",
        \"context\": \"Enterprise business presentation\",
        \"audience\": \"Executive leadership and stakeholders\"
      }
    }")

  # Save raw response
  echo "$TEXT_RESPONSE" > "$OUTPUT_DIR/${variant}_text_response.json"

  # Extract HTML body
  BODY_HTML=$(echo "$TEXT_RESPONSE" | jq -r '.html')

  if [ "$BODY_HTML" == "null" ] || [ -z "$BODY_HTML" ]; then
    echo "    ERROR: Text Service failed to generate content"
    echo "$TEXT_RESPONSE" | jq . 2>/dev/null || echo "$TEXT_RESPONSE"
    ((FAIL_COUNT++))
    continue
  fi

  echo "    Text Service: OK"
  ((SUCCESS_COUNT++))

  # Save HTML for inspection
  echo "$BODY_HTML" > "$OUTPUT_DIR/${variant}_body.html"

  # Escape for JSON
  BODY_ESCAPED=$(echo "$BODY_HTML" | jq -Rs .)

  # Build slide JSON
  SLIDE_JSON="{
    \"layout\": \"C1-text\",
    \"content\": {
      \"title\": \"$title\",
      \"subtitle\": \"$purpose ($variant)\",
      \"body\": $BODY_ESCAPED,
      \"logo\": \" \"
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
  \"title\": \"Grid C1 Variants - All 9 Templates\",
  \"template_id\": \"L25\",
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
echo "  SUCCESS!"
echo "=============================================="
echo ""
echo "Presentation ID: $PRES_ID"
echo "URL: $URL"
echo ""
echo "Slides: $SUCCESS_COUNT"
echo "Output: $OUTPUT_DIR"
echo ""

# Open in browser
echo "Opening presentation in browser..."
open "$URL"

echo "=============================================="
