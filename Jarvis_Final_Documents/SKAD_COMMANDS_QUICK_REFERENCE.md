# SKAD COMMANDS QUICK REFERENCE FOR JARVIS DEVELOPMENT

## Installation
```bash
# One-time setup
cd "E:\Bionic AI\Jarvis AI 3"
npx skad-method install --directory . --modules skm --tools claude-code --yes

# Verify
/skad-help
```

---

## PHASE 1: REQUIREMENTS (Week 1)

### Product Brief
```bash
/product-brief
```
**Answers:** Problem, users, MVP, success metrics  
**Output:** Product brief document  
**Time:** 20-30 min  

### Create PRD
```bash
/create-prd
```
**Answers:** Personas, acceptance criteria, risks, NRF  
**Output:** Product Requirements Document  
**Time:** 30-45 min  

---

## PHASE 2: ARCHITECTURE (Week 1-2)

### Technical Architecture
```bash
/create-architecture
```
**Answers:** Tech stack, deployment, real-time strategy, AI models  
**Output:** Architecture decision document  
**Time:** 30-45 min  

---

## PHASE 3: PLANNING (Week 2-3)

### Epics & Stories
```bash
/create-epics-and-stories
```
**Answers:** How to break into 10 epics, 50+ stories, priorities  
**Output:** Story list with acceptance criteria, effort estimates  
**Time:** 45-60 min  

### Sprint Planning
```bash
/sprint-planning
```
**Answers:** Team size, sprint length, capacity, velocity  
**Output:** Sprint board (6 * 2-week sprints)  
**Time:** 20-30 min  

---

## PHASE 4: DEVELOPMENT (Weeks 3-10)

### For Each Story (repeat 50+ times)

#### 1. Create Story with Full Context
```bash
/create-story
```
**Answers:** Title, acceptance criteria, dependencies, edge cases, test strategy  
**Output:** Story card with full context  
**Time:** 10-15 min per story  

#### 2. Implement the Story
```bash
/dev-story
```
**Input:** Start implementing (write code, tests, validate)  
**SKAD Help:** Offers tips, suggests patterns, links to docs  
**Output:** Code committed, tests passing  
**Time:** Varies (4-16 hours depending on story size)  

#### 3. Code Review & Merge
```bash
/code-review
```
**Answers:** Tests passing? Standards met? Ready to merge?  
**Output:** Code reviewed, approved, merged to main  
**Time:** 30-60 min per story  

---

## ONGOING SUPPORT

### Daily Standup
```bash
/sprint-status
```
**Output:** Stories in progress, blockers, ETA  
**Time:** 5-10 min  

### Weekly Review
```bash
/sprint-review
```
**Output:** Retrospective, velocity, next steps  
**Time:** 15-20 min  

### Get Expert Help (Anytime)
```bash
/skad-help I'm blocked on [specific problem]
```
**Example:**
```bash
/skad-help I'm blocked on WebSocket latency. Our messages are taking 500ms. How should we debug?
```
**Output:** Architect/Developer agent provides guidance  
**Time:** 5-10 min  

---

## OPTIONAL: ADVANCED MODULES

### Test Architect (Enterprise Testing)
```bash
# Install separately
/tea-strategy          # Risk-based test planning
/tea-automation        # Test pattern generation
/tea-gates             # Release quality gates
```
**When:** Sprint 4-5 (before release)  

### SKAD Builder (Custom Agents)
```bash
/builder-create-agent      # Create custom agent template
/builder-create-workflow   # Create custom workflow template
```
**When:** End of development (for post-launch extensibility)  

---

## KEY ABBREVIATIONS

| Abbreviation | Meaning | Jarvis Context |
|--------------|---------|----------------|
| SKM | SKAD Method (core framework) | Primary module for Jarvis |
| TEA | Test Architect | Testing strategy + quality gates |
| BMB | SKAD Builder | For post-launch custom agents |
| PRD | Product Requirements Document | Defines Jarvis personas, features, risks |
| NRF | Non-Functional Requirements | Performance budgets, scalability |
| MVP | Minimum Viable Product | 13 agents + voice + real-time streaming |
| ETA | Estimated Time to Arrival | SKAD calculates burndown |
| QA | Quality Assurance (Quinn built-in agent) | Automated testing |

---

## SPRINT CADENCE (Every 2 Weeks)

```
Friday EOD: /sprint-review (retrospective)
Monday AM:  /sprint-planning (new sprint)
Daily:      /sprint-status (blocker check-in)
Per story:  /create-story → /dev-story → /code-review
```

---

## CRITICAL CHECKPOINT DATES

| Date | Milestone | SKAD Workflow |
|------|-----------|---------------|
| Week 1 end | Product brief + PRD + Architecture locked | `/product-brief` + `/create-prd` + `/create-architecture` |
| Week 2 end | Epics, stories, sprints ready | `/create-epics-and-stories` + `/sprint-planning` |
| Week 4 end | Sprint 1 complete (FastAPI core + 2 agents) | `/sprint-review` |
| Week 6 end | Sprint 2 complete (4 more agents) | `/sprint-review` |
| Week 7 end | Sprint 3 complete (EA + OA + streaming) | `/sprint-review` |
| Week 8 end | Sprint 4 complete (React frontend + Voice UI) | `/sprint-review` |
| Week 9 end | Sprint 5 complete (App registry + workflows + backtracking) | `/sprint-review` |
| Week 10 end | Sprint 6 complete (Bundling + testing + .exe ready) | `/sprint-review` |

---

## CONTACT SKAD SUPPORT IF

- Model latency exceeds 15s → Ask `/skad-help` for optimization tips
- Story blocked for >2h → Run `/skad-help [specific problem]`
- Velocity drops suddenly → Discuss in `/sprint-review`
- Need to pivot scope → Request `/create-prd` re-review
- Testing strategy unclear → Use `/tea-strategy` (Test Architect)

---

## SUCCESS CRITERIA (By Week 10)

☑️ Product brief signed off  
☑️ PRD confirmed (personas, risks, NRF)  
☑️ Architecture ratified (tech stack, deployment)  
☑️ All 50+ stories completed + merged  
☑️ 6 sprints on track (velocity ≥16 points/week)  
☑️ Voice accuracy >90%  
☑️ WebSocket latency <200ms  
☑️ E2E tests passing (10 workflows)  
☑️ JARVIS_AI_Setup.exe built and tested  
☑️ Ready for preview/beta release  

---

**Ready?** Start with:
```bash
cd "E:\Bionic AI\Jarvis AI 3"
npx skad-method install --directory . --modules skm --tools claude-code --yes
/product-brief
```

