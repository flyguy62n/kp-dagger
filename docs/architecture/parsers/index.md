# Parser Architecture Documentation

This section covers the architectural decisions and interface design for network device configuration parsers in KP Dagger.

## Contents

- [Parser Implementation Decision](parser-implementation-decision.md): Rationale and comparison between ANTLR4 and Python-only approaches, documenting the chosen strategy for maintainability and extensibility.
- [Parsers Interface](parsers-interface.md): Specification and design of the common interface for device configuration parsers, supporting multi-vendor extensibility and integration with the core analysis engine.

## Documentation Hierarchy

- [Architecture Overview](../overview.md)
    - [Device Parsers](./parsers/index.md)
        - [Parser Implementation Decision](./parser-implementation-decision.md)
        - [Parsers Interface](./parsers-interface.md)

This section is referenced from the main architecture documentation and is part of the overall KP Dagger documentation hierarchy.
