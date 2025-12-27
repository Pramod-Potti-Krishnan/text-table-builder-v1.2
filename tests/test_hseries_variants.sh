#!/bin/bash
#
# Test Script: H-Series Hero Slide Variants with AI Image Generation
#
# Tests all 4 H-series slide types with AI-generated background images:
# - Slide 1: H1-generated → POST /v1.2/hero/title-with-image (full HTML)
# - Slide 2: H1-structured → POST /v1.2/hero/title-structured-with-image (structured fields)
# - Slide 3: H2-section → POST /v1.2/hero/section-with-image
# - Slide 4: H3-closing → POST /v1.2/hero/closing-with-image
#
# Image Generation Details:
# - Uses Image Builder v2.0 API at https://web-production-1b5df.up.railway.app
# - Aspect ratio: 16:9 (native, no cropping)
# - Archetype: Determined by visual_style (professional→photorealistic, illustrated→spot_illustration)
# - Prompt: Built from narrative + topics + image_prompt_hint
#
# Per API_USAGE.md:
# - prompt: Image description (built from narrative/topics)
# - aspect_ratio: "16:9" for H-series hero slides
# - archetype: "photorealistic", "spot_illustration", "minimalist_vector_art"
# - negative_prompt: Auto-generated based on slide type
# - metadata: topics, visual_style, slide_type, domain (for semantic cache)
#
# Usage:
#   ./test_hseries_variants.sh
#

# Service URLs
TEXT_SERVICE="https://web-production-5daf.up.railway.app"
LAYOUT_SERVICE="https://web-production-f0d13.up.railway.app"
IMAGE_SERVICE="https://web-production-1b5df.up.railway.app"

# Output directory for responses
OUTPUT_DIR="./test_outputs/hseries_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"

# Default audience/purpose context
AUDIENCE_TYPE="executives"
PURPOSE_TYPE="inform"
EMOTIONAL_TONE="professional"

echo "=============================================="
echo "  H-Series Hero Slides with Image Generation"
echo "  Testing: 4 slides (one of each H-type)"
echo "=============================================="
echo ""
echo "Text Service:   $TEXT_SERVICE"
echo "Layout Service: $LAYOUT_SERVICE"
echo "Image Service:  $IMAGE_SERVICE"
echo "Output Dir:     $OUTPUT_DIR"
echo ""
echo "Audience: $AUDIENCE_TYPE | Purpose: $PURPOSE_TYPE"
echo ""

# Array to collect slides JSON
SLIDES_JSON="["
FIRST_SLIDE=true
SUCCESS_COUNT=0
FAIL_COUNT=0

# ============================================
# SLIDE 1: H1-GENERATED (title-with-image)
# ============================================

echo "=============================================="
echo "  SLIDE 1: H1-Generated (title-with-image)"
echo "=============================================="

SLIDE_NUM=1
TITLE="Digital Transformation 2025"
SUBTITLE="Accelerating Innovation Across Industries"
NARRATIVE="Our comprehensive digital transformation strategy leverages cutting-edge technology to drive business growth"
TOPICS_JSON='["Cloud Migration", "AI Integration", "Process Automation"]'
IMAGE_HINT="modern city skyline with digital overlay futuristic technology"
VISUAL_STYLE="professional"

echo ""
echo ">>> Title: $TITLE"
echo ">>> Visual Style: $VISUAL_STYLE"
echo ">>> Image Hint: $IMAGE_HINT"
echo ""

# Call the title-with-image endpoint
TEXT_RESPONSE=$(curl -s -X POST "$TEXT_SERVICE/v1.2/hero/title-with-image" \
  -H "Content-Type: application/json" \
  -d "{
    \"slide_number\": $SLIDE_NUM,
    \"slide_type\": \"title_slide\",
    \"narrative\": \"$NARRATIVE\",
    \"topics\": $TOPICS_JSON,
    \"visual_style\": \"$VISUAL_STYLE\",
    \"image_prompt_hint\": \"$IMAGE_HINT\",
    \"context\": {
      \"theme\": \"$VISUAL_STYLE\",
      \"audience\": \"$AUDIENCE_TYPE\",
      \"presentation_title\": \"$TITLE\",
      \"content_context\": {
        \"audience\": {
          \"audience_type\": \"$AUDIENCE_TYPE\",
          \"complexity_level\": \"moderate\"
        },
        \"purpose\": {
          \"purpose_type\": \"$PURPOSE_TYPE\",
          \"emotional_tone\": \"$EMOTIONAL_TONE\"
        }
      }
    }
  }")

