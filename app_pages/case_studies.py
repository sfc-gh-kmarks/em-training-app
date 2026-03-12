import streamlit as st

CASE_STUDIES = [
    {
        "id": 1,
        "title": "The Silent JIRA on a Strategic Account",
        "archetype": "Urgency detection & engineering engagement failure",
        "case": "01270332",
        "customer": "DTCC (The Depository Trust & Clearing Corporation)",
        "account_tier": "Strategic (Awareness Period)",
        "severity": "SEV-2",
        "severity_color": "orange",
        "jira": "SNOW-3128548",
        "duration": "~18 hours at intake",
        "situation": """The customer's failover group (`ARIQAP_DFG`) began failing replication with error 003973. The secondary database contained streams referencing base tables from a shared database. The customer had performed a failover the prior day and was now stuck: unable to replicate forward or fail back without risking data loss.""",
        "intake_findings": [
            "JIRA SNOW-3128548 was filed but had **no assignee** 2+ hours after creation.",
            "The customer had **explicitly rejected** the proposed solution (failback) due to data loss concerns in the west region.",
            "Engineering was listed as \"involved\" but was **not actively engaged**.",
            "The case was approaching the 24-hour SEV-2 notification threshold.",
            "DTCC is a strategic account in an awareness period -- heightening churn and reputational risk.",
        ],
        "risk_signals": [
            ("Unassigned JIRA on active SEV-2", "Engineering Engagement", "CRITICAL"),
            ("Strategic account in awareness period", "Churn Risk", "CRITICAL"),
            ("Customer rejected proposed fix", "Perception Gap", "HIGH"),
            ("DR capabilities completely blocked", "Business Impact", "HIGH"),
            ("24hr+ duration approaching thresholds", "Timeline", "IMPORTANT"),
        ],
        "decision_points": [
            ("Escalate the JIRA immediately", "An unassigned JIRA on a strategic account is never acceptable. Contact the engineering area lead (Replication) directly."),
            ("Reframe the solution", "The customer rejected failback. Explore alternatives (e.g., force-replicate streams, drop and recreate streams on secondary)."),
            ("Consider formal escalation", "Given the account tier, awareness period, and blocked DR, this case warranted escalation even though it hadn't been formally escalated yet."),
            ("Set internal urgency", "Notify the Account Team and CSM so they can manage the customer relationship in parallel."),
        ],
        "lessons": [
            "**Always validate JIRA assignment**, not just JIRA existence. A filed-but-unassigned JIRA gives a false sense of progress.",
            "**Account tier and relationship status amplify every risk signal.** A SEV-2 on a strategic account in an awareness period has the impact profile of a SEV-1.",
            "**When a customer rejects a fix, the EM must pivot**, not push. Propose alternatives or escalate for engineering creativity.",
        ],
        "core_skill": "Urgency detection & internal advocacy",
        "key_takeaway": "Always validate engineering engagement is real, not just filed.",
    },
    {
        "id": 2,
        "title": "The Infrastructure-Side Surprise",
        "archetype": "Distinguishing customer-side vs. Snowflake-side root cause",
        "case": "01277754",
        "customer": "BlackRock",
        "account_tier": "Enterprise",
        "severity": "S1 (later downgraded to S2)",
        "severity_color": "red",
        "jira": "SNOW-3176023 (PatchCritical)",
        "duration": "Active",
        "situation": """The customer was attempting to create an Azure Private Endpoint for a Snowflake internal stage in the Azure West US 2 region. The operation failed with error `RemotePrivateLinkServiceSubscriptionNotRegistered`. The customer confirmed their own Azure subscription was properly registered and had successfully created private endpoints for the same client in Azure East and Azure West regions -- only West US 2 failed.""",
        "intake_findings": [
            "The error pointed to Snowflake's Azure subscription (`2ac35ed2-...`) not having the `Microsoft.Network` resource provider registered.",
            "The customer had **already proven** this was not on their side by showing success in other regions.",
            "The JIRA was filed at PatchCritical priority, indicating engineering recognized the severity.",
            "The root cause was a **Snowflake infrastructure-side configuration gap** -- the resource provider registration was missing on Snowflake's subscription for that specific region.",
        ],
        "risk_signals": [
            ("Customer proved their side is clean", "Perception Gap", "HIGH"),
            ("Region-specific failure pattern", "Infrastructure", "HIGH"),
            ("S1 severity on a major financial institution", "Business Impact", "CRITICAL"),
            ("Issue blocks private connectivity setup", "Security/Compliance", "HIGH"),
        ],
        "decision_points": [
            ("Acknowledge the customer's troubleshooting early", "BlackRock had already done significant diagnostic work. Recognizing this builds trust and avoids wasting their time re-running tests."),
            ("Shift focus to Snowflake-side investigation", "The region-specific failure pattern (works in East and West, fails in West US 2) is a strong signal that the issue is on Snowflake's infrastructure side."),
            ("Validate the JIRA priority", "PatchCritical was appropriate. Confirm engineering has a timeline for the resource provider registration fix."),
            ("Assess severity appropriately", "The initial S1 was reasonable given blocked private connectivity for a financial institution. The later downgrade to S2 should be validated with the customer."),
        ],
        "lessons": [
            "**Region-specific failures almost always point to infrastructure-side configuration differences.** When something works in Region A but not Region B, the problem is rarely the customer.",
            "**Financial institutions have strict private connectivity requirements.** Blocked private endpoint creation can have compliance implications beyond just convenience.",
            "**Let the customer's own evidence guide your root cause hypothesis.** When a customer says \"it works everywhere else,\" believe them and investigate the delta.",
        ],
        "core_skill": "Root cause triangulation",
        "key_takeaway": "Region-specific failures = infrastructure-side. Trust the customer's evidence.",
    },
    {
        "id": 3,
        "title": "The Go-Live Performance Crisis",
        "archetype": "Performance escalation with architectural root cause",
        "case": "01272595",
        "customer": "84.51 LLC",
        "account_tier": "Enterprise",
        "severity": "SEV-2",
        "severity_color": "orange",
        "jira": "N/A (best-practice guidance)",
        "duration": "Active (Go-Live window)",
        "situation": """The customer was going live with a new application. Their primary warehouse (`INSIGHTS_OS_STRATUM_HEAVY_PRD_WH`, 4XL Gen2 with MAX_CLUSTER_COUNT=10) was experiencing severe query queuing. Users were unable to run queries in a timely manner during the launch window.""",
        "intake_findings": [
            "Long-running CTAS queries (1-2 hours each) were **holding cluster resources**, causing contention with shorter user-facing queries.",
            "This was **not** a cluster availability issue -- the warehouse had capacity, but heavy queries monopolized it.",
            "The root cause was **architectural**: mixing long-running ETL workloads with short interactive queries on the same warehouse.",
            "The customer was under **Go-Live pressure**, meaning the EM needed to balance urgency with a sustainable fix.",
        ],
        "risk_signals": [
            ("Go-Live deadline pressure", "Timeline", "CRITICAL"),
            ("User-facing impact during launch", "Business Impact", "CRITICAL"),
            ("Architectural root cause (not a quick fix)", "Technical Scope", "HIGH"),
            ("Customer may expect Snowflake to 'fix' queuing", "Perception Gap", "IMPORTANT"),
        ],
        "decision_points": [
            ("Set expectations immediately", "This is not a bug or platform issue. Frame this as a workload architecture discussion, not a defect investigation."),
            ("Propose the multi-warehouse pattern", "Guide the customer toward workload isolation: Light (2XL) for interactive, Medium (3XL) for mid-range, Heavy (4XL) for long-running CTAS/ETL."),
            ("Provide a short-term workaround", "While the customer builds their load balancer, suggest immediate manual routing of the heaviest queries to a dedicated warehouse."),
            ("Avoid over-engineering", "The customer doesn't need engineering involvement. This is a best-practice guidance scenario, not a bug fix."),
        ],
        "lessons": [
            "**Not every escalation needs engineering.** Some of the highest-impact EM work is guiding customers toward better architecture and Snowflake best practices.",
            "**Go-Live escalations require speed AND expectation management.** The customer needs to hear \"here's what you can do right now\" before \"here's the long-term plan.\"",
            "**Frame the root cause without blame.** Instead of \"your architecture causes queuing,\" say: \"Snowflake performs best when workloads are isolated by profile -- let's set that up.\"",
        ],
        "core_skill": "Consultative guidance & expectation setting",
        "key_takeaway": "Not every escalation is a bug. Best-practice guidance can be the highest-value action.",
    },
]

