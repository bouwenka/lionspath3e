// LionPath guided help: goal routes and page-specific visual walkthroughs.
// Kept separate from the main application so Help can evolve without touching core tools.


// ── HOW TO USE / TRAINING PAGE ───────────────────────────────────────────────
const TRAINING_ROUTE_STORAGE_KEY = 'lionpath_training_route_v2';
let trainingGuideOpener = null;
let activeTrainingTour = null;
let trainingRouteMemory = null;
let trainingRouteTransitionLocked = false;
let guidedFocusToken = 0;

const TRAINING_ROUTES = {
  unsure: {
    title:'Find a direction',
    time:'About 10–15 minutes',
    outcome:'Notice a direction, save one useful idea, and leave with a next step.',
    steps:[
      { page:'compass', label:'Career Compass', button:'Take Career Compass', target:'#nativeCompass', action:'Answer each question with what feels most true right now. At the end, add the report to My Plan.', done:'Move on when your result is saved and you can name one suggested direction.' },
      { page:'explorer', label:'Find a Related Course', button:'Find Related Courses', target:'#courseSearch', action:'Search one interest from your Compass result, open two course details, and save any useful course to My Plan.', done:'Move on when at least one course is saved for discussion.' },
      { page:'plan', label:'My Plan', button:'Finish My First Plan', target:'#planName', action:'Add one possible option, one next step, and one question. Then print or download the plan.', done:'You are finished when you have something specific to discuss with a trusted adult.' }
    ]
  },
  courses: {
    title:'Choose courses with a purpose',
    time:'About 8–12 minutes',
    outcome:'Build a short course list and one question to review with your counselor.',
    steps:[
      { page:'explorer', label:'Courses', button:'Search LCHS Courses', target:'#courseSearch', action:'Search an interest, use one or two filters, open at least two Details panels, and save two or three useful courses.', done:'Move on when your small course list is saved.' },
      { page:'plan', label:'My Plan', button:'Prepare My Course List', target:'#planName', action:'Review saved courses, add your strongest question, then print or download the plan.', done:'You are finished when your course list and question are ready to share.' }
    ]
  },
  college: {
    title:'Build an Enrollment plan',
    time:'About 10–15 minutes',
    outcome:'Compare education or training options, save possible courses, and prepare questions.',
    steps:[
      { page:'enrollment', label:'Enrollment', button:'Explore Enrollment', target:'#page-enrollment .program-grid', action:'Open the category that fits your goal: Dual Enrollment, AP, Honors, BRVGS, college preparation, or applications.', done:'Move on when you know which category you want to investigate.' },
      { page:'explorer', label:'Courses', button:'Compare Enrollment Courses', target:'#courseSearch', action:'Choose your grade, open course details, and save two possible courses to My Plan.', done:'Move on when you have a small course list.' },
      { page:'plan', label:'My Plan', button:'Finish My Enrollment Plan', target:'#planName', action:'Record possible schools or programs, one deadline or cost question, and one next step.', done:'You are finished when the plan is ready for a counselor or family conversation.' }
    ]
  },
  career: {
    title:'Connect school to a career',
    time:'About 10–15 minutes',
    outcome:'Choose a possible CTE pathway, save related courses, and identify one career-building action.',
    steps:[
      { page:'employment', label:'Employment', button:'Explore CTE Programs', target:'#page-employment .program-grid', action:'Open one CTE program and review its course sequence, credentials, work-based learning, and career information.', done:'Move on when you can name one program and one connected career.' },
      { page:'explorer', label:'Courses', button:'Find Employment Courses', target:'#courseSearch', action:'Choose Employment as the 3E connection and save one or two useful courses.', done:'Move on when your possible course sequence has started.' },
      { page:'plan', label:'My Plan', button:'Finish My Career Plan', target:'#planName', action:'Add a possible career, useful skills, course options, one next step, and one question.', done:'You are finished when you have a specific action to discuss with an adult.' }
    ]
  },
  military: {
    title:'Explore military service carefully',
    time:'About 10–15 minutes',
    outcome:'Compare service routes, connect school courses, and prepare questions to verify before any commitment.',
    steps:[
      { page:'enlistment', label:'Enlistment', button:'Compare Service Routes', target:'#page-enlistment .deep-grid, #page-enlistment .branch-strip', action:'Compare at least two entry routes, review Enlisted versus Officer, and read Before signing anything.', done:'Move on when you have one possible route and one question about the obligation or contract.' },
      { page:'explorer', label:'Connected Courses', button:'Find Connected Courses', target:'#courseSearch', action:'Choose Enlistment as the 3E connection or search JROTC, cybersecurity, health science, mechanics, or public safety. Save one useful course.', done:'Move on when one connected school course is saved.' },
      { page:'plan', label:'My Plan', button:'Finish My Research Plan', target:'#planName', action:'Record the routes or careers you are comparing, your questions, and one next step.', done:'You are finished when the plan is ready to review with family and school staff.' }
    ]
  },
  meeting: {
    title:'Prepare for a productive meeting',
    time:'About 10–15 minutes',
    outcome:'Organize your evidence, options, and strongest questions before the conversation.',
    steps:[
      { page:'evidence', label:'Evidence', button:'Build My Snapshot', target:'#evidenceGrade', action:'Check only what is currently true, review the readiness meters, and add one useful move to My Plan.', done:'Move on when your snapshot reflects your current situation.' },
      { page:'plan', label:'Draft My Plan', button:'Draft My Plan', target:'#planName', action:'Add your current interest, possible options, one next step, and the questions you already have. A rough draft is enough.', done:'Move on when the plan gives AI Coach useful context.' },
      { page:'coach', label:'Prepare Questions', button:'Prepare for the Conversation', target:'#page-coach .prompt-toolkit .prompt-card', action:'Choose Prepare for a counselor meeting, use your draft plan as context, and keep the three most useful questions.', done:'You are ready when you have three specific questions and your draft plan to bring.' }
    ]
  }
};

