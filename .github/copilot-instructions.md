You are a software developer with expertise in Python.  

Code will use features available in Python 3.12.  

You will use SQLModel for the combined ORM (SQLAlchemy) and data validation (Pydantic) library:
- Pydantic will be used for data validation and serialization.
- SQLAlchemy will be used for database interactions.

You will use DuckDB as an in-process database to store all data related to the application.  

You will use Python type hints in all function definitions and initial variable declarations.  

Type hints will be consistent with Python 3.12 guidelines and PEP 484.  Do not use “from typing” unless necessary.  For instance, “list | None” should be used instead of the typing module’s “Optional”.

The application will be distributed via PyPI.

Do not use relative module imports.

All unit tests will be written using Pytest.

All package management and build actions will use UV for Python.

All type hints and linting will be checked using Ruff.  The ruff configuration file is available at https://raw.githubusercontent.com/flyguy62n/dotfiles/refs/heads/main/ruff.toml.

The application will process network device configuration files which are expected to be in plaintext format.

Supported network device configuration file formats include currently supported versions Cisco IOS, Cisco ASA, Fortigate FortiOS, and PaloAlto PAN-OS.

The application will be designed to be extensible, allowing for the addition of new network device configuration file formats in the future.

The application will use Click for command line interface (CLI) functionality.

Checks that will be performed by the application include:
1. Review of access control lists and firewall rules for potential risky rules.
2. Review of device configurations for compliance with best practices.  
  - You will use the Center for Internet Security (CIS) benchmarks as a reference.
  - Focus will be placed on Level 1 benchmarks for each device type.
3. Review of device firmware versions against known vulnerabilities.  Use the following APIs as reference:
  - [CVE Details](https://www.cvedetails.com/documentation/apis) for CVE information.
  - [End of Life.Net](https://endoflife.date/docs/api/v1/#/) for end of life information.