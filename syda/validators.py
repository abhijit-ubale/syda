"""
Schema validation module for pre-generation checks.

This module provides comprehensive validation for schemas before data generation,
catching foreign key issues, template problems, and constraint violations early.
"""

import os
import re
from typing import Dict, List, Tuple, Any, Set, Optional
from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    """Results from schema validation."""
    
    is_valid: bool = True
    error_count: int = 0
    warning_count: int = 0
    errors: Dict[str, List[str]] = field(default_factory=dict)
    warnings: Dict[str, List[str]] = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)
    
    def add_error(self, schema_name: str, error: str):
        """Add an error for a schema."""
        if schema_name not in self.errors:
            self.errors[schema_name] = []
        self.errors[schema_name].append(error)
        self.error_count += 1
        self.is_valid = False
    
    def add_warning(self, schema_name: str, warning: str):
        """Add a warning for a schema."""
        if schema_name not in self.warnings:
            self.warnings[schema_name] = []
        self.warnings[schema_name].append(warning)
        self.warning_count += 1
    
    def add_suggestion(self, suggestion: str):
        """Add a suggestion for fixing issues."""
        if suggestion not in self.suggestions:
            self.suggestions.append(suggestion)
    
    def summary(self) -> str:
        """Return a formatted summary of validation results."""
        lines = []
        
        if self.is_valid:
            lines.append("✅ All schemas passed validation!")
        else:
            lines.append(f"❌ SCHEMA VALIDATION FAILED ({self.error_count} errors, {self.warning_count} warnings):\n")
            
            # Print errors
            for schema_name, errors in self.errors.items():
                if errors:
                    lines.append(f"  {schema_name}:")
                    for error in errors:
                        lines.append(f"    ❌ {error}")
            
            # Print warnings
            for schema_name, warnings in self.warnings.items():
                if warnings:
                    lines.append(f"  {schema_name}:")
                    for warning in warnings:
                        lines.append(f"    ⚠️  {warning}")
            
            # Print suggestions
            if self.suggestions:
                lines.append(f"\n💡 SUGGESTIONS:")
                for suggestion in self.suggestions:
                    lines.append(f"  ✓ {suggestion}")
        
        return "\n".join(lines)