const TRAINING_TOURS = {
  home: {
    label:'Home walkthrough',
    frames:[
      { src:'assets/training/tours/home/home-01.webp', title:'1. Understand the three pathways', text:'Start with What is 3E? Enrollment covers education and training, Employment connects courses and credentials to work, and Enlistment supports careful military research. Watch the short overview if helpful. These are starting points, not boxes—you can explore or combine more than one pathway.', alt:'LionPath Home introduction showing the Enrollment, Employment, and Enlistment pathway summaries.', focus:{x:52,y:10,w:46,h:55} },
      { src:'assets/training/tours/home/home-02.webp', title:'2. Choose where to begin', text:'Under Explore. Compare. Plan., select Enrollment, Employment, or Enlistment when one pathway already interests you. Select Help Me Choose when you want the Career Compass personality and interest assessment to help you notice possible directions. You can always return and compare another pathway.', alt:'LionPath Home cards for Enrollment, Employment, Enlistment, and Help Me Choose.', focus:{x:51,y:28,w:47,h:24} },
      { src:'assets/training/tours/home/home-03.webp', title:'3. Follow the roadmap for your grade', text:'Find your current grade band in the Family conversation roadmap. Grades 6–8 notice interests, Grade 9 builds a foundation, Grades 10–11 test pathways, and Grade 12 confirms next steps. Use that checkpoint to decide what kind of action makes sense now.', alt:'LionPath Home family conversation roadmap organized by grade band.', focus:{x:1,y:6,w:98,h:48}, cueTop:true },
      { src:'assets/training/tours/home/home-03.webp', title:'4. Turn a question into a next step', text:'Choose one prompt from Ask your student and one from Ask the school. Write the most useful idea, unanswered question, or action in My Plan so it is ready for a counselor, teacher, or family conversation instead of being forgotten.', alt:'LionPath Home panels with questions for students, families, and school staff.', focus:{x:1,y:49,w:98,h:48}, cueTop:true }
    ]
  },
  compass: {
    label:'Career Compass walkthrough',
    frames:[
      { src:'assets/training/tours/compass/compass-01.webp', title:'1. Choose your grade', text:'Select Grade 9, 10, 11, or 12 so Career Compass loads questions written for your planning stage. Preview Sample Report is only a quick demonstration for students, families, or counselors; choose your actual grade when you want your own result.', alt:'Career Compass grade cards and Preview Sample Report option.', focus:{x:3,y:34,w:94,h:55}, cueTop:true },
      { src:'assets/training/tours/compass/compass-02.webp', title:'2. Follow the question progress', text:'The assessment contains 52 questions organized into Interests, Work Style, What Matters, Your Path, and Reflect. For rating questions, choose the answer that feels closest right now. Most single-choice questions advance automatically; use Back to revise an answer or Back to Grades to restart.', alt:'Career Compass rating question with progress, section labels, answer choices, and Back controls.', focus:{x:3,y:20,w:94,h:68}, cueTop:true },
      { src:'assets/training/tours/compass/compass-04-rank.webp', title:'3. Rank exactly three choices', text:'Some questions ask for a top three. Select three choices in the order that matters most; the circles become 1, 2, and 3. Select a choice again to remove it. The Next button becomes available only after exactly three choices are ranked.', alt:'Career Compass ranking question with three numbered choices and additional unselected options.', focus:{x:2,y:18,w:96,h:79}, cueTop:true },
      { src:'assets/training/tours/compass/compass-02.webp', title:'4. Complete every section and reflect', text:'Continue through all five sections rather than stopping after the interest questions. Scenario and either-or questions help reveal preferences, while the final reflection prompts let you explain what matters in your own words. Thoughtful reflection gives you better material for a counselor conversation; select See My Results when finished.', alt:'Career Compass question screen showing the five assessment sections and progress controls.', focus:{x:3,y:12,w:94,h:84}, cueTop:true },
      { src:'assets/training/tours/compass/compass-05-report-top.webp', title:'5. Read your student snapshot first', text:'Begin with the profile name and explanation, then check the top pathway chart, reminder, strengths, and areas to grow. Treat the result as a conversation starter—not a label, placement decision, or eligibility determination. Notice what feels accurate and what you want to question.', alt:'Career Compass student report with profile, pathway chart, strengths, and growth areas.', focus:{x:2,y:20,w:96,h:76} },
      { src:'assets/training/tours/compass/compass-06-patterns.webp', title:'6. Interpret the full pattern', text:'Review the Interest Profile, Work Style, What You Value Most, and 3E Pathway Blend together. A high bar means your answers leaned that way; it does not mean you must choose that path. Look for repeated themes you can test through classes, clubs, visits, or conversations.', alt:'Career Compass report charts for interests, work style, values, and 3E pathway blend.', focus:{x:2,y:7,w:96,h:89} },
      { src:'assets/training/tours/compass/compass-03.webp', title:'7. Explore clusters, courses, and next steps', text:'Use the suggested career clusters and Louisa course buttons to investigate real possibilities. Read Your Next Steps, Looking Ahead, and Reflect before deciding what to do next. Course buttons open details when a match is available, or help you search for the course in the Course Explorer.', alt:'Career Compass results with career clusters, course ideas, next steps, and reflection questions.', focus:{x:2,y:4,w:96,h:91}, cueTop:true },
      { src:'assets/training/tours/compass/compass-08-counselor.webp', title:'8. Switch to Counselor view', text:'Select Counselor view for a meeting-ready version of the report. It organizes pathway matches, conversation starters, course or program ideas, possible work-based learning, cautions, and suggested follow-ups so a counselor can help verify options and turn broad interests into a practical plan.', alt:'Career Compass counselor report view with pathway matches and follow-up guidance.', focus:{x:2,y:22,w:96,h:73} },
      { src:'assets/training/tours/compass/compass-09-actions.webp', title:'9. Save, share, and keep asking', text:'Select Add to My Plan to carry the assessment result, strengths, options, next steps, and questions into your plan. From My Plan, select Copy My Plan Prompt and paste it into AI Plan Review for follow-up questions. You can also Print / Save Report or Download PDF to share with a counselor or family member, or Take It Again later.', alt:'Career Compass report actions for printing, downloading, adding results to My Plan, and retaking the assessment.', focus:{x:2,y:54,w:96,h:42}, cueTop:true }
    ]
  },
  enrollment: {
    label:'Enrollment walkthrough',
    frames:[
      { src:'assets/training/tours/enrollment/enrollment-01.webp', title:'1. Start with the action staircase', text:'Name the education or training goal you are investigating, then check transcript and GPA questions, choose purposeful rigor, research cost and transfer rules, and build an application or deadline plan. AP, Dual Enrollment, admission, credit, and financial-aid details must be verified with your counselor or the institution.', alt:'Enrollment page introduction and action staircase for goals, preparation, cost, applications, and verification.', focus:{x:52,y:17,w:46,h:65} },
      { src:'assets/training/tours/enrollment/enrollment-02.webp', title:'2. Compare education and training routes', text:'Compare community college and transfer, four-year college, technical or trade training, and AP, Dual Enrollment, Honors, or BRVGS. Read both the opportunity and what must be verified: prerequisites, workload, cost, credit, transfer, application requirements, and fit.', alt:'Enrollment option cards comparing college, transfer, technical training, and advanced high-school coursework.', focus:{x:1,y:36,w:98,h:57} },
      { src:'assets/training/tours/enrollment/enrollment-04-questions.webp', title:'3. Prepare student and family questions', text:'Use the Student questions to think about learning environment, degree type, readiness, and deadlines. Use the Family questions to compare the full cost beyond tuition, location and support, financial aid, and details that need official confirmation. Save the questions that belong in My Plan.', alt:'Enrollment student and family question panels above the course explorer.', focus:{x:1,y:4,w:98,h:53} },
      { src:'assets/training/tours/enrollment/enrollment-03.webp', title:'4. Choose a course category', text:'In Enrollment course explorer, scan Dual Enrollment, AP, Honors or Weighted, BRVGS, core college-prep, and portfolio or application-building categories. Select a card or its gold plus to expand it. Show these in Course Search applies that category as a search starting point.', alt:'Enrollment course explorer with six expandable course categories and gold plus controls.', focus:{x:1,y:48,w:98,h:49}, cueTop:true },
      { src:'assets/training/tours/enrollment/enrollment-05-expanded.webp', title:'5. Read an expanded category', text:'An expanded category shows real course entries, grade and credit information, why the category helps, and the subject areas represented. Use Show these in Course Search to compare the full list, or Ask AI Coach about this category to copy a focused prompt for the Enrollment AI workspace.', alt:'Expanded Dual Enrollment category with course entries, planning guidance, subject areas, and search and AI actions.', focus:{x:2,y:24,w:96,h:73} },
      { src:'assets/training/tours/courses/courses-03.webp', title:'6. Open Course Details before saving', text:'Select Details on a course and review grade range, credits, suggested sequence, evidence or credentials, career signals, and the counselor action. Add to My Plan saves the course so it appears in your plan. Ask AI Coach copies a course-specific prompt; it does not send anything until you paste it into a coach.', alt:'Course Details panel with sequence, evidence, career signals, Add to My Plan, and Ask AI Coach actions.', focus:{x:1,y:1,w:76,h:90} },
      { src:'assets/training/tours/enrollment/enrollment-07-ai.webp', title:'7. Use the Enrollment AI Coach', text:'Choose a prompt starter that matches your question, select it to copy, paste it into the embedded workspace, and answer follow-up questions. Ask about fit, tradeoffs, and next steps, then verify GPA, eligibility, credit, transfer, cost, availability, and deadlines with school staff or the institution.', alt:'Enrollment AI Coach workspace beside Enrollment prompt starters and click, paste, confirm instructions.', focus:{x:1,y:5,w:98,h:90} },
      { src:'assets/training/tours/enrollment/enrollment-08-resources.webp', title:'8. Research with trusted resources', text:'Use the External launchpad for Virginia Wizard, College Scorecard, FAFSA, PVCC Dual Enrollment, Virginia transfer tools, College Board AP, Common App, and nearby college information. Resources open separately; compare current details and bring anything unclear back to your counselor.', alt:'Enrollment External launchpad with official college, financial aid, transfer, AP, and application resources.', focus:{x:1,y:5,w:98,h:90} },
      { src:'assets/training/tours/enrollment/enrollment-09-counselor.webp', title:'9. Prepare the counselor conversation', text:'Check the questions you want to bring to your counselor, including course readiness, application timing, cost, credit, and transfer questions. Then open My Plan or Find Courses. Bring your saved courses, important deadlines, cost questions, and anything that still needs verification to the meeting.', alt:'Enrollment counselor-question checklist and final planning area.', focus:{x:1,y:35,w:98,h:62}, cueTop:true }
    ]
  },
  employment: {
    label:'Employment walkthrough',
    frames:[
      { src:'assets/training/tours/employment/employment-04-overview.webp', title:'1. Start with the Employment staircase', text:'Choose a career or CTE program to investigate, check its course sequence and prerequisites, identify credentials or licenses, research the work itself, and look for experience such as work-based learning. The goal is a testable plan—not a promise that one class automatically leads to one job.', alt:'Employment page introduction and action staircase for programs, courses, credentials, research, and experience.', focus:{x:1,y:4,w:98,h:92} },
      { src:'assets/training/tours/employment/employment-05-options.webp', title:'2. Compare options and form better questions', text:'Review CTE completer planning, credentials and licenses, work-based learning, and career readiness. Use the Student and Family questions to ask about sequence, transportation, safety, schedule fit, starting wages, advancement, and what must be confirmed with a counselor or CTE teacher.', alt:'Employment option cards and student and family planning questions.', focus:{x:1,y:4,w:98,h:92} },
      { src:'assets/training/tours/employment/employment-01.webp', title:'3. Scan the CTE program explorer', text:'Scan every program card rather than stopping at the first row. Use the summary, course count, and evidence chips—such as CTE sequence, credential, Dual Enrollment, or Work-Based Learning—to shortlist one or two programs. The full CTE course guide is available from the explorer header.', alt:'Employment program explorer showing CTE program cards, course counts, and evidence chips.', focus:{x:1,y:12,w:98,h:84} },
      { src:'assets/training/tours/employment/employment-02.webp', title:'4. Open a program and read the pathway', text:'Select a program card or its gold plus. Compare Courses in this area, the sequence or pathway flow, credentials, and employment data. Open a second program when useful so you can compare the training path, job signals, and school courses before choosing what to investigate further.', alt:'Expanded Employment program showing courses, sequence, credentials, and career data.', focus:{x:2,y:19,w:96,h:62} },
      { src:'assets/training/tours/employment/employment-03.webp', title:'5. Open Course Details before deciding', text:'Select a gold course name or Details, then review grade range, credits, suggested sequence, evidence, credentials, career signals, and the counselor action. Add to My Plan saves the course. Ask AI Coach copies a course prompt that you can paste into the Employment AI workspace.', alt:'Employment Course Details with sequence, evidence, career signals, Add to My Plan, and Ask AI Coach actions.', focus:{x:1,y:1,w:76,h:90} },
      { src:'assets/training/tours/employment/employment-06-ai.webp', title:'6. Use an Employment prompt starter', text:'Choose a starter, select it to copy, paste it into the embedded AI workspace, and personalize only the details needed. Ask follow-up questions until you have a specific comparison or next step. Do not enter private records, and verify course, credential, wage, and work-based-learning information with current sources and LCHS staff.', alt:'Employment AI Coach workspace beside career and CTE prompt starters.', focus:{x:1,y:5,w:98,h:90} },
      { src:'assets/training/tours/employment/employment-07-resources.webp', title:'7. Verify with trusted outside sources', text:'Use the External launchpad to research current job duties, wages, growth, credentials, apprenticeships, and opportunities. O*NET, CareerOneStop, Virginia Works, and the other listed sources open separately. Compare more than one source and note the facts or questions you want to discuss.', alt:'Employment External launchpad with career, labor-market, credential, apprenticeship, and job-search resources.', focus:{x:1,y:5,w:98,h:90} },
      { src:'assets/training/tours/employment/employment-08-counselor.webp', title:'8. Bring the results into My Plan', text:'Select the counselor questions that matter to you, then use Open My Plan or Find Courses. Courses saved with Add to My Plan appear automatically; enter program findings, wage questions, experience ideas, and anything that still needs verification manually. The finished plan can be reviewed with AI and shared with a counselor or family member.', alt:'Employment resource links, counselor-question checklist, and final planning area.', focus:{x:1,y:32,w:98,h:65}, cueTop:true }
    ]
  },
  enlistment: {
    label:'Enlistment walkthrough',
    frames:[
      { src:'assets/training/tours/enlistment/enlistment-01.webp', title:'1. Start with the research staircase', text:'Begin with career interests, then compare routes, review ASVAB and AFQT information, use official sources, and write questions before any commitment. Ask about job guarantees, contract length, rank and pay, training, medical requirements, benefits, deployment expectations, and total service obligation.', alt:'Enlistment page introduction and research staircase covering interests, routes, testing, verification, and questions.', focus:{x:52,y:8,w:46,h:60} },
      { src:'assets/training/tours/enlistment/enlistment-02.webp', title:'2. Compare broad service options', text:'Review enlisted service after high school, Reserve or National Guard, ROTC and officer routes, and military career families beyond combat roles. Use the Student and Family questions below to compare fit, timeline, obligations, education, location, and what must be confirmed through official sources.', alt:'Enlistment overview cards comparing broad service options and questions to discuss.', focus:{x:1,y:45,w:98,h:52}, cueTop:true },
      { src:'assets/training/tours/enlistment/enlistment-04-entry.webp', title:'3. Compare all six entry routes', text:'Compare enlisted after high school, Reserve or National Guard, ROTC in college, a service academy or senior military college, college followed by Officer Candidate School, and specialized or direct-commission officer routes. Choose at least two routes and write down how their timing, education, eligibility, and obligation differ.', alt:'Military entry pathways section showing six routes into service.', focus:{x:1,y:3,w:98,h:94} },
      { src:'assets/training/tours/enlistment/enlistment-05-officer.webp', title:'4. Understand Enlisted versus Officer', text:'Use the comparison graphic and table to study entry timing, training, hands-on work, leadership responsibility, and education. Ask how starting rank and pay, job selection, promotion, and service obligation differ. Neither route is automatically better; the right questions depend on your goals and eligibility.', alt:'Enlisted versus Officer graphic and comparison table.', focus:{x:1,y:2,w:98,h:95} },
      { src:'assets/training/tours/enlistment/enlistment-06-branches.webp', title:'5. Open official branch snapshots', text:'Each branch card opens an official website. Compare career availability, training, location, daily work, service expectations, and eligibility rather than choosing by logo alone. Use the official links to verify claims from AI, social media, family stories, or recruiter conversations.', alt:'Official branch snapshot cards for the military services.', focus:{x:1,y:4,w:98,h:84} },
      { src:'assets/training/tours/enlistment/enlistment-07-careers.webp', title:'6. Match career families—not just combat roles', text:'Military careers include health, cyber, aviation, mechanics, engineering, logistics, public safety, communications, media, business, and many other families. Identify two that fit your interests, then connect them to LCHS courses and related civilian careers you could also explore.', alt:'Military career-family grid with health, cyber, aviation, engineering, logistics, public safety, and other fields.', focus:{x:1,y:2,w:98,h:95} },
      { src:'assets/training/tours/enlistment/enlistment-03.webp', title:'7. Verify before making a commitment', text:'Read Before signing anything and Start locally at LCHS. Confirm contract language, guaranteed-job wording, medical standards, deployment expectations, benefits, starting rank, bonuses, and the full obligation with official sources. Use JROTC, ASVAB exploration, counselors, and family conversations to learn without rushing a decision.', alt:'Enlistment page guidance for verifying commitments and starting locally at LCHS.', focus:{x:1,y:1,w:98,h:43}, cueTop:true },
      { src:'assets/training/tours/enlistment/enlistment-08-ai.webp', title:'8. Use the Enlistment AI Coach safely', text:'Select a prompt starter to copy, paste it into the embedded workspace, and add only a grade, broad interests, and the question you want to explore. Ask follow-ups and request comparisons, but never enter private records. Verify every important answer with trusted adults and official military or school sources.', alt:'Enlistment AI Coach workspace beside safe research prompt starters.', focus:{x:1,y:5,w:98,h:90} },
      { src:'assets/training/tours/enlistment/enlistment-09-courses.webp', title:'9. Connect interests to LCHS courses', text:'Review JROTC and other Enlistment-connected course cards. Open Details to check grade, credits, evidence, and sequence. Add to My Plan saves a possible course; Ask AI Coach copies a prompt. Saving a course shows interest—it does not register you or confirm military eligibility.', alt:'LCHS course connections with Details, Add to My Plan, and Ask AI Coach actions.', focus:{x:1,y:5,w:98,h:90} },
      { src:'assets/training/tours/enlistment/enlistment-10-counselor.webp', title:'10. Research, confirm, and save the plan', text:'Use the External launchpad for official branch, career, ASVAB, benefits, ROTC, academy, and Reserve or Guard research. Check the questions you want to bring to your counselor, then record routes, connected courses, unanswered contract questions, and one next step in My Plan for a trusted-adult conversation.', alt:'Enlistment official resources followed by counselor questions for routes, courses, ASVAB, guarantees, and comparison.', focus:{x:1,y:2,w:98,h:95} }
    ]
  },
  courses: {
    label:'Courses walkthrough',
    frames:[
      { src:'assets/training/tours/courses/courses-01.webp', title:'1. Search by what you know', text:'Type a course name, subject, career, credential, or interest into Search. You do not need to know the exact catalog title: words such as cybersecurity, nursing, welding, art, AP, or Dual Enrollment can give you a useful starting list.', alt:'Course-to-Pathway Explorer with the search field and course filters.', focus:{x:2,y:60,w:96,h:25}, cueTop:true },
      { src:'assets/training/tours/courses/courses-04-filtered.webp', title:'2. Narrow the results', text:'Combine the pathway, 3E connection, grade, and course-feature filters. Watch the result count change so you know how narrow the search has become. If a useful course disappears, remove one filter. Select Clear filters when you want a clean start.', alt:'Course Explorer showing a cybersecurity search with Employment and Grade 11 filters and three matching results.', focus:{x:2,y:48,w:96,h:43}, cueTop:true },
      { src:'assets/training/tours/courses/courses-02.webp', title:'3. Compare course cards', text:'Check each card’s pathway, grade range, credits, Why it matters, description, suggested next step, 3E connection, and evidence tags. Compare at least two cards before choosing. Details gives the full record; Add to My Plan saves immediately; Ask AI Coach copies a course-specific prompt.', alt:'Course result cards with pathway, grade, credits, evidence, Details, Add to My Plan, and Ask AI Coach actions.', focus:{x:1,y:4,w:98,h:92} },
      { src:'assets/training/tours/courses/courses-03.webp', title:'4. Open Details before choosing', text:'Review Course Info, Suggested Sequence, Evidence and Credentials, Career Signals, and the counselor action. Check prerequisites, grade, credits, and current availability with school staff. Add to My Plan saves the course; Ask AI Coach copies a prompt that you can paste into the coach after closing Details.', alt:'Course Details panel showing sequence, evidence, career signals, counselor action, and planning buttons.', focus:{x:1,y:1,w:76,h:90} },
      { src:'assets/training/tours/plan/plan-04-saved-course.webp', title:'5. Confirm where the saved course went', text:'After Add to My Plan, open My Plan and look under Courses I Added to My Plan. The saved card carries the pathway, grade, credits, evidence, and description with it. Use Remove for one course or Clear All Courses to reset the list. Saving interest is not the same as registering for the course.', alt:'My Plan showing a saved course card with pathway, grade, credits, evidence, Remove, and Clear All Courses.', focus:{x:2,y:24,w:40,h:48} }
    ]
  },
  coach: {
    label:'AI Coach walkthrough',
    frames:[
      { src:'assets/training/tours/coach/coach-01.webp', title:'1. Understand the workspace and privacy rules', text:'The live AI workspace is beside Prompt Starters. Use a first name or initial only, and never enter student IDs, passwords, addresses, medical details, or private records. AI Coach can help organize research and questions, but official school, college, employment, or military facts still need verification.', alt:'AI Coach page with the live workspace, prompt starters, and privacy guidance.', focus:{x:2,y:38,w:96,h:58} },
      { src:'assets/training/tours/coach/coach-02.webp', title:'2. Choose the right prompt starter', text:'Choose the card that matches your task: select a pathway, compare options, find courses, build a 30-day plan, research a career, or prepare for a counselor meeting. Starting with the closest task helps the coach ask more useful follow-up questions.', alt:'AI Coach workspace beside the list of prompt starter choices.', focus:{x:68,y:1,w:30,h:65} },
      { src:'assets/training/tours/coach/coach-02.webp', title:'3. Copy, personalize, and paste', text:'Select a prompt card to copy it—the card does not send anything automatically. If the workspace asks you to join or enter a name first, complete that visible setup. Then click inside the coach, paste the prompt, replace broad placeholders with only the details needed, and send it.', alt:'AI Coach join area beside a selected prompt and click, paste, ask instructions.', focus:{x:1,y:2,w:66,h:94} },
      { src:'assets/training/tours/coach/coach-01.webp', title:'4. Continue until the answer is usable', text:'Answer the coach’s follow-up questions, ask it to compare tradeoffs, request simpler explanations, or ask for a short list of next actions. Stop when you have something specific you can check or do—not just a broad description. Do not treat the response as an official decision.', alt:'AI Coach workspace used for an ongoing planning conversation.', focus:{x:2,y:38,w:64,h:58} },
      { src:'assets/training/tours/plan/plan-07-share.webp', title:'5. Verify and record the useful parts', text:'Select Build My Plan, then manually record the most useful question, comparison, or next step. Verify course rules, graduation requirements, deadlines, wages, eligibility, and military obligations with the correct official source. My Plan gives you a place to keep the verified result for later review.', alt:'My Plan fields and controls used to record questions, next steps, and an AI review prompt.', focus:{x:2,y:28,w:39,h:67} },
      { src:'assets/training/tours/coach/coach-03.webp', title:'6. Use Voice Coach safely', text:'Talk to a 3E Coach opens a voice conversation through an external service. Use it only in a quiet space, share no private information, and end the voice session when finished. Write any useful next step in My Plan and verify important facts exactly as you would with text AI Coach.', alt:'Voice Coach section with the quiet-space requirement and launch area.', focus:{x:2,y:38,w:96,h:58}, cueTop:true }
    ]
  },
  evidence: {
    label:'Evidence walkthrough',
    frames:[
      { src:'assets/training/tours/evidence/evidence-01.webp', title:'1. Choose the correct grade', text:'Open Grade level and choose Grade 9, 10, 11, or 12. LionPath loads the checklist for that planning stage, so a ninth grader is not judged against a senior checklist. The meters and diploma-seal signals remain empty until you choose a grade and mark current evidence.', alt:'Evidence page with grade selector, empty readiness meters, and diploma-seal signals.', focus:{x:1,y:5,w:98,h:50} },
      { src:'assets/training/tours/evidence/evidence-02.webp', title:'2. Check only what is true now', text:'Select each statement that is currently true; select it again to remove it. Work through every checklist group and avoid checking something merely because you plan to do it later. The selected count, three pathway meters, seals, and suggested moves update immediately.', alt:'Evidence checklist with current items selected and readiness results updated.', focus:{x:1,y:4,w:52,h:92}, cueTop:true },
      { src:'assets/training/tours/evidence/evidence-02.webp', title:'3. Read the 3E readiness meters', text:'Compare Enrollment, Employment, and Enlistment. Exploring, Building, and Strong summarize the evidence you selected; they are planning signals, not grades, rankings, or eligibility decisions. A lower meter identifies an area where one verified course, experience, or conversation might help.', alt:'Evidence page showing Enrollment, Employment, and Enlistment readiness meters beside the checklist.', focus:{x:53,y:4,w:45,h:43} },
      { src:'assets/training/tours/evidence/evidence-04-seals.webp', title:'4. Understand diploma-seal signals', text:'Review each Virginia diploma-seal signal and its requirement explanation. On Track, Within Reach, or a missing signal is only an informal planning view based on what you checked. A counselor must confirm official records, grades, scores, service, career evidence, and current state requirements.', alt:'Evidence page with varied Virginia diploma-seal signals and requirement explanations.', focus:{x:49,y:13,w:49,h:53} },
      { src:'assets/training/tours/evidence/evidence-03.webp', title:'5. Turn gaps into next moves', text:'Under Your next 3 moves, choose Add to My Plan to append an action to My Next Step. Or select Copy AI Coach Prompt, open AI Coach, and paste it to explore how to complete the move. Suggested moves change with your evidence, so choose one realistic action instead of trying to do all three at once.', alt:'Evidence next moves with Add to My Plan and Copy AI Coach Prompt actions.', focus:{x:42,y:4,w:56,h:66} },
      { src:'assets/training/tours/evidence/evidence-06-share.webp', title:'6. Download, share, or clear the snapshot', text:'Use Print / Save Snapshot or Download PDF to bring the current view to a counselor meeting or share it with a trusted adult. It is not an official school record. On a shared device, clear the snapshot or all saved data when finished, and keep a downloaded copy of anything you need later.', alt:'Evidence snapshot actions for printing, downloading, sharing, and clearing saved information.', focus:{x:1,y:52,w:98,h:45}, cueTop:true }
    ]
  },
  plan: {
    label:'My Plan walkthrough',
    frames:[
      { src:'assets/training/tours/plan/plan-01.webp', title:'1. Start safely', text:'Use only a first name or initial, choose your grade, and select your current 3E interest. Plan and Evidence entries are stored only in this browser and expire after 180 days without an update. Do not enter IDs, passwords, addresses, medical information, or private records.', alt:'My Plan basic information fields, privacy notice, and AI Plan Review workspace.', focus:{x:3,y:62,w:39,h:30} },
      { src:'assets/training/tours/plan/plan-04-saved-course.webp', title:'2. Review courses you saved', text:'Courses added from the Course Explorer or a pathway Course Details panel appear under Courses I Added to My Plan. Review the pathway, grade, credits, evidence, and description. Use Remove for one course or Clear All Courses to reset the list. Saving a course does not register you for it.', alt:'My Plan showing a saved course card with evidence, Remove, and Clear All Courses.', focus:{x:2,y:24,w:40,h:48} },
      { src:'assets/training/tours/plan/plan-02.webp', title:'3. Review imported Compass and Evidence clues', text:'Career Compass Add to My Plan can fill your pathway lean, strengths, options, next steps, and questions. An Evidence move is added to My Next Step. Read what was imported, edit anything that does not sound like you, and remove anything you do not want included before sharing the plan.', alt:'My Plan fields populated with Career Compass strengths, options, next steps, and questions.', focus:{x:3,y:42,w:38,h:54}, cueTop:true },
      { src:'assets/training/tours/plan/plan-02.webp', title:'4. Complete the rest of the plan', text:'Add Other Experiences, Skills or Strengths to Build, options you are considering, one realistic Next Step, and Questions You Want Help With. Enter findings from Enrollment, Employment, or Enlistment manually. A concise working draft is more useful than leaving the plan empty while waiting for a perfect answer.', alt:'My Plan form for experiences, strengths, options, next step, and questions.', focus:{x:3,y:30,w:38,h:66}, cueTop:true },
      { src:'assets/training/tours/plan/plan-07-share.webp', title:'5. Create the AI review prompt', text:'Select Copy My Plan Prompt, click inside AI Plan Review, paste, and send it after completing any visible join setup. The prompt carries the planning context you chose to enter. Ask about course fit, missing evidence, alternative pathways, questions to verify, or the smallest useful next step.', alt:'My Plan Copy My Plan Prompt control beside the AI Plan Review workspace.', focus:{x:2,y:69,w:39,h:14}, cueTop:true },
      { src:'assets/training/tours/plan/plan-01.webp', title:'6. Use AI feedback to improve the plan', text:'Ask follow-up questions until the feedback is specific and understandable. Verify official details with the correct counselor, teacher, college, employer, or military source, then manually copy only the useful conclusions back into your plan fields. AI Coach does not change your plan automatically.', alt:'My Plan editor beside the AI Plan Review workspace used for follow-up questions.', focus:{x:45,y:48,w:53,h:48} },
      { src:'assets/training/tours/plan/plan-07-share.webp', title:'7. Share the plan and finish safely', text:'Use Copy Plan Summary, Print My Plan, or Download PDF to bring or send the plan to a counselor, teacher, or family member. Clear Written Notes when you want to remove typed reflections but keep selected courses. Use Clear All Saved Data before leaving a shared device, and download anything you need to keep first.', alt:'My Plan actions for copying the AI prompt and summary, printing, downloading, and clearing saved information.', focus:{x:2,y:68,w:39,h:29}, cueTop:true }
    ]
  }
};

