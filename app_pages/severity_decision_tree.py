import streamlit as st

STEPS = [
    {
        "id": "security",
        "question": "Is there a security incident or data breach?",
        "yes_result": "SEV-1",
        "yes_detail": "Engage Security Team immediately. Follow Security Case Protocol (Section 12).",
        "yes_color": "red",
        "no_next": "service_down",
    },
    {
        "id": "service_down",
        "question": "Is the service completely unavailable?",
        "yes_result": "SEV-1",
        "yes_detail": "Complete service outage. Response within 15 minutes, updates every 30 minutes.",
        "yes_color": "red",
        "no_next": "multi_customer",
    },
    {
        "id": "multi_customer",
        "question": "Are multiple customers affected?",
        "yes_result": None,
        "yes_detail": "Assess impact scope to determine SEV-1 or SEV-2.",
        "yes_color": None,
        "no_next": "critical_blocked",
        "branch": True,
        "branch_question": "What is the scope of impact?",
        "branch_options": {
            "Widespread / Platform-level": ("SEV-1", "red", "Platform-wide impact affecting many customers."),
            "Limited to a subset": ("SEV-2", "orange", "Major impact but contained to a customer segment."),
        },
    },
    {
        "id": "critical_blocked",
        "question": "Is critical business functionality blocked?",
        "yes_result": None,
        "yes_detail": "Determine workaround availability.",
        "yes_color": None,
        "no_next": "revenue",
        "branch": True,
        "branch_question": "Is there a workaround available?",
        "branch_options": {
            "No workaround": ("SEV-2", "orange", "Major functionality impaired with no workaround. Response within 1 hour."),
            "Workaround exists": ("SEV-3", "blue", "Functionality impaired but workaround available. Response within 4 hours."),
        },
    },
    {
        "id": "revenue",
        "question": "Is revenue directly impacted?",
        "yes_result": None,
        "yes_detail": "Assess revenue amount.",
        "yes_color": None,
        "no_next": "strategic",
        "branch": True,
        "branch_question": "What is the revenue impact level?",
        "branch_options": {
            "High (>$100K at risk)": ("SEV-2", "orange", "Significant revenue at risk. Escalate urgently."),
            "Moderate (<$100K)": ("SEV-3", "blue", "Revenue impacted but manageable. Daily updates."),
        },
    },
    {
        "id": "strategic",
        "question": "Is this affecting a Strategic account?",
        "yes_result": None,
        "yes_detail": "Bump the current severity by one level.",
        "yes_color": None,
        "no_next": "default",
        "bump": True,
    },
    {
        "id": "default",
        "question": None,
        "final": True,
        "result": "SEV-4",
        "result_color": "grey",
        "detail": "Minor issue, minimal business impact. Response within 24 hours, weekly updates.",
    },
]

STEP_INDEX = {s["id"]: i for i, s in enumerate(STEPS)}

SEV_INFO = {
    "SEV-1": {
        "color": "red",
        "label": "Critical",
        "response": "Immediate (within 15 minutes)",
        "updates": "Every 30 minutes",
        "exec_notify": "Required within 1 hour",
    },
    "SEV-2": {
        "color": "orange",
        "label": "High",
        "response": "Within 1 hour",
        "updates": "Every 2 hours",
        "exec_notify": "Required within 4 hours",
    },
    "SEV-3": {
        "color": "blue",
        "label": "Medium",
        "response": "Within 4 hours",
        "updates": "Daily",
        "exec_notify": "As needed",
    },
    "SEV-4": {
        "color": "grey",
        "label": "Low",
        "response": "Within 24 hours",
        "updates": "Weekly or upon status change",
        "exec_notify": "Not required",
    },
}


def reset_tree():
    st.session_state.tree_step = 0
    st.session_state.tree_answers = []
    st.session_state.tree_result = None
    st.session_state.tree_bumped = False


st.session_state.setdefault("tree_step", 0)
st.session_state.setdefault("tree_answers", [])
st.session_state.setdefault("tree_result", None)
st.session_state.setdefault("tree_bumped", False)

st.title(":material/account_tree: Severity Decision Tree")
st.caption("Walk through the escalation severity decision tree step by step.")
st.markdown("Answer each question based on the escalation you are triaging. The tree will guide you to the correct severity level.")