class ForeignKeyValidator:
    """Validates foreign key relationships in schemas."""
    
    COMMON_TABLE_MAPPINGS = {
        'user': 'users',
        'product': 'products',
        'order': 'orders',
        'customer': 'customers',
        'category': 'categories',
        'invoice': 'invoices',
        'transaction': 'transactions',
        'account': 'accounts',
        'department': 'departments',
        'employee': 'employees'
    }
    
    def __init__(self):
        """Initialize the foreign key validator."""
        self.validated_tables = set()
        self.all_schemas = {}
    
    def _singularize(self, table_name: str) -> str:
        """Convert table name to singular form (basic heuristic)."""
        # Handle common pluralization patterns
        if table_name.endswith('ies'):
            return table_name[:-3] + 'y'
        elif table_name.endswith('es'):
            return table_name[:-2]
        elif table_name.endswith('s') and not table_name.endswith('ss'):
            return table_name[:-1]
        return table_name
    
    def _get_expected_fk_pattern(self, target_schema: str) -> str:
        """Get expected FK field naming pattern for a target schema."""
        singular = self._singularize(target_schema)
        return f"{singular}_id"
    
    def _is_naming_convention_likely_valid(self, fk_field: str, target_schema: str) -> bool:
        """Check if FK field name follows common naming conventions."""
        expected_pattern = self._get_expected_fk_pattern(target_schema)
        
        # Allow exact match
        if fk_field == expected_pattern:
            return True
        
        # Allow common variations
        variations = [
            expected_pattern,
            f"{target_schema}_id",
            f"{target_schema.lower()}_id",
            "id",  # Single column FK is valid
        ]
        
        return fk_field in variations or fk_field.endswith("_id")
    
    def validate_foreign_keys(
        self,
        schema_name: str,
        schema: Dict[str, Any],
        all_schemas: Dict[str, Dict[str, Any]]
    ) -> Tuple[List[str], List[str]]:
        """
        Validate all foreign keys in a schema.
        
        Args:
            schema_name: Name of the schema being validated
            schema: Schema definition
            all_schemas: All schemas for cross-reference
            
        Returns:
            Tuple of (errors, warnings)
        """
        errors = []
        warnings = []
        self.all_schemas = all_schemas
        
        # Skip if no foreign keys
        fks = schema.get('__foreign_keys__', {})
        if not fks:
            return errors, warnings
        
        for fk_field, fk_info in fks.items():
            # Handle both tuple and dict formats
            if isinstance(fk_info, (list, tuple)) and len(fk_info) == 2:
                target_schema, target_column = fk_info
            elif isinstance(fk_info, dict):
                target_schema = fk_info.get('schema') or fk_info.get('target_schema')
                target_column = fk_info.get('column') or fk_info.get('target_column')
            else:
                errors.append(
                    f"FK: Invalid foreign key definition for '{fk_field}': {fk_info}"
                )
                continue
            
            # Skip if schema/column not extractable
            if not target_schema or not target_column:
                errors.append(
                    f"FK: Invalid foreign key definition for '{fk_field}': missing schema or column"
                )
                continue
            
            # Validate FK field exists in current schema
            if fk_field not in schema:
                errors.append(
                    f"FK: Foreign key field '{fk_field}' is not defined in schema"
                )
            
            # Validate target schema exists
            if target_schema not in all_schemas:
                errors.append(
                    f"FK: Field '{fk_field}' references non-existent schema '{target_schema}'"
                )
                
                # Suggest similar schema names
                similar = self._find_similar_schema_names(target_schema, all_schemas.keys())
                if similar:
                    for suggestion in similar:
                        errors.append(
                            f"FK:    (Did you mean '{suggestion}'?)"
                        )
                continue
            
            # Validate target column exists in target schema
            target_schema_def = all_schemas[target_schema]
            if target_column not in target_schema_def:
                errors.append(
                    f"FK: Field '{fk_field}' references non-existent column "
                    f"'{target_schema}.{target_column}'"
                )
                
                # Suggest similar columns
                similar = self._find_similar_field_names(target_column, target_schema_def.keys())
                if similar:
                    for suggestion in similar:
                        errors.append(
                            f"FK:    (Did you mean '{target_schema}.{suggestion}'?)"
                        )
            
            # Check naming convention (warning, not error)
            if not self._is_naming_convention_likely_valid(fk_field, target_schema):
                warnings.append(
                    f"FK: Field '{fk_field}' doesn't follow naming convention for '{target_schema}' "
                    f"(expected '{self._get_expected_fk_pattern(target_schema)}')"
                )
        
        return errors, warnings
    
    @staticmethod
    def _find_similar_schema_names(target: str, candidates: Any, max_results: int = 2) -> List[str]:
        """Find similar schema names for suggestions."""
        if not target:
            return []
        
        candidates = list(candidates)
        target_lower = target.lower()
        
        # Exact case-insensitive match
        exact_matches = [c for c in candidates if c.lower() == target_lower]
        if exact_matches:
            return exact_matches[:max_results]
        
        # Substring matches
        substring_matches = [c for c in candidates if target_lower in c.lower() or c.lower() in target_lower]
        return substring_matches[:max_results]
    
    @staticmethod
    def _find_similar_field_names(target: str, candidates: Any, max_results: int = 2) -> List[str]:
        """Find similar field names for suggestions."""
        candidates = [c for c in candidates if not c.startswith('__')]
        target_lower = target.lower()
        
        # Exact case-insensitive match
        exact_matches = [c for c in candidates if c.lower() == target_lower]
        if exact_matches:
            return exact_matches[:max_results]
        
        # Substring matches
        substring_matches = [c for c in candidates if target_lower in c.lower() or c.lower() in target_lower]
        return substring_matches[:max_results]


