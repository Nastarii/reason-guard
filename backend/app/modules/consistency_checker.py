"""
Module 4: Consistency Checker
Executes the same query multiple times with variations,
calculates convergence rate, and generates a confidence score.
"""

import asyncio
import re
import json
from typing import Dict, Any, List, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
import numpy as np

from app.modules.llm_client import llm_client
from app.models.reasoning import ConsistencyCheck

# Maximum concurrent requests to avoid overwhelming the LLM API
MAX_CONCURRENT_REQUESTS = 5


VARIATION_PROMPT = """Gere {num_variations} variações semanticamente equivalentes da seguinte consulta.
Cada variação deve perguntar a mesma coisa, mas usar palavras, estrutura ou perspectiva diferentes.

Consulta original: {query}

Formate sua resposta como:
<variations>
<v1>[Primeira variação]</v1>
<v2>[Segunda variação]</v2>
... (e assim por diante)
</variations>"""


COMPARE_ALL_RESPONSES_PROMPT = """Analise as seguintes {num_responses} respostas para a mesma consulta quanto à consistência semântica.
Identifique as afirmações/conclusões principais em todas as respostas e determine onde elas concordam ou divergem.

{responses_text}

Formate sua análise como:
<analysis>
<core_claims>
- [Afirmação principal encontrada nas respostas]
- [Outra afirmação]
...
</core_claims>

<agreements>
- [Ponto onde a maioria/todas as respostas concordam]
...
</agreements>

<divergences>
- [Ponto de divergência] | Respostas: [liste quais respostas divergem, ex.: "1,3 vs 2,4,5"] | Severidade: [high/medium/low]
...
</divergences>

<pairwise_scores>
{pairwise_format}
</pairwise_scores>

<overall_similarity>[0-100]</overall_similarity>
</analysis>"""


