"""Calculator Pro — FastAPI Production Web API.
==============================================
Provides safe mathematical evaluation routes powered by Python's AST parser.
Designed for deployment on Render, connecting to Vercel frontends.
"""

import os
import sys
import math
from typing import List, Optional, Union
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Ensure root calculator engine is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from calc_engine import (
    SafeExpressionEvaluator,
    safe_square_root,
    safe_reciprocal,
    safe_percentage,
    safe_square,
    format_display_number,
    CalculationHistory
)

app = FastAPI(
    title="Calculator Pro Web API",
    description="Precision mathematical calculation microservice with AST safety validation.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration: allow deployed Vercel frontends and local development
# No unrestricted wildcard in production
raw_allowed_origins = os.environ.get("ALLOWED_ORIGINS", "")
custom_origins = [o.strip() for o in raw_allowed_origins.split(",") if o.strip()]

default_origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "https://python-basic-calculator-delta.vercel.app"
]

allowed_origins = list(dict.fromkeys(default_origins + custom_origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"^https://.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory shared session history
session_history = CalculationHistory()


# ---------------------------------------------------------
# Request / Response Schemas
# ---------------------------------------------------------
class ExpressionRequest(BaseModel):
    expression: str = Field(..., max_length=256, example="25 * (4 + 6)")


class ExpressionResponse(BaseModel):
    success: bool
    expression: str
    result: Union[int, float, str]
    formatted: str
    error: Optional[str] = None


class FunctionRequest(BaseModel):
    operation: str = Field(..., example="sqrt", description="sqrt, square, reciprocal, percentage")
    value: float = Field(..., example=64.0)


class FunctionResponse(BaseModel):
    success: bool
    operation: str
    input_value: float
    result: Union[int, float, str]
    formatted: str
    error: Optional[str] = None


class HistoryItem(BaseModel):
    expression: str
    result: str
    timestamp: str


# ---------------------------------------------------------
# Health Check Endpoint
# ---------------------------------------------------------
@app.get("/health", tags=["System"])
def health_check():
    """Liveness probe for Render / deployment monitors."""
    return {
        "status": "healthy",
        "service": "calculator-pro-api",
        "version": "1.0.0",
        "engine": "Safe AST Python 3 Evaluator (zero eval)"
    }


# ---------------------------------------------------------
# Calculation Routes
# ---------------------------------------------------------
@app.post("/api/v1/calculator/evaluate", response_model=ExpressionResponse, tags=["Calculations"])
def evaluate_expression(payload: ExpressionRequest):
    """Safely evaluates an arithmetic expression string using AST validation."""
    raw_expr = payload.expression.strip()
    if not raw_expr:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Expression string cannot be empty."
        )

    result = SafeExpressionEvaluator.evaluate(raw_expr)

    if isinstance(result, str) and ("error" in result.lower() or "cannot" in result.lower() or "invalid" in result.lower()):
        return ExpressionResponse(
            success=False,
            expression=raw_expr,
            result=result,
            formatted=result,
            error=result
        )

    formatted = format_display_number(result)
    session_history.add_entry(raw_expr, formatted)

    return ExpressionResponse(
        success=True,
        expression=raw_expr,
        result=result,
        formatted=formatted,
        error=None
    )


@app.post("/api/v1/calculator/function", response_model=FunctionResponse, tags=["Calculations"])
def execute_scientific_function(payload: FunctionRequest):
    """Executes single-operand scientific operations."""
    op = payload.operation.lower().strip()
    val = payload.value

    if op in ["sqrt", "square_root"]:
        res = safe_square_root(val)
    elif op == "square":
        res = safe_square(val)
    elif op in ["reciprocal", "invert", "1/x"]:
        res = safe_reciprocal(val)
    elif op in ["percentage", "%"]:
        res = safe_percentage(val)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported operation '{op}'. Supported: sqrt, square, reciprocal, percentage."
        )

    if isinstance(res, str):
        return FunctionResponse(
            success=False,
            operation=op,
            input_value=val,
            result=res,
            formatted=res,
            error=res
        )

    formatted = format_display_number(res)
    return FunctionResponse(
        success=True,
        operation=op,
        input_value=val,
        result=res,
        formatted=formatted,
        error=None
    )


@app.get("/api/v1/calculator/history", response_model=List[HistoryItem], tags=["History"])
def get_history():
    """Retrieve recent calculation history ledger."""
    return session_history.get_entries()


@app.delete("/api/v1/calculator/history", tags=["History"])
def clear_history():
    """Clear calculation ledger."""
    session_history.clear()
    return {"message": "Calculation history cleared successfully."}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
