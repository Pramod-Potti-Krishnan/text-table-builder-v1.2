#!/bin/bash
#
# Test Script: Single Column, Asymmetric, Sequential, Comparison C1 Variants
#
# Uses: POST /v1.2/generate endpoint
# Generates content via Text Service → Creates ONE presentation with 12 slides
#

# Service URLs
TEXT_SERVICE="https://web-production-5daf.up.railway.app"
LAYOUT_SERVICE="https://web-production-f0d13.up.railway.app"

# Output directory for responses
OUTPUT_DIR="./test_outputs/layout_c1_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"

# All 12 Layout C1 Variants
declare -a VARIANTS=(
  # Single Column (3)
  "single_column_3section_c1|Executive Summary|Key highlights and strategic recommendations for Q4"
  "single_column_4section_c1|Project Milestones|Major deliverables and timeline for product launch"
  "single_column_5section_c1|Risk Assessment|Comprehensive risk analysis and mitigation strategies"
  # Asymmetric (3)
  "asymmetric_8_4_3section_c1|Market Analysis|Industry trends and competitive landscape overview"
  "asymmetric_8_4_4section_c1|Product Strategy|Feature roadmap and development priorities"
  "asymmetric_8_4_5section_c1|Operations Review|Process improvements and efficiency metrics"
  # Sequential (3)
  "sequential_3col_c1|Implementation Phases|Three-stage rollout plan for deployment"
  "sequential_4col_c1|Customer Journey|Four-step customer acquisition framework"
  "sequential_5col_c1|Development Pipeline|Five-phase software development lifecycle"
  # Comparison (3)
  "comparison_2col_c1|Solution Comparison|Cloud vs on-premise infrastructure analysis"
  "comparison_3col_c1|Service Tiers|Basic, Professional, Enterprise comparison"
  "comparison_4col_c1|Vendor Evaluation|Four-vendor CRM selection comparison"
)

echo "=============================================="
echo "  Layout C1 Variants Test Script"
echo "  Single Column, Asymmetric, Sequential, Comparison"
echo "  Total: 12 Slides"
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
  \"title\": \"Layout C1 Variants - 12 Templates\",
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
