from database import SessionLocal, engine, Base
from models import (
    Industry, Process, Role, System, Activity, Problem,
    AIOpportunity, FutureActivity, Transformation, Benefit,
)


def pct_drop(cur, fut):
    return round((cur - fut) / cur * 100, 1) if cur else 0.0


def pct_gain(cur, fut):
    return round((fut - cur) / cur * 100, 1) if cur else 0.0


def seed():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    industry = Industry(
        name="Healthcare — Hospital Operations",
        description="A multi-specialty hospital network exploring how AI, automation and emerging "
                     "technology (GenAI, computer vision, predictive ML, RPA, agentic AI) can redesign "
                     "core patient-facing and back-office processes.",
    )
    db.add(industry)
    db.flush()

    roles = {r.name: r for r in [
        Role(name="Front Desk Staff", type="human", description="Handles walk-in patients and manual verification."),
        Role(name="Registration Officer", type="human", description="Enters patient data into hospital systems."),
        Role(name="Care Coordinator", type="hybrid", description="Oversees patient flow, resolves exceptions AI escalates."),
        Role(name="AI Intake Assistant", type="ai", description="Conversational + computer-vision agent handling check-in."),
        Role(name="Claims Officer", type="human", description="Prepares and submits insurance claims."),
        Role(name="Billing Clerk", type="human", description="Collects billing documents."),
        Role(name="Compliance Auditor", type="human", description="Reviews claims for fraud/compliance."),
        Role(name="Claims Adjudicator", type="hybrid", description="Approves/denies claims, assisted by AI scoring."),
        Role(name="AI Claims Agent", type="ai", description="Automates document extraction, coding suggestions, fraud scoring."),
        Role(name="Physician", type="human", description="Diagnoses and prescribes treatment."),
        Role(name="AI Diagnostic Assistant", type="ai", description="Suggests differentials, flags risk from imaging/labs."),
        Role(name="Discharge Nurse", type="human", description="Coordinates discharge and follow-up."),
        Role(name="AI Follow-up Agent", type="ai", description="Automates follow-up scheduling and monitoring."),
    ]}
    db.add_all(roles.values())
    db.flush()

    systems = {s.name: s for s in [
        System(name="Legacy Hospital Management System (HMS)", category="legacy_it", description="30-year-old on-prem registration system."),
        System(name="Electronic Health Record (EHR)", category="legacy_it", description="Central patient record system."),
        System(name="AI Intake Bot", category="ai_platform", description="Voice/chat + OCR kiosk for self check-in."),
        System(name="Legacy Claims System", category="legacy_it", description="Claims entry and submission tool."),
        System(name="Payer Portal", category="integration", description="External insurer web portal."),
        System(name="AI Document Intelligence", category="ai_platform", description="Extracts & validates claim documents."),
        System(name="Fraud Detection Engine", category="ai_platform", description="Real-time anomaly scoring on claims."),
        System(name="AI Diagnostic Support", category="ai_platform", description="Clinical decision support using ML on labs/imaging."),
        System(name="AI Follow-up Platform", category="ai_platform", description="Automated scheduling & remote monitoring."),
    ]}
    db.add_all(systems.values())
    db.flush()

    processes = {}
    for i, (name, desc) in enumerate([
        ("Patient Registration & Intake",
         "Everything from a patient's arrival to being handed off to the clinical department."),
        ("Insurance Verification & Claims Processing",
         "From document collection to final reimbursement of an insurance claim."),
        ("Diagnosis, Consultation & Treatment Planning",
         "Clinical assessment and treatment plan creation."),
        ("Discharge & Follow-up Care",
         "Post-treatment discharge, instructions and follow-up monitoring."),
    ]):
        p = Process(industry_id=industry.id, name=name, description=desc, order_index=i)
        db.add(p)
        processes[name] = p
    db.flush()

    # ---------------------------------------------------------------
    # PROCESS 1: Patient Registration & Intake  (fully modeled)
    # ---------------------------------------------------------------
    p1 = processes["Patient Registration & Intake"]

    a1 = Activity(process_id=p1.id, seq=1, name="Walk-in & Queue Token", activity_type="manual",
                  role_id=roles["Front Desk Staff"].id, system_id=systems["Legacy Hospital Management System (HMS)"].id,
                  avg_time_minutes=5, error_rate_pct=2, description="Patient collects a paper token upon arrival.")
    a2 = Activity(process_id=p1.id, seq=2, name="Manual ID & Insurance Card Verification", activity_type="manual",
                  role_id=roles["Front Desk Staff"].id, system_id=systems["Legacy Hospital Management System (HMS)"].id,
                  avg_time_minutes=8, error_rate_pct=12, description="Staff visually checks ID and insurance card.")
    a3 = Activity(process_id=p1.id, seq=3, name="Paper Form Filling (Demographics & History)", activity_type="manual",
                  role_id=roles["Front Desk Staff"].id, system_id=None,
                  avg_time_minutes=15, error_rate_pct=20, description="Patient fills a paper intake form by hand.")
    a4 = Activity(process_id=p1.id, seq=4, name="Manual Data Entry into EHR", activity_type="manual",
                  role_id=roles["Registration Officer"].id, system_id=systems["Electronic Health Record (EHR)"].id,
                  avg_time_minutes=10, error_rate_pct=15, description="Officer retypes the paper form into the EHR.")
    a5 = Activity(process_id=p1.id, seq=5, name="Insurance Eligibility Check (phone/portal)", activity_type="system_assisted",
                  role_id=roles["Registration Officer"].id, system_id=systems["Legacy Hospital Management System (HMS)"].id,
                  avg_time_minutes=20, error_rate_pct=18, description="Officer calls/portal-checks insurer for eligibility.")
    a6 = Activity(process_id=p1.id, seq=6, name="Queue Assignment to Department", activity_type="manual",
                  role_id=roles["Front Desk Staff"].id, system_id=systems["Legacy Hospital Management System (HMS)"].id,
                  avg_time_minutes=5, error_rate_pct=5, description="Manually routes patient to a department queue.")
    db.add_all([a1, a2, a3, a4, a5, a6])
    db.flush()

    pr2 = Problem(activity_id=a2.id, description="Identity mismatches and forged/expired insurance cards frequently go undetected in manual checks.", category="error", severity="high")
    pr3a = Problem(activity_id=a3.id, description="Illegible handwriting and incomplete paper forms cause downstream data errors.", category="error", severity="high")
    pr3b = Problem(activity_id=a3.id, description="Elderly and disabled patients struggle with paper forms, causing long delays.", category="experience", severity="medium")
    pr4 = Problem(activity_id=a4.id, description="Duplicate patient records are created due to manual re-typing of the same data.", category="error", severity="high")
    pr5 = Problem(activity_id=a5.id, description="Eligibility checks take 15-20 minutes per patient due to manual phone calls to insurers.", category="time", severity="high")
    pr6 = Problem(activity_id=a6.id, description="No real-time visibility of department load leads to uneven, unpredictable queues.", category="experience", severity="medium")
    db.add_all([pr2, pr3a, pr3b, pr4, pr5, pr6])
    db.flush()

    op2 = AIOpportunity(problem_id=pr2.id, activity_id=a2.id, technique="Computer Vision",
                         description="Kiosk-based OCR + face-match verifies ID and insurance card instantly against payer databases.",
                         feasibility="high", impact="high")
    op3 = AIOpportunity(problem_id=pr3a.id, activity_id=a3.id, technique="GenAI",
                         description="Conversational AI (voice/chat) interviews the patient and auto-fills structured demographic & history data.",
                         feasibility="high", impact="high")
    op4 = AIOpportunity(problem_id=pr4.id, activity_id=a4.id, technique="NLP",
                         description="Structured data flows straight from OCR/voice capture into the EHR — no re-typing, no duplicates.",
                         feasibility="high", impact="high")
    op5 = AIOpportunity(problem_id=pr5.id, activity_id=a5.id, technique="RPA + Predictive ML",
                         description="Real-time API integration with payer systems returns eligibility in seconds; ML pre-flags likely denials.",
                         feasibility="medium", impact="high")
    op6 = AIOpportunity(problem_id=pr6.id, activity_id=a6.id, technique="Predictive ML",
                         description="A load-prediction engine dynamically routes patients to the least congested, clinically appropriate queue.",
                         feasibility="medium", impact="medium")
    db.add_all([op2, op3, op4, op5, op6])
    db.flush()

    f1 = FutureActivity(process_id=p1.id, seq=1, name="Self-Service Kiosk / Mobile Check-in", automation_level="ai",
                         responsible_role_id=roles["AI Intake Assistant"].id, ai_opportunity_id=op2.id,
                         system_id=systems["AI Intake Bot"].id, description="Patient checks in via kiosk or phone app.")
    f2 = FutureActivity(process_id=p1.id, seq=2, name="AI ID & Insurance Verification", automation_level="ai",
                         responsible_role_id=roles["AI Intake Assistant"].id, ai_opportunity_id=op2.id,
                         system_id=systems["AI Intake Bot"].id, description="Face-match + OCR verifies identity and coverage in seconds.")
    f3 = FutureActivity(process_id=p1.id, seq=3, name="Conversational AI Intake Interview", automation_level="ai",
                         responsible_role_id=roles["AI Intake Assistant"].id, ai_opportunity_id=op3.id,
                         system_id=systems["AI Intake Bot"].id, description="Voice/chat agent captures demographics & history conversationally.")
    f4 = FutureActivity(process_id=p1.id, seq=4, name="Auto-Sync to EHR", automation_level="ai",
                         responsible_role_id=roles["AI Intake Assistant"].id, ai_opportunity_id=op4.id,
                         system_id=systems["Electronic Health Record (EHR)"].id, description="Structured data lands directly in the EHR, deduplicated.")
    f5 = FutureActivity(process_id=p1.id, seq=5, name="Real-Time Insurance Eligibility Check", automation_level="ai",
                         responsible_role_id=roles["AI Intake Assistant"].id, ai_opportunity_id=op5.id,
                         system_id=systems["AI Intake Bot"].id, description="Instant payer API call confirms coverage and co-pay.")
    f6 = FutureActivity(process_id=p1.id, seq=6, name="AI-Driven Smart Queue Routing", automation_level="hybrid",
                         responsible_role_id=roles["Care Coordinator"].id, ai_opportunity_id=op6.id,
                         system_id=systems["AI Intake Bot"].id, description="AI predicts wait times; coordinator monitors exceptions.")
    f7 = FutureActivity(process_id=p1.id, seq=7, name="Human Exception Handling", automation_level="human",
                         responsible_role_id=roles["Registration Officer"].id, ai_opportunity_id=None,
                         system_id=systems["Electronic Health Record (EHR)"].id,
                         description="A human resolves ambiguous identity, coverage, or accessibility cases the AI escalates.")
    db.add_all([f1, f2, f3, f4, f5, f6, f7])
    db.flush()

    db.add_all([
        Transformation(process_id=p1.id, current_activity_id=a1.id, future_activity_id=f1.id, transformation_type="automated", rationale="Token queue replaced by self-service check-in."),
        Transformation(process_id=p1.id, current_activity_id=a2.id, future_activity_id=f2.id, transformation_type="automated", rationale="Visual checking replaced by CV verification."),
        Transformation(process_id=p1.id, current_activity_id=a3.id, future_activity_id=f3.id, transformation_type="automated", rationale="Paper form replaced by conversational agent."),
        Transformation(process_id=p1.id, current_activity_id=a4.id, future_activity_id=f4.id, transformation_type="eliminated", rationale="Manual re-typing step is fully removed."),
        Transformation(process_id=p1.id, current_activity_id=a5.id, future_activity_id=f5.id, transformation_type="automated", rationale="Phone-based eligibility replaced by API call."),
        Transformation(process_id=p1.id, current_activity_id=a6.id, future_activity_id=f6.id, transformation_type="augmented", rationale="Human coordinator now supervises an AI router instead of doing it manually."),
        Transformation(process_id=p1.id, current_activity_id=None, future_activity_id=f7.id, transformation_type="new", rationale="New role created purely to handle AI-escalated edge cases."),
    ])

    db.add_all([
        Benefit(process_id=p1.id, metric_name="Average Registration Time", current_value=63, future_value=8, unit="minutes", improvement_pct=pct_drop(63, 8), category="time"),
        Benefit(process_id=p1.id, metric_name="Data Entry Error Rate", current_value=15, future_value=2, unit="%", improvement_pct=pct_drop(15, 2), category="quality"),
        Benefit(process_id=p1.id, metric_name="Duplicate Record Rate", current_value=9, future_value=1, unit="%", improvement_pct=pct_drop(9, 1), category="quality"),
        Benefit(process_id=p1.id, metric_name="Staff Hours per 100 Patients", current_value=40, future_value=12, unit="hours", improvement_pct=pct_drop(40, 12), category="cost"),
        Benefit(process_id=p1.id, metric_name="Patient Satisfaction (CSAT)", current_value=62, future_value=88, unit="score/100", improvement_pct=pct_gain(62, 88), category="experience"),
    ])

    # ---------------------------------------------------------------
    # PROCESS 2: Insurance Verification & Claims Processing (fully modeled)
    # ---------------------------------------------------------------
    p2 = processes["Insurance Verification & Claims Processing"]

    b1 = Activity(process_id=p2.id, seq=1, name="Manual Document Collection", activity_type="manual",
                  role_id=roles["Billing Clerk"].id, system_id=systems["Legacy Claims System"].id,
                  avg_time_minutes=25, error_rate_pct=10, description="Clerk gathers medical records & bills from multiple departments.")
    b2 = Activity(process_id=p2.id, seq=2, name="Manual Claim Form Data Entry", activity_type="manual",
                  role_id=roles["Claims Officer"].id, system_id=systems["Legacy Claims System"].id,
                  avg_time_minutes=30, error_rate_pct=22, description="Officer manually keys claim details into the system.")
    b3 = Activity(process_id=p2.id, seq=3, name="Manual Medical Coding (ICD/CPT)", activity_type="manual",
                  role_id=roles["Claims Officer"].id, system_id=None,
                  avg_time_minutes=20, error_rate_pct=25, description="Officer assigns diagnosis/procedure codes by hand.")
    b4 = Activity(process_id=p2.id, seq=4, name="Claim Submission to Payer", activity_type="system_assisted",
                  role_id=roles["Claims Officer"].id, system_id=systems["Payer Portal"].id,
                  avg_time_minutes=10, error_rate_pct=5, description="Officer uploads the claim through the payer's web portal.")
    b5 = Activity(process_id=p2.id, seq=5, name="Manual Fraud/Anomaly Review (sampling)", activity_type="manual",
                  role_id=roles["Compliance Auditor"].id, system_id=None,
                  avg_time_minutes=40, error_rate_pct=30, description="Auditor manually reviews a random ~5% sample of claims.")
    b6 = Activity(process_id=p2.id, seq=6, name="Claim Status Follow-up", activity_type="manual",
                  role_id=roles["Claims Officer"].id, system_id=systems["Legacy Claims System"].id,
                  avg_time_minutes=15, error_rate_pct=8, description="Officer calls/emails the payer to check claim status.")
    b7 = Activity(process_id=p2.id, seq=7, name="Manual Approval/Denial Decision", activity_type="decision",
                  role_id=roles["Claims Adjudicator"].id, system_id=systems["Legacy Claims System"].id,
                  avg_time_minutes=20, error_rate_pct=18, description="Adjudicator subjectively approves or denies the claim.")
    db.add_all([b1, b2, b3, b4, b5, b6, b7])
    db.flush()

    q1 = Problem(activity_id=b1.id, description="Missing or incomplete documents are discovered late, forcing costly rework cycles.", category="time", severity="high")
    q2 = Problem(activity_id=b2.id, description="High manual data-entry error rate leads directly to claim rejections.", category="error", severity="high")
    q3 = Problem(activity_id=b3.id, description="Incorrect ICD/CPT coding due to human error is a leading cause of payer denials.", category="error", severity="high")
    q5 = Problem(activity_id=b5.id, description="Fraud detection relies on random sampling — only ~5% of claims are ever audited.", category="compliance", severity="high")
    q6 = Problem(activity_id=b6.id, description="Manual status follow-up consumes significant staff time and delays reimbursement.", category="time", severity="medium")
    q7 = Problem(activity_id=b7.id, description="Approval decisions are inconsistent across adjudicators due to subjective judgment.", category="compliance", severity="medium")
    db.add_all([q1, q2, q3, q5, q6, q7])
    db.flush()

    r1 = AIOpportunity(problem_id=q1.id, activity_id=b1.id, technique="Computer Vision + NLP",
                        description="AI Document Intelligence auto-extracts & validates documents, flagging missing items instantly.",
                        feasibility="high", impact="high")
    r2 = AIOpportunity(problem_id=q2.id, activity_id=b2.id, technique="NLP",
                        description="Claim forms auto-populate directly from extracted document data — no manual keying.",
                        feasibility="high", impact="high")
    r3 = AIOpportunity(problem_id=q3.id, activity_id=b3.id, technique="GenAI",
                        description="An AI coding assistant suggests ICD/CPT codes from clinical notes with a confidence score for human sign-off.",
                        feasibility="medium", impact="high")
    r5 = AIOpportunity(problem_id=q5.id, activity_id=b5.id, technique="Predictive ML",
                        description="A fraud-detection engine scores 100% of claims in real time using anomaly detection, not sampling.",
                        feasibility="medium", impact="high")
    r6 = AIOpportunity(problem_id=q6.id, activity_id=b6.id, technique="RPA",
                        description="An automated bot polls payer APIs and proactively notifies staff/patients of status changes.",
                        feasibility="high", impact="medium")
    r7 = AIOpportunity(problem_id=q7.id, activity_id=b7.id, technique="Predictive ML + Agentic AI",
                        description="AI recommends approve/deny with an explainable rationale; a human makes the final call on complex cases.",
                        feasibility="medium", impact="high")
    db.add_all([r1, r2, r3, r5, r6, r7])
    db.flush()

    g1 = FutureActivity(process_id=p2.id, seq=1, name="AI Document Intelligence Auto-Collection", automation_level="ai",
                         responsible_role_id=roles["AI Claims Agent"].id, ai_opportunity_id=r1.id,
                         system_id=systems["AI Document Intelligence"].id, description="Documents are pulled and validated automatically.")
    g2 = FutureActivity(process_id=p2.id, seq=2, name="Auto-Populated Claim Form", automation_level="ai",
                         responsible_role_id=roles["AI Claims Agent"].id, ai_opportunity_id=r2.id,
                         system_id=systems["AI Document Intelligence"].id, description="Claim form fields populate from extracted data.")
    g3 = FutureActivity(process_id=p2.id, seq=3, name="AI-Assisted Medical Coding", automation_level="hybrid",
                         responsible_role_id=roles["Claims Officer"].id, ai_opportunity_id=r3.id,
                         system_id=systems["AI Document Intelligence"].id, description="Officer reviews/approves AI-suggested codes.")
    g4 = FutureActivity(process_id=p2.id, seq=4, name="Automated Claim Submission", automation_level="ai",
                         responsible_role_id=roles["AI Claims Agent"].id, ai_opportunity_id=None,
                         system_id=systems["Payer Portal"].id, description="Validated claim is submitted automatically via API.")
    g5 = FutureActivity(process_id=p2.id, seq=5, name="Real-Time AI Fraud Scoring (100% of claims)", automation_level="ai",
                         responsible_role_id=roles["AI Claims Agent"].id, ai_opportunity_id=r5.id,
                         system_id=systems["Fraud Detection Engine"].id, description="Every claim is scored the instant it's filed.")
    g6 = FutureActivity(process_id=p2.id, seq=6, name="Automated Status Tracking & Notifications", automation_level="ai",
                         responsible_role_id=roles["AI Claims Agent"].id, ai_opportunity_id=r6.id,
                         system_id=systems["Legacy Claims System"].id, description="Bot tracks and pushes status updates proactively.")
    g7 = FutureActivity(process_id=p2.id, seq=7, name="AI-Assisted Adjudication + Human Final Review", automation_level="hybrid",
                         responsible_role_id=roles["Claims Adjudicator"].id, ai_opportunity_id=r7.id,
                         system_id=systems["Fraud Detection Engine"].id, description="AI recommends; adjudicator finalizes with explainable rationale.")
    g8 = FutureActivity(process_id=p2.id, seq=8, name="Human Complex-Case Escalation Review", automation_level="human",
                         responsible_role_id=roles["Compliance Auditor"].id, ai_opportunity_id=None,
                         system_id=systems["Fraud Detection Engine"].id, description="High-risk / high-ambiguity claims escalate to a human auditor.")
    db.add_all([g1, g2, g3, g4, g5, g6, g7, g8])
    db.flush()

    db.add_all([
        Transformation(process_id=p2.id, current_activity_id=b1.id, future_activity_id=g1.id, transformation_type="automated", rationale="Document intelligence replaces manual collection."),
        Transformation(process_id=p2.id, current_activity_id=b2.id, future_activity_id=g2.id, transformation_type="automated", rationale="Auto-population eliminates manual keying."),
        Transformation(process_id=p2.id, current_activity_id=b3.id, future_activity_id=g3.id, transformation_type="augmented", rationale="AI suggests, human still signs off on codes."),
        Transformation(process_id=p2.id, current_activity_id=b4.id, future_activity_id=g4.id, transformation_type="automated", rationale="Submission fully automated via API."),
        Transformation(process_id=p2.id, current_activity_id=b5.id, future_activity_id=g5.id, transformation_type="automated", rationale="100% real-time scoring replaces 5% manual sampling."),
        Transformation(process_id=p2.id, current_activity_id=b6.id, future_activity_id=g6.id, transformation_type="automated", rationale="Bot replaces manual calls/emails."),
        Transformation(process_id=p2.id, current_activity_id=b7.id, future_activity_id=g7.id, transformation_type="augmented", rationale="Human retains final authority, AI improves consistency."),
        Transformation(process_id=p2.id, current_activity_id=None, future_activity_id=g8.id, transformation_type="new", rationale="Dedicated escalation path for high-risk claims flagged by AI."),
    ])

    db.add_all([
        Benefit(process_id=p2.id, metric_name="Average Claim Processing Time", current_value=160, future_value=35, unit="minutes", improvement_pct=pct_drop(160, 35), category="time"),
        Benefit(process_id=p2.id, metric_name="Claim Rejection Rate", current_value=22, future_value=5, unit="%", improvement_pct=pct_drop(22, 5), category="quality"),
        Benefit(process_id=p2.id, metric_name="Fraud Detection Coverage", current_value=5, future_value=100, unit="% of claims audited", improvement_pct=pct_gain(5, 100), category="compliance"),
        Benefit(process_id=p2.id, metric_name="Cost per Claim Processed", current_value=18, future_value=6, unit="USD", improvement_pct=pct_drop(18, 6), category="cost"),
        Benefit(process_id=p2.id, metric_name="Days to Reimbursement", current_value=21, future_value=6, unit="days", improvement_pct=pct_drop(21, 6), category="time"),
    ])

    # ---------------------------------------------------------------
    # PROCESS 3 & 4: lighter models, showing the schema scales
    # ---------------------------------------------------------------
    p3 = processes["Diagnosis, Consultation & Treatment Planning"]
    c1 = Activity(process_id=p3.id, seq=1, name="Manual Chart Review Before Consultation", activity_type="manual",
                  role_id=roles["Physician"].id, system_id=systems["Electronic Health Record (EHR)"].id,
                  avg_time_minutes=12, error_rate_pct=8, description="Physician manually reviews history/labs before seeing patient.")
    c2 = Activity(process_id=p3.id, seq=2, name="Differential Diagnosis Formulation", activity_type="decision",
                  role_id=roles["Physician"].id, system_id=None,
                  avg_time_minutes=15, error_rate_pct=10, description="Physician reasons through possible diagnoses unaided.")
    db.add_all([c1, c2])
    db.flush()
    qc = Problem(activity_id=c2.id, description="Rare or atypical conditions are sometimes missed under time pressure with no second opinion.", category="error", severity="high")
    db.add(qc)
    db.flush()
    rc = AIOpportunity(problem_id=qc.id, activity_id=c2.id, technique="Predictive ML",
                        description="AI diagnostic assistant cross-checks symptoms/labs/imaging against millions of cases and flags overlooked differentials.",
                        feasibility="medium", impact="high")
    db.add(rc)
    db.flush()
    fc1 = FutureActivity(process_id=p3.id, seq=1, name="AI-Prepared Chart Summary", automation_level="ai",
                          responsible_role_id=roles["AI Diagnostic Assistant"].id, ai_opportunity_id=None,
                          system_id=systems["AI Diagnostic Support"].id, description="AI pre-summarizes history/labs before the visit.")
    fc2 = FutureActivity(process_id=p3.id, seq=2, name="AI-Augmented Differential Diagnosis", automation_level="hybrid",
                          responsible_role_id=roles["Physician"].id, ai_opportunity_id=rc.id,
                          system_id=systems["AI Diagnostic Support"].id, description="Physician decides; AI surfaces additional differentials & risk flags.")
    db.add_all([fc1, fc2])
    db.flush()
    db.add_all([
        Transformation(process_id=p3.id, current_activity_id=c1.id, future_activity_id=fc1.id, transformation_type="automated", rationale="AI pre-reads the chart."),
        Transformation(process_id=p3.id, current_activity_id=c2.id, future_activity_id=fc2.id, transformation_type="augmented", rationale="Physician retains final diagnostic authority."),
    ])
    db.add(Benefit(process_id=p3.id, metric_name="Diagnostic Miss Rate", current_value=10, future_value=3, unit="%", improvement_pct=pct_drop(10, 3), category="quality"))
    db.add(Benefit(process_id=p3.id, metric_name="Pre-Consultation Prep Time", current_value=12, future_value=2, unit="minutes", improvement_pct=pct_drop(12, 2), category="time"))

    p4 = processes["Discharge & Follow-up Care"]
    d1 = Activity(process_id=p4.id, seq=1, name="Manual Discharge Instructions", activity_type="manual",
                  role_id=roles["Discharge Nurse"].id, system_id=systems["Electronic Health Record (EHR)"].id,
                  avg_time_minutes=20, error_rate_pct=12, description="Nurse verbally explains and hands over a printed sheet.")
    d2 = Activity(process_id=p4.id, seq=2, name="Manual Follow-up Call Scheduling", activity_type="manual",
                  role_id=roles["Discharge Nurse"].id, system_id=systems["Electronic Health Record (EHR)"].id,
                  avg_time_minutes=10, error_rate_pct=15, description="Nurse manually calls patients to schedule follow-ups; many are missed.")
    db.add_all([d1, d2])
    db.flush()
    qd = Problem(activity_id=d2.id, description="~30% of follow-up appointments are missed or never scheduled due to manual call backlogs.", category="experience", severity="high")
    db.add(qd)
    db.flush()
    rd = AIOpportunity(problem_id=qd.id, activity_id=d2.id, technique="Agentic AI",
                        description="An AI follow-up agent auto-schedules appointments, sends reminders, and monitors recovery via patient check-ins.",
                        feasibility="high", impact="high")
    db.add(rd)
    db.flush()
    fd1 = FutureActivity(process_id=p4.id, seq=1, name="Personalized AI Discharge Summary", automation_level="ai",
                          responsible_role_id=roles["AI Follow-up Agent"].id, ai_opportunity_id=None,
                          system_id=systems["AI Follow-up Platform"].id, description="AI generates a tailored, plain-language discharge summary.")
    fd2 = FutureActivity(process_id=p4.id, seq=2, name="Automated Follow-up Scheduling & Monitoring", automation_level="ai",
                          responsible_role_id=roles["AI Follow-up Agent"].id, ai_opportunity_id=rd.id,
                          system_id=systems["AI Follow-up Platform"].id, description="AI books appointments and monitors recovery signals remotely.")
    db.add_all([fd1, fd2])
    db.flush()
    db.add_all([
        Transformation(process_id=p4.id, current_activity_id=d1.id, future_activity_id=fd1.id, transformation_type="automated", rationale="AI personalizes and auto-generates instructions."),
        Transformation(process_id=p4.id, current_activity_id=d2.id, future_activity_id=fd2.id, transformation_type="automated", rationale="Agentic AI removes manual call backlog."),
    ])
    db.add(Benefit(process_id=p4.id, metric_name="Missed Follow-up Rate", current_value=30, future_value=6, unit="%", improvement_pct=pct_drop(30, 6), category="quality"))
    db.add(Benefit(process_id=p4.id, metric_name="Readmission Rate (30-day)", current_value=14, future_value=8, unit="%", improvement_pct=pct_drop(14, 8), category="quality"))

    db.commit()
    db.close()
    print("Database seeded successfully.")


if __name__ == "__main__":
    seed()
