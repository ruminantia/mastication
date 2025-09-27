# Masticator Classification Examples

This guide provides practical examples of how the classification system works with different types of input content.

## Quick Start with Classification

1. **Use the default configuration** (already set up for classification)
2. **Start Masticator:**
   ```bash
   ./run-docker.sh start
   ```
3. **Drop files in the `input/` directory** and check `output/` for JSON results

## Classification Categories

Masticator classifies content into 8 specific categories:

| Category | Description | Example Content |
|----------|-------------|-----------------|
| `notes_rants` | Personal thoughts, ideas, journal entries | "I had this great idea for a mobile app..." |
| `questions_research` | Questions seeking answers, research topics | "What's the best way to learn Python?" |
| `events_calendar` | Appointments, meetings, deadlines | "Meeting with team on Friday at 2pm" |
| `tasks_todos` | Action items, chores, work tasks | "Need to buy groceries and call plumber" |
| `personal_matters` | Health observations, dietary notes | "Sleep quality has been poor this week" |
| `news_stories` | Scraped web content, articles | "Breakthrough in quantum computing announced" |
| `emails` | Email drafts, correspondence | "Hi Team, following up on yesterday's discussion" |
| `misc` | Anything that doesn't fit other categories | Ambiguous or mixed content |

## Example Input Files and Their Classifications

### 1. Personal Notes & Ideas (notes_rants)

**Input file: `input/personal_idea.txt`**
```
I had this amazing idea for a mobile app that helps people track their daily water intake with gamification elements. Users could earn points for consistent hydration and compete with friends. The app could integrate with health APIs and send reminders.
```

**Expected classification output:**
```json
{
  "category": "notes_rants",
  "confidence": 0.88,
  "subcategory": "app_idea",
  "summary": "A concept for a gamified water tracking mobile app with social features and health integrations",
  "tags": ["mobile_app", "health", "gamification", "idea"]
}
```

### 2. Research Questions (questions_research)

**Input file: `input/research_question.md`**
```
What are the current best practices for implementing microservices architecture in Python? I'm particularly interested in:
- Service discovery patterns
- Inter-service communication
- Database per service vs shared database
- Deployment strategies for small teams
```

**Expected classification output:**
```json
{
  "category": "questions_research",
  "confidence": 0.95,
  "subcategory": "technical_research",
  "summary": "Questions about microservices architecture best practices in Python, covering service discovery, communication, databases, and deployment",
  "tags": ["microservices", "python", "architecture", "research"]
}
```

### 3. Calendar Events (events_calendar)

**Input file: `input/meeting_reminder.txt`**
```
Team sync meeting with engineering team
Date: Friday, March 15th, 2024
Time: 10:00 AM - 11:30 AM PST
Location: Conference Room B / Zoom
Agenda: Q2 planning, resource allocation, sprint review
Attendees: Sarah (PM), Mark (Lead), Jessica (QA), entire dev team
```

**Expected classification output:**
```json
{
  "category": "events_calendar",
  "confidence": 0.98,
  "subcategory": "team_meeting",
  "summary": "Scheduled team sync meeting for Q2 planning with engineering team, includes specific date, time, and agenda",
  "tags": ["meeting", "team", "planning", "calendar"]
}
```

### 4. Tasks & To-dos (tasks_todos)

**Input file: `input/daily_tasks.md`**
```
## Today's Tasks
- [ ] Review PR #245 for the authentication module
- [ ] Write unit tests for new user registration flow
- [ ] Update project documentation with API changes
- [ ] Schedule 1:1 with new team member
- [ ] Order team lunch for Friday

## Blocked Items
- Waiting on design assets for new feature
- Need approval for budget increase
```

**Expected classification output:**
```json
{
  "category": "tasks_todos",
  "confidence": 0.96,
  "subcategory": "work_tasks",
  "summary": "Daily task list including code review, testing, documentation, team coordination, and blocked items requiring follow-up",
  "tags": ["tasks", "work", "development", "blocked"]
}
```

### 5. Personal Health (personal_matters)

**Input file: `input/health_observation.txt`**
```
Sleep quality has been poor this week - waking up multiple times during the night. Energy levels low in afternoon. Started taking magnesium supplements yesterday. Need to track if this helps. Also noticing increased caffeine consumption to compensate.
```

**Expected classification output:**
```json
{
  "category": "personal_matters",
  "confidence": 0.91,
  "subcategory": "health_tracking",
  "summary": "Observations about poor sleep quality, low energy levels, and tracking the effects of magnesium supplements and caffeine intake",
  "tags": ["sleep", "health", "supplements", "tracking"]
}
```

### 6. News Articles (news_stories)

