import streamlit as st
import json
from datetime import datetime

st.set_page_config(
    page_title="EM Training Assessment",
    page_icon=":material/school:",
    layout="wide",
)

SCENARIOS = [
    {
        "id": 1,
        "title": "The Disappearing Table",
        "case": "01287244",
        "severity": "Severity-1",
        "severity_color": "red",
        "category": "Data Sharing + Replication",
        "briefing": """You receive an S1 escalation at 3:15 PM. The subject line reads: *"Table dropping randomly from a share."*

**What you know:**
- A view (`AAMTDATAWAREHOUSE.BARRYS.ACTIVE_TOTAL_MEMBERSHIP`) keeps disappearing from data share `EAST_NVA_BARRYS_DATASHARE`
- Complex replication chain: Account `tha72227` -> `EAST_NVA` account -> Barry's Snowflake account (direct share)
- Customer has re-granted USAGE on database/schema and SELECT on table -- it keeps happening again
- This is a **reopened issue** -- previous case 01268455 was closed without resolution
- Customer states this is blocking a **$2M customer contract** and their CRO is pushing for immediate resolution
- The assigned CSE is in APAC timezone; it is currently afternoon in the US""",
        "decision_points": [
            {
                "id": "dp1",
                "label": "DP-1: Severity validation",
                "question": "Is S1 appropriate here? What factors confirm or challenge the severity level?",
                "points": 5,
                "answer": """**S1 is justified** (2 pts):
- Production blocker, revenue-impacting ($2M contract), CRO-level visibility, recurring unresolved issue

**Key amplifying factor** (2 pts):
- This is a *reopened* case -- the customer already went through one full support cycle without resolution. This amplifies urgency and churn risk.

**Timezone gap** (1 pt):
- APAC CSE means US business hours may not have active coverage without EM intervention.""",
            },
            {
                "id": "dp2",
                "label": "DP-2: Root cause hypothesis",
                "question": "Based on the briefing, what is your leading hypothesis for why the view keeps disappearing? What diagnostic would you request?",
                "points": 5,
                "answer": """**Leading hypothesis** (3 pts):
- `CREATE OR REPLACE` operations during replication recreate the view as a new object, causing share grants to be silently dropped.

**Diagnostic to request** (2 pts):
- Query history analysis on the replication target account to identify any `CREATE OR REPLACE` operations on the affected view
- Request account identifiers for source/target accounts and replication type/schedule""",
            },
            {
                "id": "dp3",
                "label": "DP-3: Risk signal identification",
                "question": "Identify at least 3 risk signals present in this scenario.",
                "points": 5,
                "answer": """**(1 pt each, max 5):**
- **Churn risk**: $2M contract dependency, CRO pressure, reopened unresolved case
- **Executive visibility**: CRO is personally pushing for resolution
- **Perception gap**: Customer believes GRANT operations should fix it; root cause is architectural
- **Recurring failure**: Previous case 01268455 closed without fix -- trust is eroded
- **Coverage gap**: APAC CSE with US-hours customer urgency""",
            },
            {
                "id": "dp4",
                "label": "DP-4: Immediate actions",
                "question": "List your first 3 actions in priority order.",
                "points": 5,
                "answer": """1. **Establish internal escalation channel** (Slack) and confirm 24/7 coverage across timezones (2 pts)
2. **Review prior case 01268455** to understand what was tried and why it was closed -- avoid re-asking the customer questions already answered (2 pts)
3. **Engage Engineering** for root cause on replication + share grant interaction; confirm JIRA exists and is assigned (1 pt)""",
            },
        ],
    },
    {
        "id": 2,
        "title": "The Vanishing Users",
        "case": "01286370",
        "severity": "Severity-1",
        "severity_color": "red",
        "category": "Account Replication / Failover",
        "briefing": """You receive an S1 at 7:20 AM. The customer reports: *"Yesterday, some of our service users were dropped in the EUS2_TST account. The APIs using service users are blocked."*

**What you know:**
- 167 users (34 service accounts + 133 human users) were dropped from account `EUS2_TST` on March 9 during a 7-second window (14:56:31 to 14:56:38 UTC)
- Customer checked query history but found nothing explaining the drops
- Service account APIs are **blocked** -- production impact
- The customer did not mention performing any failover or replication operations
- Account has a failover group configured with a secondary account `CUS_TST`""",
        "decision_points": [
            {
                "id": "dp1",
                "label": "DP-1: Initial triage",
                "question": "What is your first investigative action? What backend data would you request from the support engineer?",
                "points": 4,
                "answer": """**First action** (2 pts):
- Request backend investigation of the failover group operation history for the `EUS2_TST` account around the deletion timestamp.

**Backend data** (2 pts):
- Check `ACCOUNT_USAGE` and failover group refresh logs to see if a failover/refresh was triggered around 14:56 UTC on March 9.""",
            },
            {
                "id": "dp2",
                "label": "DP-2: Root cause reasoning",
                "question": "Given the 7-second deletion window and the existence of a failover group, what is your hypothesis?",
                "points": 4,
                "answer": """**Hypothesis** (2 pts):
- A failover group refresh synchronized `EUS2_TST` with a **stale** secondary account (`CUS_TST`), which had not been refreshed since December 22, 2025 -- nearly 3 months.

**Mechanism** (2 pts):
- The 167 dropped users were all created between December 2025 and February 2026 (after the last successful replication). When EUS2_TST refreshed from the stale CUS_TST, it synced to the December user list, dropping all newer users.""",
            },
            {
                "id": "dp3",
                "label": "DP-3: Recovery assessment",
                "question": "The customer asks: 'Can you UNDROP these users?' What is the correct answer, and what alternative do you provide?",
                "points": 4,
                "answer": """**Correct answer** (2 pts):
- **UNDROP USER is not supported** in Snowflake. Dropped users must be manually recreated.

**Alternative** (2 pts):
- Provide comprehensive user recreation scripts organized by category (service users first -- they're blocking APIs), including all role grants and authentication details extracted from backend logs.""",
            },
            {
                "id": "dp4",
                "label": "DP-4: Prevention guidance",
                "question": "What recommendations would you give to prevent this from recurring?",
                "points": 4,
                "answer": """**Monitoring** (2 pts):
- Monitor replication lag -- alert if secondary account falls behind by more than a defined threshold (e.g., 7 days).

**Process** (2 pts):
- Before executing any manual failover drill, verify the secondary account is current; document a "pre-failover checklist" for the customer.""",
            },
            {
                "id": "dp5",
                "label": "DP-5: Communication strategy",
                "question": "How do you frame the root cause to the customer, given this is 'expected behavior' but caused significant production impact?",
                "points": 4,
                "answer": """**Framing** (2 pts):
- "The failover operation worked as designed, but the gap between the last replication and the failover meant the secondary didn't have the latest user list. We want to help you prevent this in the future."

**Tone** (2 pts):
- Avoid blame language ("you triggered this"). Focus on *systemic prevention* rather than fault. Lead with the recovery plan (scripts) before explaining root cause.""",
            },
        ],
    },
    {
        "id": 3,
        "title": "The Iceberg Defect",
        "case": "01283820",
        "severity": "Severity-2",
        "severity_color": "orange",
        "category": "Iceberg Tables / Product Bug",
        "briefing": """A customer reports: *"Catalog sync set at the DB level is affecting unmanaged tables."*

**What you know:**
- Customer set `CATALOG_SYNC = 'GBI_OPEN_CAT_INT'` at the database level for managed Iceberg tables to auto-sync to Open Catalog
- When creating **unmanaged** Iceberg tables (with a *different* catalog), they get: `"Insufficient privilege to operate on integration 'GBI_OPEN_CAT_INT'"`
- Customer's position: "Snowflake should only check catalog sync when `catalog=Snowflake`, not for unmanaged tables"
- Multiple jobs are failing in **both non-prod and prod** environments
- This is a **strategic customer** with proactive escalation management""",
        "decision_points": [
            {
                "id": "dp1",
                "label": "DP-1: Bug or misconfiguration?",
                "question": "How do you determine whether this is expected behavior or a product defect? What is your assessment?",
                "points": 5,
                "answer": """**Assessment** (3 pts):
- This is a **product defect**: The CATALOG_SYNC authorization check should only apply to Snowflake-managed Iceberg tables, not unmanaged tables with different catalog specifications.

**Approach** (2 pts):
- Validate the customer's claim by reviewing the DDL (the CREATE ICEBERG TABLE specifies a *different* catalog than the DB-level CATALOG_SYNC), confirm with engineering that the authorization check on CATALOG_SYNC should be scoped only to managed tables.""",
            },
            {
                "id": "dp2",
                "label": "DP-2: Workaround strategy",
                "question": "What immediate workaround would you recommend while waiting for a fix?",
                "points": 5,
                "answer": """**Immediate** (2 pts):
- Unset CATALOG_SYNC at the database level as an emergency workaround.

**Better separation** (2 pts):
- Create unmanaged tables in a separate schema or database without CATALOG_SYNC, keeping CATALOG_SYNC enabled only where managed tables reside.

**Tradeoff** (1 pt):
- Communicate that the workaround disables auto-sync for managed tables, so customer must manually sync until the fix ships.""",
            },
            {
                "id": "dp3",
                "label": "DP-3: Engineering engagement",
                "question": "What information do you need to drive urgency with the engineering team? How do you frame the JIRA?",
                "points": 5,
                "answer": """**Information needed** (2 pts):
- Query ID of the failing DDL, exact error message, account locator, proof that the DDL specifies a different catalog.

**JIRA framing** (2 pts):
- Frame as **PatchCritical**: Production impact on strategic account, affecting multiple environments, workaround degrades existing functionality.

**Request** (1 pt):
- Specific release target and estimated rollout date for the customer's region.""",
            },
            {
                "id": "dp4",
                "label": "DP-4: Customer communication",
                "question": "The customer asks: 'When will this be fixed?' How do you respond when engineering hasn't yet committed to a timeline?",
                "points": 5,
                "answer": """**Response** (3 pts):
- Never promise a date you don't have. Say: "Engineering has confirmed this is a defect and a fix is being prioritized. I'm working to get a targeted release date and will update you as soon as I have it."

**Interim support** (2 pts):
- Confirm the workaround is in place and offer to help implement the schema-separation approach if the workaround is insufficient.""",
            },
        ],
    },
    {
        "id": 4,
        "title": "The Migration Deadline",
        "case": "01283862",
        "severity": "Severity-2",
        "severity_color": "orange",
        "category": "Connectivity / 3rd Party Integration",
        "briefing": """A customer reports: *"We are moving Saviynt to SaaS service. Some jobs succeed, some fail with 'JDBC driver internal error: Timeout waiting for the download of chunk #0.' We need OCSP configuration help. Migration cutover is planned for next week."*

**What you know:**
- Saviynt (IAM/governance tool) migration to SaaS -- cutover next week
- Intermittent job failures -- some succeed, some timeout
- Customer also asking about OCSP configuration
- The error references "chunk download" -- this is a result set retrieval error, not a query execution error
- You have not yet investigated query history""",
        "decision_points": [
            {
                "id": "dp1",
                "label": "DP-1: Where is the problem?",
                "question": "Is this a Snowflake-side issue or a client-side issue? How do you determine this quickly?",
                "points": 5,
                "answer": """**Determination method** (3 pts):
- Check query execution history for the Saviynt service account: If queries complete successfully on Snowflake's side (1-19 seconds, no server errors), the problem is **client-side**.

**Diagnosis** (2 pts):
- The "chunk download timeout" error occurs during result set retrieval from cloud storage (S3), not during query execution. This points to network connectivity between Saviynt SaaS and S3 stage endpoints.""",
            },
            {
                "id": "dp2",
                "label": "DP-2: OCSP assessment",
                "question": "The customer asks for OCSP configuration help. How do you handle this alongside the primary issue?",
                "points": 5,
                "answer": """**Verify first** (2 pts):
- Check OCSP configuration status (likely already FAIL_OPEN mode) -- don't assume it's misconfigured.

**Port access** (1 pt):
- Check if port 80 to OCSP hosts is accessible from the Saviynt SaaS environment.

**Prioritize** (2 pts):
- Treat OCSP as a *secondary* concern -- the timeout error is the primary blocker. Don't let the OCSP request distract from root cause triage.""",
            },
            {
                "id": "dp3",
                "label": "DP-3: Stakeholder management",
                "question": "With a cutover deadline next week, who needs to be in the room (on both sides)?",
                "points": 5,
                "answer": """**Customer side** (2 pts):
- Saviynt migration team, network/infra team (for firewall/proxy investigation), and the project manager owning the cutover deadline.

**Snowflake side** (2 pts):
- Account team (AE/CSM) for awareness of deadline risk, and potentially the Saviynt partner team if one exists.

**Format** (1 pt):
- Open a bridge call given the timeline pressure rather than async case updates.""",
            },
            {
                "id": "dp4",
                "label": "DP-4: Resolution path",
                "question": "If you confirm this is a client-side / network issue, what do you recommend?",
                "points": 5,
                "answer": """**Recommendations** (2 pts):
- Network connectivity check from Saviynt SaaS to S3 stage endpoints, JDBC driver version upgrade, firewall/proxy rule review.

**Key insight** (2 pts):
- Since the customer is migrating to *SaaS*, the network path has changed from on-prem to Saviynt's cloud -- old firewall rules may not apply, and new egress paths need to be validated.

**Ownership** (1 pt):
- Suggest the customer loop in Saviynt support directly -- this is ultimately a Saviynt network configuration issue.""",
            },
        ],
    },
    {
        "id": 5,
        "title": "It Worked Yesterday",
        "case": "01285933",
        "severity": "Severity-3",
        "severity_color": "blue",
        "category": "Cortex / Platform Change",
        "briefing": """A customer reports: *"We can't use Cortex models from CLI. We allowed GPT-5.2 via the allowlist, but it says 'not authorized or not available in your region.' Claude models that worked Thursday stopped working Friday."*

**What you know:**
- Account: CARGURUS in AWS_US_EAST_1
- Customer set `CORTEX_MODELS_ALLOWLIST = 'openai-gpt-5'` on Sunday
- Cross-region inference is **disabled** on the account
- Diagnostics show "Available models: none"
- Claude models worked on Thursday (03/06) but stopped Friday (03/07)
- Customer says this is delaying POCs and active migration projects
- Case filed as S4, but customer is requesting upgrade""",
        "decision_points": [
            {
                "id": "dp1",
                "label": "DP-1: Root cause analysis",
                "question": "What changed between Thursday and Friday to break Claude access? What is your hypothesis?",
                "points": 5,
                "answer": """**Platform change** (2 pts):
- A platform-side change removed Claude Sonnet 3.5 from the Cortex Code CLI's supported model list as part of a deprecation cycle (retirement: March 31, 2026).

**Mechanism** (2 pts):
- On Thursday, the CLI fell back to Claude Sonnet 3.5, which was available in-region without cross-region inference. On Friday, that model was removed from the supported list, leaving only Claude 4.x models which **require** cross-region inference.

**Compounding factor** (1 pt):
- The additional `CORTEX_MODELS_ALLOWLIST = 'openai-gpt-5'` set on Sunday further restricted available models to zero.""",
            },
            {
                "id": "dp2",
                "label": "DP-2: Severity assessment",
                "question": "The case was filed as S4. The customer wants an upgrade. What severity do you recommend and why?",
                "points": 5,
                "answer": """**Recommendation** (3 pts):
- Upgrade to **S3**: Not a production system outage (S1/S2), but it's blocking active POCs and migrations -- which has real business impact on adoption and pipeline.

**Trust factor** (2 pts):
- "It worked and then stopped without customer action" creates a trust issue regardless of severity. Acknowledge the disruption.""",
            },
            {
                "id": "dp3",
                "label": "DP-3: Resolution",
                "question": "What specific commands need to be run, and by whom?",
                "points": 5,
                "answer": """**Two commands needed, run by ACCOUNTADMIN** (2 pts):

1. `ALTER ACCOUNT SET CORTEX_ENABLED_CROSS_REGION = 'AWS_US';` (1 pt)
   - Enables cross-region inference

2. `ALTER ACCOUNT UNSET CORTEX_MODELS_ALLOWLIST;` (1 pt)
   - Removes the restrictive allowlist

**CLI update** (1 pt):
- Also recommend: `cortex update` to get the latest CLI version.""",
            },
            {
                "id": "dp4",
                "label": "DP-4: Proactive risk identification",
                "question": "What broader risk does this scenario represent for other customers?",
                "points": 5,
                "answer": """**Broader risk** (2 pts):
- Any customer in a region without local model deployment who has cross-region inference disabled will lose access when deprecated models are removed.

**Action** (2 pts):
- Flag to Product/PM that model deprecation without proactive customer notification creates support escalations. Recommend a deprecation notice email or in-CLI warning before removal.

**Pattern** (1 pt):
- This is a pattern risk, not just a one-off: other model retirements will cause the same issue.""",
            },
        ],
    },
]


