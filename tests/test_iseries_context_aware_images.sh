#!/bin/bash
#
# Test Script: I-Series Context-Aware Image Generation (v4.6)
#
# Tests the new 2-step spotlight image generation with:
# - ImageStyleAgreement context parameters
# - Different audience types (executives, technical, general, kids_tween)
# - Different purpose types (inform, persuade, inspire, educate)
# - Domain detection (technology, business, healthcare, education)
#
# This verifies that images are contextually relevant:
# - Executives/Technology → photorealistic, minimal, no anime
# - Kids/Education → playful illustrations, vibrant colors
# - Technical/Inform → clean diagrams, no people
#
# Uses: POST /v1.2/iseries/{I1|I2|I3|I4} endpoint with image_style_agreement
#

# Service URLs
TEXT_SERVICE="https://web-production-5daf.up.railway.app"
LAYOUT_SERVICE="https://web-production-f0d13.up.railway.app"

# Skip image generation flag (set SKIP_IMAGES=true to skip)
# Usage: SKIP_IMAGES=true ./test_iseries_context_aware_images.sh
SKIP_IMAGES=${SKIP_IMAGES:-false}

# Output directory for responses
OUTPUT_DIR="./test_outputs/iseries_context_aware_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"

# Test configurations: layout|variant|layout_name|title|narrative|topics|image_hint|audience_type|purpose_type|archetype|mood|color_scheme|quality_tier
declare -a TESTS=(
  # Test 1: EXECUTIVES + TECHNOLOGY + INFORM → photorealistic, minimal, no anime
  "I1|sequential_3col_i1|I1-image-left|Technology Stack Overview|Our enterprise technology stack comprises five integrated layers for robust cloud performance|Infrastructure,Platform,Applications|server rack data center cloud computing|executives|inform|photorealistic|professional|neutral|smart"

  # Test 2: TECHNICAL + TECHNOLOGY + EDUCATE → minimalist, clean diagrams
  "I2|single_column_3section_i1|I2-image-right|API Integration Pipeline|Four stages of our RESTful API integration pipeline with microservices architecture|Authentication,Routing,Processing,Response|api endpoints code architecture|technical|educate|minimalist|informative|cool|standard"

  # Test 3: EXECUTIVES + BUSINESS + PERSUADE → photorealistic, dynamic composition
  "I3|sequential_3col_i3|I3-image-left-narrow|Market Expansion Strategy|Our three-phase market expansion drives sustainable growth across new regions|Research,Launch,Scale|business growth chart expansion|executives|persuade|photorealistic|compelling|neutral|smart"

  # Test 4: GENERAL + BUSINESS + INSPIRE → illustrated, warm, aspirational
  "I4|single_column_4section_i3|I4-image-right-narrow|Customer Success Journey|Four milestones that transform customers into advocates for our brand|Onboard,Engage,Succeed,Advocate|customer success handshake partnership|general|inspire|illustrated|aspirational|warm|standard"

  # Test 5: STUDENTS + EDUCATION + EDUCATE → illustrated, vibrant, educational
  "I1|sequential_3col_i1|I1-image-left|Learning Path Framework|Three stages of our interactive learning journey for modern students|Discover,Practice,Master|learning path education books|students|educate|illustrated|educational|vibrant|standard"

  # Test 6: KIDS_TWEEN + EDUCATION + ENTERTAIN → vibrant, playful, colorful
  "I2|single_column_3section_i1|I2-image-right|Science Adventure Steps|Four exciting steps in our science exploration journey|Wonder,Experiment,Discover,Share|science fun colorful adventure|kids_tween|entertain|vibrant|accessible|vibrant|standard"

  # Test 7: TECHNICAL + SCIENCE + INFORM → minimalist, realistic lab imagery
  "I3|sequential_3col_i3|I3-image-left-narrow|Research Methodology|Our three-phase scientific research methodology ensures rigorous analysis|Hypothesize,Experiment,Analyze|laboratory research science equipment|technical|inform|minimalist|informative|cool|standard"

  # Test 8: EXECUTIVES + HEALTHCARE + INFORM → photorealistic, clean medical imagery
  "I4|single_column_4section_i3|I4-image-right-narrow|Patient Care Pathway|Four stages of our patient-centered care model for better outcomes|Assess,Plan,Treat,Follow-up|healthcare medical professional clean|executives|inform|photorealistic|professional|neutral|smart"
)

