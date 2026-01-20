"""
Module 1: Reasoning Tracer (CoT)
Intercepts requests, injects Chain-of-Thought instructions,
parses responses to extract premises and intermediate steps,
and stores everything in JSON with integrity hash.
"""

import hashlib
import json
import re
from typing import Dict, Any, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.modules.llm_client import llm_client
from app.models.reasoning import ReasoningTrace, ReasoningStep


COT_SYSTEM_PROMPT = """Você é um assistente de raciocínio lógico. Ao responder perguntas, você DEVE seguir este processo de pensamento estruturado:

1. Primeiro, identifique e liste claramente todas as PREMISSAS (fatos ou suposições dadas)
2. Em seguida, mostre cada passo de INFERÊNCIA, explicando como você deriva novas conclusões a partir das premissas
3. Por fim, declare sua CONCLUSÃO

Formate sua resposta EXATAMENTE da seguinte forma:

<reasoning>
<premises>
- [Liste cada premissa em uma nova linha]
</premises>

<inferences>
- Passo 1: [Primeira inferência, citando quais premissas ela utiliza]
- Passo 2: [Segunda inferência, citando passos anteriores ou premissas]
- ... (continue conforme necessário)
</inferences>

<conclusion>
[Sua conclusão final baseada no raciocínio acima]
</conclusion>
</reasoning>

<answer>
[Sua resposta direta à pergunta]
</answer>

Sempre seja explícito sobre sua cadeia de raciocínio. Se você estiver incerto sobre qualquer passo, expresse essa incerteza com um nível de confiança (0-100%)."""


