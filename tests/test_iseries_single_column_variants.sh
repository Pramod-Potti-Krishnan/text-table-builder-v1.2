#!/bin/bash
#
# Test Script: I-Series Single Column Variants (Phase 1)
#
# Tests 12 slides total:
# - 3 variants (single_column_3section, 4section, 5section)
# - 4 layouts (I1, I2, I3, I4)
#
# Uses: POST /v1.2/iseries/{I1|I2|I3|I4} endpoint
# Includes v4.6 ImageStyleAgreement for consistent image generation
#

# Service URLs
TEXT_SERVICE="https://web-production-5daf.up.railway.app"
LAYOUT_SERVICE="https://web-production-f0d13.up.railway.app"

# Skip image generation flag (set SKIP_IMAGES=true to skip)
# Usage: SKIP_IMAGES=true ./test_iseries_single_column_variants.sh
SKIP_IMAGES=${SKIP_IMAGES:-false}

# Output directory for responses
OUTPUT_DIR="./test_outputs/iseries_single_column_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"

# Default image style (executives + professional)
AUDIENCE_TYPE="executives"
PURPOSE_TYPE="inform"
ARCHETYPE="photorealistic"
MOOD="professional"
COLOR_SCHEME="neutral"
AVOID_ELEMENTS='["anime", "cartoon", "playful", "childish"]'
QUALITY_TIER="smart"

# Test configurations: layout|variant|layout_name|title|narrative|topics|image_hint
declare -a TESTS=(
  # I1: Wide Image Left (3 slides)
  "I1|single_column_3section_i1|I1-image-left|Digital Transformation Strategy|Our digital transformation focuses on three core pillars: technology modernization, process optimization, and people development|Technology Modernization,Process Optimization,People Development|futuristic digital transformation technology office"
  "I1|single_column_4section_i1|I1-image-left|Implementation Roadmap|Our implementation follows four distinct phases ensuring measurable success at each milestone|Discovery & Planning,Foundation Building,Scaling Up,Optimization|roadmap journey milestone path achievement"
  "I1|single_column_5section_i1|I1-image-left|Core Value Proposition|Our solution delivers five core benefits that transform business operations|Speed,Reliability,Cost Savings,Scalability,Security|value proposition business benefits abstract"

  # I2: Wide Image Right (3 slides)
  "I2|single_column_3section_i1|I2-image-right|Customer Success Framework|Our customer success framework ensures long-term partnership through three strategic stages|Onboarding Excellence,Growth Partnership,Strategic Alignment|customer success partnership handshake professional"
  "I2|single_column_4section_i1|I2-image-right|Market Expansion Strategy|Our market expansion leverages four distinct growth vectors for sustainable success|Geographic Expansion,Product Innovation,Channel Partnerships,Market Penetration|market expansion growth chart business"
  "I2|single_column_5section_i1|I2-image-right|Technology Stack Overview|Our technology stack comprises five integrated layers for robust performance|Infrastructure,Platform,Services,Applications,Experience|technology stack architecture layers modern"

  # I3: Narrow Image Left (3 slides)
  "I3|single_column_3section_i3|I3-image-left-narrow|Operational Excellence|Operational excellence is achieved through three fundamental principles|Continuous Improvement,Quality First,Team Empowerment|operational excellence quality improvement team"
  "I3|single_column_4section_i3|I3-image-left-narrow|Product Development Cycle|Our product development follows a proven four-stage cycle for consistent delivery|Ideation,Design,Development,Launch|product development cycle innovation creative"
  "I3|single_column_5section_i3|I3-image-left-narrow|Enterprise Security Framework|Our enterprise security implements five defense layers for comprehensive protection|Perimeter,Network,Endpoint,Application,Data|enterprise security shield protection layers"

  # I4: Narrow Image Right (3 slides)
  "I4|single_column_3section_i3|I4-image-right-narrow|Brand Strategy Blueprint|Our brand strategy is built on three interconnected strategic pillars|Brand Identity,Market Position,Customer Connection|brand strategy marketing blueprint professional"
  "I4|single_column_4section_i3|I4-image-right-narrow|Innovation Pipeline|Our innovation pipeline moves ideas through four structured stages|Research,Prototype,Validate,Scale|innovation pipeline funnel ideas lightbulb"
  "I4|single_column_5section_i3|I4-image-right-narrow|Sustainability Commitment|Our sustainability commitment spans five critical focus areas|Carbon Neutral,Circular Economy,Ethical Sourcing,Community Impact,Innovation|sustainability green environment nature eco"
)

echo "=============================================="
echo "  I-Series Single Column Variants Test"
echo "  Phase 1: 12 Slides (3 variants x 4 layouts)"
echo "  With v4.6 ImageStyleAgreement"
echo "=============================================="
echo ""
echo "Text Service:   $TEXT_SERVICE"
echo "Layout Service: $LAYOUT_SERVICE"
echo "Output Dir:     $OUTPUT_DIR"
echo ""
echo "Image Style: $ARCHETYPE, $MOOD, $COLOR_SCHEME"
echo "Skip Images: $SKIP_IMAGES"
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

  # Generate content from Text Service I-series endpoint with v4.6 context
  TEXT_RESPONSE=$(curl -s -X POST "$TEXT_SERVICE/v1.2/iseries/$layout" \
    -H "Content-Type: application/json" \
    -d "{
      \"slide_number\": $SLIDE_NUM,
      \"layout_type\": \"$layout\",
      \"title\": \"$title\",
      \"subtitle\": \"Phase 1 Test\",
      \"narrative\": \"$narrative\",
      \"topics\": $TOPICS_JSON,
      \"visual_style\": \"illustrated\",
      \"image_prompt_hint\": \"$image_hint\",
      \"content_style\": \"bullets\",
      \"max_bullets\": 6,
      \"content_variant\": \"$variant\",
      \"skip_image_generation\": $SKIP_IMAGES,
      \"context\": {
        \"content_context\": {
          \"audience\": {
            \"audience_type\": \"$AUDIENCE_TYPE\",
            \"complexity_level\": \"moderate\"
          },
          \"purpose\": {
            \"purpose_type\": \"$PURPOSE_TYPE\",
            \"emotional_tone\": \"$MOOD\"
          }
        },
        \"image_style_agreement\": {
          \"archetype\": \"$ARCHETYPE\",
          \"mood\": \"$MOOD\",
          \"color_scheme\": \"$COLOR_SCHEME\",
          \"lighting\": \"professional\",
          \"avoid_elements\": $AVOID_ELEMENTS,
          \"quality_tier\": \"$QUALITY_TIER\"
        },
        \"styling_mode\": \"inline_styles\"
      }
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
      \"logo\": \" \",
      \"presentation_name\": \"I-Series Phase 1\"
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
  \"title\": \"I-Series Phase 1: Single Column (12 slides)\",
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
echo "  SUCCESS! Phase 1 Complete"
echo "=============================================="
echo ""
echo "Presentation ID: $PRES_ID"
echo "URL: $URL"
echo ""
echo "Slides: $SUCCESS_COUNT / 12"
echo "Output: $OUTPUT_DIR"
echo ""
echo "Review Checklist:"
echo "  [ ] Content fits within layout bounds (6 bullets/section)"
echo "  [ ] Image + content balance looks correct"
echo "  [ ] Character counts are appropriate (40-85 chars)"
echo "  [ ] No overflow or truncation"
echo "  [ ] Visual consistency across I1-I4"
echo "  [ ] Images are $ARCHETYPE style (no anime/cartoon)"
echo ""

# Open in browser
echo "Opening presentation in browser..."
open "$URL"

echo "=============================================="
