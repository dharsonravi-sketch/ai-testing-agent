import subprocess
import os

TEMP_CODE_PATH = "sample_code/temp_input.py"
TEMP_TEST_PATH = "tests/test_generated.py"

def save_input_code(code: str):
    """Save pasted code to temp file and ensure __init__.py exists."""
    os.makedirs("sample_code", exist_ok=True)

    # ✅ Make sample_code a proper Python package
    init_path = "sample_code/__init__.py"
    if not os.path.exists(init_path):
        with open(init_path, "w") as f:
            f.write("")

    with open(TEMP_CODE_PATH, "w", encoding="utf-8") as f:
        f.write(code.strip() + "\n")

def read_file(filepath: str) -> str:
    """Read source code from a file."""
    with open(filepath, "r") as f:
        return f.read()

def write_test_file(test_code: str, output_path: str = TEMP_TEST_PATH):
    """Save generated tests to file."""
    os.makedirs("tests", exist_ok=True)

    # ✅ Make tests a proper Python package
    init_path = "tests/__init__.py"
    if not os.path.exists(init_path):
        with open(init_path, "w") as f:
            f.write("")

    # Clean markdown fences
    test_code = test_code.replace("```python", "").replace("```", "").strip()
    lines = test_code.splitlines()
    cleaned_lines = [line for line in lines if not line.strip().startswith("```")]
    cleaned_code = "\n".join(cleaned_lines).strip()

    # ✅ Always ensure correct import is at top
    import_line = "from sample_code.temp_input import *"
    if import_line not in cleaned_code:
        cleaned_code = import_line + "\n\n" + cleaned_code

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(cleaned_code)

    print(f"✅ Tests written to {output_path}")

def run_tests(test_path: str = TEMP_TEST_PATH) -> dict:
    """Run pytest and capture results."""
    result = subprocess.run(
        ["python", "-m", "pytest", test_path, "-v", "--tb=short"],
        capture_output=True,
        text=True
    )
    return {
        "stdout":     result.stdout,
        "stderr":     result.stderr,
        "passed":     result.returncode == 0,
        "returncode": result.returncode
    }