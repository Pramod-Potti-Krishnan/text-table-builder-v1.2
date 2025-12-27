#!/bin/bash
#
# Test Script: I-Series Director Integration (Mini Test - 3 Slides)
#
# Purpose: Test I-series endpoints exactly as Director Service would call them
# with global_brand parameters + local slide parameters for image generation.
#
# Tests 3 slides (mixed layouts and content variants):
#   1. I1 + single_column_3section (wide image left)
#   2. I3 + comparison_2col (narrow image left)
#   3. I4 + sequential_3col (narrow image right)
#
# Uses: POST /v1.2/iseries/{I1|I3|I4} endpoint
# Image Generation: global_brand (Director) + local parameters (slide-specific)
#

# Service URLs
TEXT_SERVICE="https://web-production-5daf.up.railway.app"
LAYOUT_SERVICE="https://web-production-f0d13.up.railway.app"

# Skip image generation flag (set SKIP_IMAGES=true to skip)
# Usage: SKIP_IMAGES=true ./test_iseries_director_mini.sh
SKIP_IMAGES=${SKIP_IMAGES:-false}

# Output directory for responses
OUTPUT_DIR="./test_outputs/iseries_director_mini_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"

# =============================================================================
# GLOBAL BRAND VARIABLES (from Director - set once per presentation)
# =============================================================================
# These simulate what the Director Service would send for the entire deck
GLOBAL_TARGET_DEMOGRAPHIC="enterprise executives, corporate leadership"
GLOBAL_VISUAL_STYLE="sleek modern photorealistic"
GLOBAL_COLOR_PALETTE="cool blues and metallic silvers"
GLOBAL_LIGHTING_MOOD="professional dramatic lighting, sophisticated atmosphere"

echo "=============================================="
echo "  I-Series Director Integration Mini Test"
echo "  3 Slides with global_brand Parameters"
echo "=============================================="
echo ""
echo "Text Service:   $TEXT_SERVICE"
echo "Layout Service: $LAYOUT_SERVICE"
echo "Output Dir:     $OUTPUT_DIR"
echo "Skip Images:    $SKIP_IMAGES"
echo ""
echo "Global Brand (from Director):"
echo "  target_demographic: $GLOBAL_TARGET_DEMOGRAPHIC"
echo "  visual_style:       $GLOBAL_VISUAL_STYLE"
echo "  color_palette:      $GLOBAL_COLOR_PALETTE"
echo "  lighting_mood:      $GLOBAL_LIGHTING_MOOD"
echo ""

# Array to collect slides JSON
SLIDES_JSON="["
FIRST_SLIDE=true
SUCCESS_COUNT=0
FAIL_COUNT=0

# =============================================================================
# SLIDE 1: I1 + single_column_3section (Wide Image Left)
# =============================================================================
echo "----------------------------------------------"
echo ">>> Slide 1: I1 + single_column_3section_i1"
echo "    Title: Digital Transformation Strategy"

SLIDE1_RESPONSE=$(curl -s -X POST "$TEXT_SERVICE/v1.2/iseries/I1" \
  -H "Content-Type: application/json" \
  -d '{
    "slide_number": 1,
    "layout_type": "I1",
    "title": "Digital Transformation Strategy",
    "subtitle": "Three Pillars of Success",
    "narrative": "Our digital transformation focuses on three core pillars: technology modernization, process optimization, and people development to drive competitive advantage",
    "topics": ["Technology Modernization", "Process Optimization", "People Development"],
    "visual_style": "professional",
    "content_style": "bullets",
    "max_bullets": 5,
    "content_variant": "single_column_3section_i1",
    "image_prompt_hint": "digital transformation technology innovation",
    "skip_image_generation": '"$SKIP_IMAGES"',
    "global_brand": {
      "target_demographic": "'"$GLOBAL_TARGET_DEMOGRAPHIC"'",
      "visual_style": "'"$GLOBAL_VISUAL_STYLE"'",
      "color_palette": "'"$GLOBAL_COLOR_PALETTE"'",
      "lighting_mood": "'"$GLOBAL_LIGHTING_MOOD"'"
    }
  }')

echo "$SLIDE1_RESPONSE" > "$OUTPUT_DIR/1_I1_single_column_response.json"

CONTENT_HTML_1=$(echo "$SLIDE1_RESPONSE" | jq -r '.content_html')
IMAGE_URL_1=$(echo "$SLIDE1_RESPONSE" | jq -r '.image_url')
IMAGE_FALLBACK_1=$(echo "$SLIDE1_RESPONSE" | jq -r '.image_fallback')

if [ "$CONTENT_HTML_1" == "null" ] || [ -z "$CONTENT_HTML_1" ]; then
  echo "    ERROR: Text Service failed"
  echo "$SLIDE1_RESPONSE" | jq . 2>/dev/null || echo "$SLIDE1_RESPONSE"
  ((FAIL_COUNT++))
