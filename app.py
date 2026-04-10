import streamlit as st
from tools import save_input_code, write_test_file, run_tests
from llm_client import get_response, get_response_with_rag
from rag_store import save_test_pattern, retrieve_similar_patterns

st.set_page_config(page_title="AI Testing Agent", page_icon="🤖")
st.title("🤖 AI Testing Agent — Groq Powered")
st.caption("Paste Python code → Agent generates tests → Finds bugs → Fixes them")

code_input = st.text_area(
    "📋 Paste your Python code here:",
    height=200,
    value="""def divide(a, b):
    return a / b

def find_max(lst):
    max_val = 0
    for x in lst:
        if x > max_val:
            max_val = x
    return max_val"""
)

if st.button("🚀 Run Agent", type="primary"):

    analysis = ""
    bug_count = 0

    # Save pasted code to importable temp file
    save_input_code(code_input)

    # Step 1: Generate tests with RAG memory
    with st.spinner("🤖 Generating tests with Groq + RAG..."):
        past_patterns = retrieve_similar_patterns(code_input)

        if past_patterns:
            st.info(f"📚 Found {len(past_patterns)} similar past test patterns — using as context")

        test_code = get_response_with_rag(
            system_prompt="""You are an expert Python QA engineer.
Write pytest tests for the given Python code.

STRICT RULES:
- Output ONLY valid Python pytest code
- Do NOT add any explanation or comments
- Do NOT add markdown fences like ```
- Import functions using: from sample_code.temp_input import *
- Only test functions that exist in the provided code
- Do NOT redefine the original functions
- Cover: normal inputs, empty string, wrong type, boundary values
- For None inputs: use assert result == "Missing credentials" (do NOT use pytest.raises unless the function actually raises an exception)
- Keep tests realistic and passing-safe
""",
            user_message=f"Code:\n{code_input}",
            past_patterns=past_patterns
        )

        test_code = test_code.replace("```python", "").replace("```", "").strip()
        write_test_file(test_code)

    st.subheader("📝 Generated Tests")
    st.code(test_code, language="python")

    # Step 2: Run tests
    with st.spinner("🧪 Running tests..."):
        results = run_tests()

    st.subheader("🧪 Test Results")

    if results["passed"]:
        st.success("✅ All tests passed! Code is clean.")
        bug_count = 0
        save_test_pattern(code_input, test_code, "No bugs")
        st.success("💾 Pattern saved to RAG memory")

        st.subheader("📊 Agent Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("Tests Generated", test_code.count("def test_"))
        col2.metric("Bugs Found", bug_count)
        col3.metric("Status", "✅ Clean")

    else:
        st.error("❌ Tests failed — bugs found!")
        st.code(results["stdout"])

        # Step 3: Analyze
        with st.spinner("🔍 Analyzing bugs..."):
            analysis = get_response(
                system_prompt="""You are a senior QA engineer.
Analyze the failed pytest output and explain:
1. Bug name
2. Root cause
3. Which test failed and why
4. Suggested code fix
Keep it clear and short.""",
                user_message=f"Code:\n{code_input}\n\nTest failures:\n{results['stdout']}"
            )

        st.subheader("🐛 Bug Analysis")
        st.markdown(analysis)

        # Step 4: Fix
        with st.spinner("🔧 Fixing code..."):
            fixed = get_response(
                system_prompt="""You are a Python developer.
Return ONLY the corrected Python code.
Rules:
- No explanation
- No markdown fences
- Keep the same function names
- Fix only the detected bugs""",
                user_message=f"Buggy code:\n{code_input}\n\nBugs:\n{analysis}"
            )
            fixed = fixed.replace("```python", "").replace("```", "").strip()

        st.subheader("✅ Fixed Code")
        st.code(fixed, language="python")
        st.download_button("⬇️ Download Fixed Code", fixed, "fixed_code.py")

        bug_count = results["stdout"].lower().count("failed")
        save_test_pattern(code_input, test_code, analysis)
        st.success("💾 Pattern saved to RAG memory")

        st.subheader("📊 Agent Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("Tests Generated", test_code.count("def test_"))
        col2.metric("Bugs Found", bug_count)
        col3.metric("Status", "⚠️ Review")