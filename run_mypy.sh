#!/bin/bash

# Run mypy on all Python files in the project
echo "Running mypy type checking..."
mypy --config-file=mypy.ini *.py

# Exit with the same code as mypy
exit $? 