const TRAINING_TOUR_PAGE_KEYS = {
  home:'home',
  compass:'compass',
  enrollment:'enrollment',
  employment:'employment',
  enlistment:'enlistment',
  explorer:'courses',
  coach:'coach',
  evidence:'evidence',
  plan:'plan'
};

function normalizeTrainingRouteState(value) {
  const fallback = { goal:'', grade:'', completed:[], activeIndex:0, active:false };
  const parsed = value && typeof value === 'object' && !Array.isArray(value) ? value : null;
  if (!parsed || !TRAINING_ROUTES[parsed.goal]) return fallback;
  const route = TRAINING_ROUTES[parsed.goal];
  const completed = Array.isArray(parsed.completed)
    ? [...new Set(parsed.completed.filter(index => Number.isInteger(index) && index >= 0 && index < route.steps.length))]
    : [];
  const activeIndex = Number.isInteger(parsed.activeIndex)
    ? Math.max(0, Math.min(parsed.activeIndex, route.steps.length - 1))
    : 0;
  const grade = ['9','10','11','12'].includes(String(parsed.grade || '')) ? String(parsed.grade) : '';
  return { goal:parsed.goal, grade, completed, activeIndex, active:parsed.active === true };
}

function readTrainingRouteState() {
  if (trainingRouteMemory) return normalizeTrainingRouteState(trainingRouteMemory);
  try {
    const raw = localStorage.getItem(TRAINING_ROUTE_STORAGE_KEY);
    trainingRouteMemory = normalizeTrainingRouteState(raw ? JSON.parse(raw) : null);
  } catch(e) {
    trainingRouteMemory = normalizeTrainingRouteState(null);
  }
  return normalizeTrainingRouteState(trainingRouteMemory);
}