class TemplateValidator:
    """Validates template schemas and Jinja2 placeholders."""
    
    def __init__(self):
        """Initialize the template validator."""
        self.placeholder_pattern = re.compile(r'{{\s*([a-zA-Z0-9_]+)\s*}}')
        self.jinja_pattern = re.compile(r'{%.*?%}|{#.*?#}')
    
    def _extract_placeholders(self, text: str) -> Set[str]:
        """Extract all placeholder field names from text."""
        return set(self.placeholder_pattern.findall(text))
    
    def _is_jinja_syntax_valid(self, text: str) -> Tuple[bool, Optional[str]]:
        """Validate Jinja2 syntax in text."""
        try:
            import jinja2
            # Try to parse the template
            env = jinja2.Environment()
            env.parse(text)
            return True, None
        except jinja2.TemplateSyntaxError as e:
            return False, str(e)
        except ImportError:
            # jinja2 not installed, skip validation
            return True, None
    
    def validate_templates(
        self,
        schema_name: str,
        schema: Dict[str, Any]
    ) -> Tuple[List[str], List[str]]:
        """
        Validate template-related schema fields.
        
        Args:
            schema_name: Name of the schema
            schema: Schema definition
            
        Returns:
            Tuple of (errors, warnings)
        """
        errors = []
        warnings = []
        
        # Check if this is a template schema
        if '__template_source__' not in schema:
            return errors, warnings  # Not a template schema
        
        template_path = schema['__template_source__']
        
        # Validate template file exists
        if not os.path.exists(template_path):
            errors.append(
                f"Template: File not found: '{template_path}'"
            )
            return errors, warnings
        
        # Validate file is readable
        if not os.path.isfile(template_path):
            errors.append(
                f"Template: '{template_path}' is not a file"
            )
            return errors, warnings
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except (IOError, UnicodeDecodeError) as e:
            errors.append(
                f"Template: Unable to read file: {str(e)}"
            )
            return errors, warnings
        
        # Extract placeholders
        placeholders = self._extract_placeholders(content)
        
        if not placeholders:
            warnings.append(
                f"Template: No placeholders found in template"
            )
        
        # Validate each placeholder exists in schema
        schema_fields = {k: v for k, v in schema.items() if not k.startswith('__')}
        
        for placeholder in placeholders:
            if placeholder not in schema_fields:
                errors.append(
                    f"Template: Placeholder '{{{{ {placeholder} }}}}' is not defined in schema"
                )
        
        # Check for schema fields not used in template
        unused_fields = set(schema_fields.keys()) - placeholders
        if unused_fields:
            warnings.append(
                f"Template: Schema fields not used in template: {', '.join(sorted(unused_fields))}"
            )
        
        # Validate Jinja2 syntax
        is_valid, error_msg = self._is_jinja_syntax_valid(content)
        if not is_valid:
            errors.append(
                f"Template: Invalid Jinja2 syntax: {error_msg}"
            )
        
        # Validate required metadata
        required_metadata = {
            '__input_file_type__': 'Input file type (html, txt, rtf)',
            '__output_file_type__': 'Output file type (pdf, html, txt, rtf)'
        }
        
        for metadata_key, description in required_metadata.items():
            if metadata_key not in schema:
                errors.append(
                    f"Template: Missing '{metadata_key}' metadata ({description})"
                )
        
        return errors, warnings


