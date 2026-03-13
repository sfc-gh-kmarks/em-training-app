import streamlit as st

PRACTICE_CASES = [
    {
        "id": 1,
        "title": "The Private Endpoint Lockout",
        "expected_severity": "SEV-1",
        "expected_color": "red",
        "source_case": "01277754",
        "briefing": """A major financial institution reports they cannot create an Azure Private Endpoint for a Snowflake internal stage in the Azure West US 2 region. The operation fails with error `RemotePrivateLinkServiceSubscriptionNotRegistered`.

**Key facts:**
- The customer has **successfully created** private endpoints in Azure East and Azure West regions — only West US 2 fails.
- The customer confirmed their own Azure subscription is properly registered.
- The error points to **Snowflake's Azure subscription** not having the `Microsoft.Network` resource provider registered for that region.
- Private connectivity is a **compliance requirement** for this financial institution.
- Multiple teams across the organization are blocked from onboarding workloads in this region.""",
        "tree_path": [
            {"question": "Is there a security incident or data breach?", "answer": "NO", "explanation": "No breach, but private connectivity is a security/compliance requirement."},
            {"question": "Is the service completely unavailable?", "answer": "YES", "explanation": "Private endpoint creation is completely non-functional in this region. The customer cannot establish required secure connectivity — the service (private link provisioning in West US 2) is unavailable."},
        ],
        "result_explanation": "The service (private endpoint creation) is completely unavailable in a specific region due to a Snowflake infrastructure-side configuration gap. This is a SEV-1 because the customer has no workaround — they cannot use the region without private connectivity due to compliance requirements.",
        "key_lesson": "Region-specific failures where the service is fully non-functional constitute service unavailability even if other regions work.",
    },
    {
        "id": 2,
        "title": "The Replication Dead End",
        "expected_severity": "SEV-2",
        "expected_color": "orange",
        "source_case": "01270332",
        "briefing": """A strategic account (in their awareness period) reports their failover group is failing replication with error 003973. The secondary database contains streams referencing base tables from a shared database.

**Key facts:**
- The customer performed a failover the prior day and is now stuck: unable to replicate forward or fail back.
- Failback was proposed but the customer **rejected it** due to data loss risk in the west region.
- A JIRA was filed but has **no assignee** 2+ hours after creation.
- The issue has been ongoing for ~18 hours.
- This is a **Strategic account** in an awareness period.
- Disaster Recovery capabilities are completely blocked.""",
        "tree_path": [
            {"question": "Is there a security incident or data breach?", "answer": "NO", "explanation": "No security incident."},
            {"question": "Is the service completely unavailable?", "answer": "NO", "explanation": "Snowflake is operational; the specific failover/replication feature is failing."},
            {"question": "Are multiple customers affected?", "answer": "NO", "explanation": "Single customer issue."},
            {"question": "Is critical business functionality blocked?", "answer": "YES", "explanation": "Disaster Recovery (replication/failover) is completely blocked."},
            {"question": "Is there a workaround available?", "answer": "NO", "explanation": "Customer rejected failback (data loss risk). No alternative path exists. → **SEV-2**"},
        ],
        "result_explanation": "Critical business functionality (DR/replication) is blocked with no viable workaround. Note: Because this is a Strategic account in an awareness period, an EM should strongly consider bumping to SEV-1 behavior — the account tier amplifies every risk signal.",
        "key_lesson": "When a customer rejects the proposed workaround due to legitimate risk (data loss), treat it as 'no workaround available.'",
    },
    {
        "id": 3,
        "title": "The Iceberg Catalog Conflict",
        "expected_severity": "SEV-3",
        "expected_color": "blue",
        "source_case": "01283820",
        "briefing": """A strategic customer reports that setting `CATALOG_SYNC` at the database level for managed Iceberg tables is blocking the creation of unmanaged Iceberg tables.

**Key facts:**
- Customer set `CATALOG_SYNC = 'GBI_OPEN_CAT_INT'` at the database level.
- When creating **unmanaged** Iceberg tables (with a different catalog), they get an authorization error.
- Multiple jobs are failing in both non-prod and prod environments.
- The customer can **work around the issue** by unsetting CATALOG_SYNC at the database level or creating unmanaged tables in a separate database.
- The workaround degrades functionality (disables auto-sync for managed tables).
- Engineering has confirmed this is a product defect.""",
        "tree_path": [
            {"question": "Is there a security incident or data breach?", "answer": "NO", "explanation": "No security incident."},
            {"question": "Is the service completely unavailable?", "answer": "NO", "explanation": "Snowflake is operational; specific Iceberg table creation path is affected."},
            {"question": "Are multiple customers affected?", "answer": "NO", "explanation": "Single customer reporting (though the defect could affect others)."},
            {"question": "Is critical business functionality blocked?", "answer": "YES", "explanation": "Production jobs are failing — creating unmanaged Iceberg tables is part of their pipeline."},
            {"question": "Is there a workaround available?", "answer": "YES", "explanation": "Unset CATALOG_SYNC or use separate database/schema for unmanaged tables. → **SEV-3**"},
        ],
        "result_explanation": "Critical functionality is impaired but a workaround exists (schema/database separation or unsetting CATALOG_SYNC). The workaround degrades other functionality, which the EM should communicate clearly, but it does unblock the customer. Note: Strategic account status could justify bumping to SEV-2.",
        "key_lesson": "A workaround that degrades other features is still a workaround — but communicate the tradeoffs clearly and push for a permanent fix timeline.",
    },
    {
        "id": 4,
        "title": "The Disappearing Cortex Models",
        "expected_severity": "SEV-3",
        "expected_color": "blue",
        "source_case": "01285933",
        "briefing": """A customer reports that Cortex AI models are no longer available from the CLI. Claude models that worked on Thursday stopped working on Friday. The customer also set `CORTEX_MODELS_ALLOWLIST = 'openai-gpt-5'` on Sunday.

**Key facts:**
- Account is in AWS_US_EAST_1 with cross-region inference **disabled**.
- Diagnostics show "Available models: none."
- A platform-side deprecation removed Claude Sonnet 3.5 from the supported model list.
- The allowlist further restricted available models.
- This is blocking **POCs and active migration projects** — not production workloads.
- No revenue is directly at risk, but adoption pipeline is affected.
- The account is not a Strategic account.""",
        "tree_path": [
            {"question": "Is there a security incident or data breach?", "answer": "NO", "explanation": "No security incident."},
            {"question": "Is the service completely unavailable?", "answer": "NO", "explanation": "Snowflake platform is operational; Cortex CLI models are unavailable."},
            {"question": "Are multiple customers affected?", "answer": "NO", "explanation": "Single customer reporting (though the deprecation pattern could affect others)."},
            {"question": "Is critical business functionality blocked?", "answer": "NO", "explanation": "POCs and migrations are delayed, but no production systems are down."},
            {"question": "Is revenue directly impacted?", "answer": "NO", "explanation": "No current revenue at risk — these are pre-production POCs and migration projects."},
            {"question": "Is this affecting a Strategic account?", "answer": "NO", "explanation": "Not flagged as Strategic."},
        ],
        "result_explanation": "Following the tree strictly, this lands at SEV-4 (default). However, the EM should consider upgrading to SEV-3 because: (1) 'it worked and then stopped without customer action' creates a trust issue, and (2) blocked POCs represent future pipeline risk. The original case was filed as S4 and upgraded to S3.",
        "key_lesson": "The decision tree provides a starting point, not a final answer. EMs should use judgment to adjust severity when trust or adoption risk factors are present even without direct revenue or production impact.",
    },
    {
        "id": 5,
        "title": "The Confusing Error Message",
        "expected_severity": "SEV-4",
        "expected_color": "grey",
        "source_case": "N/A (composite)",
        "briefing": """A customer opens a case: *"The error message when I try to create a table with a reserved keyword name says 'unexpected COMMENT'. This is misleading — the real issue is the reserved word, not a comment."*

**Key facts:**
- The customer figured out the root cause themselves (reserved keyword usage).
- They are requesting that the error message be improved for clarity.
- No functionality is blocked — they renamed the column and moved on.
- No other customers have reported this.
- The customer explicitly states: "Not urgent, just feedback."
- The account is a Professional-tier customer.""",
        "tree_path": [
            {"question": "Is there a security incident or data breach?", "answer": "NO", "explanation": "No security incident."},
            {"question": "Is the service completely unavailable?", "answer": "NO", "explanation": "Service is fully available."},
            {"question": "Are multiple customers affected?", "answer": "NO", "explanation": "Single customer feedback."},
            {"question": "Is critical business functionality blocked?", "answer": "NO", "explanation": "Customer already resolved the issue themselves."},
            {"question": "Is revenue directly impacted?", "answer": "NO", "explanation": "No revenue impact."},
            {"question": "Is this affecting a Strategic account?", "answer": "NO", "explanation": "Professional tier, not Strategic."},
        ],
        "result_explanation": "This is a textbook SEV-4: a minor UX improvement request with no business impact. The customer self-resolved and explicitly flagged it as non-urgent. File a feature request JIRA, acknowledge the feedback, and provide weekly updates if the JIRA progresses.",
        "key_lesson": "Not every case that reaches an EM needs urgent treatment. Correctly identifying SEV-4 items preserves EM bandwidth for true emergencies.",
    },
]


