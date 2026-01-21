# WO Artifact Generator

A tool to automatically generate Workload Orchestrator schemas and templates from Helm charts using Azure OpenAI for parameter analysis.

## Features
- AI-powered parameter analysis
- Automatic parameter categorization
- Hierarchy-based configuration management 
- Custom prompt support
- Nested parameter handling
- Smart validation rules

## Prerequisites
- Python 3.8+
- Azure OpenAI API access
- Azure CLI (for hierarchy management)
- Helm charts to analyze

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
python src/wo_gen.py <chart_path> \
  --schema-name <name> \
  --schema-version <version> \
  --ai-endpoint <azure-endpoint> \
  --ai-key <api-key> \
  --ai-model <deployment-name> \
  [--output-dir ./output] \
  [--prompt custom/prompt.txt] \
  [--verbose]
```

## Project Structure
```
WOArtiGen/
├── src/
│   ├── ai_analyzer/      # AI analysis components
│   ├── helm_parser/      # Helm chart parsing
│   ├── schema_generator/ # Schema generation
│   ├── template_generator/ # Template generation
│   └── utils/           # Utility modules
├── prompts/
│   ├── default/         # Default prompt templates
│   └── custom/          # Custom prompt templates
├── config/              # Configuration files
└── output/             # Generated artifacts
```

## Configuration

### Hierarchy Levels
- Managed through config/hierarchy_levels.json
- Default: ['factory', 'line']
- Auto-updates from Azure Edge contexts

### Custom Prompts
- Place in prompts/custom/
- Reference using --prompt argument
- Must specify guidelines for:
  * Parameter configurability
  * Required vs optional parameters
  * Management responsibility (IT/OT)
  * Hierarchy level assignment
- See prompts/custom/example_prompt.txt

## Parameter Analysis

### AI Response Format
For each parameter, the AI analyzes:
- configurable: Whether parameter can be modified
- required: Whether parameter must appear in template
- managed_by: Who can modify this parameter (IT/OT)
- edit_level: At which hierarchy level it can be modified

### Management Levels

#### IT (Information Technology)
- Security configurations
- Infrastructure settings
- Network parameters
- Compliance controls

#### OT (Operational Technology)
- Production settings
- Performance tuning
- Operational thresholds
- Local customizations

### Required vs Optional Parameters
Parameters marked as required will appear in the solution template.

## Output Files

### Schema (name-schema.yaml)
```yaml
name: schema-name
version: schema-version
rules:
  configs:
    parameter.name:
      type: string|integer|boolean|array
      required: true/false
      editableAt: [hierarchy-level]
      editableBy: [IT/OT]
```

### Template (name-template.yaml)
```yaml
schema:
  name: schema-name
  version: schema-version
configs:
  parameter.name: ${$val(parameter.name)}
```

## Testing

The project includes comprehensive unit tests for all components. Tests are located alongside their respective modules with the `test_` prefix.

### Running Tests

Run individual test files:
```bash
# Run specific component tests
python src/helm_parser/test_parser.py      # Test chart parsing
python src/ai_analyzer/test_analyzer.py     # Test AI analysis
python src/ai_analyzer/test_client.py      # Test AI client
python src/schema_generator/test_generator.py # Test schema generation
python src/template_generator/test_generator.py # Test template generation
```
### Integration Tests
Integration tests are included in `src/test_wo_gen.py` and cover:

#### End-to-End Workflow
```bash
python src/test_wo_gen.py
```


### links
### https://microsoftapc-my.sharepoint.com/personal/kup_microsoft_com/_layouts/15/stream.aspx?id=%2Fpersonal%2Fkup%5Fmicrosoft%5Fcom%2FDocuments%2FRecordings%2FRegular%20Sync%2D20250630%5F120340%2DMeeting%20Recording%2Emp4&referrer=StreamWebApp%2EWeb&referrerScenario=AddressBarCopied%2Eview%2Ede10ca09%2D93c4%2D4174%2Da75b%2De4d84b7071e6

##### https://microsoftapc-my.sharepoint.com/personal/kup_microsoft_com/_layouts/15/stream.aspx?id=%2Fpersonal%2Fkup%5Fmicrosoft%5Fcom%2FDocuments%2FRecordings%2FIntern%20Project%20Presentation%20%2D%20Kawalijeet%20%20Generate%20WO%20Artifacts%20using%20AI%20%5BIn%2Dperson%5D%2D20250630%5F100312%2DMeeting%20Recording%2Emp4&referrer=StreamWebApp%2EWeb&referrerScenario=AddressBarCopied%2Eview%2Ec1704787%2D5cc0%2D4ab7%2D919a%2D108729bb9665


#### https://microsoftapc-my.sharepoint.com/:p:/g/personal/t-kawsingh_microsoft_com/EcSJzE3h2NNPofXMEVSXJfcBC8OIdy3V8usnDDCgjxBotA?wdOrigin=TEAMS-MAGLEV.p2p_ns.rwc&wdExp=TEAMS-TREATMENT&wdhostclicktime=1752024095271&web=1