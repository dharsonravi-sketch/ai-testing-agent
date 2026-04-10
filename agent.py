from llm_client import get_response
from tools import read_file, write_test_file, run_tests

# ─── Prompts ───────────────────────────────────────────────────────────────────

GENERATE_PROMPT = """You are an expert Python QA engineer.
Given Python source code, write thorough pytest test cases.
Cover: normal cases, edge cases, null/empty inputs, negative numbers, boundaries.
Output ONLY valid Python pytest code. No explanations. No markdown fences."""

ANALYZE_PROMPT = """You are a senior QA engineer.
Given Python source code and failing test output, explain:
1. What each bug is
2. Why it causes the failure  
3. How to fix it
Be clear and concise."""

FIX_PROMPT = """You are a Python developer.
Given buggy source code and a bug analysis, return the FIXED version.
Output ONLY the fixed Python code. No explanations. No markdown fences."""

# ─── Agent Steps ───────────────────────────────────────────────────────────────

def step1_generate_tests(source_code: str) -> str:
    print("🤖 Step 1: Generating tests with Groq...")
    return get_response(
        system_prompt=GENERATE_PROMPT,
        user_message=f"Write pytest tests for this code:\n\n{source_code}"
    )

def step2_analyze_failures(source_code: str, test_output: str) -> str:
    print("🔍 Step 2: Analyzing failures with Groq...")
    return get_response(
        system_prompt=ANALYZE_PROMPT,
        user_message=f"Source code:\n{source_code}\n\nTest output:\n{test_output}"
    )

def step3_fix_code(source_code: str, analysis: str) -> str:
    print("🔧 Step 3: Generating fix with Groq...")
    return get_response(
        system_prompt=FIX_PROMPT,
        user_message=f"Buggy code:\n{source_code}\n\nBug analysis:\n{analysis}"
    )

# ─── Main Agent Loop ───────────────────────────────────────────────────────────

def run_agent(filepath: str):
    print("\n" + "="*55)
    print("  🚀 AI Testing Agent — Powered by Groq")
    print("="*55 + "\n")

    # ── Read source code
    print(f"📂 Reading: {filepath}")
    source_code = read_file(filepath)

    # ── Step 1: Generate tests
    test_code = step1_generate_tests(source_code)
    write_test_file(test_code)

    # ── Step 2: Run tests
    print("\n🧪 Running generated tests...\n")
    results = run_tests()
    print(results["stdout"])

    if results["passed"]:
        print("✅ Code is clean. No bugs found.")
        return

    # ── Step 3: Analyze failures
    print("❌ Tests failed. Analyzing bugs...\n")
    analysis = step2_analyze_failures(source_code, results["stdout"])
    print("─" * 50)
    print("🐛 BUG REPORT:\n")
    print(analysis)

    # ── Step 4: Auto-fix the code
    print("\n" + "─" * 50)
    fixed_code = step3_fix_code(source_code, analysis)
    fixed_code = fixed_code.replace("```python", "").replace("```", "").strip()

    fixed_path = filepath.replace(".py", "_fixed.py")
    with open(fixed_path, "w") as f:
        f.write(fixed_code)
    print(f"\n✅ Fixed code saved → {fixed_path}")

    # ── Step 5: Re-run tests on fixed code
    print("\n🔁 Re-running tests on fixed code...\n")
    with open("tests/test_generated.py", "r") as f:
        test_src = f.read()

    test_src = test_src.replace(
        "from sample_code.buggy_math import",
        "from sample_code.buggy_math_fixed import"
    )
    with open("tests/test_fixed.py", "w") as f:
        f.write(test_src)

    final = run_tests("tests/test_fixed.py")
    print(final["stdout"])

    if final["passed"]:
        print("🎉 Agent fixed all bugs successfully!")
    else:
        print("⚠️  Some bugs remain. Manual review needed.")

# ─── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run_agent("sample_code/buggy_math.py")