def get_rating(score):
    if score >= 90:
        return "Expert", "green", "Ready for independent escalation management"
    elif score >= 75:
        return "Proficient", "blue", "Ready with occasional senior EM coaching"
    elif score >= 60:
        return "Developing", "orange", "Shadow 2-3 more live escalations before solo work"
    else:
        return "Needs Coaching", "red", "Pair with senior EM for all escalations; retake after 2 weeks"


st.session_state.setdefault("trainee_name", "")
st.session_state.setdefault("current_scenario", 0)
st.session_state.setdefault("responses", {})
st.session_state.setdefault("scores", {})
st.session_state.setdefault("submitted", {})
st.session_state.setdefault("show_answers", {})
st.session_state.setdefault("assessment_complete", False)

with st.sidebar:
    st.header(":material/school: EM Training")
    st.caption("Escalation Manager Simulation Assessment")

    st.session_state.setdefault("trainee_name_input", "")
    st.text_input("Trainee name", key="trainee_name_input")
    st.session_state.trainee_name = st.session_state.get("trainee_name_input", "")

    st.markdown("**Scenarios**")
    for i, s in enumerate(SCENARIOS):
        scenario_key = f"scenario_{s['id']}"
        is_submitted = st.session_state.submitted.get(scenario_key, False)
        score = st.session_state.scores.get(scenario_key, None)

        if is_submitted and score is not None:
            icon = ":material/check_circle:"
            label = f"{icon} {s['title']} ({score}/{sum(dp['points'] for dp in s['decision_points'])})"
        elif i == st.session_state.current_scenario:
            label = f":material/arrow_right: **{s['title']}**"
        else:
            label = f":material/radio_button_unchecked: {s['title']}"

        if st.button(label, key=f"nav_{i}", use_container_width=True):
            st.session_state.current_scenario = i

    total_possible = sum(sum(dp["points"] for dp in s["decision_points"]) for s in SCENARIOS)
    total_scored = sum(st.session_state.scores.get(f"scenario_{s['id']}", 0) for s in SCENARIOS)
    completed = sum(1 for s in SCENARIOS if st.session_state.submitted.get(f"scenario_{s['id']}", False))

    st.markdown(f"**Progress:** {completed}/5 completed")
    st.progress(completed / 5)

    if completed == 5:
        st.markdown(f"### Total: {total_scored}/{total_possible}")
        rating, color, guidance = get_rating(total_scored)
        st.badge(rating, color=color)
        st.caption(guidance)