# Save raw response
echo "$TEXT_RESPONSE" > "$OUTPUT_DIR/${SLIDE_NUM}_H1_generated_response.json"

# Extract fields from response
HERO_CONTENT=$(echo "$TEXT_RESPONSE" | jq -r '.hero_content // .content')
BACKGROUND_IMAGE=$(echo "$TEXT_RESPONSE" | jq -r '.metadata.background_image // .background_image // "N/A"')
IMAGE_FALLBACK=$(echo "$TEXT_RESPONSE" | jq -r '.metadata.fallback_to_gradient // .image_fallback // false')

# Extract image generation metadata for logging
IMAGE_PROMPT_BUILT=$(echo "$TEXT_RESPONSE" | jq -r '.metadata.image_prompt_built // "N/A"')
IMAGE_ARCHETYPE=$(echo "$TEXT_RESPONSE" | jq -r '.metadata.image_archetype_built // "N/A"')
IMAGE_GENERATOR=$(echo "$TEXT_RESPONSE" | jq -r '.metadata.image_generator // "N/A"')
IMAGE_MODEL=$(echo "$TEXT_RESPONSE" | jq -r '.metadata.image_model // "N/A"')
GEN_TIME=$(echo "$TEXT_RESPONSE" | jq -r '.metadata.generation_time_ms // .metadata.image_generation_time_ms // "N/A"')

if [ "$HERO_CONTENT" == "null" ] || [ -z "$HERO_CONTENT" ]; then
  echo "    ERROR: Text Service failed to generate content"
  echo "$TEXT_RESPONSE" | jq . 2>/dev/null || echo "$TEXT_RESPONSE"
  ((FAIL_COUNT++))
else
  echo "    Text Service: OK"
  echo "    Content: ${#HERO_CONTENT} chars"
  echo "    Background Image: ${BACKGROUND_IMAGE:0:80}..."
  echo "    Image Fallback: $IMAGE_FALLBACK"
  echo ""
  echo "    === IMAGE GENERATION DETAILS ==="
  echo "    Generator: $IMAGE_GENERATOR"
  echo "    Model: $IMAGE_MODEL"
  echo "    Archetype: $IMAGE_ARCHETYPE"
  echo "    Generation Time: ${GEN_TIME}ms"
  echo ""
  echo "    === IMAGE PROMPT BUILT ==="
  echo "    $IMAGE_PROMPT_BUILT" | head -c 500
  echo ""
  echo "    =============================="
  ((SUCCESS_COUNT++))

  # Save image prompt to separate file for reference
  echo "=== H1-generated Slide $SLIDE_NUM ===" > "$OUTPUT_DIR/${SLIDE_NUM}_H1_generated_image_prompt.txt"
  echo "Title: $TITLE" >> "$OUTPUT_DIR/${SLIDE_NUM}_H1_generated_image_prompt.txt"
  echo "Visual Style: $VISUAL_STYLE" >> "$OUTPUT_DIR/${SLIDE_NUM}_H1_generated_image_prompt.txt"
  echo "Image Hint: $IMAGE_HINT" >> "$OUTPUT_DIR/${SLIDE_NUM}_H1_generated_image_prompt.txt"
  echo "" >> "$OUTPUT_DIR/${SLIDE_NUM}_H1_generated_image_prompt.txt"
  echo "=== BUILT PROMPT ===" >> "$OUTPUT_DIR/${SLIDE_NUM}_H1_generated_image_prompt.txt"
  echo "$IMAGE_PROMPT_BUILT" >> "$OUTPUT_DIR/${SLIDE_NUM}_H1_generated_image_prompt.txt"
  echo "" >> "$OUTPUT_DIR/${SLIDE_NUM}_H1_generated_image_prompt.txt"
  echo "=== METADATA ===" >> "$OUTPUT_DIR/${SLIDE_NUM}_H1_generated_image_prompt.txt"
  echo "Archetype: $IMAGE_ARCHETYPE" >> "$OUTPUT_DIR/${SLIDE_NUM}_H1_generated_image_prompt.txt"
  echo "Generator: $IMAGE_GENERATOR" >> "$OUTPUT_DIR/${SLIDE_NUM}_H1_generated_image_prompt.txt"
  echo "Model: $IMAGE_MODEL" >> "$OUTPUT_DIR/${SLIDE_NUM}_H1_generated_image_prompt.txt"
  echo "Generation Time: ${GEN_TIME}ms" >> "$OUTPUT_DIR/${SLIDE_NUM}_H1_generated_image_prompt.txt"

  # Save HTML for inspection
  echo "$HERO_CONTENT" > "$OUTPUT_DIR/${SLIDE_NUM}_H1_generated_hero.html"

  # Escape for JSON
  HERO_ESCAPED=$(echo "$HERO_CONTENT" | jq -Rs .)

  # Build slide JSON for Layout Service
  SLIDE_JSON="{
    \"layout\": \"H1-generated\",
    \"content\": {
      \"slide_title\": \"$TITLE\",
      \"subtitle\": \"$SUBTITLE\",
      \"hero_content\": $HERO_ESCAPED,
      \"logo\": \" \",
      \"presentation_name\": \"H-Series Test\"
    }
  }"

  SLIDES_JSON="$SLIDES_JSON$SLIDE_JSON"
  FIRST_SLIDE=false