RISK_COLORS = {
    "CRITICAL": "red",
    "HIGH": "orange",
    "IMPORTANT": "blue",
}

st.title(":material/menu_book: EM Manual -- Case Studies")
st.caption("Section 5: Real Escalation Case Studies")
st.markdown("Three real escalation scenarios, each representing a distinct archetype an Escalation Manager will encounter.")

st.divider()

st.subheader(":material/compare_arrows: Archetype Summary")
summary_data = []
for cs in CASE_STUDIES:
    summary_data.append({
        "Archetype": cs["title"],
        "Core EM Skill": cs["core_skill"],
        "Key Takeaway": cs["key_takeaway"],
    })
st.table(summary_data)

st.divider()

for cs in CASE_STUDIES:
    with st.container(border=True):
        col_title, col_meta = st.columns([3, 1])
        with col_title:
            st.subheader(f"Case Study {cs['id']}: {cs['title']}")
            st.caption(cs["archetype"])
        with col_meta:
            st.badge(cs["severity"], color=cs["severity_color"])
            st.caption(f"Case {cs['case']}")
            st.caption(f"Customer: {cs['customer']}")

        tab_situation, tab_intake, tab_risks, tab_decisions, tab_lessons = st.tabs([
            ":material/description: Situation",
            ":material/search: Intake Findings",
            ":material/warning: Risk Signals",
            ":material/decision: EM Decision Points",
            ":material/lightbulb: Lessons Learned",
        ])

        with tab_situation:
            col_brief, col_details = st.columns([2, 1])
            with col_brief:
                st.markdown(cs["situation"])
            with col_details:
                st.markdown(f"**Account Tier:** {cs['account_tier']}")
                st.markdown(f"**JIRA:** {cs['jira']}")
                st.markdown(f"**Duration:** {cs['duration']}")

        with tab_intake:
            for finding in cs["intake_findings"]:
                st.markdown(f"- {finding}")

        with tab_risks:
            for signal, category, severity in cs["risk_signals"]:
                col_signal, col_cat, col_sev = st.columns([3, 2, 1])
                with col_signal:
                    st.markdown(signal)
                with col_cat:
                    st.caption(category)
                with col_sev:
                    st.badge(severity, color=RISK_COLORS.get(severity, "grey"))

        with tab_decisions:
            for i, (action, detail) in enumerate(cs["decision_points"], 1):
                with st.expander(f"**{i}. {action}**"):
                    st.markdown(detail)

        with tab_lessons:
            for lesson in cs["lessons"]:
                st.markdown(f"- {lesson}")

    st.markdown("")

st.divider()
st.caption("These case studies map to the Intake Checklist (Section 4). Use them as worked examples of the checklist in action.")
