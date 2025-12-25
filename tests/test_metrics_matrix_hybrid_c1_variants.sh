#!/bin/bash
#
# Test Script: Metrics, Matrix, Hybrid C1 Themed Variants
#
# Uses: POST /v1.2/generate endpoint
# Generates content via Text Service → Creates ONE presentation with 8 slides
#

# Service URLs
TEXT_SERVICE="https://web-production-5daf.up.railway.app"
LAYOUT_SERVICE="https://web-production-f0d13.up.railway.app"

# Output directory for responses
OUTPUT_DIR="./test_outputs/metrics_matrix_hybrid_c1_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"

# All 8 C1 Variants: Metrics (4), Matrix (2), Hybrid (2)
declare -a VARIANTS=(
  # Metrics (4)
  "metrics_2x2_grid_c1|Q4 Performance|Four key metrics demonstrating quarterly business performance"
  "metrics_3col_c1|Revenue Highlights|Three essential revenue metrics for investor review"
  "metrics_3x2_grid_c1|Operations Dashboard|Six operational metrics tracking efficiency and output"
  "metrics_4col_c1|Growth Indicators|Four growth metrics showing year-over-year progress"
  # Matrix (2)
  "matrix_2x2_c1|Strategic Quadrant|Two-by-two strategic analysis of market positioning"
  "matrix_2x3_c1|Priority Matrix|Two-by-three priority matrix for project evaluation"
  # Hybrid (2)
  "hybrid_left_2x2_c1|Feature Overview|Left panel description with four key feature highlights"
  "hybrid_top_2x2_c1|Product Summary|Top panel summary with four supporting details"
)

echo "=============================================="
echo "  Metrics, Matrix, Hybrid C1 Variants Test"
echo "  Total: 8 Slides"
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
  \"title\": \"Metrics, Matrix, Hybrid C1 Variants - 8 Templates\",
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
