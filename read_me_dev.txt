Only one Admin and multiple Agents exist
agent_restricted has been deprecate - a boolean value in Village is used to restrict access to the Agent when it is set to TRUE


# NOTE:
# Multi-agent support is introduced with agent_id ownership model.


SYSTEM OVERVIEW
- prepaid cable system
- payments collected in cash
- no invoices / no postpaid

CORE ASSUMPTION
- currently MULTIPLE agent system

WHY agent_id
- Multiple agents  → ownership certainty - one agent per village

ACCESS LOGIC
- agent sees customers ONLY where:
    village.agent_id = User.id 

ADMIN POWERS
- admin bypasses restriction