function saveTrainingRouteState(value) {
  trainingRouteMemory = normalizeTrainingRouteState(value);
  try { localStorage.setItem(TRAINING_ROUTE_STORAGE_KEY, JSON.stringify(trainingRouteMemory)); } catch(e) {}
  return normalizeTrainingRouteState(trainingRouteMemory);
}

function clearTrainingRouteState(showMessage=false) {
  trainingRouteMemory = normalizeTrainingRouteState(null);
  try { localStorage.removeItem(TRAINING_ROUTE_STORAGE_KEY); } catch(e) {}
  renderTrainingRoute();
  syncTrainingRouteBar(state.activePage);
  if (showMessage) showToast('Guided route cleared');
}

function renderTrainingRoute() {
  const routeState = readTrainingRouteState();
  const route = TRAINING_ROUTES[routeState.goal];
  const page = $('page-training');
  const result = $('trainingRouteResult');
  const grade = $('trainingGrade');
  page?.querySelectorAll('[data-training-goal]').forEach(button => {
    const selected = Boolean(route && button.dataset.trainingGoal === routeState.goal);
    button.classList.toggle('active', selected);
    button.setAttribute('aria-pressed', String(selected));
  });
  const pathwayGroup = page?.querySelector('[data-training-goal-group="pathway"]');
  const pathwaySelected = ['college','career','military'].includes(routeState.goal);
  pathwayGroup?.classList.toggle('active', pathwaySelected);
  pathwayGroup?.setAttribute('aria-pressed', String(pathwaySelected));
  if (grade && grade.value !== routeState.grade) grade.value = routeState.grade || '';
  if (!route || !result) {
    if (result) result.hidden = true;
    return;
  }

  result.hidden = false;
  const completeCount = routeState.completed.length;
  const gradeText = routeState.grade ? ` • Grade ${routeState.grade}` : '';
  const title = $('trainingRouteTitle');
  const summary = $('trainingRouteSummary');
  const steps = $('trainingRouteSteps');
  const current = $('trainingRouteCurrent');
  const progress = $('trainingRouteProgress');
  const progressValue = $('trainingRouteProgressValue');
  if (title) title.textContent = route.title;
  if (summary) {
    summary.innerHTML = `<strong>${escHtml(route.time)}</strong>${escHtml(gradeText)} • ${escHtml(route.outcome)}`;
  }
  if (progress) {
    progress.setAttribute('aria-valuemax', String(route.steps.length));
    progress.setAttribute('aria-valuenow', String(completeCount));
  }
  if (progressValue) progressValue.style.width = `${(completeCount / route.steps.length) * 100}%`;
  if (!steps || !current) return;
  steps.innerHTML = route.steps.map((step, index) => {
    const complete = routeState.completed.includes(index);
    const active = index === routeState.activeIndex;
    return `<button type="button" class="${complete ? 'complete' : ''} ${active ? 'current' : ''}" data-route-select-index="${index}" ${active ? 'aria-current="step"' : ''}>
      <span>${complete ? '✓' : index + 1}</span>${escHtml(step.label)}
    </button>`;
  }).join('');
  if (completeCount >= route.steps.length) {
    current.innerHTML = `<article class="training-flow-current training-flow-complete">
      <div>
        <span class="training-flow-current-kicker">Guide complete</span>
        <h4>You’re ready for your next conversation.</h4>
        <p>Your ideas, courses, or questions are ready to review in My Plan and discuss with someone you trust.</p>
      </div>
      <div class="training-flow-current-actions">
        <button type="button" class="btn primary" data-page="plan">Open My Plan</button>
        <button type="button" class="btn" data-change-training-goal>Choose another goal</button>
      </div>
    </article>`;
    return;
  }
  const activeStep = route.steps[routeState.activeIndex] || route.steps[0];
  const doneText = activeStep.done.replace(/^(Move on when|You are finished when|You are ready when)\s*/i, '');
  current.innerHTML = `<article class="training-flow-current">
    <div>
      <span class="training-flow-current-kicker">Step ${routeState.activeIndex + 1} of ${route.steps.length}</span>
      <h4>${escHtml(activeStep.label)}</h4>
      <p>${escHtml(activeStep.action)}</p>
      <p class="training-flow-ready"><strong>You’re ready when:</strong> ${escHtml(doneText)}</p>
      <p class="training-flow-ready"><strong>To continue:</strong> Return to Help and choose “I finished this step.”</p>
    </div>
    <div class="training-flow-current-actions">
      <button type="button" class="btn primary" data-guided-page="${escAttr(activeStep.page)}" data-route-index="${routeState.activeIndex}">${escHtml(activeStep.button)}</button>
      <button type="button" class="btn" data-route-tour="${escAttr(activeStep.page)}">Show me how</button>
      <button type="button" class="btn" data-route-done>I finished this step</button>
    </div>
  </article>`;
}

