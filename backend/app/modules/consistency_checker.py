"""
Module 4: Consistency Checker
Executes the same query multiple times with variations,
calculates convergence rate, and generates a confidence score.
"""

import re
import json
from typing import Dict, Any, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
import numpy as np

from app.modules.llm_client import llm_client
from app.models.reasoning import ConsistencyCheck


VARIATION_PROMPT = """Generate {num_variations} semantically equivalent variations of the following query.
Each variation should ask the same thing but use different wording, structure, or perspective.

Original query: {query}

Format your response as:
<variations>
<v1>[First variation]</v1>
<v2>[Second variation]</v2>
... (and so on)
</variations>"""


COMPARE_RESPONSES_PROMPT = """Compare the following responses to determine if they are semantically consistent.
Identify the core claims/conclusions in each response and check if they agree or diverge.

Response 1: {response1}

Response 2: {response2}

Format your analysis as:
<comparison>
<core_claims_1>
- [Claim 1 from response 1]
- [Claim 2 from response 1]
...
</core_claims_1>

<core_claims_2>
- [Claim 1 from response 2]
- [Claim 2 from response 2]
...
</core_claims_2>

<agreements>
- [Point where they agree]
...
</agreements>

<divergences>
- [Point where they diverge]
- [Severity: high/medium/low]
...
</divergences>

<similarity_score>[0-100]</similarity_score>
</comparison>"""


class ConsistencyChecker:
    """Multi-run consistency analyzer."""

    def __init__(self, db: Session):
        self.db = db

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

        content = response["content"]
        variations = [query]  # Include original

        # Parse variations
        for i in range(1, num_variations + 1):
            pattern = rf"<v{i}>(.*?)</v{i}>"
            match = re.search(pattern, content, re.DOTALL)
            if match:
                variations.append(match.group(1).strip())

        return variations

    async def _compare_responses(
        self,
        response1: str,
        response2: str,
        provider: str,
        model: Optional[str],
    ) -> Dict[str, Any]:
        """Compare two responses for semantic consistency."""
        prompt = COMPARE_RESPONSES_PROMPT.format(
            response1=response1,
            response2=response2,
        )

        response = await llm_client.generate(
            prompt=prompt,
            provider=provider,
            model=model,
            temperature=0.2,
        )

        content = response["content"]

        comparison = {
            "similarity_score": 50,
            "agreements": [],
            "divergences": [],
        }

        # Parse similarity score
        score_match = re.search(r"<similarity_score>(\d+)</similarity_score>", content)
        if score_match:
            comparison["similarity_score"] = int(score_match.group(1))

        # Parse agreements
        agreements_match = re.search(r"<agreements>(.*?)</agreements>", content, re.DOTALL)
        if agreements_match:
            text = agreements_match.group(1)
            agreements = [
                line.strip().lstrip("- ").strip()
                for line in text.split("\n")
                if line.strip() and line.strip() != "-"
            ]
            comparison["agreements"] = agreements

        # Parse divergences
        divergences_match = re.search(r"<divergences>(.*?)</divergences>", content, re.DOTALL)
        if divergences_match:
            text = divergences_match.group(1)
            divergences = [
                line.strip().lstrip("- ").strip()
                for line in text.split("\n")
                if line.strip() and line.strip() != "-"
            ]
            comparison["divergences"] = divergences

        return comparison

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

        # Execute each query
        responses = []
        for i, variation in enumerate(variations):
            response = await llm_client.generate(
                prompt=variation,
                provider=provider,
                model=model,
                temperature=temperature,
            )

            responses.append({
                "run": i + 1,
                "query": variation,
                "response": response["content"],
                "model": response["model"],
            })

        # Compare responses pairwise
        similarity_scores = []
        all_divergences = []

        for i in range(len(responses)):
            for j in range(i + 1, len(responses)):
                comparison = await self._compare_responses(
                    responses[i]["response"],
                    responses[j]["response"],
                    provider,
                    model,
                )
                similarity_scores.append(comparison["similarity_score"])

                for div in comparison["divergences"]:
                    all_divergences.append({
                        "between_runs": [i + 1, j + 1],
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
                "High Consistency" if check.convergence_rate > 0.8
                else "Medium Consistency" if check.convergence_rate > 0.5
                else "Low Consistency"
            ),
            "recommendation": (
                "Results are highly reliable"
                if check.confidence_score > 0.8
                else "Review divergent points before relying on results"
                if check.confidence_score > 0.5
                else "Results may be unreliable - consider rephrasing the query"
            ),
        }