class ConstraintValidator:
    """Validates field constraints."""
    
    VALID_FIELD_TYPES = {
        'integer', 'number', 'float', 'decimal',
        'text', 'string',
        'email', 'phone', 'url',
        'date', 'datetime', 'time',
        'boolean', 'bool',
        'json', 'dict',
        'foreign_key',
        'id', 'uuid'
    }
    
    def __init__(self):
        """Initialize the constraint validator."""
        pass
    
    def validate_constraints(
        self,
        schema_name: str,
        schema: Dict[str, Any]
    ) -> Tuple[List[str], List[str]]:
        """
        Validate field constraints.
        
        Args:
            schema_name: Name of the schema
            schema: Schema definition
            
        Returns:
            Tuple of (errors, warnings)
        """
        errors = []
        warnings = []
        
        for field_name, field_def in schema.items():
            # Skip metadata fields
            if field_name.startswith('__'):
                continue
            
            # Validate field type
            if isinstance(field_def, str):
                if field_def.lower() not in self.VALID_FIELD_TYPES:
                    warnings.append(
                        f"Constraint: Field '{field_name}' has unknown type '{field_def}' "
                        f"(valid types: {', '.join(sorted(self.VALID_FIELD_TYPES))})"
                    )
            
            # Validate constraints if defined
            if isinstance(field_def, dict):
                constraints = field_def.get('constraints', {})
                
                # Numeric constraint validation
                if 'min' in constraints and 'max' in constraints:
                    try:
                        min_val = float(constraints['min'])
                        max_val = float(constraints['max'])
                        
                        if min_val > max_val:
                            errors.append(
                                f"Constraint: Field '{field_name}' has min ({min_val}) > max ({max_val})"
                            )
                    except (ValueError, TypeError) as e:
                        errors.append(
                            f"Constraint: Field '{field_name}' has invalid numeric constraints: {str(e)}"
                        )
                
                # String pattern validation
                if 'pattern' in constraints:
                    try:
                        re.compile(constraints['pattern'])
                    except re.error as e:
                        errors.append(
                            f"Constraint: Field '{field_name}' has invalid regex pattern: {str(e)}"
                        )
                
                # String length validation
                if 'min_length' in constraints and 'max_length' in constraints:
                    try:
                        min_len = int(constraints['min_length'])
                        max_len = int(constraints['max_length'])
                        
                        if min_len > max_len:
                            errors.append(
                                f"Constraint: Field '{field_name}' has min_length ({min_len}) > max_length ({max_len})"
                            )
                    except (ValueError, TypeError) as e:
                        errors.append(
                            f"Constraint: Field '{field_name}' has invalid length constraints: {str(e)}"
                        )
        
        return errors, warnings


class CircularDependencyValidator:
    """Validates for circular dependencies in foreign keys."""
    
    def validate_circular_dependencies(
        self,
        schema_name: str,
        schema: Dict[str, Any],
        all_schemas: Dict[str, Dict[str, Any]],
        max_depth: int = 10
    ) -> Tuple[List[str], List[str]]:
        """
        Validate that foreign keys don't create circular dependencies.
        
        Args:
            schema_name: Schema being validated
            schema: Schema definition
            all_schemas: All schemas for graph traversal
            max_depth: Maximum allowed dependency depth
            
        Returns:
            Tuple of (errors, warnings)
        """
        errors = []
        warnings = []
        
        try:
            import networkx as nx
            
            # Build dependency graph
            graph = nx.DiGraph()
            
            for sname, sdef in all_schemas.items():
                graph.add_node(sname)
                fks = sdef.get('__foreign_keys__', {})
                
                for fk_field, fk_info in fks.items():
                    if isinstance(fk_info, (list, tuple)) and len(fk_info) == 2:
                        target_schema = fk_info[0]
                    elif isinstance(fk_info, dict):
                        target_schema = fk_info.get('schema') or fk_info.get('target_schema')
                    else:
                        continue
                    
                    if target_schema in all_schemas:
                        graph.add_edge(sname, target_schema)
            
            # Check for cycles
            if not nx.is_directed_acyclic_graph(graph):
                cycles = list(nx.simple_cycles(graph))
                for cycle in cycles:
                    cycle_str = ' → '.join(cycle) + f' → {cycle[0]}'
                    errors.append(
                        f"Circular dependency detected: {cycle_str}"
                    )
            
            # Check for deep dependencies
            if schema_name in graph:
                for target in nx.descendants(graph, schema_name):
                    path_length = nx.shortest_path_length(graph, schema_name, target)
                    if path_length > max_depth:
                        warnings.append(
                            f"Deep dependency chain detected for '{schema_name}' "
                            f"(depth: {path_length}, max recommended: {max_depth})"
                        )
        
        except ImportError:
            # networkx not available, skip validation
            pass
        
        return errors, warnings


