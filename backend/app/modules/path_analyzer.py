"""
Module 2: Path Analyzer (ToT)
Decomposes problems into subproblems, explores multiple hypotheses
in parallel (tree of possibilities), and documents pruning of
less promising paths.
"""

import json
from typing import Dict, Any, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.modules.llm_client import llm_client
from app.models.reasoning import PathAnalysis, PathNode


DECOMPOSITION_PROMPT = """Analyze the following problem and decompose it into smaller, manageable subproblems.

Problem: {problem}

Please structure your response as follows:

<decomposition>
<main_goal>
[State the main goal clearly]
</main_goal>

<subproblems>
1. [First subproblem]
2. [Second subproblem]
3. [Third subproblem]
... (as many as needed)
</subproblems>

<dependencies>
[Describe any dependencies between subproblems]
</dependencies>
</decomposition>"""


HYPOTHESIS_PROMPT = """Given the following context, generate {breadth} distinct hypotheses or approaches to solve this subproblem.

Context: {context}
Current subproblem: {subproblem}
Parent hypothesis (if any): {parent}

For each hypothesis, provide:
1. A clear statement of the approach
2. Potential benefits
3. Potential risks or limitations

<hypotheses>
<hypothesis_1>
<approach>[Your approach]</approach>
<benefits>[Benefits]</benefits>
<risks>[Risks]</risks>
</hypothesis_1>
... (repeat for each hypothesis)
</hypotheses>"""


EVALUATION_PROMPT = """Evaluate the following hypothesis for solving the problem.

Problem context: {context}
Hypothesis: {hypothesis}

Rate this hypothesis on a scale of 0-100 based on:
1. Feasibility (can it be done?)
2. Effectiveness (will it solve the problem?)
3. Efficiency (is it a good use of resources?)
4. Completeness (does it address all aspects?)

<evaluation>
<feasibility_score>[0-100]</feasibility_score>
<effectiveness_score>[0-100]</effectiveness_score>
<efficiency_score>[0-100]</efficiency_score>
<completeness_score>[0-100]</completeness_score>
<overall_score>[0-100]</overall_score>
<reasoning>[Brief explanation]</reasoning>
<should_prune>[yes/no]</should_prune>
<prune_reason>[If yes, why should this be pruned]</prune_reason>
</evaluation>"""


