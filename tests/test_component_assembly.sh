#!/bin/bash
#
# Test Script: Component-Based Agentic Element Generation
#
# Tests the /api/ai/element/text endpoint with component assembly
# Creates 3 slides with different use cases to verify component selection:
#   1. Metrics slide → should select metrics_card
#   2. Process slide → should select numbered_card
#   3. Key points slide → should select colored_section
#
# Uses: POST /api/ai/element/text endpoint (component-based)
#

# Service URLs
TEXT_SERVICE="https://web-production-5daf.up.railway.app"
LAYOUT_SERVICE="https://web-production-f0d13.up.railway.app"

# Output directory for responses
OUTPUT_DIR="./test_outputs/component_assembly_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"

# Test configurations: prompt|audience|purpose|expected_component|title
declare -a TESTS=(
  "Show our Q4 performance with revenue growth at 23%, customer acquisition up 45%, and profit margin improved to 18%|executive|inform|metrics_card|Q4 Performance Highlights"
  "4-step employee onboarding process: orientation, training, mentorship, and evaluation|general|explain|numbered_card|Employee Onboarding Process"
  "Key benefits of our sustainability initiative including reduced carbon footprint, cost savings, and improved brand reputation|executive|persuade|colored_section|Sustainability Initiative Benefits"
)

echo "=============================================="
echo "  Component-Based Assembly Test"
echo "  3 Slides with Different Use Cases"
echo "=============================================="
echo ""
echo "Text Service:   $TEXT_SERVICE"
echo "Layout Service: $LAYOUT_SERVICE"
echo "Output Dir:     $OUTPUT_DIR"
echo ""
echo "Expected Component Selection:"
echo "  1. Metrics slide    → metrics_card"
echo "  2. Process slide    → numbered_card"
echo "  3. Key points slide → colored_section"
echo ""

# Array to collect slides JSON
SLIDES_JSON="["
FIRST_SLIDE=true
SUCCESS_COUNT=0
FAIL_COUNT=0
SLIDE_NUM=0

for item in "${TESTS[@]}"; do
  IFS='|' read -r prompt audience purpose expected_component title <<< "$item"
  ((SLIDE_NUM++))

  echo "----------------------------------------------"
  echo ">>> Slide $SLIDE_NUM: $title"
  echo "    Prompt: ${prompt:0:60}..."
  echo "    Audience: $audience | Purpose: $purpose"
  echo "    Expected: $expected_component"

  # Generate content from Text Service /api/ai/element/text endpoint
  TEXT_RESPONSE=$(curl -s -X POST "$TEXT_SERVICE/api/ai/element/text" \
    -H "Content-Type: application/json" \
    -d "{
      \"prompt\": \"$prompt\",
      \"constraints\": {
        \"gridWidth\": 28,
        \"gridHeight\": 12,
        \"outerPadding\": 10,
        \"innerPadding\": 16
      },
      \"typographyLevel\": \"body\",
      \"use_components\": true,
      \"audience\": \"$audience\",
      \"purpose\": \"$purpose\"
    }")

  # Save raw response
  echo "$TEXT_RESPONSE" > "$OUTPUT_DIR/${SLIDE_NUM}_${expected_component}_response.json"

  # Check for success
  SUCCESS=$(echo "$TEXT_RESPONSE" | jq -r '.success')

  if [ "$SUCCESS" != "true" ]; then
    echo "    ERROR: Text Service failed"
    echo "$TEXT_RESPONSE" | jq . 2>/dev/null || echo "$TEXT_RESPONSE"
    ((FAIL_COUNT++))
    continue
  fi

  # Extract content and assembly info
  CONTENT_HTML=$(echo "$TEXT_RESPONSE" | jq -r '.data.content')
  COMPONENT_TYPE=$(echo "$TEXT_RESPONSE" | jq -r '.data.assembly_info.component_type // "unknown"')
  COMPONENT_COUNT=$(echo "$TEXT_RESPONSE" | jq -r '.data.assembly_info.component_count // 0')
  ARRANGEMENT=$(echo "$TEXT_RESPONSE" | jq -r '.data.assembly_info.arrangement // "unknown"')
  VARIANTS=$(echo "$TEXT_RESPONSE" | jq -r '.data.assembly_info.variants_used // []')

  echo "    Text Service: OK"
  echo "    Component: $COMPONENT_TYPE x$COMPONENT_COUNT ($ARRANGEMENT)"
  echo "    Variants: $VARIANTS"

  # Check if expected component was selected
  if [ "$COMPONENT_TYPE" == "$expected_component" ]; then
    echo "    Match: ✓ Component matches expected"
  else
    echo "    Match: ✗ Expected $expected_component, got $COMPONENT_TYPE"
  fi

  echo "    Content: ${#CONTENT_HTML} chars"
  ((SUCCESS_COUNT++))

  # Save HTML for inspection
  echo "$CONTENT_HTML" > "$OUTPUT_DIR/${SLIDE_NUM}_${expected_component}_body.html"

  # Escape for JSON
  BODY_ESCAPED=$(echo "$CONTENT_HTML" | jq -Rs .)

  # Build slide JSON for Layout Service
  SLIDE_JSON="{
    \"layout\": \"C1-text\",
    \"content\": {
      \"title\": \"$title\",
      \"subtitle\": \"Component: $COMPONENT_TYPE ($ARRANGEMENT)\",
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
  \"title\": \"Component Assembly Test - 3 Slides\",
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
echo "Slides: $SUCCESS_COUNT / 3"
echo "Output: $OUTPUT_DIR"
echo ""
echo "Review Checklist:"
echo "  [ ] Slide 1: metrics_card with 3 gradient cards"
echo "  [ ] Slide 2: numbered_card with 4 numbered steps"
echo "  [ ] Slide 3: colored_section with bullet lists"
echo "  [ ] Component selection matches prompts"
echo "  [ ] Content is coherent and professional"
echo "  [ ] Layout is visually balanced"
echo ""

# Open in browser
echo "Opening presentation in browser..."
open "$URL"

echo "=============================================="
