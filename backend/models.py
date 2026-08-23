from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Industry(Base):
    __tablename__ = "industries"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    processes = relationship("Process", back_populates="industry", cascade="all, delete-orphan")


class Process(Base):
    __tablename__ = "processes"
    id = Column(Integer, primary_key=True)
    industry_id = Column(Integer, ForeignKey("industries.id"))
    name = Column(String, nullable=False)
    description = Column(Text)
    order_index = Column(Integer, default=0)

    industry = relationship("Industry", back_populates="processes")
    activities = relationship("Activity", back_populates="process", cascade="all, delete-orphan")
    future_activities = relationship("FutureActivity", back_populates="process", cascade="all, delete-orphan")
    transformations = relationship("Transformation", back_populates="process", cascade="all, delete-orphan")
    benefits = relationship("Benefit", back_populates="process", cascade="all, delete-orphan")


class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String)  # human | ai | hybrid
    description = Column(Text)


class System(Base):
    __tablename__ = "systems"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String)  # legacy_it | ai_platform | integration
    description = Column(Text)


class Activity(Base):
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True)
    process_id = Column(Integer, ForeignKey("processes.id"))
    seq = Column(Integer)
    name = Column(String, nullable=False)
    description = Column(Text)
    activity_type = Column(String)  # manual | decision | system_assisted
    role_id = Column(Integer, ForeignKey("roles.id"))
    system_id = Column(Integer, ForeignKey("systems.id"))
    avg_time_minutes = Column(Float)
    error_rate_pct = Column(Float)

    process = relationship("Process", back_populates="activities")
    role = relationship("Role")
    system = relationship("System")
    problems = relationship("Problem", back_populates="activity", cascade="all, delete-orphan")


class Problem(Base):
    __tablename__ = "problems"
    id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, ForeignKey("activities.id"))
    description = Column(Text, nullable=False)
    category = Column(String)  # time | cost | error | experience | compliance
    severity = Column(String)  # low | medium | high

    activity = relationship("Activity", back_populates="problems")
    ai_opportunities = relationship("AIOpportunity", back_populates="problem", cascade="all, delete-orphan")


class AIOpportunity(Base):
    __tablename__ = "ai_opportunities"
    id = Column(Integer, primary_key=True)
    problem_id = Column(Integer, ForeignKey("problems.id"))
    activity_id = Column(Integer, ForeignKey("activities.id"))
    technique = Column(String)  # NLP | GenAI | Computer Vision | RPA | Predictive ML | Agentic AI
    description = Column(Text, nullable=False)
    feasibility = Column(String)  # low | medium | high
    impact = Column(String)  # low | medium | high

    problem = relationship("Problem", back_populates="ai_opportunities")
    activity = relationship("Activity")


class FutureActivity(Base):
    __tablename__ = "future_activities"
    id = Column(Integer, primary_key=True)
    process_id = Column(Integer, ForeignKey("processes.id"))
    seq = Column(Integer)
    name = Column(String, nullable=False)
    description = Column(Text)
    automation_level = Column(String)  # human | ai | hybrid
    responsible_role_id = Column(Integer, ForeignKey("roles.id"))
    ai_opportunity_id = Column(Integer, ForeignKey("ai_opportunities.id"))
    system_id = Column(Integer, ForeignKey("systems.id"))

    process = relationship("Process", back_populates="future_activities")
    responsible_role = relationship("Role")
    ai_opportunity = relationship("AIOpportunity")
    system = relationship("System")


class Transformation(Base):
    __tablename__ = "transformations"
    id = Column(Integer, primary_key=True)
    process_id = Column(Integer, ForeignKey("processes.id"))
    current_activity_id = Column(Integer, ForeignKey("activities.id"), nullable=True)
    future_activity_id = Column(Integer, ForeignKey("future_activities.id"), nullable=True)
    transformation_type = Column(String)  # eliminated | automated | augmented | new | unchanged
    rationale = Column(Text)

    process = relationship("Process", back_populates="transformations")
    current_activity = relationship("Activity")
    future_activity = relationship("FutureActivity")


class Benefit(Base):
    __tablename__ = "benefits"
    id = Column(Integer, primary_key=True)
    process_id = Column(Integer, ForeignKey("processes.id"))
    metric_name = Column(String, nullable=False)
    current_value = Column(Float)
    future_value = Column(Float)
    unit = Column(String)
    improvement_pct = Column(Float)
    category = Column(String)  # time | cost | quality | experience | compliance

    process = relationship("Process", back_populates="benefits")