function applyTrainingGrade(gradeValue) {
  const grade = ['9','10','11','12'].includes(String(gradeValue || '')) ? String(gradeValue) : '';
  if (!grade) return;
  const courseGrade = $('courseGrade');
  if (courseGrade && courseGrade.value !== grade) {
    courseGrade.value = grade;
    if (state.activePage === 'explorer') renderCourses();
  }
  const evidenceState = normalizeEvidenceState();
  if (evidenceState.grade !== grade) {
    evidenceState.grade = grade;
    pruneEvidenceCheckedForGrade(evidenceState);
    renderEvidence();
  }
  const planGrade = $('planGrade');
  if (planGrade && planGrade.value !== grade) {
    planGrade.value = grade;
    updatePlanPromptPreview();
  }
}

function focusActivePageHeading() {
  const page = $('page-' + state.activePage);
  const target = page?.querySelector('h1,h2,h3') || $('mainContent');
  if (!target) return;
  if (!/^(A|BUTTON|INPUT|SELECT|TEXTAREA)$/.test(target.tagName) && !target.hasAttribute('tabindex')) target.setAttribute('tabindex', '-1');
  try { target.focus({ preventScroll:true }); } catch(e) {}
}

function focusGuidedTarget(step) {
  if (!step) return;
  const token = ++guidedFocusToken;
  window.requestAnimationFrame(() => window.requestAnimationFrame(() => {
    if (token !== guidedFocusToken) return;
    const page = $('page-' + step.page);
    if (!page || state.activePage !== step.page || !page.classList.contains('active')) return;
    const target = (step.target && page.querySelector(step.target)) || page.querySelector('h1,h2,h3,button,input,select');
    if (!target) return;
    const naturallyFocusable = /^(A|BUTTON|INPUT|SELECT|TEXTAREA)$/.test(target.tagName);
    if (!naturallyFocusable && !target.hasAttribute('tabindex')) target.setAttribute('tabindex', '-1');
    const reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    try { target.scrollIntoView({ behavior:reduceMotion ? 'auto' : 'smooth', block:'center' }); } catch(e) {}
    try { target.focus({ preventScroll:true }); } catch(e) {}
  }));
}

