import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from typing import Optional
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Rule

router = APIRouter()

class RuleCreate(BaseModel):
    name: str
    description: str = ""
    conditions: str  # JSON string
    risk_level: int
    priority: int = 0
    enabled: bool = True

    @field_validator("conditions")
    @classmethod
    def validate_conditions_json(cls, v):
        try:
            json.loads(v)
        except json.JSONDecodeError as e:
            raise ValueError(f"conditions must be valid JSON: {e}")
        return v

class RuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    conditions: Optional[str] = None
    risk_level: Optional[int] = None
    priority: Optional[int] = None
    enabled: Optional[bool] = None

    @field_validator("conditions")
    @classmethod
    def validate_conditions_json(cls, v):
        try:
            json.loads(v)
        except json.JSONDecodeError as e:
            raise ValueError(f"conditions must be valid JSON: {e}")
        return v

def _serialize(r: Rule):
    return {"id": r.id, "name": r.name, "description": r.description,
            "conditions": r.conditions, "risk_level": r.risk_level,
            "enabled": r.enabled, "priority": r.priority}

@router.get("/rules")
def list_rules(db: Session = Depends(get_db)):
    return [_serialize(r) for r in db.query(Rule).order_by(Rule.priority.desc()).all()]

@router.post("/rules", status_code=201)
def create_rule(body: RuleCreate, db: Session = Depends(get_db)):
    rule = Rule(name=body.name, description=body.description, conditions=body.conditions,
                risk_level=body.risk_level, priority=body.priority, enabled=body.enabled)
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return _serialize(rule)

@router.put("/rules/{rid}")
def update_rule(rid: int, body: RuleUpdate, db: Session = Depends(get_db)):
    rule = db.get(Rule, rid)
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    for field, val in body.model_dump(exclude_none=True).items():
        setattr(rule, field, val)
    db.commit()
    db.refresh(rule)
    return _serialize(rule)

@router.delete("/rules/{rid}")
def delete_rule(rid: int, db: Session = Depends(get_db)):
    rule = db.get(Rule, rid)
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    db.delete(rule)
    db.commit()
    return {"ok": True}
