#!/usr/bin/env python3
"""
Workload Orchestration Template Generator
"""
from argparse import ArgumentParser
from typing import Dict, Any, Optional
import json
import os
import asyncio
import yaml
from helm_parser.parser import HelmChartParser
from schema_generator.generator import SchemaGenerator
from template_generator.generator import TemplateGenerator
from utils.prompt_manager import PromptManager
from utils.hierarchy_manager import HierarchyManager
from ai_analyzer.analyzer import AIParameterAnalyzer

def parse_args():
    """Parse command line arguments"""
    parser = ArgumentParser(description="Generate WO schema and template from Helm chart")
    
    parser.add_argument(
        'chart_path',
        help='Path to Helm chart'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        default='./output',
        help='Output directory for generated files'
    )
    
    parser.add_argument(
        '--schema-name',
        required=True,
        help='Name for generated schema'
    )
    
    parser.add_argument(
        '--schema-version',
        required=True,
        help='Version for generated schema'
    )
    
    parser.add_argument(
        '--ai-endpoint',
        required=True,
        help='Azure OpenAI endpoint URL'
    )
    
    parser.add_argument(
        '--ai-key',
        required=True,
        help='Azure OpenAI API key'
    )
    
    parser.add_argument(
        '--ai-model',
        required=True,
        help='Azure OpenAI model deployment name'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--prompt',
        help='Path to custom prompt file relative to prompts directory',
        default=None
    )

    return parser.parse_args()

def ensure_output_dir(path: str):
    """Ensure output directory exists"""
    if not os.path.exists(path):
        os.makedirs(path)

async def main():
    """Main entry point"""
    args = parse_args()
    
    # Update hierarchy levels
    hierarchy_manager = HierarchyManager()
    hierarchy_manager.update_hierarchy_levels()  # Update on each run
    hierarchy_levels = hierarchy_manager.get_hierarchy_levels()
    
    # Load custom prompt if specified
    prompt_manager = PromptManager(args.prompt)
    custom_prompt = prompt_manager.get_prompt()
    
    # Initialize AI analyzer
    ai_analyzer = AIParameterAnalyzer(
        endpoint=args.ai_endpoint,
        api_key=args.ai_key,
        deployment=args.ai_model,
        custom_prompt=custom_prompt,
        hierarchy_levels=hierarchy_levels
    )
    
    # Parse Helm chart
    parser = HelmChartParser(args.chart_path)
    chart_data = parser.parse()
    
    # Generate schema
    schema_generator = SchemaGenerator(ai_analyzer=ai_analyzer)
    schema = await schema_generator.generate(
        chart_data=chart_data,
        name=args.schema_name,
        version=args.schema_version
    )
    
    # Create output files
    ensure_output_dir(args.output_dir)
    
    schema_file = os.path.join(args.output_dir, f"{args.schema_name}-schema.yaml")
    print(f"Schema saved to {schema_file}")
    with open(schema_file, 'w') as f:
        f.write(schema)
    
    # Parse schema from YAML
    try:
        schema_dict = yaml.safe_load(schema)
    except Exception as e:
        print(f"Warning: Failed to parse schema as YAML, template generation may be incomplete: {e}")
        schema_dict = None
    
    # Generate template
    template_generator = TemplateGenerator()
    template = template_generator.generate(
        chart_data=chart_data,
        name=args.schema_name,
        version=args.schema_version,
        schema=schema_dict
    )
        
    # Save template
    template_file = os.path.join(args.output_dir, f"{args.schema_name}-template.yaml")
    print(f"Template saved to {template_file}")
    with open(template_file, 'w') as f:
        f.write(template)

if __name__ == '__main__':
    asyncio.run(main())