fi

# ============================================
# SLIDE 2: H1-STRUCTURED (title-structured-with-image)
# ============================================

echo ""
echo "=============================================="
echo "  SLIDE 2: H1-Structured (title-structured-with-image)"
echo "=============================================="

SLIDE_NUM=2
TITLE="Q4 Financial Review"
SUBTITLE="Annual Performance Summary"
NARRATIVE="Comprehensive review of our financial performance and strategic achievements"
TOPICS_JSON='["Revenue Growth", "Cost Optimization", "Market Share"]'
VISUAL_STYLE="professional"

echo ""
echo ">>> Title: $TITLE"
echo ">>> Visual Style: $VISUAL_STYLE"
echo ""

# Call the title-structured-with-image endpoint (returns structured fields + background_image)
TEXT_RESPONSE=$(curl -s -X POST "$TEXT_SERVICE/v1.2/hero/title-structured-with-image" \
  -H "Content-Type: application/json" \
  -d "{
    \"slide_number\": $SLIDE_NUM,
    \"slide_type\": \"title_slide\",
    \"narrative\": \"$NARRATIVE\",
    \"topics\": $TOPICS_JSON,
    \"visual_style\": \"$VISUAL_STYLE\",
    \"context\": {
      \"theme\": \"$VISUAL_STYLE\",
      \"audience\": \"$AUDIENCE_TYPE\",
      \"presentation_title\": \"$TITLE\",
      \"content_context\": {
        \"audience\": {
          \"audience_type\": \"$AUDIENCE_TYPE\",
          \"complexity_level\": \"moderate\"
        },
        \"purpose\": {
          \"purpose_type\": \"$PURPOSE_TYPE\",
          \"emotional_tone\": \"$EMOTIONAL_TONE\"
        }
      }
    }
  }")

# Save raw response
echo "$TEXT_RESPONSE" > "$OUTPUT_DIR/${SLIDE_NUM}_H1_structured_response.json"

# Extract structured fields (this endpoint returns separate fields, not hero_content)
SLIDE_TITLE=$(echo "$TEXT_RESPONSE" | jq -r '.slide_title // "N/A"')
SUBTITLE_RESP=$(echo "$TEXT_RESPONSE" | jq -r '.subtitle // "N/A"')
AUTHOR_INFO=$(echo "$TEXT_RESPONSE" | jq -r '.author_info // "N/A"')
BACKGROUND_IMAGE=$(echo "$TEXT_RESPONSE" | jq -r '.background_image // "N/A"')

# Extract image generation metadata for logging
IMAGE_PROMPT_BUILT=$(echo "$TEXT_RESPONSE" | jq -r '.metadata.image_prompt_built // "N/A"')
IMAGE_ARCHETYPE=$(echo "$TEXT_RESPONSE" | jq -r '.metadata.image_archetype_built // "N/A"')
IMAGE_GENERATOR=$(echo "$TEXT_RESPONSE" | jq -r '.metadata.image_generator // "N/A"')
IMAGE_MODEL=$(echo "$TEXT_RESPONSE" | jq -r '.metadata.image_model // "N/A"')
IMAGE_FALLBACK=$(echo "$TEXT_RESPONSE" | jq -r '.metadata.fallback_to_gradient // false')
GEN_TIME=$(echo "$TEXT_RESPONSE" | jq -r '.metadata.image_generation_time_ms // "N/A"')