echo "=============================================="
echo "  I-Series Context-Aware Image Test (v4.6)"
echo "  Testing: ImageStyleAgreement + 2-Step Spotlight"
echo "=============================================="
echo ""
echo "Text Service:   $TEXT_SERVICE"
echo "Layout Service: $LAYOUT_SERVICE"
echo "Output Dir:     $OUTPUT_DIR"
echo ""
echo "Test Matrix (8 slides):"
echo "  1. executives + technology + inform   → photorealistic, minimal"
echo "  2. technical + technology + educate   → minimalist, clean diagrams"
echo "  3. executives + business + persuade   → photorealistic, dynamic"
echo "  4. general + business + inspire       → illustrated, warm"
echo "  5. students + education + educate     → illustrated, vibrant"
echo "  6. kids_tween + education + entertain → vibrant, playful"
echo "  7. technical + science + inform       → minimalist, lab imagery"
echo "  8. executives + healthcare + inform   → photorealistic, clean"
echo ""
echo "Skip Images: $SKIP_IMAGES"
echo ""

# Array to collect slides JSON
SLIDES_JSON="["
FIRST_SLIDE=true
SUCCESS_COUNT=0
FAIL_COUNT=0
SLIDE_NUM=0

for item in "${TESTS[@]}"; do
  IFS='|' read -r layout variant layout_name title narrative topics image_hint audience_type purpose_type archetype mood color_scheme quality_tier <<< "$item"
  ((SLIDE_NUM++))

  echo "----------------------------------------------"
  echo ">>> Test $SLIDE_NUM: $layout + $variant"
  echo "    Title: $title"
  echo "    Audience: $audience_type | Purpose: $purpose_type"
  echo "    Style: archetype=$archetype, mood=$mood, colors=$color_scheme"

  # Convert comma-separated topics to JSON array
  TOPICS_JSON=$(echo "$topics" | sed 's/,/","/g' | sed 's/^/["/' | sed 's/$/"]/')

  # Build avoid_elements based on audience
  case $audience_type in
    executives|professional)
      AVOID_ELEMENTS='["anime", "cartoon", "playful", "childish", "bright colors"]'
      ;;
    technical|developers)
      AVOID_ELEMENTS='["people", "faces", "cartoon characters", "decorative"]'
      ;;
    kids_tween|kids_young)
      AVOID_ELEMENTS='["realistic faces", "corporate", "adult themes", "scary"]'
      ;;
    students)
      AVOID_ELEMENTS='["corporate stock photos", "boring office"]'
      ;;
    *)
      AVOID_ELEMENTS='["complex technical diagrams", "jargon-heavy imagery"]'
      ;;
  esac

  # Generate content from Text Service I-series endpoint with FULL image_style_agreement
  TEXT_RESPONSE=$(curl -s -X POST "$TEXT_SERVICE/v1.2/iseries/$layout" \
    -H "Content-Type: application/json" \
    -d "{
      \"slide_number\": $SLIDE_NUM,
      \"layout_type\": \"$layout\",
      \"title\": \"$title\",
      \"subtitle\": \"Context-Aware Test v4.6\",
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
            \"audience_type\": \"$audience_type\",
            \"complexity_level\": \"moderate\",
            \"avoid_jargon\": false
          },
          \"purpose\": {
            \"purpose_type\": \"$purpose_type\",
            \"emotional_tone\": \"$mood\",
            \"include_data\": true
          }
        },
        \"image_style_agreement\": {
          \"archetype\": \"$archetype\",
          \"mood\": \"$mood\",
          \"color_scheme\": \"$color_scheme\",
          \"lighting\": \"professional\",
          \"avoid_elements\": $AVOID_ELEMENTS,
          \"quality_tier\": \"$quality_tier\"
        },
        \"styling_mode\": \"inline_styles\"
      }
    }")

  # Save raw response
  echo "$TEXT_RESPONSE" > "$OUTPUT_DIR/${SLIDE_NUM}_${layout}_${audience_type}_${purpose_type}_response.json"

  # Extract fields from response
  CONTENT_HTML=$(echo "$TEXT_RESPONSE" | jq -r '.content_html')
  IMAGE_URL=$(echo "$TEXT_RESPONSE" | jq -r '.image_url')
  IMAGE_FALLBACK=$(echo "$TEXT_RESPONSE" | jq -r '.image_fallback')
  SPOTLIGHT_METADATA=$(echo "$TEXT_RESPONSE" | jq -r '.spotlight_metadata // "N/A"')

  if [ "$CONTENT_HTML" == "null" ] || [ -z "$CONTENT_HTML" ]; then
    echo "    ERROR: Text Service failed to generate content"
    echo "$TEXT_RESPONSE" | jq . 2>/dev/null || echo "$TEXT_RESPONSE"
    ((FAIL_COUNT++))
    continue
  fi

  echo "    Text Service: OK"
  echo "    Image: ${IMAGE_URL:0:60}..."
  echo "    Fallback: $IMAGE_FALLBACK"
  echo "    Content: ${#CONTENT_HTML} chars"
  echo "    Spotlight: $SPOTLIGHT_METADATA"
  ((SUCCESS_COUNT++))

  # Save HTML for inspection
  echo "$CONTENT_HTML" > "$OUTPUT_DIR/${SLIDE_NUM}_${layout}_${audience_type}_${purpose_type}_body.html"

  # Escape for JSON
  BODY_ESCAPED=$(echo "$CONTENT_HTML" | jq -Rs .)
  IMAGE_ESCAPED=$(echo "$IMAGE_URL" | jq -Rs . | sed 's/^"//;s/"$//')

  # Build slide JSON for Layout Service with context info in subtitle
  SLIDE_JSON="{
    \"layout\": \"$layout_name\",
    \"content\": {
      \"slide_title\": \"$title\",
      \"subtitle\": \"$audience_type + $purpose_type | $archetype\",
      \"image_url\": \"$IMAGE_ESCAPED\",
      \"body\": $BODY_ESCAPED,
      \"logo\": \" \",
      \"presentation_name\": \"Context-Aware Image Test v4.6\"
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
  \"title\": \"I-Series Context-Aware Image Test v4.6 (8 slides)\",
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
echo "  SUCCESS! Context-Aware Test Complete"
echo "=============================================="
echo ""
echo "Presentation ID: $PRES_ID"
echo "URL: $URL"
echo ""
echo "Slides: $SUCCESS_COUNT / 8"
echo "Output: $OUTPUT_DIR"
echo ""
echo "Review Checklist - Verify Image Style Consistency:"
echo "  [ ] Slide 1 (executives+tech): Photorealistic server/data center, NOT anime"
echo "  [ ] Slide 2 (technical+tech): Minimalist diagrams, clean, no people"
echo "  [ ] Slide 3 (executives+business): Photorealistic professional photo"
echo "  [ ] Slide 4 (general+inspire): Warm illustrated, aspirational imagery"
echo "  [ ] Slide 5 (students+educate): Vibrant illustrated educational"
echo "  [ ] Slide 6 (kids+entertain): Playful, colorful, vibrant"
echo "  [ ] Slide 7 (technical+science): Minimalist realistic lab"
echo "  [ ] Slide 8 (executives+healthcare): Photorealistic clean medical"
echo ""
echo "New v4.6 Features to Verify:"
echo "  [ ] image_style_agreement parameters applied correctly"
echo "  [ ] 2-step spotlight concept extraction working"
echo "  [ ] Negative prompts from avoid_elements effective"
echo "  [ ] Quality tier (smart/standard) selection working"
echo ""

# Open in browser
echo "Opening presentation in browser..."
open "$URL"

echo "=============================================="