else
  echo "    Text Service: OK"
  echo "    Image URL: ${IMAGE_URL_1:0:60}..."
  echo "    Fallback: $IMAGE_FALLBACK_1"
  ((SUCCESS_COUNT++))

  echo "$CONTENT_HTML_1" > "$OUTPUT_DIR/1_I1_body.html"
  BODY_ESCAPED_1=$(echo "$CONTENT_HTML_1" | jq -Rs .)
  IMAGE_ESCAPED_1=$(echo "$IMAGE_URL_1" | jq -Rs . | sed 's/^"//;s/"$//')

  SLIDE_JSON_1="{
    \"layout\": \"I1-image-left\",
    \"content\": {
      \"slide_title\": \"Digital Transformation Strategy\",
      \"subtitle\": \"single_column_3section_i1\",
      \"image_url\": \"$IMAGE_ESCAPED_1\",
      \"body\": $BODY_ESCAPED_1,
      \"logo\": \" \",
      \"presentation_name\": \"Director Mini Test\"
    }
  }"
  SLIDES_JSON="$SLIDES_JSON$SLIDE_JSON_1"
  FIRST_SLIDE=false
fi

# =============================================================================
# SLIDE 2: I3 + comparison_2col (Narrow Image Left)
# =============================================================================
echo ""
echo "----------------------------------------------"
echo ">>> Slide 2: I3 + comparison_2col_i3"
echo "    Title: Cloud vs On-Premise"

SLIDE2_RESPONSE=$(curl -s -X POST "$TEXT_SERVICE/v1.2/iseries/I3" \
  -H "Content-Type: application/json" \
  -d '{
    "slide_number": 2,
    "layout_type": "I3",
    "title": "Cloud vs On-Premise",
    "subtitle": "Infrastructure Decision",
    "narrative": "Detailed comparison of cloud-based and on-premise infrastructure options for enterprise deployment scenarios",
    "topics": ["Cloud Solution", "On-Premise Solution"],
    "visual_style": "professional",
    "content_style": "bullets",
    "max_bullets": 5,
    "content_variant": "comparison_2col_i3",
    "image_prompt_hint": "cloud computing servers data center",
    "skip_image_generation": '"$SKIP_IMAGES"',
    "global_brand": {
      "target_demographic": "'"$GLOBAL_TARGET_DEMOGRAPHIC"'",
      "visual_style": "'"$GLOBAL_VISUAL_STYLE"'",
      "color_palette": "'"$GLOBAL_COLOR_PALETTE"'",
      "lighting_mood": "'"$GLOBAL_LIGHTING_MOOD"'"
    }
  }')

echo "$SLIDE2_RESPONSE" > "$OUTPUT_DIR/2_I3_comparison_response.json"

CONTENT_HTML_2=$(echo "$SLIDE2_RESPONSE" | jq -r '.content_html')
IMAGE_URL_2=$(echo "$SLIDE2_RESPONSE" | jq -r '.image_url')
IMAGE_FALLBACK_2=$(echo "$SLIDE2_RESPONSE" | jq -r '.image_fallback')

if [ "$CONTENT_HTML_2" == "null" ] || [ -z "$CONTENT_HTML_2" ]; then
  echo "    ERROR: Text Service failed"
  echo "$SLIDE2_RESPONSE" | jq . 2>/dev/null || echo "$SLIDE2_RESPONSE"
  ((FAIL_COUNT++))
else
  echo "    Text Service: OK"
  echo "    Image URL: ${IMAGE_URL_2:0:60}..."
  echo "    Fallback: $IMAGE_FALLBACK_2"
  ((SUCCESS_COUNT++))

  echo "$CONTENT_HTML_2" > "$OUTPUT_DIR/2_I3_body.html"
  BODY_ESCAPED_2=$(echo "$CONTENT_HTML_2" | jq -Rs .)
  IMAGE_ESCAPED_2=$(echo "$IMAGE_URL_2" | jq -Rs . | sed 's/^"//;s/"$//')

  SLIDE_JSON_2="{
    \"layout\": \"I3-image-left-narrow\",
    \"content\": {
      \"slide_title\": \"Cloud vs On-Premise\",
      \"subtitle\": \"comparison_2col_i3\",
      \"image_url\": \"$IMAGE_ESCAPED_2\",
      \"body\": $BODY_ESCAPED_2,
      \"logo\": \" \",
      \"presentation_name\": \"Director Mini Test\"
    }
  }"

  if [ "$FIRST_SLIDE" = false ]; then
    SLIDES_JSON="$SLIDES_JSON,$SLIDE_JSON_2"
  else
    SLIDES_JSON="$SLIDES_JSON$SLIDE_JSON_2"
    FIRST_SLIDE=false
  fi