function goToTrainingRouteStep(index) {
  const routeState = readTrainingRouteState();
  const route = TRAINING_ROUTES[routeState.goal];
  if (!route) return;
  const nextIndex = Math.max(0, Math.min(Number(index) || 0, route.steps.length - 1));
  routeState.activeIndex = nextIndex;
  routeState.active = true;
  saveTrainingRouteState(routeState);
  renderTrainingRoute();
  const step = route.steps[nextIndex];
  applyTrainingGrade(routeState.grade);
  if (step.page === 'compass' && routeState.grade && nativeCompassModel?.state?.screen === 'grade') {
    nativeCompassModel.onPickGrade(Number(routeState.grade));
  }
  setPage(step.page, false, { scroll:false });
  if (step.page === 'explorer') renderCourses();
  syncTrainingRouteBar(step.page);
  focusGuidedTarget(step);
}

function showTrainingTourForPage(page) {
  const key = TRAINING_TOUR_PAGE_KEYS[page] || page;
  const config = TRAINING_TOURS[key];
  const dialog = $('trainingGuideDialog');
  const host = $('trainingOverlayTour');
  const title = $('trainingGuideDialogTitle');
  if (!config || !dialog || !host) return;
  trainingGuideOpener = document.activeElement;
  if (title) title.textContent = config.label.replace('walkthrough', 'page guide');
  const controller = mountTrainingTour(host, key);
  if (!controller) return;
  if (!dialog.open) {
    if (typeof dialog.showModal === 'function') dialog.showModal();
    else dialog.setAttribute('open', '');
  }
  host.classList.add('has-started');
  const reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!reduceMotion) playTrainingTour(controller);
  else host.querySelector('[data-tour-play]')?.focus({ preventScroll:true });
}

function closeTrainingGuide() {
  const dialog = $('trainingGuideDialog');
  pauseActiveTrainingTour();
  if (!dialog) return;
  if (typeof dialog.close === 'function' && dialog.open) dialog.close();
  else dialog.removeAttribute('open');
}

