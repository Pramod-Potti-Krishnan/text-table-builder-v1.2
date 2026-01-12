"""
Content Analyzer for Service Coordination

Provides logic for:
- Analyzing content to determine best service fit
- Calculating confidence scores
- Recommending variants based on content and space
- Checking space utilization
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


# =============================================================================
# Constants
# =============================================================================

# Keywords that suggest text service is a good fit
TEXT_SERVICE_KEYWORDS = [
    "compare", "comparison", "versus", "vs",
    "features", "benefits", "advantages",
    "steps", "step", "process", "workflow",
    "matrix", "grid", "table",
    "metrics", "kpis", "key performance",
    "points", "bullet", "list",
    "overview", "summary", "highlights",
    "pros", "cons", "differences",
    "timeline", "sequence", "sequential"
]

# Keywords that suggest chart/analytics service is better
CHART_KEYWORDS = [
    "chart", "graph", "trend", "trends",
    "over time", "by quarter", "by month", "by year",
    "percentage", "percent", "growth rate",
    "revenue trend", "sales trend",
    "distribution", "breakdown",
    "pie chart", "bar chart", "line chart",
    "visualization", "visualize"
]

# Keywords that suggest illustrator/diagram service
DIAGRAM_KEYWORDS = [
    "pyramid", "funnel", "hierarchy", "levels",
    "flow", "flowchart", "diagram",
    "architecture", "system", "components",
    "process flow", "decision tree",
    "layers", "ecosystem", "core"
]


# =============================================================================
# C1 Variant Mapping (L25 → C1)
# C1 variants are the new default with explicit bullet placeholders
# L25 variants are deprecated but still available for explicit requests
# =============================================================================

C1_VARIANT_MAP = {
    # Comparison
    "comparison_2col": "comparison_2col_c1",
    "comparison_3col": "comparison_3col_c1",
    "comparison_4col": "comparison_4col_c1",
    # Sequential
    "sequential_3col": "sequential_3col_c1",
    "sequential_4col": "sequential_4col_c1",
    "sequential_5col": "sequential_5col_c1",
    # Grid
    "grid_2x2_centered": "grid_2x2_centered_c1",
    "grid_2x2_left": "grid_2x2_left_c1",
    "grid_2x2_numbered": "grid_2x2_numbered_c1",
    "grid_2x3": "grid_2x3_c1",
    "grid_2x3_left": "grid_2x3_left_c1",
    "grid_2x3_numbered": "grid_2x3_numbered_c1",
    "grid_3x2": "grid_3x2_c1",
    "grid_3x2_left": "grid_3x2_left_c1",
    "grid_3x2_numbered": "grid_3x2_numbered_c1",
    # Matrix
    "matrix_2x2": "matrix_2x2_c1",
    "matrix_2x3": "matrix_2x3_c1",
    # Asymmetric
    "asymmetric_8_4_3section": "asymmetric_8_4_3section_c1",
    "asymmetric_8_4_4section": "asymmetric_8_4_4section_c1",
    "asymmetric_8_4_5section": "asymmetric_8_4_5section_c1",
    # Hybrid
    "hybrid_top_2x2": "hybrid_top_2x2_c1",
    "hybrid_left_2x2": "hybrid_left_2x2_c1",
    # Metrics
    "metrics_3col": "metrics_3col_c1",
    "metrics_4col": "metrics_4col_c1",
    "metrics_2x2_grid": "metrics_2x2_grid_c1",
    "metrics_3x2_grid": "metrics_3x2_grid_c1",
    # Table
    "table_2col": "table_2col_c1",
    "table_3col": "table_3col_c1",
    "table_4col": "table_4col_c1",
    "table_5col": "table_5col_c1",
    # Single Column
    "single_column_3section": "single_column_3section_c1",
    "single_column_4section": "single_column_4section_c1",
    "single_column_5section": "single_column_5section_c1",
    # Impact Quote
    "impact_quote": "impact_quote_c1",
}


# =============================================================================
# Variant Specifications
# =============================================================================

@dataclass
class VariantSpec:
    """Specification for a content variant."""
    variant_id: str
    slide_type: str
    item_count_range: Tuple[int, int]  # (min, max) topics
    min_width: int  # pixels
    min_height: int  # pixels
    compatible_layouts: List[str]
    description: str


# =============================================================================
# All 34 Variant Specifications (from variant_index.json)
# =============================================================================

VARIANT_SPECS: Dict[str, VariantSpec] = {
    # =========================================================================
    # MATRIX (2 variants)
    # =========================================================================
    "matrix_2x2": VariantSpec(
        variant_id="matrix_2x2",
        slide_type="matrix",
        item_count_range=(4, 4),
        min_width=1200,
        min_height=600,
        compatible_layouts=["L25", "C01", "C02"],
        description="2x2 grid (4 boxes)"
    ),
    "matrix_2x3": VariantSpec(
        variant_id="matrix_2x3",
        slide_type="matrix",
        item_count_range=(6, 6),
        min_width=1600,
        min_height=600,
        compatible_layouts=["L25", "C01"],
        description="2x3 grid (6 boxes)"
    ),

    # =========================================================================
    # GRID (9 variants)
    # =========================================================================
    "grid_2x3": VariantSpec(
        variant_id="grid_2x3",
        slide_type="grid",
        item_count_range=(6, 6),
        min_width=1600,
        min_height=600,
        compatible_layouts=["L25", "C01"],
        description="2x3 grid centered (6 boxes with icons, 35% extended)"
    ),
    "grid_3x2": VariantSpec(
        variant_id="grid_3x2",
        slide_type="grid",
        item_count_range=(6, 6),
        min_width=1600,
        min_height=700,
        compatible_layouts=["L25", "C01"],
        description="3x2 grid centered (6 boxes with icons, 35% extended)"
    ),
    "grid_2x2_centered": VariantSpec(
        variant_id="grid_2x2_centered",
        slide_type="grid",
        item_count_range=(4, 4),
        min_width=1200,
        min_height=600,
        compatible_layouts=["L25", "C01", "C02"],
        description="2x2 grid centered (4 boxes with icons, 70% extended)"
    ),
    "grid_2x3_left": VariantSpec(
        variant_id="grid_2x3_left",
        slide_type="grid",
        item_count_range=(6, 6),
        min_width=1600,
        min_height=600,
        compatible_layouts=["L25", "C01"],
        description="2x3 grid left-aligned (6 boxes with icons, 70% extended)"
    ),
    "grid_3x2_left": VariantSpec(
        variant_id="grid_3x2_left",
        slide_type="grid",
        item_count_range=(6, 6),
        min_width=1600,
        min_height=700,
        compatible_layouts=["L25", "C01"],
        description="3x2 grid left-aligned (6 boxes with icons, 70% extended)"
    ),
    "grid_2x2_left": VariantSpec(
        variant_id="grid_2x2_left",
        slide_type="grid",
        item_count_range=(4, 4),
        min_width=1200,
        min_height=600,
        compatible_layouts=["L25", "C01", "C02"],
        description="2x2 grid left-aligned (4 boxes with icons, 70% extended)"
    ),
    "grid_2x3_numbered": VariantSpec(
        variant_id="grid_2x3_numbered",
        slide_type="grid",
        item_count_range=(6, 6),
        min_width=1600,
        min_height=600,
        compatible_layouts=["L25", "C01"],
        description="2x3 grid numbered (6 boxes with numbers 1-6, 70% extended)"
    ),
    "grid_3x2_numbered": VariantSpec(
        variant_id="grid_3x2_numbered",
        slide_type="grid",
        item_count_range=(6, 6),
        min_width=1600,
        min_height=700,
        compatible_layouts=["L25", "C01"],
        description="3x2 grid numbered (6 boxes with numbers 1-6, 70% extended)"
    ),
    "grid_2x2_numbered": VariantSpec(
        variant_id="grid_2x2_numbered",
        slide_type="grid",
        item_count_range=(4, 4),
        min_width=1200,
        min_height=600,
        compatible_layouts=["L25", "C01", "C02"],
        description="2x2 grid numbered (4 boxes with numbers 1-4, 70% extended)"
    ),

    # =========================================================================
    # COMPARISON (3 variants)
    # =========================================================================
    "comparison_2col": VariantSpec(
        variant_id="comparison_2col",
        slide_type="comparison",
        item_count_range=(2, 2),
        min_width=1200,
        min_height=500,
        compatible_layouts=["L25", "C02"],
        description="2 columns with headers and item lists"
    ),
    "comparison_3col": VariantSpec(
        variant_id="comparison_3col",
        slide_type="comparison",
        item_count_range=(3, 3),
        min_width=1600,
        min_height=500,
        compatible_layouts=["L25", "C01"],
        description="3 columns with headers and item lists"
    ),
    "comparison_4col": VariantSpec(
        variant_id="comparison_4col",
        slide_type="comparison",
        item_count_range=(4, 4),
        min_width=1800,
        min_height=500,
        compatible_layouts=["L25"],
        description="4 columns with headers and item lists"
    ),

    # =========================================================================
    # SEQUENTIAL (3 variants)
    # =========================================================================
    "sequential_3col": VariantSpec(
        variant_id="sequential_3col",
        slide_type="sequential",
        item_count_range=(3, 3),
        min_width=1400,
        min_height=400,
        compatible_layouts=["L25", "C01"],
        description="3 steps with numbers, titles, and paragraphs"
    ),
    "sequential_4col": VariantSpec(
        variant_id="sequential_4col",
        slide_type="sequential",
        item_count_range=(4, 4),
        min_width=1600,
        min_height=400,
        compatible_layouts=["L25", "C01"],
        description="4 steps with numbers, titles, and paragraphs"
    ),
    "sequential_5col": VariantSpec(
        variant_id="sequential_5col",
        slide_type="sequential",
        item_count_range=(5, 5),
        min_width=1800,
        min_height=400,
        compatible_layouts=["L25"],
        description="5 steps with numbers, titles, and paragraphs"
    ),

    # =========================================================================
    # ASYMMETRIC (3 variants)
    # =========================================================================
    "asymmetric_8_4_3section": VariantSpec(
        variant_id="asymmetric_8_4_3section",
        slide_type="asymmetric",
        item_count_range=(3, 3),
        min_width=1600,
        min_height=600,
        compatible_layouts=["L25"],
        description="3 colored sections (3 bullets each) + sidebar"
    ),
    "asymmetric_8_4_4section": VariantSpec(
        variant_id="asymmetric_8_4_4section",
        slide_type="asymmetric",
        item_count_range=(4, 4),
        min_width=1600,
        min_height=600,
        compatible_layouts=["L25"],
        description="4 colored sections (2 bullets each) + sidebar"
    ),
    "asymmetric_8_4_5section": VariantSpec(
        variant_id="asymmetric_8_4_5section",
        slide_type="asymmetric",
        item_count_range=(5, 5),
        min_width=1600,
        min_height=650,
        compatible_layouts=["L25"],
        description="5 colored sections (2 bullets each) + sidebar"
    ),

    # =========================================================================
    # HYBRID (2 variants)
    # =========================================================================
    "hybrid_top_2x2": VariantSpec(
        variant_id="hybrid_top_2x2",
        slide_type="hybrid",
        item_count_range=(4, 4),
        min_width=1400,
        min_height=650,
        compatible_layouts=["L25"],
        description="2x2 grid on top, text box at bottom"
    ),
    "hybrid_left_2x2": VariantSpec(
        variant_id="hybrid_left_2x2",
        slide_type="hybrid",
        item_count_range=(4, 4),
        min_width=1600,
        min_height=600,
        compatible_layouts=["L25"],
        description="2x2 grid on left, text box on right"
    ),

    # =========================================================================
    # METRICS (4 variants)
    # =========================================================================
    "metrics_3col": VariantSpec(
        variant_id="metrics_3col",
        slide_type="metrics",
        item_count_range=(3, 3),
        min_width=1500,
        min_height=500,
        compatible_layouts=["L25", "C01"],
        description="3 metric cards with insights box"
    ),
    "metrics_4col": VariantSpec(
        variant_id="metrics_4col",
        slide_type="metrics",
        item_count_range=(4, 4),
        min_width=1800,
        min_height=500,
        compatible_layouts=["L25"],
        description="4 metric cards with Key Insights box"
    ),
    "metrics_3x2_grid": VariantSpec(
        variant_id="metrics_3x2_grid",
        slide_type="metrics",
        item_count_range=(6, 6),
        min_width=1600,
        min_height=600,
        compatible_layouts=["L25"],
        description="3x2 grid (6 cards) with insights box"
    ),
    "metrics_2x2_grid": VariantSpec(
        variant_id="metrics_2x2_grid",
        slide_type="metrics",
        item_count_range=(4, 4),
        min_width=1400,
        min_height=600,
        compatible_layouts=["L25", "C01"],
        description="2x2 grid (4 large cards)"
    ),

    # =========================================================================
    # IMPACT QUOTE (1 variant)
    # =========================================================================
    "impact_quote": VariantSpec(
        variant_id="impact_quote",
        slide_type="impact_quote",
        item_count_range=(1, 1),
        min_width=1200,
        min_height=400,
        compatible_layouts=["L25", "C01", "C02"],
        description="Large centered quote with attribution"
    ),

    # =========================================================================
    # TABLE (4 variants)
    # =========================================================================
    "table_2col": VariantSpec(
        variant_id="table_2col",
        slide_type="table",
        item_count_range=(2, 8),
        min_width=1000,
        min_height=400,
        compatible_layouts=["L25", "C01", "C02"],
        description="2 columns (category + 1 data column), 5 rows"
    ),
    "table_3col": VariantSpec(
        variant_id="table_3col",
        slide_type="table",
        item_count_range=(2, 8),
        min_width=1200,
        min_height=400,
        compatible_layouts=["L25", "C01", "C02"],
        description="3 columns (category + 2 data columns), 5 rows"
    ),
    "table_4col": VariantSpec(
        variant_id="table_4col",
        slide_type="table",
        item_count_range=(2, 8),
        min_width=1400,
        min_height=400,
        compatible_layouts=["L25", "C01"],
        description="4 columns (category + 3 data columns), 5 rows"
    ),
    "table_5col": VariantSpec(
        variant_id="table_5col",
        slide_type="table",
        item_count_range=(2, 8),
        min_width=1600,
        min_height=400,
        compatible_layouts=["L25"],
        description="5 columns (category + 4 data columns), 5 rows"
    ),

    # =========================================================================
    # SINGLE COLUMN (3 variants)
    # =========================================================================
    "single_column_3section": VariantSpec(
        variant_id="single_column_3section",
        slide_type="single_column",
        item_count_range=(3, 3),
        min_width=1400,
        min_height=600,
        compatible_layouts=["L25", "C01"],
        description="3 sections with 4 bullets each"
    ),
    "single_column_4section": VariantSpec(
        variant_id="single_column_4section",
        slide_type="single_column",
        item_count_range=(4, 4),
        min_width=1400,
        min_height=650,
        compatible_layouts=["L25", "C01"],
        description="4 sections with 3 bullets each"
    ),
    "single_column_5section": VariantSpec(
        variant_id="single_column_5section",
        slide_type="single_column",
        item_count_range=(5, 5),
        min_width=1400,
        min_height=700,
        compatible_layouts=["L25"],
        description="5 sections with 2 bullets each"
    ),
}


# =============================================================================
# Content Analyzer
# =============================================================================

class ContentAnalyzer:
    """
    Analyzes content for Text Service coordination.

    Provides methods to:
    - Calculate confidence scores for content handling
    - Analyze content type (metrics, comparison, etc.)
    - Check space utilization
    - Recommend variants
    """

    def __init__(self):
        self.variant_specs = VARIANT_SPECS

    def calculate_confidence(
        self,
        topic_count: int,
        detected_keywords: List[str],
        has_numbers: bool = False,
        is_comparison: bool = False,
        is_time_based: bool = False
    ) -> float:
        """
        Calculate confidence score for Text Service handling this content.

        Scoring factors:
        - Base: 0.5 (neutral)
        - +0.2 if topic_count between 3-6 (optimal range)
        - +0.15 if detected_keywords match text service keywords
        - +0.1 if is_comparison=True
        - -0.2 if has_numbers=True and is_time_based=True (better for charts)
        - -0.15 if detected_keywords include chart/graph/trend

        Returns:
            float: Confidence score between 0.0 and 1.0
        """
        confidence = 0.5  # Base confidence

        # Topic count scoring
        if 3 <= topic_count <= 6:
            confidence += 0.2
        elif 2 <= topic_count <= 8:
            confidence += 0.1
        elif topic_count > 8:
            confidence -= 0.1

        # Keyword matching for text service
        keywords_lower = [kw.lower() for kw in detected_keywords]
        text_matches = sum(
            1 for kw in TEXT_SERVICE_KEYWORDS
            if any(kw in k for k in keywords_lower)
        )
        if text_matches >= 2:
            confidence += 0.15
        elif text_matches >= 1:
            confidence += 0.08

        # Comparison boost
        if is_comparison:
            confidence += 0.1

        # Chart/time-series penalty
        if has_numbers and is_time_based:
            confidence -= 0.2

        # Chart keyword penalty
        chart_matches = sum(
            1 for kw in CHART_KEYWORDS
            if any(kw in k for k in keywords_lower)
        )
        if chart_matches >= 2:
            confidence -= 0.15
        elif chart_matches >= 1:
            confidence -= 0.08

        # Diagram keyword penalty
        diagram_matches = sum(
            1 for kw in DIAGRAM_KEYWORDS
            if any(kw in k for k in keywords_lower)
        )
        if diagram_matches >= 2:
            confidence -= 0.1

        # Clamp to valid range
        return max(0.0, min(1.0, confidence))

    def analyze_content_type(
        self,
        topics: List[str],
        detected_keywords: List[str],
        has_numbers: bool = False,
        is_comparison: bool = False
    ) -> str:
        """
        Analyze content to suggest the best slide type.

        Returns:
            str: Suggested slide type (metrics, comparison, matrix, etc.)
        """
        topic_count = len(topics)
        keywords_lower = [kw.lower() for kw in detected_keywords]
        topics_lower = " ".join(topics).lower()

        # Check for metrics (KPIs, numbers)
        if has_numbers and topic_count <= 4:
            metrics_keywords = ["revenue", "users", "growth", "rate", "nps", "score", "kpi"]
            if any(mk in topics_lower or any(mk in k for k in keywords_lower) for mk in metrics_keywords):
                return "metrics"

        # Check for comparison
        if is_comparison or any(kw in topics_lower for kw in ["vs", "versus", "compare", "comparison"]):
            return "comparison"

        # Check for sequential/process
        process_indicators = ["step", "phase", "stage", "first", "then", "finally", "process"]
        if any(pi in topics_lower for pi in process_indicators):
            return "sequential"

        # Check for matrix (2D organization)
        if topic_count in [4, 6, 9]:
            matrix_indicators = ["matrix", "quadrant", "categories"]
            if any(mi in topics_lower or any(mi in k for k in keywords_lower) for mi in matrix_indicators):
                return "matrix"

        # Default to grid for structured content
        if topic_count >= 3:
            return "grid"

        return "comparison"  # Fallback

    def check_space_fit(
        self,
        variant_id: str,
        available_width: int,
        available_height: int,
        layout_id: Optional[str] = None
    ) -> Tuple[bool, int]:
        """
        Check if a variant fits in the available space.

        Returns:
            Tuple[bool, int]: (fits_well, estimated_fill_percent)
        """
        if variant_id not in self.variant_specs:
            return False, 0

        spec = self.variant_specs[variant_id]

        # Check minimum dimensions
        fits_width = available_width >= spec.min_width
        fits_height = available_height >= spec.min_height

        if not (fits_width and fits_height):
            return False, 0

        # Check layout compatibility
        if layout_id and layout_id not in spec.compatible_layouts:
            return False, 0

        # Calculate fill percentage
        width_usage = min(100, int((spec.min_width / available_width) * 100))
        height_usage = min(100, int((spec.min_height / available_height) * 100))
        fill_percent = (width_usage + height_usage) // 2

        return True, fill_percent

    def get_variant_recommendations(
        self,
        topic_count: int,
        available_width: int,
        available_height: int,
        layout_id: Optional[str] = None,
        suggested_type: Optional[str] = None,
        prefer_c1: bool = True
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Get ranked variant recommendations for the content.

        Args:
            topic_count: Number of topics/items
            available_width: Available width in pixels
            available_height: Available height in pixels
            layout_id: Optional layout ID for compatibility check
            suggested_type: Optional suggested slide type
            prefer_c1: If True (default), return C1 variants instead of L25.
                       Set to False to get deprecated L25 variants.

        Returns:
            Tuple[List[Dict], List[Dict]]: (recommended_variants, not_recommended)
        """
        recommended = []
        not_recommended = []

        for variant_id, spec in self.variant_specs.items():
            min_items, max_items = spec.item_count_range

            # Check item count fit
            item_fit = min_items <= topic_count <= max_items
            exact_match = topic_count == min_items or topic_count == max_items

            # Check space fit
            fits_well, fill_percent = self.check_space_fit(
                variant_id, available_width, available_height, layout_id
            )

            if not fits_well:
                if min_items <= topic_count <= max_items:
                    not_recommended.append({
                        "variant_id": variant_id,
                        "reason": f"Space too small: needs {spec.min_width}x{spec.min_height}px, have {available_width}x{available_height}px"
                    })
                continue

            if not item_fit:
                not_recommended.append({
                    "variant_id": variant_id,
                    "reason": f"Needs {min_items}-{max_items} topics, {topic_count} provided"
                })
                continue

            # Calculate confidence
            confidence = 0.7  # Base for fitting variants

            # Boost for exact match
            if exact_match:
                confidence += 0.15

            # Boost for suggested type match
            if suggested_type and spec.slide_type == suggested_type:
                confidence += 0.1

            # Boost for better space utilization
            if fill_percent >= 70:
                confidence += 0.05
            elif fill_percent >= 85:
                confidence += 0.02

            # Build recommendation
            recommended.append({
                "variant_id": variant_id,
                "confidence": min(1.0, confidence),
                "reason": f"{spec.description}, {topic_count} topics fit well",
                "requires_space": {
                    "width": spec.min_width,
                    "height": spec.min_height
                }
            })

        # Sort by confidence descending
        recommended.sort(key=lambda x: x["confidence"], reverse=True)

        # Apply C1 preference: swap L25 variant IDs to their C1 equivalents
        if prefer_c1:
            for rec in recommended:
                l25_variant = rec["variant_id"]
                if l25_variant in C1_VARIANT_MAP:
                    c1_variant = C1_VARIANT_MAP[l25_variant]
                    rec["variant_id"] = c1_variant
                    rec["reason"] = rec["reason"] + " (C1 layout)"

        return recommended, not_recommended

    def suggest_approach_from_content(
        self,
        topics: List[str],
        has_numbers: bool,
        is_comparison: bool,
        available_sub_zones: Optional[List[Dict]] = None
    ) -> str:
        """
        Suggest the best approach based on content and layout structure.

        Returns:
            str: Suggested approach (metrics, comparison, grid, etc.)
        """
        topic_count = len(topics)
        topics_text = " ".join(topics).lower()

        # Check for metrics indicators in topics
        metrics_patterns = [":", "$", "%", "k", "m", "billion"]
        metrics_score = sum(1 for t in topics if any(p in t.lower() for p in metrics_patterns))

        if metrics_score >= 2 and topic_count <= 4:
            return "metrics"

        # Check for comparison structure
        if is_comparison or "vs" in topics_text or "versus" in topics_text:
            return "comparison"

        # Check sub-zones alignment
        if available_sub_zones:
            zone_count = len(available_sub_zones)
            if zone_count == topic_count:
                if zone_count == 3:
                    return "metrics" if has_numbers else "comparison"
                elif zone_count == 4:
                    return "matrix" if not has_numbers else "metrics"

        # Default based on count
        if topic_count <= 3:
            return "comparison"
        elif topic_count == 4:
            return "matrix"
        elif topic_count <= 6:
            return "grid"
        else:
            return "table"
