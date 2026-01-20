"""
Module 2: Path Analyzer (ToT)
Decomposes problems into subproblems, explores multiple hypotheses
in parallel (tree of possibilities), and documents pruning of
less promising paths.

OPTIMIZED VERSION: Uses a single LLM request to perform the complete
Tree of Thought analysis, avoiding multiple API calls.
"""

import json
import re
from typing import Dict, Any, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.modules.llm_client import llm_client
from app.models.reasoning import PathAnalysis, PathNode


# Single comprehensive prompt for complete ToT analysis
TOT_ANALYSIS_PROMPT = """You are an expert problem-solving analyst using the Tree of Thought methodology.

Analyze the following problem completely in ONE response:

PROBLEM: {problem}

Perform a complete Tree of Thought analysis with the following structure:

1. DECOMPOSITION: Break down the problem into 2-4 key subproblems
2. HYPOTHESIS GENERATION: For each subproblem, generate 2-3 possible approaches
3. EVALUATION: Score each approach (0-100) and decide if it should be pruned (score < 40)
4. BEST PATH SELECTION: Identify the most promising solution path

Respond EXACTLY in this JSON format (no markdown, no extra text):
{{
    "main_goal": "Clear statement of the main goal",
    "dependencies": "Brief description of dependencies between subproblems",
    "subproblems": [
        {{
            "description": "Subproblem description",
            "hypotheses": [
                {{
                    "approach": "Approach description",
                    "benefits": "Key benefits",
                    "risks": "Key risks",
                    "score": 75,
                    "is_pruned": false,
                    "prune_reason": null,
                    "implementation_steps": ["Step 1", "Step 2"]
                }}
            ]
        }}
    ],
    "best_path": {{
        "subproblem": "The subproblem being solved",
        "selected_approach": "The best approach",
        "score": 85,
        "benefits": "Why this is the best choice",
        "implementation_steps": ["Step 1", "Step 2", "Step 3"]
    }},
    "summary": "Brief summary of the analysis and recommendation"
}}

IMPORTANT:
- Generate exactly 2-4 subproblems (keep it focused)
- Generate exactly 2-3 hypotheses per subproblem
- Prune hypotheses with score < 40
- Select the single best path based on highest score
- Be concise but thorough"""


class PathAnalyzer:
    """
    Tree of Thought path analyzer.

    OPTIMIZED: Performs complete ToT analysis in a single LLM request
    instead of multiple requests for decomposition, hypothesis generation,
    and evaluation separately.
    """

    def __init__(self, db: Session):
        self.db = db
        self.pruning_threshold = 40  # Paths with score below this are pruned

    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """Parse JSON response from LLM, handling common formatting issues."""
        # Remove markdown code blocks if present
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to find JSON object in the response
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass

            # Return a default structure if parsing fails
            return {
                "main_goal": "Unable to parse response",
                "dependencies": "",
                "subproblems": [],
                "best_path": None,
                "summary": "Error parsing LLM response"
            }

    async def analyze(
        self,
        user_id: UUID,
        problem: str,
        provider: str = "openai",
        model: Optional[str] = None,
        max_depth: int = 3,
        breadth: int = 3,
    ) -> PathAnalysis:
        """
        Perform Tree of Thought analysis on a problem.

        OPTIMIZED: Uses a single LLM request to perform the complete analysis,
        reducing API calls from 40+ to just 1.
        """
        # Single LLM request for complete analysis
        prompt = TOT_ANALYSIS_PROMPT.format(problem=problem)

        response = await llm_client.generate(
            prompt=prompt,
            provider=provider,
            model=model,
            temperature=0.7,
        )

        # Parse the response
        analysis_data = self._parse_json_response(response["content"])

        # Build decomposition structure
        decomposition = {
            "main_goal": analysis_data.get("main_goal", ""),
            "subproblems": [sp.get("description", "") for sp in analysis_data.get("subproblems", [])],
            "dependencies": analysis_data.get("dependencies", ""),
        }

        # Build exploration tree from the analysis
        exploration_tree = {
            "root": {
                "problem": problem,
                "goal": analysis_data.get("main_goal", ""),
                "subproblems": decomposition["subproblems"],
                "branches": [],
            }
        }

        pruned_paths = []
        nodes_explored = 0
        paths_pruned = 0

        # Process subproblems and hypotheses from the single response
        for subproblem_data in analysis_data.get("subproblems", []):
            branch = {
                "subproblem": subproblem_data.get("description", ""),
                "hypotheses": [],
            }

            for hyp in subproblem_data.get("hypotheses", []):
                nodes_explored += 1

                is_pruned = hyp.get("is_pruned", False)
                score = hyp.get("score", 50)

                # Apply pruning threshold
                if score < self.pruning_threshold:
                    is_pruned = True

                hypothesis_node = {
                    "approach": hyp.get("approach", ""),
                    "benefits": hyp.get("benefits", ""),
                    "risks": hyp.get("risks", ""),
                    "score": score,
                    "is_pruned": is_pruned,
                    "prune_reason": hyp.get("prune_reason"),
                    "children": [
                        {"approach": step, "score": score, "is_pruned": False, "prune_reason": None}
                        for step in hyp.get("implementation_steps", [])
                    ],
                }

                if is_pruned:
                    paths_pruned += 1
                    pruned_paths.append({
                        "subproblem": subproblem_data.get("description", ""),
                        "hypothesis": hyp.get("approach", ""),
                        "reason": hyp.get("prune_reason") or f"Score below threshold ({score} < {self.pruning_threshold})",
                        "score": score,
                    })

                branch["hypotheses"].append(hypothesis_node)

            exploration_tree["root"]["branches"].append(branch)

        # Get best path from the analysis
        best_path = analysis_data.get("best_path")
        if best_path:
            best_path = {
                "subproblem": best_path.get("subproblem", ""),
                "selected_approach": best_path.get("selected_approach", ""),
                "score": best_path.get("score", 0),
                "benefits": best_path.get("benefits", ""),
                "implementation_steps": best_path.get("implementation_steps", []),
            }

        # Create analysis record
        analysis = PathAnalysis(
            user_id=user_id,
            original_problem=problem,
            decomposition=decomposition,
            exploration_tree=exploration_tree,
            pruned_paths=pruned_paths,
            selected_path=best_path,
            total_nodes_explored=nodes_explored,
            total_paths_pruned=paths_pruned,
            model_provider=provider,
            model_name=model or "default",
        )
        self.db.add(analysis)
        self.db.flush()

        # Create PathNode records for each hypothesis
        for branch in exploration_tree["root"]["branches"]:
            for hyp in branch["hypotheses"]:
                path_node = PathNode(
                    analysis_id=analysis.id,
                    depth=0,
                    hypothesis=hyp["approach"],
                    evaluation_score=hyp["score"],
                    is_pruned=hyp["is_pruned"],
                    pruning_reason=hyp["prune_reason"],
                )
                self.db.add(path_node)

        self.db.commit()
        self.db.refresh(analysis)

        return analysis

    def get_analysis(self, analysis_id: UUID) -> Optional[PathAnalysis]:
        """Retrieve a path analysis by ID."""
        return self.db.query(PathAnalysis).filter(PathAnalysis.id == analysis_id).first()

    def get_user_analyses(self, user_id: UUID, limit: int = 50) -> List[PathAnalysis]:
        """Get all path analyses for a user."""
        return (
            self.db.query(PathAnalysis)
            .filter(PathAnalysis.user_id == user_id)
            .order_by(PathAnalysis.created_at.desc())
            .limit(limit)
            .all()
        )
