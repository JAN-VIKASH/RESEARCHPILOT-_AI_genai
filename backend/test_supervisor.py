import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(__file__))

from app.services.supervisor_agent import supervisor_agent, ResearchTool

# Test cases including the exact user prompt
test_cases = [
    # 1. Research Gap Queries (should prioritize RESEARCH_GAPS even with "papers on")
    ("Identify the research gaps and limitations in existing research papers on deep learning", ResearchTool.RESEARCH_GAPS),
    ("Identify research gaps and unaddressed limitations across our papers", ResearchTool.RESEARCH_GAPS),
    ("What are the key limitations and open challenges in these papers?", ResearchTool.RESEARCH_GAPS),
    ("What are the unaddressed research questions and future directions in our workspace papers?", ResearchTool.RESEARCH_GAPS),

    # 2. Academic Paper Search Queries
    ("Search for recent papers on Graph Neural Networks for drug discovery", ResearchTool.ACADEMIC_SEARCH),
    ("Find papers on multimodal contrastive learning in robotics", ResearchTool.ACADEMIC_SEARCH),
    ("Search arxiv for diffusion models in medical imaging", ResearchTool.ACADEMIC_SEARCH),
    ("Discover new papers on reinforcement learning from human feedback", ResearchTool.ACADEMIC_SEARCH),

    # 3. Paper Summarization Queries
    ("Summarize the key contributions and methodology of the Attention paper", ResearchTool.PAPER_SUMMARY),
    ("Give me a comprehensive summary of our uploaded paper on BERT", ResearchTool.PAPER_SUMMARY),
    ("Summarize the methodology of the paper on deep learning architectures", ResearchTool.PAPER_SUMMARY),

    # 4. Paper Comparison Queries
    ("Compare the models and datasets of these papers side by side", ResearchTool.PAPER_COMPARISON),
    ("What is the difference between paper 1 and paper 2 in their evaluation metrics?", ResearchTool.PAPER_COMPARISON),
    ("Compare the papers on CNN and Transformer architectures", ResearchTool.PAPER_COMPARISON),

    # 5. Literature Review Queries
    ("Conduct a comprehensive literature review of the collected literature", ResearchTool.LITERATURE_REVIEW),
    ("Synthesize the papers in this workspace into a state of the art review", ResearchTool.LITERATURE_REVIEW),
    ("Provide a thematic literature review of our papers on reinforcement learning", ResearchTool.LITERATURE_REVIEW),

    # 6. Workspace Q&A (Direct RAG)
    ("What equation is used to compute attention weights?", ResearchTool.WORKSPACE_QA),
    ("What was the batch size used in section 4.2?", ResearchTool.WORKSPACE_QA),
]

print("=== VERIFYING SUPERVISOR AGENT INTENTION UNDERSTANDING & TOOL SELECTION ===\n")
all_passed = True
for idx, (query, expected_tool) in enumerate(test_cases, 1):
    selected_tool, reasoning = supervisor_agent._classify_intent(query, papers_count=2, paper_ids=[1, 2])
    tool_name = supervisor_agent.tools[selected_tool]["name"]
    expected_name = supervisor_agent.tools[expected_tool]["name"]
    passed = (selected_tool == expected_tool)
    status_str = "PASS" if passed else "FAIL"
    print(f"[{status_str}] Test {idx:02d}: \"{query}\"")
    print(f"       -> Selected Tool: {tool_name} (Expected: {expected_name})")
    print(f"       -> Reasoning: {reasoning}\n")
    if not passed:
        all_passed = False

if all_passed:
    print(f"ALL {len(test_cases)} INTENTION UNDERSTANDING TESTS PASSED PERFECTLY!")
else:
    print("SOME TESTS FAILED!")
    sys.exit(1)
