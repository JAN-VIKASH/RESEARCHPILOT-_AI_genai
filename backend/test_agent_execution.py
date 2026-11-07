import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import SessionLocal, Base, engine
from app.models.user import User
from app.models.workspace import Workspace
from app.models.paper import Paper
from app.models.chat import ChatSession, ChatMessage
from app.services.supervisor_agent import supervisor_agent, ResearchTool

Base.metadata.create_all(bind=engine)
db = SessionLocal()

try:
    # 1. Setup test user
    user = db.query(User).filter(User.email == "supervisor_test@example.com").first()
    if not user:
        user = User(email="supervisor_test@example.com", hashed_password="hashed_pw_test")
        db.add(user)
        db.commit()
        db.refresh(user)

    # 2. Setup empty workspace (to verify empty workspace behavior)
    empty_workspace = db.query(Workspace).filter(
        Workspace.user_id == user.id, Workspace.name == "Empty Workspace"
    ).first()
    if not empty_workspace:
        empty_workspace = Workspace(name="Empty Workspace", description="No papers here", user_id=user.id)
        db.add(empty_workspace)
        db.commit()
        db.refresh(empty_workspace)

    # Clean any existing papers from empty workspace
    db.query(Paper).filter(Paper.workspace_id == empty_workspace.id).delete()
    db.commit()

    # 3. Setup populated workspace with 2 sample deep learning papers
    pop_workspace = db.query(Workspace).filter(
        Workspace.user_id == user.id, Workspace.name == "Deep Learning Lab"
    ).first()
    if not pop_workspace:
        pop_workspace = Workspace(name="Deep Learning Lab", description="Deep learning papers", user_id=user.id)
        db.add(pop_workspace)
        db.commit()
        db.refresh(pop_workspace)

    # Add paper 1: Transformer
    p1 = db.query(Paper).filter(Paper.workspace_id == pop_workspace.id, Paper.title == "Attention Is All You Need").first()
    if not p1:
        p1 = Paper(
            workspace_id=pop_workspace.id,
            title="Attention Is All You Need",
            authors="Vaswani et al.",
            abstract="The Transformer is based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.",
            text_content="We propose the Transformer model. Limitation: quadratic complexity O(N^2) in sequence length prohibits long-context scaling. Future work includes evaluating local attention strategies.",
            published_date="2017-06-12",
            source="arXiv",
        )
        db.add(p1)

    # Add paper 2: ResNet
    p2 = db.query(Paper).filter(Paper.workspace_id == pop_workspace.id, Paper.title == "Deep Residual Learning for Image Recognition").first()
    if not p2:
        p2 = Paper(
            workspace_id=pop_workspace.id,
            title="Deep Residual Learning for Image Recognition",
            authors="He et al.",
            abstract="Deeper neural networks are more difficult to train. We present a residual learning framework to ease the training of networks.",
            text_content="We address the degradation problem with identity shortcut connections. Limitation: residual networks do not explicitly model spatial long-range dependencies, requiring hybrid convolutional-attention mechanisms for global context.",
            published_date="2015-12-10",
            source="arXiv",
        )
        db.add(p2)
    db.commit()

    # Create test chat sessions
    sess_empty = ChatSession(workspace_id=empty_workspace.id, user_id=user.id, title="Empty Test")
    sess_pop = ChatSession(workspace_id=pop_workspace.id, user_id=user.id, title="Populated Test")
    db.add(sess_empty)
    db.add(sess_pop)
    db.commit()

    target_query = "Identify the research gaps and limitations in existing research papers on deep learning"

    # =========================================================================
    # TEST 1: Research Gap Query on EMPTY workspace (Requirements 4 & 5)
    # =========================================================================
    print("="*70)
    print("TEST 1: Research Gap Query on EMPTY workspace")
    print(f"Query: \"{target_query}\"")
    print("="*70)
    msg1 = ChatMessage(session_id=sess_empty.id, role="user", content=target_query)
    db.add(msg1)
    db.commit()

    res1 = supervisor_agent.run(
        db=db,
        workspace_id=empty_workspace.id,
        session_id=sess_empty.id,
        query=target_query,
        user_msg_id=msg1.id,
    )
    print(res1[:600])
    print("...\n")

    assert "Research Gap Identification" in res1, "FAIL: Tool selected was not Research Gap Identification!"
    assert "No research papers found in this workspace" in res1 or "No papers found" in res1, "FAIL: Should alert user about empty workspace!"
    assert "upload" in res1.lower() or "import" in res1.lower(), "FAIL: Should prompt user to upload/import papers!"
    print(">>> PASS: Empty workspace correctly triggers prompt to upload/import without generating fake research gaps!\n")

    # =========================================================================
    # TEST 2: Research Gap Query on POPULATED workspace (Requirements 3 & 4)
    # =========================================================================
    print("="*70)
    print("TEST 2: Research Gap Query on POPULATED workspace")
    print(f"Query: \"{target_query}\"")
    print("="*70)
    msg2 = ChatMessage(session_id=sess_pop.id, role="user", content=target_query)
    db.add(msg2)
    db.commit()

    res2 = supervisor_agent.run(
        db=db,
        workspace_id=pop_workspace.id,
        session_id=sess_pop.id,
        query=target_query,
        user_msg_id=msg2.id,
    )
    print(res2[:600])
    print("...\n")

    assert "Research Gap Identification" in res2, "FAIL: Tool selected was not Research Gap Identification!"
    assert ("Attention Is All You Need" in res2 or "Deep Residual Learning" in res2 or "Analyzed workspace literature" in res2), "FAIL: Must analyze workspace papers!"
    print(">>> PASS: Populated workspace invokes Research Gap Identification and analyzes workspace papers!\n")

    # =========================================================================
    # TEST 3: Academic Paper Search Tool (Requirement 6)
    # =========================================================================
    print("="*70)
    print("TEST 3: Academic Paper Search Query")
    query_search = "Search for recent papers on Graph Neural Networks for drug discovery"
    print(f"Query: \"{query_search}\"")
    print("="*70)
    msg3 = ChatMessage(session_id=sess_pop.id, role="user", content=query_search)
    db.add(msg3)
    db.commit()

    res3 = supervisor_agent.run(
        db=db,
        workspace_id=pop_workspace.id,
        session_id=sess_pop.id,
        query=query_search,
        user_msg_id=msg3.id,
    )
    print(res3[:600])
    print("...\n")

    assert "Academic Paper Search" in res3, "FAIL: Academic Paper Search tool not selected!"
    print(">>> PASS: Search query correctly selects and invokes Academic Paper Search tool!\n")

    # =========================================================================
    # TEST 4: Paper Summarization Tool (Requirement 6)
    # =========================================================================
    print("="*70)
    print("TEST 4: Paper Summarization Query")
    query_sum = "Summarize the key contributions and methodology of the Attention paper"
    print(f"Query: \"{query_sum}\"")
    print("="*70)
    msg4 = ChatMessage(session_id=sess_pop.id, role="user", content=query_sum)
    db.add(msg4)
    db.commit()

    res4 = supervisor_agent.run(
        db=db,
        workspace_id=pop_workspace.id,
        session_id=sess_pop.id,
        query=query_sum,
        user_msg_id=msg4.id,
    )
    print(res4[:600])
    print("...\n")

    assert "Paper Summarization" in res4, "FAIL: Paper Summarization tool not selected!"
    print(">>> PASS: Summarization query correctly selects and invokes Paper Summarization tool!\n")

    # =========================================================================
    # TEST 5: Paper Comparison Tool (Requirement 6)
    # =========================================================================
    print("="*70)
    print("TEST 5: Paper Comparison Query")
    query_comp = "Compare the models and datasets of these papers side by side"
    print(f"Query: \"{query_comp}\"")
    print("="*70)
    msg5 = ChatMessage(session_id=sess_pop.id, role="user", content=query_comp)
    db.add(msg5)
    db.commit()

    res5 = supervisor_agent.run(
        db=db,
        workspace_id=pop_workspace.id,
        session_id=sess_pop.id,
        query=query_comp,
        user_msg_id=msg5.id,
    )
    print(res5[:600])
    print("...\n")

    assert "Paper Comparison" in res5, "FAIL: Paper Comparison tool not selected!"
    print(">>> PASS: Comparison query correctly selects and invokes Paper Comparison tool!\n")

    # =========================================================================
    # TEST 6: Literature Review Tool (Requirement 6)
    # =========================================================================
    print("="*70)
    print("TEST 6: Literature Review Query")
    query_lit = "Conduct a comprehensive literature review of the collected literature"
    print(f"Query: \"{query_lit}\"")
    print("="*70)
    msg6 = ChatMessage(session_id=sess_pop.id, role="user", content=query_lit)
    db.add(msg6)
    db.commit()

    res6 = supervisor_agent.run(
        db=db,
        workspace_id=pop_workspace.id,
        session_id=sess_pop.id,
        query=query_lit,
        user_msg_id=msg6.id,
    )
    print(res6[:600])
    print("...\n")

    assert "Literature Review" in res6, "FAIL: Literature Review tool not selected!"
    print(">>> PASS: Literature review query correctly selects and invokes Literature Review tool!\n")

    print("="*70)
    print("ALL 6 SUPERVISOR AGENT REQUIREMENTS VERIFIED AND PASSED SUCCESSFULLY!")
    print("="*70)

finally:
    db.close()