if [ "$SLIDE_TITLE" == "null" ] || [ -z "$SLIDE_TITLE" ] || [ "$SLIDE_TITLE" == "N/A" ]; then
  echo "    ERROR: Text Service failed to generate structured content"
  echo "$TEXT_RESPONSE" | jq . 2>/dev/null || echo "$TEXT_RESPONSE"
  ((FAIL_COUNT++))
else
  echo "    Text Service: OK (structured fields)"
  echo "    slide_title: $SLIDE_TITLE"
  echo "    subtitle: $SUBTITLE_RESP"
  echo "    author_info: $AUTHOR_INFO"
  echo "    Background Image: ${BACKGROUND_IMAGE:0:80}..."
  echo "    Image Fallback: $IMAGE_FALLBACK"
  echo ""
  echo "    === IMAGE GENERATION DETAILS ==="
  echo "    Generator: $IMAGE_GENERATOR"
  echo "    Model: $IMAGE_MODEL"
  echo "    Archetype: $IMAGE_ARCHETYPE"
  echo "    Generation Time: ${GEN_TIME}ms"
  echo ""
  echo "    === IMAGE PROMPT BUILT ==="
  echo "    $IMAGE_PROMPT_BUILT" | head -c 500
  echo ""
  echo "    =============================="
  ((SUCCESS_COUNT++))

  # Save image prompt to separate file for reference
  echo "=== H1-structured Slide $SLIDE_NUM ===" > "$OUTPUT_DIR/${SLIDE_NUM}_H1_structured_image_prompt.txt"
  echo "Title: $TITLE" >> "$OUTPUT_DIR/${SLIDE_NUM}_H1_structured_image_prompt.txt"
  echo "Visual Style: $VISUAL_STYLE" >> "$OUTPUT_DIR/${SLIDE_NUM}_H1_structured_image_prompt.txt"
  echo "" >> "$OUTPUT_DIR/${SLIDE_NUM}_H1_structured_image_prompt.txt"
  echo "=== BUILT PROMPT ===" >> "$OUTPUT_DIR/${SLIDE_NUM}_H1_structured_image_prompt.txt"
  echo "$IMAGE_PROMPT_BUILT" >> "$OUTPUT_DIR/${SLIDE_NUM}_H1_structured_image_prompt.txt"
  echo "" >> "$OUTPUT_DIR/${SLIDE_NUM}_H1_structured_image_prompt.txt"
  echo "=== METADATA ===" >> "$OUTPUT_DIR/${SLIDE_NUM}_H1_structured_image_prompt.txt"
  echo "Archetype: $IMAGE_ARCHETYPE" >> "$OUTPUT_DIR/${SLIDE_NUM}_H1_structured_image_prompt.txt"
  echo "Generator: $IMAGE_GENERATOR" >> "$OUTPUT_DIR/${SLIDE_NUM}_H1_structured_image_prompt.txt"
  echo "Model: $IMAGE_MODEL" >> "$OUTPUT_DIR/${SLIDE_NUM}_H1_structured_image_prompt.txt"
  echo "Generation Time: ${GEN_TIME}ms" >> "$OUTPUT_DIR/${SLIDE_NUM}_H1_structured_image_prompt.txt"

  # Build slide JSON for Layout Service (uses structured fields + background_image)
  SLIDE_JSON="{
    \"layout\": \"H1-structured\",
    \"content\": {
      \"slide_title\": \"$SLIDE_TITLE\",
      \"subtitle\": \"$SUBTITLE_RESP\",
      \"author_info\": \"$AUTHOR_INFO\",
      \"background_image\": \"$BACKGROUND_IMAGE\",
      \"logo\": \" \",
      \"presentation_name\": \"H-Series Test\"
    }
  }"

  SLIDES_JSON="$SLIDES_JSON,$SLIDE_JSON"
fi