st.divider()

col_tree, col_ref = st.columns([3, 1])

with col_ref:
    st.markdown("##### Quick Reference")
    for sev, info in SEV_INFO.items():
        with st.expander(f"**{sev}** — {info['label']}"):
            st.markdown(f"**Response:** {info['response']}")
            st.markdown(f"**Updates:** {info['updates']}")
            st.markdown(f"**Exec notify:** {info['exec_notify']}")

    st.markdown("---")
    st.markdown("##### Decision Tree")
    st.code(
        "START\n"
        "├ Security/breach? → SEV-1\n"
        "├ Service down? → SEV-1\n"
        "├ Multi-customer? → SEV-1/2\n"
        "├ Critical blocked?\n"
        "│ ├ No workaround → SEV-2\n"
        "│ └ Workaround → SEV-3\n"
        "├ Revenue impact? → SEV-2/3\n"
        "├ Strategic acct? → Bump +1\n"
        "└ Default → SEV-4",
        language=None,
    )

with col_tree:
    if st.session_state.tree_answers:
        st.markdown("##### Path so far")
        for ans in st.session_state.tree_answers:
            icon = ":material/check_circle:" if ans["answer"] == "YES" else ":material/cancel:"
            st.markdown(f"{icon} **{ans['question']}** → {ans['answer']}")

    if st.session_state.tree_result:
        sev = st.session_state.tree_result
        info = SEV_INFO[sev]
        st.markdown("---")
        st.subheader(f"Result: {sev}")
        st.badge(f"{sev} — {info['label']}", color=info["color"])
        if st.session_state.tree_bumped:
            st.info("Severity was bumped by one level due to Strategic account status.", icon=":material/arrow_upward:")
        st.markdown(f"**Response time:** {info['response']}")
        st.markdown(f"**Update cadence:** {info['updates']}")
        st.markdown(f"**Executive notification:** {info['exec_notify']}")
        st.markdown("---")
        if st.button(":material/restart_alt: Start over", type="primary"):
            reset_tree()
            st.rerun()
    else:
        step_idx = st.session_state.tree_step
        step = STEPS[step_idx]

        if step.get("final"):
            st.session_state.tree_result = step["result"]
            st.rerun()
        else:
            st.markdown("---")
            progress_pct = step_idx / (len(STEPS) - 1)
            st.progress(progress_pct, text=f"Step {step_idx + 1} of {len(STEPS) - 1}")

            with st.container(border=True):
                st.subheader(step["question"])

                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button(":material/check: YES", key=f"yes_{step['id']}", use_container_width=True, type="primary"):
                        st.session_state.tree_answers.append({"question": step["question"], "answer": "YES"})

                        if step.get("bump"):
                            st.session_state.tree_bumped = True
                            st.session_state.tree_result = "SEV-3"
                            st.rerun()
                        elif step.get("branch"):
                            st.session_state.tree_step = step_idx
                            st.session_state[f"branch_{step['id']}"] = True
                            st.rerun()
                        elif step["yes_result"]:
                            st.session_state.tree_result = step["yes_result"]
                            st.rerun()

                with col_no:
                    if st.button(":material/close: NO", key=f"no_{step['id']}", use_container_width=True):
                        st.session_state.tree_answers.append({"question": step["question"], "answer": "NO"})
                        if step.get("bump"):
                            st.session_state.tree_result = "SEV-4"
                            st.rerun()
                        else:
                            next_idx = STEP_INDEX.get(step["no_next"], step_idx + 1)
                            st.session_state.tree_step = next_idx
                            st.rerun()

            if step.get("branch") and st.session_state.get(f"branch_{step['id']}"):
                with st.container(border=True):
                    st.markdown(f"**{step['branch_question']}**")
                    for opt_label, (sev, color, desc) in step["branch_options"].items():
                        if st.button(f"{opt_label} → {sev}", key=f"branch_{step['id']}_{opt_label}", use_container_width=True):
                            st.session_state.tree_answers.append({"question": step["branch_question"], "answer": opt_label})
                            st.session_state.tree_result = sev
                            st.rerun()

        if st.session_state.tree_answers and not st.session_state.tree_result:
            if st.button(":material/restart_alt: Start over"):
                reset_tree()
                st.rerun()
