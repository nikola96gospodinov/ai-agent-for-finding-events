This is running a local LLM.

## Type Checking with mypy

This project uses mypy for static type checking. To run the type checker:

```bash
# Install required packages
pip install -r requirements.txt

# Run mypy type checking
./run_mypy.sh
```

### VSCode Integration

If you're using VSCode, mypy integration is already set up. The editor will show type errors inline as you code.

### Configuration

The mypy configuration is stored in `mypy.ini`. You can adjust the strictness level by modifying this file.