fi

# =============================================================================
# SLIDE 3: I4 + sequential_3col (Narrow Image Right)
# =============================================================================
echo ""
echo "----------------------------------------------"
echo ">>> Slide 3: I4 + sequential_3col_i4"
echo "    Title: Innovation Process"

SLIDE3_RESPONSE=$(curl -s -X POST "$TEXT_SERVICE/v1.2/iseries/I4" \
  -H "Content-Type: application/json" \
  -d '{
    "slide_number": 3,
    "layout_type": "I4",
    "title": "Innovation Process",
    "subtitle": "From Idea to Launch",
    "narrative": "Our proven three-stage innovation process drives breakthrough solutions from initial ideation through prototyping to market launch",
    "topics": ["Ideate", "Prototype", "Launch"],
    "visual_style": "professional",
    "content_style": "bullets",
    "max_bullets": 5,
    "content_variant": "sequential_3col_i4",
    "image_prompt_hint": "innovation lightbulb creative process",
    "skip_image_generation": '"$SKIP_IMAGES"',
    "global_brand": {
      "target_demographic": "'"$GLOBAL_TARGET_DEMOGRAPHIC"'",
      "visual_style": "'"$GLOBAL_VISUAL_STYLE"'",
      "color_palette": "'"$GLOBAL_COLOR_PALETTE"'",
      "lighting_mood": "'"$GLOBAL_LIGHTING_MOOD"'"
    }
  }')

echo "$SLIDE3_RESPONSE" > "$OUTPUT_DIR/3_I4_sequential_response.json"

CONTENT_HTML_3=$(echo "$SLIDE3_RESPONSE" | jq -r '.content_html')
IMAGE_URL_3=$(echo "$SLIDE3_RESPONSE" | jq -r '.image_url')
IMAGE_FALLBACK_3=$(echo "$SLIDE3_RESPONSE" | jq -r '.image_fallback')

if [ "$CONTENT_HTML_3" == "null" ] || [ -z "$CONTENT_HTML_3" ]; then
  echo "    ERROR: Text Service failed"
  echo "$SLIDE3_RESPONSE" | jq . 2>/dev/null || echo "$SLIDE3_RESPONSE"
  ((FAIL_COUNT++))
else
  echo "    Text Service: OK"
  echo "    Image URL: ${IMAGE_URL_3:0:60}..."
  echo "    Fallback: $IMAGE_FALLBACK_3"
  ((SUCCESS_COUNT++))

  echo "$CONTENT_HTML_3" > "$OUTPUT_DIR/3_I4_body.html"
  BODY_ESCAPED_3=$(echo "$CONTENT_HTML_3" | jq -Rs .)
  IMAGE_ESCAPED_3=$(echo "$IMAGE_URL_3" | jq -Rs . | sed 's/^"//;s/"$//')

  SLIDE_JSON_3="{
    \"layout\": \"I4-image-right-narrow\",
    \"content\": {
      \"slide_title\": \"Innovation Process\",
      \"subtitle\": \"sequential_3col_i4\",
      \"image_url\": \"$IMAGE_ESCAPED_3\",
      \"body\": $BODY_ESCAPED_3,
      \"logo\": \" \",
      \"presentation_name\": \"Director Mini Test\"
    }
  }"

  if [ "$FIRST_SLIDE" = false ]; then
    SLIDES_JSON="$SLIDES_JSON,$SLIDE_JSON_3"
  else
    SLIDES_JSON="$SLIDES_JSON$SLIDE_JSON_3"
    FIRST_SLIDE=false
  fi
fi

# Close slides array
SLIDES_JSON="$SLIDES_JSON]"

echo ""
echo "=============================================="
echo "  Creating Presentation"
echo "=============================================="
echo ""
echo "Slides generated: $SUCCESS_COUNT success, $FAIL_COUNT failed"

# Save slides JSON for debugging
echo "$SLIDES_JSON" > "$OUTPUT_DIR/all_slides.json"

# Create presentation with all slides
LAYOUT_REQUEST="{
  \"title\": \"I-Series Director Mini Test (3 Slides)\",
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
echo "Test Coverage:"
echo "  [x] I1 - Wide image LEFT  + single_column_3section"
echo "  [x] I3 - Narrow image LEFT  + comparison_2col"
echo "  [x] I4 - Narrow image RIGHT + sequential_3col"
echo ""
echo "Review Checklist:"
echo "  [ ] Images follow global_brand style (photorealistic, cool blues)"
echo "  [ ] Content fits within layout bounds"
echo "  [ ] Image + content balance looks correct"
echo "  [ ] No overflow or truncation"
echo ""

# Open in browser
echo "Opening presentation in browser..."
open "$URL"

echo "=============================================="