**Input file: `input/tech_article.md`**
```
# Breakthrough in Quantum Computing Announced

Researchers at Quantum Labs today announced a significant advancement in quantum error correction that could pave the way for more stable quantum computers. The new technique reduces error rates by 40% compared to previous methods.

The breakthrough involves a novel approach to quantum entanglement that maintains coherence for longer periods. This development could accelerate practical applications in drug discovery, materials science, and cryptography.

Dr. Elena Rodriguez, lead researcher, stated: "This brings us one step closer to fault-tolerant quantum computing that can solve real-world problems."
```

**Expected classification output:**
```json
{
  "category": "news_stories",
  "confidence": 0.94,
  "subcategory": "technology_news",
  "summary": "Article about quantum computing breakthrough involving improved error correction techniques that could enable practical applications",
  "tags": ["quantum_computing", "research", "technology", "science"]
}
```

### 7. Email Drafts (emails)

**Input file: `input/email_draft.txt`**
```
Subject: Follow-up: Project Timeline Discussion

Hi Team,

I wanted to follow up on our conversation yesterday regarding the Q3 project timeline. Based on the feedback received, I've updated the proposed schedule:

Key Changes:
- Moved feature A completion to Week 3 (was Week 2)
- Added buffer time for testing in Week 4
- Adjusted resource allocation for the integration phase

Please review the attached updated timeline and let me know if you have any concerns by EOD tomorrow.

Best regards,
Alex
```

**Expected classification output:**
```json
{
  "category": "emails",
  "confidence": 0.97,
  "subcategory": "project_communication",
  "summary": "Email draft following up on project timeline discussion with updated schedule and request for team feedback",
  "tags": ["email", "project", "timeline", "follow_up"]
}
```

### 8. Miscellaneous Content (misc)

**Input file: `input/ambiguous_content.txt`**
```
Not sure what this is about. Could be a reminder? Or maybe just a random thought. Need to figure this out later when I have more context.
```

**Expected classification output:**
```json
{
  "category": "misc",
  "confidence": 0.65,
  "subcategory": "ambiguous_content",
  "summary": "Unclear content that could be a reminder or random thought requiring additional context",
  "tags": ["ambiguous", "unclear", "needs_review"]
}
```

## Testing the Classification System

### Create Test Files

```bash
# Create example files for testing
echo "What's the best way to implement OAuth2 in a React application?" > input/test_question.txt
echo "Dentist appointment on Thursday at 3:00 PM" > input/test_event.txt
echo "Need to buy groceries: milk, eggs, bread, vegetables" > input/test_task.txt
```

### Monitor Output

```bash
# Watch for classification results
./run-docker.sh logs

# Or check the output directory
ls -la output/
cat output/*.json
```

### Expected Output Structure

All classification results follow this JSON schema:

```json
{
  "category": "string",           // Primary classification category
  "confidence": number,           // 0.0 to 1.0 confidence score
  "subcategory": "string|null",   // More specific classification
  "summary": "string",            // Brief content summary
  "tags": ["array", "of", "tags"] // Relevant keywords
}
```

## Customizing Classification

### Modify Categories

Edit `config/config.yaml` to add or modify categories:

```yaml
classification:
  categories:
    - "notes_rants"
    - "questions_research"
    - "events_calendar"
    - "tasks_todos"
    - "personal_matters"
    - "news_stories"
    - "emails"
    - "misc"
    - "your_custom_category"  # Add new categories here
```

### Adjust Classification Guidelines

Update the guidelines for better accuracy:

```yaml
guidelines:
  notes_rants: "Personal thoughts, creative ideas, journal entries, unstructured content"
  questions_research: "Questions seeking answers, research topics, knowledge gaps"
  # ... other categories
```

## Troubleshooting Classification

### Common Issues

**Low confidence scores:**
- Content may be ambiguous or too short
- Consider adding more context to your files
- Review and adjust category guidelines

**Incorrect categorization:**
- Check if your content clearly fits one category
- Consider adding more specific subcategories
- Adjust the temperature setting (lower = more consistent)

**JSON parsing errors:**
- Ensure the LLM is following the exact response format
- Use a model known for good structured output
- Check the logs for raw LLM responses

### Viewing Classification Logs

```bash
# View detailed logs
./run-docker.sh logs

# Check for classification-specific messages
docker compose logs masticator | grep -i classification
```

## Next Steps After Classification

Once files are classified, you can:

1. **Route to different processing pipelines** based on category
2. **Set priority levels** using confidence scores
3. **Automate workflows** using the tags and categories
4. **Track patterns** in your content types over time

The classification system provides a solid foundation for building more sophisticated content processing workflows tailored to your specific needs.