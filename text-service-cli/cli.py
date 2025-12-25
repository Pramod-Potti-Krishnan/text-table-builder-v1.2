#!/usr/bin/env python3
"""
Text Service CLI Tool

Automates integration of new slide formats into Text & Table Builder v1.2.
Supports both content slide variants and hero slide generators.
"""

import click
import json
import logging
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.prompt import Prompt

# Import core modules
from core.input_validator import InputValidator
from core.placeholder_detector import PlaceholderDetector
from core.spec_analyzer import SpecAnalyzer
from generators.variant_gen import VariantGenerator
from generators.hero_gen import HeroGenerator

console = Console()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base path for Text Service
TEXT_SERVICE_ROOT = Path(__file__).parent.parent


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """
    Text Service CLI Tool

    Automates the integration of new slide formats into:
    - Content slide variants (26+ variants like matrix, grid, comparison)
    - Hero slide generators (title, section, closing slides)

    Use --type variant for content slides, --type hero for hero slides.
    """
    pass


@cli.command()
@click.argument('input_dir', type=click.Path(exists=True))
@click.option('--type', 'format_type', type=click.Choice(['variant', 'hero']),
              required=True, help='Type of format to validate')
def validate(input_dir, format_type):
    """
    Validate input files for integration.

    For --type variant:
      - template.html (required)
      - metadata.json (required)
      - constraints.json (optional)

    For --type hero:
      - metadata.json (required)
      - prompt_template.md (required)
      - validation_rules.json (required)
      - example_html.html (optional)
    """
    console.print(f"\n[bold blue]Validating {format_type.upper()} Input Files[/bold blue]\n")

    input_path = Path(input_dir)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Validating...", total=None)

        validator = InputValidator(input_path, format_type)
        is_valid, results = validator.validate_all()

    # Display results
    if is_valid:
        console.print("[bold green]All validations passed![/bold green]\n")
    else:
        console.print("[bold red]Validation failed[/bold red]\n")

    # Create results table
    table = Table(title="Validation Results")
    table.add_column("File", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details", style="white")

    for file_type, result in results.items():
        if file_type in ['errors', 'warnings']:
            continue

        if result.get('valid'):
            status = "Valid"
        elif result.get('optional'):
            status = "Optional"
        else:
            status = "Invalid"

        details = []
        if 'size' in result:
            details.append(f"Size: {result['size']} bytes")
        if 'placeholders' in result:
            details.append(f"Placeholders: {result['placeholders']}")
        if 'elements' in result:
            details.append(f"Elements: {result['elements']}")
        if 'slide_type' in result:
            details.append(f"Slide type: {result['slide_type']}")

        table.add_row(
            file_type,
            status,
            ", ".join(details) if details else "N/A"
        )

    console.print(table)

    # Show errors and warnings
    if results.get('errors'):
        console.print("\n[bold red]Errors:[/bold red]")
        for error in results['errors']:
            console.print(f"  {error}")

    if results.get('warnings'):
        console.print("\n[bold yellow]Warnings:[/bold yellow]")
        for warning in results['warnings']:
            console.print(f"  {warning}")

    console.print()

    if not is_valid:
        raise click.ClickException("Validation failed. Fix errors and try again.")


@cli.command()
@click.argument('input_dir', type=click.Path(exists=True))
@click.option('--type', 'format_type', type=click.Choice(['variant', 'hero']),
              required=True, help='Type of format to analyze')
def analyze(input_dir, format_type):
    """
    Analyze template/generator structure and provide insights.

    For variants: Shows placeholder structure, element grouping, constraints.
    For heroes: Shows prompt structure, validation patterns.
    """
    input_path = Path(input_dir)

    console.print(f"\n[bold blue]Analyzing {format_type.upper()} Format[/bold blue]\n")

    if format_type == 'variant':
        _analyze_variant(input_path)
    else:
        _analyze_hero(input_path)


def _analyze_variant(input_path: Path):
    """Analyze content variant template."""
    # Load files
    template_path = input_path / 'template.html'
    metadata_path = input_path / 'metadata.json'
    constraints_path = input_path / 'constraints.json'

    if not template_path.exists():
        raise click.ClickException("template.html not found")
    if not metadata_path.exists():
        raise click.ClickException("metadata.json not found")

    with open(template_path) as f:
        template_html = f.read()

    with open(metadata_path) as f:
        metadata = json.load(f)

    constraints = {}
    if constraints_path.exists():
        with open(constraints_path) as f:
            constraints = json.load(f)

    # Analyze placeholders
    detector = PlaceholderDetector()
    analysis = detector.detect_placeholders(template_html)

    # Display results
    console.print(f"[bold]Variant: {metadata.get('display_name', metadata.get('variant_id'))}[/bold]")
    console.print(f"Slide Type: {metadata.get('slide_type', 'unknown')}")
    console.print(f"Total placeholders: {analysis['total_placeholders']}")
    console.print(f"Unique placeholders: {analysis['unique_placeholders']}\n")

    # Show placeholder groups
    console.print("[bold]Placeholder Groups:[/bold]")
    for group, fields in analysis['placeholder_groups'].items():
        console.print(f"  {group}: {len(fields)} fields")
        for field in fields[:5]:  # Show first 5
            console.print(f"    - {field}")
        if len(fields) > 5:
            console.print(f"    ... ({len(fields) - 5} more)")

    # Show structure
    console.print("\n[bold]Structure Analysis:[/bold]")
    structure = analysis['structure']
    for key, value in structure.items():
        console.print(f"  {key}: {value}")

    # Suggest spec structure
    analyzer = SpecAnalyzer()
    suggested_spec = analyzer.suggest_variant_spec(analysis, metadata)

    console.print("\n[bold]Suggested Variant Spec:[/bold]")
    console.print(f"  Elements: {len(suggested_spec.get('elements', []))}")
    for elem in suggested_spec.get('elements', [])[:3]:
        console.print(f"    - {elem['element_id']}: {elem['required_fields']}")

    # Validate against constraints if provided
    if constraints:
        console.print("\n[bold]Constraint Validation:[/bold]")
        validation = detector.validate_against_constraints(analysis, constraints)

        if validation['valid']:
            console.print("  All placeholders have constraints")
        else:
            console.print("  Issues found:")
            for issue in validation['issues']:
                console.print(f"    - {issue}")

    console.print()


def _analyze_hero(input_path: Path):
    """Analyze hero slide type."""
    metadata_path = input_path / 'metadata.json'
    prompt_path = input_path / 'prompt_template.md'
    rules_path = input_path / 'validation_rules.json'

    if not metadata_path.exists():
        raise click.ClickException("metadata.json not found")
    if not prompt_path.exists():
        raise click.ClickException("prompt_template.md not found")

    with open(metadata_path) as f:
        metadata = json.load(f)

    with open(prompt_path) as f:
        prompt_template = f.read()

    validation_rules = {}
    if rules_path.exists():
        with open(rules_path) as f:
            validation_rules = json.load(f)

    # Display results
    console.print(f"[bold]Hero Type: {metadata.get('display_name', metadata.get('hero_type'))}[/bold]")
    console.print(f"Endpoint: /v1.2/hero/{metadata.get('endpoint_path', 'unknown')}")
    console.print(f"Description: {metadata.get('description', 'N/A')}\n")

    # Show HTML structure
    console.print("[bold]HTML Structure:[/bold]")
    html_structure = metadata.get('html_structure', {})
    console.print(f"  Container: {html_structure.get('container', 'N/A')}")
    console.print(f"  Elements: {html_structure.get('elements', [])}")

    # Show character constraints
    console.print("\n[bold]Character Constraints:[/bold]")
    char_constraints = metadata.get('character_constraints', {})
    for field, limits in char_constraints.items():
        console.print(f"  {field}: {limits.get('min', 0)}-{limits.get('max', 'unlimited')} chars")

    # Show prompt template stats
    console.print("\n[bold]Prompt Template:[/bold]")
    console.print(f"  Length: {len(prompt_template)} chars")
    console.print(f"  Lines: {len(prompt_template.splitlines())}")

    # Show validation rules
    if validation_rules:
        console.print("\n[bold]Validation Rules:[/bold]")
        console.print(f"  Required elements: {len(validation_rules.get('required_elements', []))}")
        console.print(f"  Character limits: {len(validation_rules.get('character_limits', {}))}")
        console.print(f"  Forbidden patterns: {len(validation_rules.get('forbidden_patterns', []))}")

    console.print()


@cli.command()
@click.argument('input_dir', type=click.Path(exists=True))
@click.option('--type', 'format_type', type=click.Choice(['variant', 'hero']),
              required=True, help='Type of format to integrate')
@click.option('--with-image', is_flag=True,
              help='Also generate image-enhanced variant (hero only)')
@click.option('--dry-run', is_flag=True,
              help='Preview changes without writing files')
@click.option('--skip-validation', is_flag=True,
              help='Skip input validation')
@click.option('--yes', '-y', is_flag=True,
              help='Skip confirmation prompts')
def integrate(input_dir, format_type, with_image, dry_run, skip_validation, yes):
    """
    Integrate new format into Text Service v1.2.

    For --type variant:
      1. Validates input files
      2. Generates variant spec JSON
      3. Copies/processes HTML template
      4. Generates test script
      5. Shows variant_index.json update snippet

    For --type hero:
      1. Validates input files
      2. Generates hero generator Python class
      3. Generates test script
      4. Shows route and __init__.py update snippets

    Use --dry-run to preview without making changes.
    Use --with-image (hero only) to also generate image-enhanced variant.
    """
    input_path = Path(input_dir)

    mode_str = 'Dry Run' if dry_run else 'Live'
    if with_image and format_type == 'hero':
        mode_str += ' + Image Variant'

    console.print(Panel.fit(
        f"[bold]Text Service Integration Tool[/bold]\n"
        f"Type: {format_type.upper()}\n"
        f"Input: {input_dir}\n"
        f"Mode: {mode_str}",
        border_style="blue"
    ))

    # Step 1: Validate
    if not skip_validation:
        console.print("\n[bold]Step 1: Input Validation[/bold]")
        validator = InputValidator(input_path, format_type)
        is_valid, results = validator.validate_all()

        if not is_valid:
            console.print(validator.get_summary())
            raise click.ClickException("Validation failed")

        console.print("Validation passed")
    else:
        console.print("\n[bold yellow]Skipping validation[/bold yellow]")

    # Step 2: Load input files
    console.print("\n[bold]Step 2: Loading Input Files[/bold]")

    with open(input_path / 'metadata.json') as f:
        metadata = json.load(f)

    if format_type == 'variant':
        with open(input_path / 'template.html') as f:
            template_html = f.read()

        constraints = {}
        constraints_path = input_path / 'constraints.json'
        if constraints_path.exists():
            with open(constraints_path) as f:
                constraints = json.load(f)

        console.print(f"Loaded: {metadata.get('display_name', metadata.get('variant_id'))}")
        console.print(f"   Slide type: {metadata.get('slide_type')}")
        console.print(f"   Elements: {len(metadata.get('elements', []))}")

    else:  # hero
        with open(input_path / 'prompt_template.md') as f:
            prompt_template = f.read()

        validation_rules = {}
        rules_path = input_path / 'validation_rules.json'
        if rules_path.exists():
            with open(rules_path) as f:
                validation_rules = json.load(f)

        console.print(f"Loaded: {metadata.get('display_name', metadata.get('hero_type'))}")
        console.print(f"   Endpoint: /v1.2/hero/{metadata.get('endpoint_path')}")

    # Step 3: Generate files
    console.print("\n[bold]Step 3: Generating Code Files[/bold]")

    templates_dir = Path(__file__).parent / 'templates'

    if format_type == 'variant':
        generator = VariantGenerator(TEXT_SERVICE_ROOT, templates_dir)
        generated_files = generator.generate_all(metadata, constraints, template_html)
    else:  # hero
        generator = HeroGenerator(TEXT_SERVICE_ROOT, templates_dir)
        generated_files = generator.generate_all(
            metadata, prompt_template, validation_rules,
            with_image=with_image
        )

    console.print(f"Generated {len(generated_files)} files:")

    for file_path in sorted(generated_files.keys()):
        if file_path.startswith('_'):
            continue  # Skip internal markers
        console.print(f"   {file_path}")

    # Step 4: Determine output location
    if not dry_run:
        console.print("\n[bold]Step 4: Output Location[/bold]")

        if yes:
            output_choice = '1'
        else:
            console.print("Where should files be written?")
            console.print("  [1] Directly to service directories")
            console.print("  [2] To output directory (text-service-cli/output/)")
            output_choice = Prompt.ask("Choose", choices=['1', '2'], default='2')

        write_direct = (output_choice == '1')
        output_base = TEXT_SERVICE_ROOT if write_direct else Path(__file__).parent / 'test_output'

    # Step 5: Preview or write files
    if dry_run:
        console.print("\n[bold yellow]Dry run mode - no files written[/bold yellow]")
        console.print("\nGenerated code preview:")

        # Show first file as example
        for file_path, content in generated_files.items():
            if file_path.startswith('_'):
                continue

            console.print(f"\n[cyan]{file_path}[/cyan] (first 30 lines):")
            lines = content.split('\n')[:30]
            for line in lines:
                console.print(f"  {line}")

            if len(content.split('\n')) > 30:
                console.print(f"  ... ({len(content.split(chr(10)))} lines total)")
            break

        console.print(f"\n... ({len(generated_files)} files total)")

        # Show manual update snippets
        _show_update_snippets(format_type, metadata, generated_files)

    else:
        if yes or click.confirm('\nReady to write files. Continue?', default=True):
            console.print("\n[bold]Writing files...[/bold]")

            for file_path, content in generated_files.items():
                if file_path.startswith('_'):
                    continue

                full_path = output_base / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)

                with open(full_path, 'w') as f:
                    f.write(content)

                console.print(f"   {file_path}")

            console.print("\n[bold green]Integration complete![/bold green]")

            # Show manual update snippets
            _show_update_snippets(format_type, metadata, generated_files)

            # Next steps
            console.print("\n[bold]Next Steps:[/bold]")
            if format_type == 'variant':
                console.print("  1. Review generated files")
                console.print("  2. Update app/variant_specs/variant_index.json (see snippet above)")
                console.print(f"  3. Run: python3 tests/test_{metadata['variant_id']}.py")
                console.print("  4. Test via API: POST /v1.2/generate")
            else:
                console.print("  1. Review generated files")
                console.print("  2. Update app/core/hero/__init__.py (see snippet above)")
                console.print("  3. Update app/api/hero_routes.py (see snippet above)")
                console.print(f"  4. Run: python3 tests/test_{metadata['hero_type']}.py")
                console.print(f"  5. Test via API: POST /v1.2/hero/{metadata['endpoint_path']}")

        else:
            console.print("\n[yellow]Aborted[/yellow]")


def _show_update_snippets(format_type: str, metadata: dict, generated_files: dict):
    """Show manual update code snippets."""
    console.print("\n[bold]Manual Updates Required:[/bold]")

    if format_type == 'variant':
        # variant_index.json update
        console.print("\n[cyan]Add to app/variant_specs/variant_index.json:[/cyan]")
        snippet = generated_files.get('_index_update', '')
        if snippet:
            console.print(snippet)
        else:
            variant_id = metadata['variant_id']
            slide_type = metadata['slide_type']
            console.print(f'''
In "slide_types" > "{slide_type}" > "variants" array, add:
  "{variant_id}"

In "variant_lookup", add:
  "{variant_id}": "{slide_type}"
''')

    else:  # hero
        # __init__.py update
        console.print("\n[cyan]Add to app/core/hero/__init__.py:[/cyan]")
        init_snippet = generated_files.get('_init_update', '')
        if init_snippet:
            console.print(init_snippet)

        # hero_routes.py update
        console.print("\n[cyan]Add to app/api/hero_routes.py:[/cyan]")
        routes_snippet = generated_files.get('_routes_update', '')
        if routes_snippet:
            console.print(routes_snippet)


if __name__ == '__main__':
    cli()
