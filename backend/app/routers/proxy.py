from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.reasoning import ProxyRequest, ProxyResponse
from app.modules.reasoning_tracer import ReasoningTracer
from app.modules.path_analyzer import PathAnalyzer
from app.modules.logic_validator import LogicValidator
from app.modules.consistency_checker import ConsistencyChecker

router = APIRouter(prefix="/proxy", tags=["LLM Proxy"])


@router.post("/chat", response_model=ProxyResponse)
async def proxy_chat(
    request: ProxyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Proxy endpoint for LLM interactions with reasoning analysis.
    Acts as middleware between client and LLM provider.
    """
    response_data = {
        "response": "",
        "reasoning_trace_id": None,
        "path_analysis_id": None,
        "logic_graph_id": None,
        "consistency_check_id": None,
        "metadata": {},
    }

    try:
        # Module 1: Reasoning Tracer (CoT)
        if request.enable_cot:
            tracer = ReasoningTracer(db)
            trace = await tracer.trace(
                user_id=current_user.id,
                prompt=request.prompt,
                provider=request.model_provider.value,
                model=request.model_name,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )
            response_data["response"] = tracer.get_extracted_answer(trace) or trace.raw_response
            response_data["reasoning_trace_id"] = trace.id
            response_data["metadata"]["cot"] = {
                "steps_count": len(trace.steps) if trace.steps else 0,
                "integrity_hash": trace.integrity_hash,
            }

        # Module 2: Path Analyzer (ToT)
        if request.enable_tot:
            analyzer = PathAnalyzer(db)
            analysis = await analyzer.analyze(
                user_id=current_user.id,
                problem=request.prompt,
                provider=request.model_provider.value,
                model=request.model_name,
            )
            response_data["path_analysis_id"] = analysis.id
            response_data["metadata"]["tot"] = {
                "nodes_explored": analysis.total_nodes_explored,
                "paths_pruned": analysis.total_paths_pruned,
                "selected_path": analysis.selected_path,
            }

            # If no CoT was run, use ToT selected path as response
            if not request.enable_cot and analysis.selected_path:
                response_data["response"] = (
                    f"Abordagem selecionada: {analysis.selected_path.get('selected_approach', 'N/A')}\n"
                    f"Score: {analysis.selected_path.get('score', 'N/A')}"
                )

        # Module 3: Logic Validator (GoT)
        if request.enable_got and response_data["reasoning_trace_id"]:
            validator = LogicValidator(db)
            graph = await validator.validate(
                user_id=current_user.id,
                reasoning_trace_id=response_data["reasoning_trace_id"],
                provider=request.model_provider.value,
                model=request.model_name,
            )
            response_data["logic_graph_id"] = graph.id
            response_data["metadata"]["got"] = {
                "has_contradictions": graph.has_contradictions,
                "has_logic_gaps": graph.has_logic_gaps,
                "has_hidden_premises": graph.has_hidden_premises,
                "has_circularity": graph.has_circularity,
                "validity_score": graph.overall_validity_score,
            }

        # Module 4: Consistency Checker
        if request.enable_consistency:
            checker = ConsistencyChecker(db)
            check = await checker.check(
                user_id=current_user.id,
                query=request.prompt,
                provider=request.model_provider.value,
                model=request.model_name,
                num_runs=request.consistency_runs,
            )
            response_data["consistency_check_id"] = check.id
            response_data["metadata"]["consistency"] = {
                "convergence_rate": check.convergence_rate,
                "confidence_score": check.confidence_score,
                "total_runs": check.total_runs,
            }

        return ProxyResponse(**response_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simple", response_model=ProxyResponse)
async def simple_chat(
    request: ProxyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Simple proxy endpoint without reasoning analysis.
    Just forwards the request to the LLM and returns the response.
    """
    from app.modules.llm_client import llm_client

    try:
        response = await llm_client.generate(
            prompt=request.prompt,
            provider=request.model_provider.value,
            model=request.model_name,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        return ProxyResponse(
            response=response["content"],
            metadata={"model": response["model"]},
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