function finishTrainingRouteStep(markComplete=true) {
  if (trainingRouteTransitionLocked) return;
  trainingRouteTransitionLocked = true;
  const routeState = readTrainingRouteState();
  const route = TRAINING_ROUTES[routeState.goal];
  if (!route) {
    trainingRouteTransitionLocked = false;
    return;
  }
  const index = routeState.activeIndex;
  if (markComplete && !routeState.completed.includes(index)) routeState.completed.push(index);
  if (index < route.steps.length - 1) {
    routeState.activeIndex = index + 1;
    routeState.active = true;
    saveTrainingRouteState(routeState);
    renderTrainingRoute();
    trainingRouteTransitionLocked = false;
    syncTrainingRouteBar(state.activePage);
    showToast(`Step complete — next: ${route.steps[routeState.activeIndex].label}`);
    return;
  }
  routeState.active = false;
  saveTrainingRouteState(routeState);
  renderTrainingRoute();
  trainingRouteTransitionLocked = false;
  syncTrainingRouteBar(state.activePage);
  setPage('training', false, { scroll:false });
  window.requestAnimationFrame(() => {
    $('trainingRouteResult')?.scrollIntoView({ behavior:'smooth', block:'start' });
    $('trainingRouteTitle')?.focus({ preventScroll:true });
  });
  showToast(markComplete ? 'Guide complete — your plan is ready to share' : 'Guide finished');
}

function syncTrainingRouteBar() {
  const bar = $('trainingRouteBar');
  if (bar) bar.hidden = true;
  document.body.classList.remove('training-route-bar-visible');
  document.body.style.removeProperty('--training-route-bar-space');
}

function stopTrainingTour(controller) {
  if (!controller) return;
  if (controller.timer) window.clearTimeout(controller.timer);
  controller.timer = null;
  controller.playing = false;
  controller.host.classList.remove('playing');
  const playButton = controller.host.querySelector('[data-tour-play]');
  const finalFrame = controller.index >= controller.config.frames.length - 1;
  const reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (playButton) {
    playButton.textContent = reduceMotion
      ? (finalFrame ? '↻ Restart' : 'Next Frame')
      : (finalFrame ? '↻ Replay' : '▶ Play guide');
    playButton.setAttribute('aria-pressed', 'false');
  }
  if (activeTrainingTour === controller) activeTrainingTour = null;
}

function pauseActiveTrainingTour() {
  if (activeTrainingTour) stopTrainingTour(activeTrainingTour);
}

function renderTrainingTourFrame(controller, nextIndex, manual=false) {
  const frames = controller.config.frames;
  const index = Math.max(0, Math.min(nextIndex, frames.length - 1));
  const frame = frames[index];
  const previousIndex = controller.index;
  controller.index = index;
  const images = [...controller.host.querySelectorAll('[data-tour-image]')];
  const title = controller.host.querySelector('[data-tour-caption-title]');
  const text = controller.host.querySelector('[data-tour-caption-text]');
  const step = controller.host.querySelector('[data-tour-step]');
  const cue = controller.host.querySelector('[data-tour-cue]');
  const focus = controller.host.querySelector('[data-tour-focus]');
  const progress = controller.host.querySelector('[data-tour-progress]');
  const frameCount = controller.host.querySelector('[data-tour-frame-count]');
  const caption = controller.host.querySelector('[data-tour-caption]');
  const previous = controller.host.querySelector('[data-tour-prev]');
  const next = controller.host.querySelector('[data-tour-next]');
  if (caption) caption.setAttribute('aria-live', manual ? 'polite' : 'off');
  if (images.length >= 2) {
    if (previousIndex < 0) {
      images[0].src = frame.src;
      images[0].alt = frame.alt;
      images[0].classList.add('is-visible');
      images[1].classList.remove('is-visible');
      controller.activeLayer = 0;
    } else if (previousIndex !== index) {
      const nextLayer = controller.activeLayer === 0 ? 1 : 0;
      const currentImage = images[controller.activeLayer];
      const nextImage = images[nextLayer];
      nextImage.src = frame.src;
      nextImage.alt = frame.alt;
      window.requestAnimationFrame(() => {
        nextImage.classList.add('is-visible');
        currentImage.classList.remove('is-visible');
      });
      controller.activeLayer = nextLayer;
    }
  }
  if (title) title.textContent = frame.title;
  if (text) text.textContent = frame.text;
  if (step) step.textContent = `Step ${index + 1} of ${frames.length}`;
  if (cue) cue.textContent = `Look for: ${frame.cue || frame.title.replace(/^\d+\.\s*/, '')}`;
  if (cue) cue.classList.toggle('at-top', frame.cueTop === true);
  if (progress) progress.style.width = `${((index + 1) / frames.length) * 100}%`;
  if (frameCount) frameCount.textContent = `${index + 1} of ${frames.length}`;
  const focusBox = frame.focus || {x:2,y:2,w:96,h:96};
  if (focus && focusBox) {
    focus.style.left = `${focusBox.x}%`;
    focus.style.top = `${focusBox.y}%`;
    focus.style.width = `${focusBox.w}%`;
    focus.style.height = `${focusBox.h}%`;
  }
  if (previous) previous.disabled = index === 0;
  if (next) next.disabled = index === frames.length - 1;
  if (!controller.playing) stopTrainingTour(controller);
}

function playTrainingTour(controller) {
  const reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  controller.host.classList.add('has-started');
  if (reduceMotion) {
    const next = controller.index >= controller.config.frames.length - 1 ? 0 : controller.index + 1;
    renderTrainingTourFrame(controller, next, true);
    return;
  }
  if (controller.playing) {
    stopTrainingTour(controller);
    return;
  }
  if (activeTrainingTour && activeTrainingTour !== controller) stopTrainingTour(activeTrainingTour);
  if (controller.index >= controller.config.frames.length - 1) renderTrainingTourFrame(controller, 0, false);
  controller.playing = true;
  controller.host.classList.add('playing');
  const playButton = controller.host.querySelector('[data-tour-play]');
  if (playButton) {
    playButton.textContent = '❚❚ Pause';
    playButton.setAttribute('aria-pressed', 'true');
  }
  activeTrainingTour = controller;
  const advance = () => {
    if (!controller.playing) return;
    if (controller.index >= controller.config.frames.length - 1) {
      stopTrainingTour(controller);
      return;
    }
    renderTrainingTourFrame(controller, controller.index + 1, false);
    if (controller.index >= controller.config.frames.length - 1) {
      stopTrainingTour(controller);
      return;
    }
    controller.timer = window.setTimeout(advance, 11000);
  };
  controller.timer = window.setTimeout(advance, 11000);
}

