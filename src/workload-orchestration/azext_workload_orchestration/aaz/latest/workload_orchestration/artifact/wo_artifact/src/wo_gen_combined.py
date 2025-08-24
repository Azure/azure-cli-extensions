#!/usr/bin/env python3
"""
Combined Workload Orchestration Template Generator
Simplified version that combines parsing, schema and template generation
"""
import os
import yaml
from dataclasses import dataclass
from typing import Dict, Any, Optional, List

@dataclass
class ChartParameter:
    """Data class representing a Helm chart parameter"""
    name: str
    type: str
    default_value: Optional[Any] = None
    description: Optional[str] = None
    required: bool = False
    nested_path: Optional[List[str]] = None
    
@dataclass
class ChartData:
    """Data class representing parsed Helm chart data"""
    name: str
    version: str
    description: Optional[str]
    parameters: Dict[str, ChartParameter]
    dependencies: List[Dict[str, Any]]

class HelmChartParser:
    """Simplified Helm chart parser"""
    
    def __init__(self, chart_path: str):
        self.chart_path = chart_path
        self.values_file = os.path.join(chart_path, 'values.yaml')
        self.chart_file = os.path.join(chart_path, 'Chart.yaml')
        
    def _read_yaml(self, file_path: str) -> Dict[str, Any]:
        """Read and parse a YAML file"""
        try:
            if not os.path.exists(file_path):
                print(f"Warning: File not found: {file_path}")
                return {}
            with open(file_path, 'r') as f:
                return yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML file {file_path}: {str(e)}")

    def _extract_parameters(self, data: Dict[str, Any], path: List[str] = None) -> Dict[str, ChartParameter]:
        """Recursively extract parameters from values.yaml"""
        if path is None:
            path = []
            
        parameters = {}
        for key, value in data.items():
            current_path = path + [key]
            
            if isinstance(value, dict):
                nested_params = self._extract_parameters(value, current_path)
                parameters.update(nested_params)
            else:
                param_name = '.'.join(current_path)
                param_type = self._infer_type(value)
                parameters[param_name] = ChartParameter(
                    name=param_name,
                    type=param_type,
                    default_value=value,
                    nested_path=current_path,
                    required=True  # Simplified: treat all as required
                )
        return parameters
    
    def _infer_type(self, value: Any) -> str:
        """Infer parameter type"""
        if isinstance(value, bool):
            return 'boolean'
        elif isinstance(value, int):
            return 'int'
        elif isinstance(value, float):
            return 'float'
        elif isinstance(value, list):
            return 'array[string]'
        else:
            return 'string'
    
    def parse(self) -> ChartData:
        """Parse the Helm chart"""
        chart_info = self._read_yaml(self.chart_file)
        if not chart_info:
            raise ValueError(f"Invalid or missing Chart.yaml in {self.chart_path}")
            
        values = self._read_yaml(self.values_file)
        parameters = self._extract_parameters(values)
        
        return ChartData(
            name=chart_info.get('name', ''),
            version=chart_info.get('version', ''),
            description=chart_info.get('description'),
            parameters=parameters,
            dependencies=chart_info.get('dependencies', [])
        )

class SchemaGenerator:
    """Simplified schema generator"""
    
    def generate(self, chart_data: ChartData, name: str, version: str) -> str:
        """Generate schema from chart data"""
        schema = {
            'name': name,
            'version': version,
            'rules': {
                'configs': {}
            }
        }

        for param_name, param in chart_data.parameters.items():
            schema['rules']['configs'][param_name] = {
                'type': param.type,
                'required': param.required,
                'editableAt': ['target'],  # Simplified: always editable at target
                'editableBy': ['admin']    # Simplified: always editable by admin
            }
        
        if chart_data.description:
            schema['description'] = chart_data.description
            
        return yaml.dump(schema, sort_keys=False, allow_unicode=True)

class TemplateGenerator:
    """Simplified template generator"""
    
    def generate(self, chart_data: ChartData, name: str, version: str, schema: Dict[str, Any] = None) -> str:
        """Generate solution template"""
        template = {
            'schema': {
                'name': name,
                'version': version
            }
        }
        
        # Generate configs section
        configs = {}
        for param_name, param in chart_data.parameters.items():
            if param.nested_path:
                self._set_nested_value(configs, param.nested_path, 
                                     self._generate_template_value(param_name))
            else:
                configs[param_name] = self._generate_template_value(param_name)
        
        template['configs'] = configs
        
        if chart_data.dependencies:
            template['dependencies'] = [{
                'solutionTemplateId': '/common/1.0.0',
                'configsToBeInjected': [],
                'solutionTemplateVersion': '2.x.x'
            }]
        
        return yaml.dump(template, sort_keys=False, allow_unicode=True)
    
    def _generate_template_value(self, param_name: str) -> str:
        """Generate template value"""
        return f"${{{{$val({param_name})}}}}"
    
    def _set_nested_value(self, config_dict: Dict[str, Any], path: List[str], value: Any) -> None:
        """Set nested dictionary value"""
        current = config_dict
        for component in path[:-1]:
            if component not in current:
                current[component] = {}
            current = current[component]
        if path:
            current[path[-1]] = value

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate WO schema and template from Helm chart")
    parser.add_argument('chart_path', help='Path to Helm chart')
    parser.add_argument('--output-dir', '-o', default='./output', help='Output directory')
    parser.add_argument('--schema-name', required=True, help='Schema name')
    parser.add_argument('--schema-version', required=True, help='Schema version')
    
    args = parser.parse_args()
    
    # Ensure output directory exists
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    # Parse Helm chart
    parser = HelmChartParser(args.chart_path)
    chart_data = parser.parse()
    
    # Generate schema
    schema_generator = SchemaGenerator()
    schema = schema_generator.generate(
        chart_data=chart_data,
        name=args.schema_name,
        version=args.schema_version
    )
    
    # Save schema
    schema_file = os.path.join(args.output_dir, f"{args.schema_name}-schema.yaml")
    print(f"Saving schema to {schema_file}")
    with open(schema_file, 'w') as f:
        f.write(schema)
    
    # Parse schema for template generation
    schema_dict = yaml.safe_load(schema)
    
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
    print(f"Saving template to {template_file}")
    with open(template_file, 'w') as f:
        f.write(template)

if __name__ == '__main__':
    main()
