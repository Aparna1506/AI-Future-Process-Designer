from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os

from database import get_db, engine, Base
import models as m

app = FastAPI(
    title="AI Future Process Designer API",
    description="Structured backend that stores Current Process -> Activities -> Problems -> "
                "AI Opportunities -> Future Process -> Human/AI Responsibility -> Expected Benefit "
                "as queryable, related data (not paragraphs).",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

if not os.path.exists(os.path.join(os.path.dirname(__file__), "app.db")):
    Base.metadata.create_all(bind=engine)


# ---------- serializers ----------

def role_dict(r):
    return r and {"id": r.id, "name": r.name, "type": r.type, "description": r.description}


def system_dict(s):
    return s and {"id": s.id, "name": s.name, "category": s.category, "description": s.description}


def activity_dict(a):
    return {
        "id": a.id, "seq": a.seq, "name": a.name, "description": a.description,
        "activity_type": a.activity_type, "role": role_dict(a.role), "system": system_dict(a.system),
        "avg_time_minutes": a.avg_time_minutes, "error_rate_pct": a.error_rate_pct,
        "problems": [problem_dict(p) for p in a.problems],
    }


def problem_dict(p):
    return {
        "id": p.id, "description": p.description, "category": p.category, "severity": p.severity,
        "ai_opportunities": [ai_dict(o) for o in p.ai_opportunities],
    }


def ai_dict(o):
    return {
        "id": o.id, "technique": o.technique, "description": o.description,
        "feasibility": o.feasibility, "impact": o.impact,
    }


def future_activity_dict(f):
    return {
        "id": f.id, "seq": f.seq, "name": f.name, "description": f.description,
        "automation_level": f.automation_level, "responsible_role": role_dict(f.responsible_role),
        "system": system_dict(f.system),
        "ai_opportunity": ai_dict(f.ai_opportunity) if f.ai_opportunity else None,
    }


def transformation_dict(t):
    return {
        "id": t.id, "transformation_type": t.transformation_type, "rationale": t.rationale,
        "current_activity": {"id": t.current_activity.id, "name": t.current_activity.name} if t.current_activity else None,
        "future_activity": {"id": t.future_activity.id, "name": t.future_activity.name} if t.future_activity else None,
    }


def benefit_dict(b):
    return {
        "id": b.id, "metric_name": b.metric_name, "current_value": b.current_value,
        "future_value": b.future_value, "unit": b.unit, "improvement_pct": b.improvement_pct,
        "category": b.category,
    }


def process_summary(p):
    return {"id": p.id, "name": p.name, "description": p.description, "order_index": p.order_index}


# ---------- routes ----------

@app.get("/")
def root():
    return {
        "message": "AI Future Process Designer API",
        "docs": "/docs",
        "key_endpoint": "/processes/{id}/reasoning-chain",
    }


@app.get("/industries")
def list_industries(db: Session = Depends(get_db)):
    industries = db.query(m.Industry).all()
    return [{"id": i.id, "name": i.name, "description": i.description,
             "processes": [process_summary(p) for p in i.processes]} for i in industries]


@app.get("/processes")
def list_processes(db: Session = Depends(get_db)):
    return [process_summary(p) for p in db.query(m.Process).order_by(m.Process.order_index).all()]


@app.get("/processes/{process_id}")
def get_process(process_id: int, db: Session = Depends(get_db)):
    p = db.query(m.Process).get(process_id)
    if not p:
        raise HTTPException(404, "Process not found")
    return process_summary(p)


@app.get("/processes/{process_id}/activities")
def get_activities(process_id: int, db: Session = Depends(get_db)):
    acts = db.query(m.Activity).filter(m.Activity.process_id == process_id).order_by(m.Activity.seq).all()
    return [activity_dict(a) for a in acts]


@app.get("/processes/{process_id}/problems")
def get_problems(process_id: int, db: Session = Depends(get_db)):
    acts = db.query(m.Activity).filter(m.Activity.process_id == process_id).all()
    problems = []
    for a in acts:
        problems.extend(a.problems)
    return [problem_dict(p) for p in problems]


@app.get("/processes/{process_id}/ai-opportunities")
def get_ai_opportunities(process_id: int, db: Session = Depends(get_db)):
    ops = db.query(m.AIOpportunity).join(m.Activity).filter(m.Activity.process_id == process_id).all()
    return [ai_dict(o) for o in ops]


@app.get("/processes/{process_id}/future-activities")
def get_future_activities(process_id: int, db: Session = Depends(get_db)):
    fs = db.query(m.FutureActivity).filter(m.FutureActivity.process_id == process_id).order_by(m.FutureActivity.seq).all()
    return [future_activity_dict(f) for f in fs]


@app.get("/processes/{process_id}/transformations")
def get_transformations(process_id: int, db: Session = Depends(get_db)):
    ts = db.query(m.Transformation).filter(m.Transformation.process_id == process_id).all()
    return [transformation_dict(t) for t in ts]


@app.get("/processes/{process_id}/benefits")
def get_benefits(process_id: int, db: Session = Depends(get_db)):
    bs = db.query(m.Benefit).filter(m.Benefit.process_id == process_id).all()
    return [benefit_dict(b) for b in bs]


@app.get("/processes/{process_id}/reasoning-chain")
def reasoning_chain(process_id: int, db: Session = Depends(get_db)):
    """
    Returns the FULL structured chain:
    Current Process -> Activities -> Problems -> AI Opportunities
      -> Future Process -> Human vs AI Responsibility -> Expected Benefit
    as nested, queryable JSON (not prose).
    """
    p = db.query(m.Process).get(process_id)
    if not p:
        raise HTTPException(404, "Process not found")

    acts = db.query(m.Activity).filter(m.Activity.process_id == process_id).order_by(m.Activity.seq).all()
    futures = db.query(m.FutureActivity).filter(m.FutureActivity.process_id == process_id).order_by(m.FutureActivity.seq).all()
    transformations = db.query(m.Transformation).filter(m.Transformation.process_id == process_id).all()
    benefits = db.query(m.Benefit).filter(m.Benefit.process_id == process_id).all()

    responsibility_split = {
        "human_only": len([f for f in futures if f.automation_level == "human"]),
        "ai_only": len([f for f in futures if f.automation_level == "ai"]),
        "hybrid": len([f for f in futures if f.automation_level == "hybrid"]),
    }

    return {
        "process": process_summary(p),
        "current_process": {
            "activities": [activity_dict(a) for a in acts],
        },
        "future_process": {
            "activities": [future_activity_dict(f) for f in futures],
        },
        "human_vs_ai_responsibility": responsibility_split,
        "transformations": [transformation_dict(t) for t in transformations],
        "expected_benefits": [benefit_dict(b) for b in benefits],
    }


@app.get("/processes/{process_id}/compare")
def compare(process_id: int, db: Session = Depends(get_db)):
    """CURRENT -> TRANSITION -> FUTURE side-by-side comparison, driven by the transformations table."""
    p = db.query(m.Process).get(process_id)
    if not p:
        raise HTTPException(404, "Process not found")
    ts = db.query(m.Transformation).filter(m.Transformation.process_id == process_id).order_by(m.Transformation.id).all()
    rows = []
    for t in ts:
        rows.append({
            "current": activity_dict(t.current_activity) if t.current_activity else None,
            "transition_type": t.transformation_type,
            "rationale": t.rationale,
            "future": future_activity_dict(t.future_activity) if t.future_activity else None,
        })
    return {"process": process_summary(p), "comparison_rows": rows}


# ---------- lightweight write endpoints (proves data is a real, queryable store) ----------

@app.post("/processes/{process_id}/activities")
def create_activity(process_id: int, payload: dict, db: Session = Depends(get_db)):
    a = m.Activity(process_id=process_id, **payload)
    db.add(a)
    db.commit()
    db.refresh(a)
    return activity_dict(a)


@app.post("/activities/{activity_id}/problems")
def create_problem(activity_id: int, payload: dict, db: Session = Depends(get_db)):
    pr = m.Problem(activity_id=activity_id, **payload)
    db.add(pr)
    db.commit()
    db.refresh(pr)
    return problem_dict(pr)


@app.post("/problems/{problem_id}/ai-opportunities")
def create_ai_opportunity(problem_id: int, payload: dict, db: Session = Depends(get_db)):
    pr = db.query(m.Problem).get(problem_id)
    if not pr:
        raise HTTPException(404, "Problem not found")
    op = m.AIOpportunity(problem_id=problem_id, activity_id=pr.activity_id, **payload)
    db.add(op)
    db.commit()
    db.refresh(op)
    return ai_dict(op)