class SchemaValidator:
    """Main schema validation orchestrator."""
    
    def __init__(self):
        """Initialize the schema validator."""
        self.fk_validator = ForeignKeyValidator()
        self.template_validator = TemplateValidator()
        self.constraint_validator = ConstraintValidator()
        self.circular_validator = CircularDependencyValidator()
    
    def validate_schemas(
        self,
        schemas: Dict[str, Dict[str, Any]],
        strict: bool = False
    ) -> ValidationResult:
        """
        Validate all schemas before generation.
        
        Args:
            schemas: Dictionary of schema definitions
            strict: If True, treat warnings as errors
            
        Returns:
            ValidationResult object
        """
        result = ValidationResult()
        
        if not schemas:
            result.add_error("__global__", "No schemas provided")
            return result
        
        # Validate each schema
        for schema_name, schema in schemas.items():
            if not isinstance(schema, dict):
                result.add_error(schema_name, f"Schema must be a dictionary, got {type(schema)}")
                continue
            
            # Count non-metadata fields
            field_count = sum(1 for k in schema.keys() if not k.startswith('__'))
            if field_count == 0:
                result.add_error(schema_name, "Schema must define at least one data field (not just metadata)")
            
            # Validate foreign keys
            fk_errors, fk_warnings = self.fk_validator.validate_foreign_keys(
                schema_name, schema, schemas
            )
            for error in fk_errors:
                result.add_error(schema_name, error)
            for warning in fk_warnings:
                result.add_warning(schema_name, warning)
            
            # Validate templates
            template_errors, template_warnings = self.template_validator.validate_templates(
                schema_name, schema
            )
            for error in template_errors:
                result.add_error(schema_name, error)
            for warning in template_warnings:
                result.add_warning(schema_name, warning)
            
            # Validate constraints
            constraint_errors, constraint_warnings = self.constraint_validator.validate_constraints(
                schema_name, schema
            )
            for error in constraint_errors:
                result.add_error(schema_name, error)
            for warning in constraint_warnings:
                result.add_warning(schema_name, warning)
            
            # Validate circular dependencies
            circular_errors, circular_warnings = self.circular_validator.validate_circular_dependencies(
                schema_name, schema, schemas
            )
            for error in circular_errors:
                result.add_error(schema_name, error)
            for warning in circular_warnings:
                result.add_warning(schema_name, warning)
        
        # Add suggestions for common issues
        if result.errors:
            if any('naming convention' in str(e).lower() for errors in result.errors.values() for e in errors):
                result.add_suggestion(
                    "Use explicit foreign key definitions instead of relying on naming convention inference"
                )
            if any('not found' in str(e).lower() or 'non-existent' in str(e).lower() for errors in result.errors.values() for e in errors):
                result.add_suggestion(
                    "Verify all schema names and column names match exactly (case-sensitive)"
                )
            if any('template' in str(e).lower() for errors in result.errors.values() for e in errors):
                result.add_suggestion(
                    "Ensure template files exist and all placeholders are defined in the schema"
                )
        
        # If strict mode, convert warnings to errors
        if strict and result.warnings:
            for schema_name, warnings in result.warnings.items():
                for warning in warnings:
                    result.add_error(schema_name, f"(Strict mode) {warning}")
            result.warnings = {}
        
        return result
