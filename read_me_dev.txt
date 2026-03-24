Only one Admin and only one Agent exist
agent_restricted, a boolean value in Village is used to restrict access to the Agent when it is set to TRUE


# NOTE:
# Currently single-agent system.
# agent_restricted acts as "is_active_for_agent".
# If multi-agent support is introduced, replace with agent_id ownership model.


SYSTEM OVERVIEW
- prepaid cable system
- payments collected in cash
- no invoices / no postpaid

CORE ASSUMPTION
- currently SINGLE agent system

KEY DESIGN DECISIONS
- Village.agent_restricted:
    False → active for agent (can collect)
    True  → inactive / blocked

WHY NO agent_id
- only one agent → no ownership ambiguity
- boolean used as lightweight control instead

ACCESS LOGIC
- agent sees customers ONLY where:
    village.agent_restricted = False

ADMIN POWERS
- admin bypasses restriction

LIMITATION (IMPORTANT)
- does NOT support multi-agent isolation
- no ownership tracking

FUTURE TRIGGER
- if more agents added:
    → introduce Village.agent_id
    → convert boolean to secondary control

GOTCHA
- agent_restricted is NOT "security"
- it's operational enable/disable