# ============================================
# SLIDE 3: H2-SECTION (section-with-image)
# ============================================

echo ""
echo "=============================================="
echo "  SLIDE 3: H2-Section (section-with-image)"
echo "=============================================="

SLIDE_NUM=3
SECTION_TITLE="Strategic Overview"
NARRATIVE="This section covers our strategic vision and market positioning"
TOPICS_JSON='["Market Analysis", "Competitive Landscape", "Growth Opportunities"]'
VISUAL_STYLE="professional"

echo ""
echo ">>> Section: $SECTION_TITLE"
echo ">>> Visual Style: $VISUAL_STYLE"
echo ""

# Call the section-with-image endpoint
TEXT_RESPONSE=$(curl -s -X POST "$TEXT_SERVICE/v1.2/hero/section-with-image" \
  -H "Content-Type: application/json" \
  -d "{
    \"slide_number\": $SLIDE_NUM,
    \"slide_type\": \"section_divider\",
    \"narrative\": \"$NARRATIVE\",
    \"topics\": $TOPICS_JSON,
    \"visual_style\": \"$VISUAL_STYLE\",
    \"context\": {
      \"theme\": \"$VISUAL_STYLE\",
      \"audience\": \"$AUDIENCE_TYPE\",
      \"section_title\": \"$SECTION_TITLE\",
      \"content_context\": {
        \"audience\": {
          \"audience_type\": \"$AUDIENCE_TYPE\",
          \"complexity_level\": \"moderate\"
        },
        \"purpose\": {
          \"purpose_type\": \"$PURPOSE_TYPE\",
          \"emotional_tone\": \"$EMOTIONAL_TONE\"
        }
      }
    }
  }")

# Save raw response
echo "$TEXT_RESPONSE" > "$OUTPUT_DIR/${SLIDE_NUM}_H2_section_response.json"

# Extract fields from response
HERO_CONTENT=$(echo "$TEXT_RESPONSE" | jq -r '.hero_content // .content')
BACKGROUND_IMAGE=$(echo "$TEXT_RESPONSE" | jq -r '.metadata.background_image // .background_image // "N/A"')
IMAGE_FALLBACK=$(echo "$TEXT_RESPONSE" | jq -r '.metadata.fallback_to_gradient // .image_fallback // false')

# Extract image generation metadata for logging
IMAGE_PROMPT_BUILT=$(echo "$TEXT_RESPONSE" | jq -r '.metadata.image_prompt_built // "N/A"')
IMAGE_ARCHETYPE=$(echo "$TEXT_RESPONSE" | jq -r '.metadata.image_archetype_built // "N/A"')
IMAGE_GENERATOR=$(echo "$TEXT_RESPONSE" | jq -r '.metadata.image_generator // "N/A"')
IMAGE_MODEL=$(echo "$TEXT_RESPONSE" | jq -r '.metadata.image_model // "N/A"')
GEN_TIME=$(echo "$TEXT_RESPONSE" | jq -r '.metadata.generation_time_ms // .metadata.image_generation_time_ms // "N/A"')

if [ "$HERO_CONTENT" == "null" ] || [ -z "$HERO_CONTENT" ]; then
  echo "    ERROR: Text Service failed to generate content"
  echo "$TEXT_RESPONSE" | jq . 2>/dev/null || echo "$TEXT_RESPONSE"
  ((FAIL_COUNT++))