class PathAnalyzer:
    """Tree of Thought path analyzer."""

    def __init__(self, db: Session):
        self.db = db
        self.pruning_threshold = 30  # Paths with score below this are pruned

    async def _decompose_problem(
        self,
        problem: str,
        provider: str,
        model: Optional[str],
    ) -> Dict[str, Any]:
        """Decompose a problem into subproblems."""
        prompt = DECOMPOSITION_PROMPT.format(problem=problem)

        response = await llm_client.generate(
            prompt=prompt,
            provider=provider,
            model=model,
            temperature=0.7,
        )

        content = response["content"]

        # Parse the decomposition
        decomposition = {
            "main_goal": "",
            "subproblems": [],
            "dependencies": "",
        }

        import re

        main_goal_match = re.search(r"<main_goal>(.*?)</main_goal>", content, re.DOTALL)
        if main_goal_match:
            decomposition["main_goal"] = main_goal_match.group(1).strip()

        subproblems_match = re.search(r"<subproblems>(.*?)</subproblems>", content, re.DOTALL)
        if subproblems_match:
            text = subproblems_match.group(1).strip()
            subproblems = []
            for line in text.split("\n"):
                line = line.strip()
                if line and re.match(r"^\d+\.", line):
                    subproblems.append(re.sub(r"^\d+\.\s*", "", line))
            decomposition["subproblems"] = subproblems

        deps_match = re.search(r"<dependencies>(.*?)</dependencies>", content, re.DOTALL)
        if deps_match:
            decomposition["dependencies"] = deps_match.group(1).strip()

        return decomposition

    async def _generate_hypotheses(
        self,
        context: str,
        subproblem: str,
        parent: str,
        breadth: int,
        provider: str,
        model: Optional[str],
    ) -> List[Dict[str, Any]]:
        """Generate multiple hypotheses for a subproblem."""
        prompt = HYPOTHESIS_PROMPT.format(
            context=context,
            subproblem=subproblem,
            parent=parent or "None",
            breadth=breadth,
        )

        response = await llm_client.generate(
            prompt=prompt,
            provider=provider,
            model=model,
            temperature=0.8,  # Higher temperature for more diverse hypotheses
        )

        content = response["content"]
        hypotheses = []

        import re

        # Parse each hypothesis
        for i in range(1, breadth + 1):
            pattern = rf"<hypothesis_{i}>(.*?)</hypothesis_{i}>"
            match = re.search(pattern, content, re.DOTALL)
            if match:
                hyp_content = match.group(1)

                approach_match = re.search(r"<approach>(.*?)</approach>", hyp_content, re.DOTALL)
                benefits_match = re.search(r"<benefits>(.*?)</benefits>", hyp_content, re.DOTALL)
                risks_match = re.search(r"<risks>(.*?)</risks>", hyp_content, re.DOTALL)

                hypotheses.append({
                    "approach": approach_match.group(1).strip() if approach_match else "",
                    "benefits": benefits_match.group(1).strip() if benefits_match else "",
                    "risks": risks_match.group(1).strip() if risks_match else "",
                })

        return hypotheses

    async def _evaluate_hypothesis(
        self,
        context: str,
        hypothesis: str,
        provider: str,
        model: Optional[str],
    ) -> Dict[str, Any]:
        """Evaluate a hypothesis and determine if it should be pruned."""
        prompt = EVALUATION_PROMPT.format(
            context=context,
            hypothesis=hypothesis,
        )

        response = await llm_client.generate(
            prompt=prompt,
            provider=provider,
            model=model,
            temperature=0.3,  # Lower temperature for more consistent evaluation
        )

        content = response["content"]
        evaluation = {
            "overall_score": 50,
            "should_prune": False,
            "prune_reason": None,
            "reasoning": "",
        }

        import re

        score_match = re.search(r"<overall_score>(\d+)</overall_score>", content)
        if score_match:
            evaluation["overall_score"] = int(score_match.group(1))

        prune_match = re.search(r"<should_prune>(yes|no)</should_prune>", content, re.IGNORECASE)
        if prune_match:
            evaluation["should_prune"] = prune_match.group(1).lower() == "yes"

        prune_reason_match = re.search(r"<prune_reason>(.*?)</prune_reason>", content, re.DOTALL)
        if prune_reason_match:
            evaluation["prune_reason"] = prune_reason_match.group(1).strip()

        reasoning_match = re.search(r"<reasoning>(.*?)</reasoning>", content, re.DOTALL)
        if reasoning_match:
            evaluation["reasoning"] = reasoning_match.group(1).strip()

        # Force prune if score is below threshold
        if evaluation["overall_score"] < self.pruning_threshold:
            evaluation["should_prune"] = True
            if not evaluation["prune_reason"]:
                evaluation["prune_reason"] = f"Score below threshold ({evaluation['overall_score']} < {self.pruning_threshold})"

        return evaluation

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
        """
        # Decompose the problem
        decomposition = await self._decompose_problem(problem, provider, model)

        # Create analysis record
        analysis = PathAnalysis(
            user_id=user_id,
            original_problem=problem,
            decomposition=decomposition,
            exploration_tree={},
            pruned_paths=[],
            selected_path=None,
            total_nodes_explored=0,
            total_paths_pruned=0,
            model_provider=provider,
            model_name=model or "default",
        )
        self.db.add(analysis)
        self.db.flush()

        # Build exploration tree
        exploration_tree = {
            "root": {
                "problem": problem,
                "goal": decomposition["main_goal"],
                "subproblems": decomposition["subproblems"],
                "branches": [],
            }
        }

        pruned_paths = []
        nodes_explored = 0
        paths_pruned = 0

        # Explore each subproblem
        for subproblem in decomposition["subproblems"]:
            branch = {
                "subproblem": subproblem,
                "hypotheses": [],
            }

            # Generate hypotheses
            hypotheses = await self._generate_hypotheses(
                context=problem,
                subproblem=subproblem,
                parent=None,
                breadth=breadth,
                provider=provider,
                model=model,
            )

            for hyp in hypotheses:
                nodes_explored += 1

                # Evaluate hypothesis
                evaluation = await self._evaluate_hypothesis(
                    context=f"Problem: {problem}\nSubproblem: {subproblem}",
                    hypothesis=hyp["approach"],
                    provider=provider,
                    model=model,
                )

                hypothesis_node = {
                    "approach": hyp["approach"],
                    "benefits": hyp["benefits"],
                    "risks": hyp["risks"],
                    "score": evaluation["overall_score"],
                    "is_pruned": evaluation["should_prune"],
                    "prune_reason": evaluation["prune_reason"],
                    "children": [],
                }

                if evaluation["should_prune"]:
                    paths_pruned += 1
                    pruned_paths.append({
                        "subproblem": subproblem,
                        "hypothesis": hyp["approach"],
                        "reason": evaluation["prune_reason"],
                        "score": evaluation["overall_score"],
                    })
                else:
                    # If not pruned and we haven't reached max depth, explore deeper
                    if max_depth > 1:
                        # Generate next level hypotheses
                        deeper_hypotheses = await self._generate_hypotheses(
                            context=f"Problem: {problem}\nSubproblem: {subproblem}",
                            subproblem=f"How to implement: {hyp['approach']}",
                            parent=hyp["approach"],
                            breadth=max(2, breadth - 1),
                            provider=provider,
                            model=model,
                        )

                        for deeper_hyp in deeper_hypotheses:
                            nodes_explored += 1
                            deeper_eval = await self._evaluate_hypothesis(
                                context=f"Problem: {problem}\nApproach: {hyp['approach']}",
                                hypothesis=deeper_hyp["approach"],
                                provider=provider,
                                model=model,
                            )

                            deeper_node = {
                                "approach": deeper_hyp["approach"],
                                "score": deeper_eval["overall_score"],
                                "is_pruned": deeper_eval["should_prune"],
                                "prune_reason": deeper_eval["prune_reason"],
                            }

                            if deeper_eval["should_prune"]:
                                paths_pruned += 1
                                pruned_paths.append({
                                    "parent": hyp["approach"],
                                    "hypothesis": deeper_hyp["approach"],
                                    "reason": deeper_eval["prune_reason"],
                                    "score": deeper_eval["overall_score"],
                                })

                            hypothesis_node["children"].append(deeper_node)

                branch["hypotheses"].append(hypothesis_node)

                # Create PathNode record
                path_node = PathNode(
                    analysis_id=analysis.id,
                    depth=0,
                    hypothesis=hyp["approach"],
                    evaluation_score=evaluation["overall_score"],
                    is_pruned=evaluation["should_prune"],
                    pruning_reason=evaluation["prune_reason"],
                )
                self.db.add(path_node)

            exploration_tree["root"]["branches"].append(branch)

        # Find best path
        best_path = self._select_best_path(exploration_tree)

        # Update analysis
        analysis.exploration_tree = exploration_tree
        analysis.pruned_paths = pruned_paths
        analysis.selected_path = best_path
        analysis.total_nodes_explored = nodes_explored
        analysis.total_paths_pruned = paths_pruned

        self.db.commit()
        self.db.refresh(analysis)

        return analysis

    def _select_best_path(self, tree: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Select the best path from the exploration tree."""
        best_path = None
        best_score = 0

        for branch in tree["root"]["branches"]:
            for hyp in branch["hypotheses"]:
                if not hyp["is_pruned"] and hyp["score"] > best_score:
                    best_score = hyp["score"]
                    best_path = {
                        "subproblem": branch["subproblem"],
                        "selected_approach": hyp["approach"],
                        "score": hyp["score"],
                        "benefits": hyp["benefits"],
                        "implementation_steps": [
                            child["approach"]
                            for child in hyp.get("children", [])
                            if not child["is_pruned"]
                        ],
                    }

        return best_path

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