scenario = SCENARIOS[st.session_state.current_scenario]
scenario_key = f"scenario_{scenario['id']}"
is_submitted = st.session_state.submitted.get(scenario_key, False)
answers_visible = st.session_state.show_answers.get(scenario_key, False)

col_header, col_badges = st.columns([3, 1])
with col_header:
    st.title(f"Scenario {scenario['id']}: {scenario['title']}")
with col_badges:
    st.badge(scenario["severity"], color=scenario["severity_color"])
    st.badge(scenario["category"], color="blue")
    st.caption(f"Case {scenario['case']}")

with st.container(border=True):
    st.subheader(":material/description: Briefing", divider="gray")
    st.markdown(scenario["briefing"])

st.subheader(":material/quiz: Decision Points")

if not is_submitted:
    st.info("Read the briefing above, then answer each decision point below. Click **Submit answers** when ready.", icon=":material/lightbulb:")

for dp in scenario["decision_points"]:
    dp_key = f"{scenario_key}_{dp['id']}"

    with st.container(border=True):
        st.markdown(f"**{dp['label']}** ({dp['points']} pts)")
        st.markdown(dp["question"])

        st.session_state.setdefault(f"response_{dp_key}", "")
        st.text_area(
            "Your response",
            key=f"response_{dp_key}",
            height=120,
            disabled=is_submitted,
            label_visibility="collapsed",
            placeholder="Type your answer here...",
        )
        st.session_state.responses[dp_key] = st.session_state.get(f"response_{dp_key}", "")

        if is_submitted:
            score_key = f"score_{dp_key}"
            with st.expander(":material/key: Answer key", expanded=answers_visible):
                st.markdown(dp["answer"])
                current_score = st.session_state.get(score_key, 0)
                new_score = st.slider(
                    f"Score (0-{dp['points']})",
                    0,
                    dp["points"],
                    current_score,
                    key=f"slider_{dp_key}",
                )
                st.session_state[score_key] = new_score