else
  echo "    Text Service: OK"
  echo "    Content: ${#HERO_CONTENT} chars"
  echo "    Background Image: ${BACKGROUND_IMAGE:0:80}..."
  echo "    Image Fallback: $IMAGE_FALLBACK"
  echo ""
  echo "    === IMAGE GENERATION DETAILS ==="
  echo "    Generator: $IMAGE_GENERATOR"
  echo "    Model: $IMAGE_MODEL"
  echo "    Archetype: $IMAGE_ARCHETYPE"
  echo "    Generation Time: ${GEN_TIME}ms"
  echo ""
  echo "    === IMAGE PROMPT BUILT ==="
  echo "    $IMAGE_PROMPT_BUILT" | head -c 500
  echo ""
  echo "    =============================="
  ((SUCCESS_COUNT++))

  # Save image prompt to separate file for reference
  echo "=== H2-section Slide $SLIDE_NUM ===" > "$OUTPUT_DIR/${SLIDE_NUM}_H2_section_image_prompt.txt"
  echo "Section: $SECTION_TITLE" >> "$OUTPUT_DIR/${SLIDE_NUM}_H2_section_image_prompt.txt"
  echo "Visual Style: $VISUAL_STYLE" >> "$OUTPUT_DIR/${SLIDE_NUM}_H2_section_image_prompt.txt"
  echo "" >> "$OUTPUT_DIR/${SLIDE_NUM}_H2_section_image_prompt.txt"
  echo "=== BUILT PROMPT ===" >> "$OUTPUT_DIR/${SLIDE_NUM}_H2_section_image_prompt.txt"
  echo "$IMAGE_PROMPT_BUILT" >> "$OUTPUT_DIR/${SLIDE_NUM}_H2_section_image_prompt.txt"
  echo "" >> "$OUTPUT_DIR/${SLIDE_NUM}_H2_section_image_prompt.txt"
  echo "=== METADATA ===" >> "$OUTPUT_DIR/${SLIDE_NUM}_H2_section_image_prompt.txt"
  echo "Archetype: $IMAGE_ARCHETYPE" >> "$OUTPUT_DIR/${SLIDE_NUM}_H2_section_image_prompt.txt"
  echo "Generator: $IMAGE_GENERATOR" >> "$OUTPUT_DIR/${SLIDE_NUM}_H2_section_image_prompt.txt"
  echo "Model: $IMAGE_MODEL" >> "$OUTPUT_DIR/${SLIDE_NUM}_H2_section_image_prompt.txt"
  echo "Generation Time: ${GEN_TIME}ms" >> "$OUTPUT_DIR/${SLIDE_NUM}_H2_section_image_prompt.txt"

  # Save HTML for inspection
  echo "$HERO_CONTENT" > "$OUTPUT_DIR/${SLIDE_NUM}_H2_section_hero.html"

  # Escape for JSON
  HERO_ESCAPED=$(echo "$HERO_CONTENT" | jq -Rs .)

  # Extract slide_title and subtitle from response if available
  RESP_SLIDE_TITLE=$(echo "$TEXT_RESPONSE" | jq -r '.slide_title // ""')
  RESP_SUBTITLE=$(echo "$TEXT_RESPONSE" | jq -r '.subtitle // ""')

  # Use response fields if available, otherwise use defaults
  if [ -z "$RESP_SLIDE_TITLE" ] || [ "$RESP_SLIDE_TITLE" == "null" ]; then
    RESP_SLIDE_TITLE="$SECTION_TITLE"
  fi
  if [ -z "$RESP_SUBTITLE" ] || [ "$RESP_SUBTITLE" == "null" ]; then
    RESP_SUBTITLE="Section Overview"
  fi

  # Build slide JSON for Layout Service
  # NOTE: H2-section uses background_image at SLIDE level, NOT hero_content
  SLIDE_JSON="{
    \"layout\": \"H2-section\",
    \"content\": {
      \"section_number\": \"01\",
      \"slide_title\": \"$RESP_SLIDE_TITLE\"
    },
    \"background_image\": \"$BACKGROUND_IMAGE\"
  }"

  SLIDES_JSON="$SLIDES_JSON,$SLIDE_JSON"
fi

# ============================================
# SLIDE 4: H3-CLOSING (closing-with-image)
# ============================================

echo ""
echo "=============================================="
echo "  SLIDE 4: H3-Closing (closing-with-image)"
echo "=============================================="

SLIDE_NUM=4
CLOSING_MESSAGE="Thank You"
NARRATIVE="We appreciate your time and look forward to partnering with you"
TOPICS_JSON='["Partnership", "Growth", "Innovation"]'
VISUAL_STYLE="professional"

echo ""
echo ">>> Closing Message: $CLOSING_MESSAGE"
echo ">>> Visual Style: $VISUAL_STYLE"
echo ""