def reset_case(case_id):
    key = f"practice_{case_id}"
    st.session_state[f"{key}_step"] = 0
    st.session_state[f"{key}_answers"] = []
    st.session_state[f"{key}_done"] = False
    st.session_state[f"{key}_revealed"] = False


st.title(":material/school: Severity Practice Cases")
st.caption("Apply the Severity Decision Tree to real escalation scenarios.")
st.markdown("For each case, read the briefing and answer the decision tree questions. After completing the tree, compare your path with the expected answer.")

st.divider()

for case in PRACTICE_CASES:
    key = f"practice_{case['id']}"
    st.session_state.setdefault(f"{key}_step", 0)
    st.session_state.setdefault(f"{key}_answers", [])
    st.session_state.setdefault(f"{key}_done", False)
    st.session_state.setdefault(f"{key}_revealed", False)

tabs = st.tabs([f"Case {c['id']}: {c['title']}" for c in PRACTICE_CASES])

for tab, case in zip(tabs, PRACTICE_CASES):
    with tab:
        key = f"practice_{case['id']}"
        step = st.session_state[f"{key}_step"]
        answers = st.session_state[f"{key}_answers"]
        done = st.session_state[f"{key}_done"]
        revealed = st.session_state[f"{key}_revealed"]

        col_info, col_sev = st.columns([4, 1])
        with col_info:
            st.subheader(case["title"])
        with col_sev:
            if done or revealed:
                st.badge(f"Expected: {case['expected_severity']}", color=case["expected_color"])
            if case["source_case"] != "N/A (composite)":
                st.caption(f"Source: Case {case['source_case']}")

        with st.container(border=True):
            st.markdown("**Briefing**")
            st.markdown(case["briefing"])

        if not done:
            if step < len(case["tree_path"]):
                tree_step = case["tree_path"][step]
                st.markdown(f"**Step {step + 1} of {len(case['tree_path'])}:** {tree_step['question']}")

                col_y, col_n = st.columns(2)
                with col_y:
                    if st.button(":material/check: YES", key=f"{key}_yes_{step}", use_container_width=True, type="primary"):
                        answers.append({"question": tree_step["question"], "user_answer": "YES", "expected": tree_step["answer"]})
                        st.session_state[f"{key}_answers"] = answers
                        st.session_state[f"{key}_step"] = step + 1
                        if step + 1 >= len(case["tree_path"]):
                            st.session_state[f"{key}_done"] = True
                        st.rerun()
                with col_n:
                    if st.button(":material/close: NO", key=f"{key}_no_{step}", use_container_width=True):
                        answers.append({"question": tree_step["question"], "user_answer": "NO", "expected": tree_step["answer"]})
                        st.session_state[f"{key}_answers"] = answers
                        st.session_state[f"{key}_step"] = step + 1
                        if step + 1 >= len(case["tree_path"]):
                            st.session_state[f"{key}_done"] = True
                        st.rerun()

            if answers:
                st.markdown("##### Your answers so far")
                for a in answers:
                    match = a["user_answer"] == a["expected"]
                    icon = ":material/check_circle:" if match else ":material/error:"
                    expected = a['expected']
                    result_text = '(correct)' if match else f'(expected: {expected})'
                    st.markdown(f"{icon} **{a['question']}** — You said: **{a['user_answer']}** {result_text}")

        if done:
            st.markdown("##### Your decision path")
            correct_count = 0
            for a in answers:
                match = a["user_answer"] == a["expected"]
                if match:
                    correct_count += 1
                icon = ":material/check_circle:" if match else ":material/error:"
                expected = a['expected']
                result_text = '(correct)' if match else f'(expected: {expected})'
                st.markdown(f"{icon} **{a['question']}** — You: **{a['user_answer']}** {result_text}")

            score_pct = correct_count / len(answers) if answers else 0
            score_color = "green" if score_pct == 1.0 else "orange" if score_pct >= 0.5 else "red"
            st.badge(f"{correct_count}/{len(answers)} correct", color=score_color)

            if not revealed:
                if st.button(":material/visibility: Reveal answer & explanation", key=f"{key}_reveal", type="primary"):
                    st.session_state[f"{key}_revealed"] = True
                    st.rerun()

        if revealed:
            with st.container(border=True):
                st.markdown(f"##### Expected result: {case['expected_severity']}")
                st.badge(case["expected_severity"], color=case["expected_color"])
                st.markdown("**Reasoning:**")
                st.markdown(case["result_explanation"])

                st.markdown("**Step-by-step rationale:**")
                for tree_step in case["tree_path"]:
                    with st.expander(f"{tree_step['question']} → {tree_step['answer']}"):
                        st.markdown(tree_step["explanation"])

                st.info(f"**Key lesson:** {case['key_lesson']}", icon=":material/lightbulb:")

        if done or revealed:
            if st.button(":material/restart_alt: Reset this case", key=f"{key}_reset"):
                reset_case(case["id"])
                st.rerun()