if not is_submitted:
    if st.button(":material/send: Submit answers", type="primary", use_container_width=True):
        has_response = any(
            st.session_state.get(f"response_{scenario_key}_{dp['id']}", "").strip()
            for dp in scenario["decision_points"]
        )
        if has_response:
            for dp in scenario["decision_points"]:
                dp_key = f"{scenario_key}_{dp['id']}"
                st.session_state.responses[dp_key] = st.session_state.get(f"response_{dp_key}", "")
            st.session_state.submitted[scenario_key] = True
            st.session_state.show_answers[scenario_key] = True
            for dp in scenario["decision_points"]:
                dp_key = f"{scenario_key}_{dp['id']}"
                st.session_state.setdefault(f"score_{dp_key}", 0)
            st.rerun()
        else:
            st.warning("Please answer at least one decision point before submitting.", icon=":material/warning:")
else:
    total_dp_score = sum(
        st.session_state.get(f"score_{scenario_key}_{dp['id']}", 0)
        for dp in scenario["decision_points"]
    )
    max_score = sum(dp["points"] for dp in scenario["decision_points"])
    st.session_state.scores[scenario_key] = total_dp_score

    col_score, col_nav = st.columns([1, 1])
    with col_score:
        st.metric(
            label=f"Scenario {scenario['id']} score",
            value=f"{total_dp_score} / {max_score}",
        )
    with col_nav:
        if st.session_state.current_scenario < len(SCENARIOS) - 1:
            if st.button(":material/arrow_forward: Next scenario", type="primary", use_container_width=True):
                st.session_state.current_scenario += 1
                st.rerun()

    all_submitted = all(
        st.session_state.submitted.get(f"scenario_{s['id']}", False)
        for s in SCENARIOS
    )
    if all_submitted:
        st.subheader(":material/emoji_events: Final results")

        total_scored = sum(
            st.session_state.scores.get(f"scenario_{s['id']}", 0)
            for s in SCENARIOS
        )
        total_possible = sum(
            sum(dp["points"] for dp in s["decision_points"])
            for s in SCENARIOS
        )
        rating, color, guidance = get_rating(total_scored)

        col_total, col_rating, col_guidance = st.columns(3)
        with col_total:
            st.metric("Total score", f"{total_scored} / {total_possible}")
        with col_rating:
            st.markdown("**Rating**")
            st.badge(rating, color=color)
        with col_guidance:
            st.markdown("**Next steps**")
            st.caption(guidance)

        results_data = []
        for s in SCENARIOS:
            s_key = f"scenario_{s['id']}"
            s_score = st.session_state.scores.get(s_key, 0)
            s_max = sum(dp["points"] for dp in s["decision_points"])
            results_data.append({
                "Scenario": f"{s['id']}. {s['title']}",
                "Category": s["category"],
                "Severity": s["severity"],
                "Score": f"{s_score}/{s_max}",
                "Pct": f"{int(s_score/s_max*100)}%",
            })

        st.table(results_data)

        trainee_display = st.session_state.trainee_name or "Anonymous"
        summary = {
            "trainee": trainee_display,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "total_score": total_scored,
            "total_possible": total_possible,
            "rating": rating,
            "scenarios": {},
        }
        for s in SCENARIOS:
            s_key = f"scenario_{s['id']}"
            s_data = {"score": st.session_state.scores.get(s_key, 0)}
            for dp in s["decision_points"]:
                dp_key = f"{s_key}_{dp['id']}"
                s_data[dp["id"]] = {
                    "response": st.session_state.responses.get(dp_key, ""),
                    "score": st.session_state.get(f"score_{dp_key}", 0),
                }
            summary["scenarios"][s["title"]] = s_data

        st.download_button(
            ":material/download: Download results (JSON)",
            data=json.dumps(summary, indent=2),
            file_name=f"em_training_{trainee_display}_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True,
        )