class ConsistencyChecker:
    """Multi-run consistency analyzer."""

    def __init__(self, db: Session):
        self.db = db
        self._semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

    async def _execute_with_semaphore(self, coro):
        """Execute a coroutine with semaphore to limit concurrency."""
        async with self._semaphore:
            return await coro

    async def _generate_variations(
        self,
        query: str,
        num_variations: int,
        provider: str,
        model: Optional[str],
    ) -> List[str]:
        """Generate query variations."""
        prompt = VARIATION_PROMPT.format(
            query=query,
            num_variations=num_variations,
        )

        response = await llm_client.generate(
            prompt=prompt,
            provider=provider,
            model=model,
            temperature=0.8,
        )

        content = re.sub(r"```(?:xml|html|text)?\s*\n?", "", response["content"]).strip()
        variations = [query]  # Include original

        # Parse variations
        for i in range(1, num_variations + 1):
            pattern = rf"<v{i}>(.*?)</v{i}>"
            match = re.search(pattern, content, re.DOTALL)
            if match:
                variations.append(match.group(1).strip())

        return variations

    async def _compare_all_responses(
        self,
        responses: List[Dict[str, Any]],
        provider: str,
        model: Optional[str],
    ) -> Dict[str, Any]:
        """Compare all responses in a single request for semantic consistency."""
        # Build responses text
        responses_text = "\n\n".join([
            f"Response {i+1}:\n{r['response']}"
            for i, r in enumerate(responses)
        ])

        # Build pairwise format instruction
        pairs = []
        for i in range(len(responses)):
            for j in range(i + 1, len(responses)):
                pairs.append(f"{i+1}-{j+1}: [score 0-100]")
        pairwise_format = "\n".join(pairs)

        prompt = COMPARE_ALL_RESPONSES_PROMPT.format(
            num_responses=len(responses),
            responses_text=responses_text,
            pairwise_format=pairwise_format,
        )

        response = await llm_client.generate(
            prompt=prompt,
            provider=provider,
            model=model,
            temperature=0.2,
        )

        content = re.sub(r"```(?:xml|html|text)?\s*\n?", "", response["content"]).strip()

        result = {
            "overall_similarity": None,
            "pairwise_scores": {},
            "agreements": [],
            "divergences": [],
        }

        # Parse overall similarity
        overall_match = re.search(r"<overall_similarity>\s*([\d.]+)\s*%?\s*</overall_similarity>", content)
        if overall_match:
            score = float(overall_match.group(1))
            if score <= 1.0 and score > 0:
                score = score * 100
            result["overall_similarity"] = min(int(round(score)), 100)

        # Parse pairwise scores
        pairwise_match = re.search(r"<pairwise_scores>(.*?)</pairwise_scores>", content, re.DOTALL)
        if pairwise_match:
            text = pairwise_match.group(1)
            for line in text.split("\n"):
                line = line.strip()
                if not line:
                    continue
                # Parse format like "1-2: 85" or "1-2: [85]"
                score_match = re.search(r"(\d+)-(\d+):\s*\[?(\d+)\]?", line)
                if score_match:
                    i, j, score = int(score_match.group(1)), int(score_match.group(2)), int(score_match.group(3))
                    result["pairwise_scores"][(i, j)] = score

        # Parse agreements
        agreements_match = re.search(r"<agreements>(.*?)</agreements>", content, re.DOTALL)
        if agreements_match:
            text = agreements_match.group(1)
            result["agreements"] = [
                line.strip().lstrip("- ").strip()
                for line in text.split("\n")
                if line.strip() and line.strip() != "-"
            ]

        # Parse divergences
        divergences_match = re.search(r"<divergences>(.*?)</divergences>", content, re.DOTALL)
        if divergences_match:
            text = divergences_match.group(1)
            result["divergences"] = [
                line.strip().lstrip("- ").strip()
                for line in text.split("\n")
                if line.strip() and line.strip() != "-"
            ]

        # Calculate overall_similarity from pairwise scores if not parsed
        if result["overall_similarity"] is None:
            if result["pairwise_scores"]:
                scores = list(result["pairwise_scores"].values())
                result["overall_similarity"] = int(round(sum(scores) / len(scores)))
            else:
                # Estimate from divergences: fewer divergences = higher similarity
                num_div = len(result["divergences"])
                result["overall_similarity"] = max(0, 100 - (num_div * 15))

        return result

    def _calculate_convergence_rate(self, similarity_scores: List[float]) -> float:
        """Calculate overall convergence rate from pairwise similarity scores."""
        if not similarity_scores:
            return 0.0

        # Average of all similarity scores
        return sum(similarity_scores) / len(similarity_scores) / 100

    def _calculate_confidence_score(
        self,
        convergence_rate: float,
        num_divergent_points: int,
        total_responses: int,
    ) -> float:
        """Calculate overall confidence score."""
        # Base score from convergence
        base_score = convergence_rate

        # Penalty for divergent points
        divergence_penalty = min(0.3, num_divergent_points * 0.05)

        # Bonus for more responses (more data = more confidence if consistent)
        response_bonus = min(0.1, (total_responses - 2) * 0.02) if convergence_rate > 0.7 else 0

        confidence = base_score - divergence_penalty + response_bonus
        return max(0.0, min(1.0, confidence))

    async def check(
        self,
        user_id: UUID,
        query: str,
        provider: str = "openai",
        model: Optional[str] = None,
        num_runs: int = 5,
        include_variations: bool = True,
        temperature: float = 0.7,
    ) -> ConsistencyCheck:
        """
        Execute consistency check by running the same query multiple times.
        """
        # Generate query variations if requested
        if include_variations:
            variations = await self._generate_variations(
                query, num_runs - 1, provider, model
            )
        else:
            variations = [query] * num_runs

        # Ensure we have exactly num_runs variations
        while len(variations) < num_runs:
            variations.append(query)
        variations = variations[:num_runs]

        # Execute all queries in parallel with semaphore limiting concurrency
        async def execute_query(index: int, variation: str) -> Dict[str, Any]:
            response = await self._execute_with_semaphore(
                llm_client.generate(
                    prompt=variation,
                    provider=provider,
                    model=model,
                    temperature=temperature,
                )
            )
            return {
                "run": index + 1,
                "query": variation,
                "response": response["content"],
                "model": response["model"],
            }

        # Run all queries concurrently (limited by semaphore)
        query_tasks = [
            execute_query(i, variation)
            for i, variation in enumerate(variations)
        ]
        responses = await asyncio.gather(*query_tasks)
        responses = list(responses)

        # Compare all responses in a single request
        comparison_result = await self._compare_all_responses(
            responses, provider, model
        )

        # Extract pairwise similarity scores
        similarity_scores = []
        for i in range(len(responses)):
            for j in range(i + 1, len(responses)):
                score = comparison_result["pairwise_scores"].get(
                    (i + 1, j + 1),
                    comparison_result["overall_similarity"]  # Fallback to overall
                )
                similarity_scores.append(score)

        # Process divergences
        all_divergences = []
        for div in comparison_result["divergences"]:
            all_divergences.append({
                "between_runs": "multiple",
                "point": div,
            })

        # Calculate metrics
        convergence_rate = self._calculate_convergence_rate(similarity_scores)
        confidence_score = self._calculate_confidence_score(
            convergence_rate,
            len(all_divergences),
            num_runs,
        )

        # Identify unique divergent points
        unique_divergences = []
        seen_points = set()
        for div in all_divergences:
            point_key = div["point"].lower()[:100]  # Simple deduplication
            if point_key not in seen_points:
                seen_points.add(point_key)
                unique_divergences.append(div)

        # Create ConsistencyCheck record
        consistency_check = ConsistencyCheck(
            user_id=user_id,
            original_query=query,
            query_variations=variations,
            responses=responses,
            convergence_rate=convergence_rate,
            confidence_score=confidence_score,
            divergent_points=unique_divergences if unique_divergences else None,
            total_runs=num_runs,
            model_provider=provider,
            model_name=model or "default",
        )
        self.db.add(consistency_check)
        self.db.commit()
        self.db.refresh(consistency_check)

        return consistency_check

    def get_check(self, check_id: UUID) -> Optional[ConsistencyCheck]:
        """Retrieve a consistency check by ID."""
        return self.db.query(ConsistencyCheck).filter(ConsistencyCheck.id == check_id).first()

    def get_user_checks(self, user_id: UUID, limit: int = 50) -> List[ConsistencyCheck]:
        """Get all consistency checks for a user."""
        return (
            self.db.query(ConsistencyCheck)
            .filter(ConsistencyCheck.user_id == user_id)
            .order_by(ConsistencyCheck.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_summary(self, check: ConsistencyCheck) -> Dict[str, Any]:
        """Get a summary of the consistency check results."""
        return {
            "query": check.original_query,
            "total_runs": check.total_runs,
            "convergence_rate": f"{check.convergence_rate * 100:.1f}%",
            "confidence_score": f"{check.confidence_score * 100:.1f}%",
            "num_divergent_points": len(check.divergent_points) if check.divergent_points else 0,
            "status": (
                "Alta Consistência" if check.convergence_rate > 0.8
                else "Média Consistência" if check.convergence_rate > 0.5
                else "Baixa Consistência"
            ),
            "recommendation": (
                "Os resultados são altamente confiáveis"
                if check.confidence_score > 0.8
                else "Revise os pontos divergentes antes de confiar nos resultados"
                if check.confidence_score > 0.5
                else "Os resultados podem não ser confiáveis - considere reformular a consulta"
            ),
        }
