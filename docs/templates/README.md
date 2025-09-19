# KP Dagger Documentation Templates

This directory contains standardized templates and instructions for creating consistent, high-quality documentation across the KP Dagger project.

## Available Templates

### Architecture Documentation
- **Template**: [`architecture-document-template.md`](./architecture-document-template.md)
- **Instructions**: [`architecture-documentation-instructions.md`](./architecture-documentation-instructions.md)
- **Purpose**: Standardized format for documenting service and component architectures
- **Usage**: Copy template and replace all `{placeholder}` text with service-specific content

## Template Usage Guidelines

### For Architecture Documents
1. Copy `architecture-document-template.md` to appropriate location in `docs/architecture/`
2. Read `architecture-documentation-instructions.md` thoroughly
3. Replace all placeholder text in `{curly braces}`
4. Follow the established patterns from existing architecture docs
5. Review using the checklist in the instructions

### Quality Standards
All documentation templates enforce:
- **Consistency**: Standardized structure and formatting
- **Completeness**: Comprehensive coverage of all relevant aspects
- **Clarity**: Clear, accessible language and visual elements
- **Accuracy**: Tested code examples and technical correctness
- **Maintainability**: Structured for easy updates and maintenance

### Integration with Project Standards
These templates extend and complement the project's documentation standards:
- Base documentation standards: `.github/instructions/docs.instructions.md`
- Python coding standards: `.github/instructions/python.instructions.md`
- Overall project guidelines: `.github/copilot-instructions.md`

## Contributing to Templates

### Template Updates
- Propose changes through standard PR process
- Test templates with real documentation before submitting
- Update instructions when template structure changes
- Maintain backward compatibility where possible

### New Templates
- Follow established patterns from existing templates
- Include comprehensive instructions for template usage
- Provide examples of completed documentation using the template
- Update this README when adding new templates

## Template Maintenance

### Review Schedule
- **Quarterly**: Review templates for accuracy and completeness
- **On major changes**: Update when project architecture evolves
- **On feedback**: Iterate based on documentation author feedback

### Version Control
- Templates are versioned with the main project
- Breaking changes to templates require documentation migration plan
- Archive old template versions in `docs/archive/templates/`

These templates ensure that KP Dagger maintains high-quality, consistent documentation that serves both developers and users effectively.