# Call the closing-with-image endpoint
TEXT_RESPONSE=$(curl -s -X POST "$TEXT_SERVICE/v1.2/hero/closing-with-image" \
  -H "Content-Type: application/json" \
  -d "{
    \"slide_number\": $SLIDE_NUM,
    \"slide_type\": \"closing_slide\",
    \"narrative\": \"$NARRATIVE\",
    \"topics\": $TOPICS_JSON,
    \"visual_style\": \"$VISUAL_STYLE\",
    \"context\": {
      \"theme\": \"$VISUAL_STYLE\",
      \"audience\": \"$AUDIENCE_TYPE\",
      \"contact_info\": \"contact@company.com | +1 (555) 123-4567 | www.company.com\",
      \"content_context\": {
        \"audience\": {
          \"audience_type\": \"$AUDIENCE_TYPE\",
          \"complexity_level\": \"moderate\"
        },
        \"purpose\": {
          \"purpose_type\": \"$PURPOSE_TYPE\",
          \"emotional_tone\": \"$EMOTIONAL_TONE\"
        }
      }
    }
  }")

# Save raw response
echo "$TEXT_RESPONSE" > "$OUTPUT_DIR/${SLIDE_NUM}_H3_closing_response.json"

# Extract fields from response
HERO_CONTENT=$(echo "$TEXT_RESPONSE" | jq -r '.hero_content // .content')
BACKGROUND_IMAGE=$(echo "$TEXT_RESPONSE" | jq -r '.metadata.background_image // .background_image // "N/A"')
IMAGE_FALLBACK=$(echo "$TEXT_RESPONSE" | jq -r '.metadata.fallback_to_gradient // .image_fallback // false')

# Extract image generation metadata for logging
IMAGE_PROMPT_BUILT=$(echo "$TEXT_RESPONSE" | jq -r '.metadata.image_prompt_built // "N/A"')
IMAGE_ARCHETYPE=$(echo "$TEXT_RESPONSE" | jq -r '.metadata.image_archetype_built // "N/A"')
IMAGE_GENERATOR=$(echo "$TEXT_RESPONSE" | jq -r '.metadata.image_generator // "N/A"')
IMAGE_MODEL=$(echo "$TEXT_RESPONSE" | jq -r '.metadata.image_model // "N/A"')
GEN_TIME=$(echo "$TEXT_RESPONSE" | jq -r '.metadata.generation_time_ms // .metadata.image_generation_time_ms // "N/A"')

if [ "$HERO_CONTENT" == "null" ] || [ -z "$HERO_CONTENT" ]; then
  echo "    ERROR: Text Service failed to generate content"
  echo "$TEXT_RESPONSE" | jq . 2>/dev/null || echo "$TEXT_RESPONSE"
  ((FAIL_COUNT++))