class ReasoningTracer:
    """Chain of Thought reasoning tracer."""

    def __init__(self, db: Session):
        self.db = db

    def _create_integrity_hash(self, data: Dict[str, Any]) -> str:
        """Create SHA-256 hash for data integrity verification."""
        json_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(json_str.encode()).hexdigest()

    def _parse_reasoning(self, response: str) -> Dict[str, Any]:
        """Parse the structured reasoning from the response."""
        result = {
            "premises": [],
            "inferences": [],
            "conclusion": None,
            "answer": None,
            "raw_parsing": True,
        }

        # Extract premises
        premises_match = re.search(r"<premises>(.*?)</premises>", response, re.DOTALL)
        if premises_match:
            premises_text = premises_match.group(1).strip()
            premises = [
                p.strip().lstrip("- ").strip()
                for p in premises_text.split("\n")
                if p.strip() and p.strip() != "-"
            ]
            result["premises"] = premises

        # Extract inferences
        inferences_match = re.search(r"<inferences>(.*?)</inferences>", response, re.DOTALL)
        if inferences_match:
            inferences_text = inferences_match.group(1).strip()
            inferences = []
            for line in inferences_text.split("\n"):
                line = line.strip()
                if line and line != "-":
                    # Parse step number and content
                    step_match = re.match(r"[-•]?\s*(?:Step\s*)?(\d+)?[:.)]?\s*(.*)", line, re.IGNORECASE)
                    if step_match:
                        content = step_match.group(2).strip()
                        if content:
                            # Check for confidence level
                            confidence = None
                            conf_match = re.search(r"\((\d+)%?\s*confidence\)", content, re.IGNORECASE)
                            if conf_match:
                                confidence = int(conf_match.group(1)) / 100
                            inferences.append({
                                "content": content,
                                "confidence": confidence,
                            })
            result["inferences"] = inferences

        # Extract conclusion
        conclusion_match = re.search(r"<conclusion>(.*?)</conclusion>", response, re.DOTALL)
        if conclusion_match:
            result["conclusion"] = conclusion_match.group(1).strip()

        # Extract answer
        answer_match = re.search(r"<answer>(.*?)</answer>", response, re.DOTALL)
        if answer_match:
            result["answer"] = answer_match.group(1).strip()

        # If structured parsing failed, try to extract any reasoning
        if not result["premises"] and not result["inferences"]:
            result["raw_parsing"] = False
            # Fallback: try to identify reasoning patterns
            lines = response.split("\n")
            for line in lines:
                line = line.strip()
                if line.lower().startswith(("because", "since", "given that", "assuming")):
                    result["premises"].append(line)
                elif line.lower().startswith(("therefore", "thus", "hence", "so")):
                    if not result["conclusion"]:
                        result["conclusion"] = line
                elif re.match(r"^\d+\.", line):
                    result["inferences"].append({"content": line, "confidence": None})

        return result

    async def trace(
        self,
        user_id: UUID,
        prompt: str,
        provider: str = "openai",
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> ReasoningTrace:
        """
        Execute a prompt with Chain-of-Thought reasoning and trace the process.
        """
        # Create enhanced prompt with CoT instructions
        enhanced_prompt = f"""Por favor, analise e responda a seguinte pergunta usando raciocínio estruturado:

{prompt}

Lembre-se de mostrar claramente suas premissas, passos de raciocínio e conclusão."""

        # Generate response with CoT system prompt
        response = await llm_client.generate(
            prompt=enhanced_prompt,
            provider=provider,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=COT_SYSTEM_PROMPT,
        )

        raw_response = response["content"]
        parsed_reasoning = self._parse_reasoning(raw_response)

        # Create integrity hash
        integrity_data = {
            "original_prompt": prompt,
            "enhanced_prompt": enhanced_prompt,
            "raw_response": raw_response,
            "parsed_reasoning": parsed_reasoning,
            "model": response["model"],
        }
        integrity_hash = self._create_integrity_hash(integrity_data)

        # Store in database
        trace = ReasoningTrace(
            user_id=user_id,
            original_prompt=prompt,
            enhanced_prompt=enhanced_prompt,
            raw_response=raw_response,
            parsed_reasoning=parsed_reasoning,
            model_provider=provider,
            model_name=response["model"],
            integrity_hash=integrity_hash,
        )
        self.db.add(trace)
        self.db.flush()

        # Create reasoning steps
        step_number = 0

        # Add premises as steps
        for premise in parsed_reasoning.get("premises", []):
            step_number += 1
            step = ReasoningStep(
                trace_id=trace.id,
                step_number=step_number,
                step_type="premise",
                content=premise,
                confidence=1.0,
            )
            self.db.add(step)

        # Add inferences as steps
        for inference in parsed_reasoning.get("inferences", []):
            step_number += 1
            step = ReasoningStep(
                trace_id=trace.id,
                step_number=step_number,
                step_type="inference",
                content=inference["content"],
                confidence=inference.get("confidence"),
            )
            self.db.add(step)

        # Add conclusion as step
        if parsed_reasoning.get("conclusion"):
            step_number += 1
            step = ReasoningStep(
                trace_id=trace.id,
                step_number=step_number,
                step_type="conclusion",
                content=parsed_reasoning["conclusion"],
                confidence=None,
            )
            self.db.add(step)

        self.db.commit()
        self.db.refresh(trace)

        return trace

    def verify_integrity(self, trace: ReasoningTrace) -> bool:
        """Verify the integrity of a stored reasoning trace."""
        integrity_data = {
            "original_prompt": trace.original_prompt,
            "enhanced_prompt": trace.enhanced_prompt,
            "raw_response": trace.raw_response,
            "parsed_reasoning": trace.parsed_reasoning,
            "model": trace.model_name,
        }
        computed_hash = self._create_integrity_hash(integrity_data)
        return computed_hash == trace.integrity_hash

    def get_trace(self, trace_id: UUID) -> Optional[ReasoningTrace]:
        """Retrieve a reasoning trace by ID."""
        return self.db.query(ReasoningTrace).filter(ReasoningTrace.id == trace_id).first()

    def get_user_traces(self, user_id: UUID, limit: int = 50) -> List[ReasoningTrace]:
        """Get all reasoning traces for a user."""
        return (
            self.db.query(ReasoningTrace)
            .filter(ReasoningTrace.user_id == user_id)
            .order_by(ReasoningTrace.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_extracted_answer(self, trace: ReasoningTrace) -> Optional[str]:
        """Extract the final answer from a reasoning trace."""
        if trace.parsed_reasoning and trace.parsed_reasoning.get("answer"):
            return trace.parsed_reasoning["answer"]
        elif trace.parsed_reasoning and trace.parsed_reasoning.get("conclusion"):
            return trace.parsed_reasoning["conclusion"]
        return None
