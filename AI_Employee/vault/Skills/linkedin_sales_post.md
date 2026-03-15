# Skill: LinkedIn Sales Post Generator

## Description
This skill generates high-impact, sales-focused LinkedIn posts by reading the `Business_Goals.md` context and following the latest LinkedIn algorithm best practices (hook, value, CTA).

## System Instructions
1.  **Read Context**: Open and analyze `AI_Employee/vault/Business_Goals.md`.
2.  **Persona**: Act as a thought leader in the AI Workforce Automation space. Tone should be professional, innovative, and slightly provocative.
3.  **Content Strategy**:
    - **Hook**: Start with a bold claim or a common pain point.
    - **Body**: Explain the value of the "Autonomous FTE" system.
    - **CTA**: Ask for a comment or a DM for more information.
4.  **Format**: Save the output to `/Pending_Approval/LINKEDIN_POST_<DATE>.md`.

## Output Template
```markdown
---
type: linkedin_post
status: pending
source_skill: linkedin_sales_post
---

# Post Content
[Post text here]

# Hashtags
#AI #Automation #FutureOfWork #AutonomousFTE

# Suggested Image
[Description of an AI/Efficiency themed visual]
```

## Workflow Execution
1.  Verify `Business_Goals.md` exists.
2.  Generate 3 variations of the hook.
3.  Select the best variation and build the post.
4.  Write the file to `AI_Employee/vault/Pending_Approval/`.