function mountTrainingTour(host, key) {
  const reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const config = TRAINING_TOURS[key];
  if (!host || !config) return null;
  if (host._trainingTour) stopTrainingTour(host._trainingTour);
  host.dataset.trainingTour = key;
  host.setAttribute('role', 'region');
  host.setAttribute('aria-roledescription', 'carousel');
  host.setAttribute('aria-label', config.label);
  host.classList.remove('has-started','playing','changing');
  host.innerHTML = `<div class="training-tour-stage">
    <img class="training-tour-image is-visible" data-tour-image src="${escAttr(config.frames[0].src)}" alt="${escAttr(config.frames[0].alt)}" width="1200" height="824" loading="eager" decoding="async">
    <img class="training-tour-image" data-tour-image src="${escAttr(config.frames[1]?.src || config.frames[0].src)}" alt="" width="1200" height="824" loading="eager" decoding="async">
    <span class="training-tour-focus" data-tour-focus aria-hidden="true"></span>
    <span class="training-tour-step-pill" data-tour-step>Step 1 of ${config.frames.length}</span>
    <span class="training-tour-cue" data-tour-cue></span>
    <button type="button" class="training-tour-poster" data-tour-poster aria-label="${reduceMotion ? 'Open' : 'Play'} ${escAttr(config.label)}"><span>${reduceMotion ? 'Open guide' : '▶ Play ' + config.frames.length + '-step guide'}</span></button>
  </div>
  <div class="training-tour-progress" aria-hidden="true"><span data-tour-progress></span></div>
  <div class="training-tour-caption" data-tour-caption aria-live="off">
    <h4 data-tour-caption-title></h4>
    <p data-tour-caption-text></p>
  </div>
  <div class="training-tour-controls">
    <button type="button" class="btn small" data-tour-prev aria-label="Previous guide step">← Previous</button>
    <button type="button" class="btn small" data-tour-play aria-pressed="false">${reduceMotion ? 'Next Frame' : '▶ Play guide'}</button>
    <button type="button" class="btn small" data-tour-next aria-label="Next guide step">Next →</button>
    <span class="training-tour-frame-count" data-tour-frame-count aria-live="polite">1 of ${config.frames.length}</span>
  </div>`;
  const controller = { host, key, config, index:-1, activeLayer:0, timer:null, playing:false };
  host._trainingTour = controller;
  config.frames.forEach(frame => {
    const preload = new Image();
    preload.decoding = 'async';
    preload.src = frame.src;
    if (typeof preload.decode === 'function') preload.decode().catch(() => {});
  });
  renderTrainingTourFrame(controller, 0, false);
  host.querySelector('[data-tour-poster]')?.addEventListener('click', () => {
    host.classList.add('has-started');
    playTrainingTour(controller);
    host.querySelector('[data-tour-play]')?.focus({ preventScroll:true });
  });
  host.querySelector('[data-tour-play]')?.addEventListener('click', () => playTrainingTour(controller));
  host.querySelector('[data-tour-prev]')?.addEventListener('click', () => {
    stopTrainingTour(controller);
    host.classList.add('has-started');
    renderTrainingTourFrame(controller, controller.index - 1, true);
  });
  host.querySelector('[data-tour-next]')?.addEventListener('click', () => {
    stopTrainingTour(controller);
    host.classList.add('has-started');
    renderTrainingTourFrame(controller, controller.index + 1, true);
  });
  return controller;
}

function initTrainingTours() {
  const host = $('trainingOverlayTour');
  if (host && !host._trainingTour) mountTrainingTour(host, 'home');
}

function initTrainingGuidanceV2() {
  if (document.body.dataset.trainingGuidanceReady === 'true') return;
  document.body.dataset.trainingGuidanceReady = 'true';
  initTrainingTours();
  const page = $('page-training');
  const routeResult = $('trainingRouteResult');
  const grade = $('trainingGrade');
  const pathwayChoices = $('trainingPathwayChoices');
  const pathwayGroup = page?.querySelector('[data-training-goal-group="pathway"]');

  const chooseGoal = goal => {
    if (!TRAINING_ROUTES[goal]) return;
    const previous = readTrainingRouteState();
    const next = previous.goal === goal
      ? { ...previous, grade:grade?.value || previous.grade, active:true }
      : { goal, grade:grade?.value || '', completed:[], activeIndex:0, active:true };
    saveTrainingRouteState(next);
    applyTrainingGrade(next.grade);
    if (pathwayChoices) pathwayChoices.hidden = true;
    pathwayGroup?.setAttribute('aria-expanded', 'false');
    renderTrainingRoute();
    window.requestAnimationFrame(() => {
      const reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      routeResult?.scrollIntoView({ behavior:reduceMotion ? 'auto' : 'smooth', block:'start' });
    });
  };

  page?.querySelectorAll('[data-training-goal]').forEach(button => {
    button.addEventListener('click', () => {
      chooseGoal(button.dataset.trainingGoal);
    });
  });
  pathwayGroup?.addEventListener('click', () => {
    if (!pathwayChoices) return;
    const open = pathwayChoices.hidden;
    pathwayChoices.hidden = !open;
    pathwayGroup.setAttribute('aria-expanded', String(open));
    if (open) window.requestAnimationFrame(() => pathwayChoices.querySelector('button')?.focus({ preventScroll:true }));
  });

  grade?.addEventListener('change', () => {
    const routeState = readTrainingRouteState();
    if (!TRAINING_ROUTES[routeState.goal]) return;
    routeState.grade = grade.value;
    saveTrainingRouteState(routeState);
    applyTrainingGrade(routeState.grade);
    renderTrainingRoute();
  });

  routeResult?.addEventListener('click', ev => {
    const doneButton = ev.target.closest('[data-route-done]');
    if (doneButton) {
      ev.preventDefault();
      finishTrainingRouteStep(true);
      return;
    }
    const tourButton = ev.target.closest('[data-route-tour]');
    if (tourButton) {
      ev.preventDefault();
      showTrainingTourForPage(tourButton.dataset.routeTour);
      return;
    }
    const selectButton = ev.target.closest('[data-route-select-index]');
    if (selectButton) {
      ev.preventDefault();
      const routeState = readTrainingRouteState();
      routeState.activeIndex = Number(selectButton.dataset.routeSelectIndex);
      routeState.active = true;
      saveTrainingRouteState(routeState);
      renderTrainingRoute();
      return;
    }
    if (ev.target.closest('[data-change-training-goal]')) {
      ev.preventDefault();
      $('trainingGoalTitle')?.scrollIntoView({ behavior:'smooth', block:'start' });
      return;
    }
    const button = ev.target.closest('[data-guided-page]');
    if (!button) return;
    ev.preventDefault();
    goToTrainingRouteStep(Number(button.dataset.routeIndex));
  });

  $('trainingChangeGoal')?.addEventListener('click', () => {
    $('trainingGoalTitle')?.scrollIntoView({ behavior:'smooth', block:'start' });
  });
  $('trainingOpenPageGuides')?.addEventListener('click', () => {
    const guides = $('trainingPages');
    if (!guides) return;
    guides.open = true;
    window.requestAnimationFrame(() => guides.scrollIntoView({ behavior:'smooth', block:'start' }));
  });
  page?.querySelectorAll('[data-page-guide]').forEach(button => {
    button.addEventListener('click', () => showTrainingTourForPage(button.dataset.pageGuide));
  });

  $('trainingRouteGo')?.addEventListener('click', () => goToTrainingRouteStep(readTrainingRouteState().activeIndex));
  $('trainingRouteDone')?.addEventListener('click', () => finishTrainingRouteStep(true));
  $('trainingRouteWatch')?.addEventListener('click', () => {
    const routeState = readTrainingRouteState();
    const route = TRAINING_ROUTES[routeState.goal];
    const step = route?.steps[routeState.activeIndex];
    if (step) showTrainingTourForPage(step.page);
  });
  $('trainingRouteBarExit')?.addEventListener('click', () => {
    const routeState = readTrainingRouteState();
    routeState.active = false;
    saveTrainingRouteState(routeState);
    syncTrainingRouteBar(state.activePage);
    focusActivePageHeading();
    showToast('Guide paused — your place is saved');
  });

  const guideDialog = $('trainingGuideDialog');
  $('trainingGuideDialogClose')?.addEventListener('click', closeTrainingGuide);
  guideDialog?.addEventListener('click', ev => {
    if (ev.target === guideDialog) closeTrainingGuide();
  });
  guideDialog?.addEventListener('close', () => {
    pauseActiveTrainingTour();
    if (trainingGuideOpener && typeof trainingGuideOpener.focus === 'function') {
      trainingGuideOpener.focus({ preventScroll:true });
    }
    trainingGuideOpener = null;
  });
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) pauseActiveTrainingTour();
  });
  renderTrainingRoute();
  applyTrainingGrade(readTrainingRouteState().grade);
  syncTrainingRouteBar(state.activePage);
}


window.LionPathTraining = {
  clear: () => clearTrainingRouteState(false),
  pause: pauseActiveTrainingTour
};

document.addEventListener('DOMContentLoaded', () => {
  try { initTrainingGuidanceV2(); }
  catch (error) { console.error('LionPath Help failed to initialize:', error); }
});