else
  echo "    Text Service: OK"
  echo "    Content: ${#HERO_CONTENT} chars"
  echo "    Background Image: ${BACKGROUND_IMAGE:0:80}..."
  echo "    Image Fallback: $IMAGE_FALLBACK"
  echo ""
  echo "    === IMAGE GENERATION DETAILS ==="
  echo "    Generator: $IMAGE_GENERATOR"
  echo "    Model: $IMAGE_MODEL"
  echo "    Archetype: $IMAGE_ARCHETYPE"
  echo "    Generation Time: ${GEN_TIME}ms"
  echo ""
  echo "    === IMAGE PROMPT BUILT ==="
  echo "    $IMAGE_PROMPT_BUILT" | head -c 500
  echo ""
  echo "    =============================="
  ((SUCCESS_COUNT++))

  # Save image prompt to separate file for reference
  echo "=== H3-closing Slide $SLIDE_NUM ===" > "$OUTPUT_DIR/${SLIDE_NUM}_H3_closing_image_prompt.txt"
  echo "Message: $CLOSING_MESSAGE" >> "$OUTPUT_DIR/${SLIDE_NUM}_H3_closing_image_prompt.txt"
  echo "Visual Style: $VISUAL_STYLE" >> "$OUTPUT_DIR/${SLIDE_NUM}_H3_closing_image_prompt.txt"
  echo "" >> "$OUTPUT_DIR/${SLIDE_NUM}_H3_closing_image_prompt.txt"
  echo "=== BUILT PROMPT ===" >> "$OUTPUT_DIR/${SLIDE_NUM}_H3_closing_image_prompt.txt"
  echo "$IMAGE_PROMPT_BUILT" >> "$OUTPUT_DIR/${SLIDE_NUM}_H3_closing_image_prompt.txt"
  echo "" >> "$OUTPUT_DIR/${SLIDE_NUM}_H3_closing_image_prompt.txt"
  echo "=== METADATA ===" >> "$OUTPUT_DIR/${SLIDE_NUM}_H3_closing_image_prompt.txt"
  echo "Archetype: $IMAGE_ARCHETYPE" >> "$OUTPUT_DIR/${SLIDE_NUM}_H3_closing_image_prompt.txt"
  echo "Generator: $IMAGE_GENERATOR" >> "$OUTPUT_DIR/${SLIDE_NUM}_H3_closing_image_prompt.txt"
  echo "Model: $IMAGE_MODEL" >> "$OUTPUT_DIR/${SLIDE_NUM}_H3_closing_image_prompt.txt"
  echo "Generation Time: ${GEN_TIME}ms" >> "$OUTPUT_DIR/${SLIDE_NUM}_H3_closing_image_prompt.txt"

  # Save HTML for inspection
  echo "$HERO_CONTENT" > "$OUTPUT_DIR/${SLIDE_NUM}_H3_closing_hero.html"

  # Extract or use defaults for closing slide fields
  RESP_SLIDE_TITLE=$(echo "$TEXT_RESPONSE" | jq -r '.slide_title // ""')
  RESP_SUBTITLE=$(echo "$TEXT_RESPONSE" | jq -r '.subtitle // ""')
  RESP_CONTACT=$(echo "$TEXT_RESPONSE" | jq -r '.contact_info // ""')

  # Use response fields if available, otherwise use defaults
  if [ -z "$RESP_SLIDE_TITLE" ] || [ "$RESP_SLIDE_TITLE" == "null" ]; then
    RESP_SLIDE_TITLE="$CLOSING_MESSAGE"
  fi
  if [ -z "$RESP_SUBTITLE" ] || [ "$RESP_SUBTITLE" == "null" ]; then
    RESP_SUBTITLE="Questions & Discussion"
  fi
  if [ -z "$RESP_CONTACT" ] || [ "$RESP_CONTACT" == "null" ]; then
    RESP_CONTACT="contact@company.com | www.company.com"
  fi

  # Build slide JSON for Layout Service
  # NOTE: H3-closing uses background_image at SLIDE level, NOT hero_content
  SLIDE_JSON="{
    \"layout\": \"H3-closing\",
    \"content\": {
      \"slide_title\": \"$RESP_SLIDE_TITLE\",
      \"subtitle\": \"$RESP_SUBTITLE\",
      \"contact_info\": \"$RESP_CONTACT\"
    },
    \"background_image\": \"$BACKGROUND_IMAGE\"
  }"

  SLIDES_JSON="$SLIDES_JSON,$SLIDE_JSON"
fi

# Close slides array
SLIDES_JSON="$SLIDES_JSON]"

echo ""
echo "=============================================="
echo "  Creating Combined Presentation"
echo "=============================================="
echo ""
echo "Slides generated: $SUCCESS_COUNT success, $FAIL_COUNT failed"

# Save slides JSON for debugging
echo "$SLIDES_JSON" > "$OUTPUT_DIR/all_slides.json"

# Create single presentation with all slides
LAYOUT_REQUEST="{
  \"title\": \"H-Series Hero Slides with Images (4 slides)\",
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
echo "  SUCCESS! H-Series Test Complete"
echo "=============================================="
echo ""
echo "Presentation ID: $PRES_ID"
echo "URL: $URL"
echo ""
echo "Slides: $SUCCESS_COUNT / 4"
echo "Output: $OUTPUT_DIR"
echo ""
echo "Review Checklist:"
echo "  [ ] Slide 1 (H1-generated): AI image background renders correctly"
echo "  [ ] Slide 2 (H1-structured): AI image background + structured fields"
echo "  [ ] Slide 3 (H2-section): AI image background on section divider"
echo "  [ ] Slide 4 (H3-closing): AI image background on closing slide"
echo "  [ ] All slides: Background images are contextually relevant"
echo "  [ ] All slides: Text is readable over images"
echo "  [ ] All slides: No fallback to gradient (unless intended)"
echo ""
echo "Image Prompt Logs:"
echo "  See: $OUTPUT_DIR/*_image_prompt.txt"
echo ""

# Open in browser using bash open command
echo "Opening presentation in browser..."
open "$URL"

echo "=============================================="
