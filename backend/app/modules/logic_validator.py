"""
Module 3: Logic Validator (GoT)
Transforms reasoning into a graph of propositions.
Detects contradictions, logic gaps, hidden premises, and circularity.
"""

import re
import json
from typing import Dict, Any, List, Optional, Tuple
from uuid import UUID
import networkx as nx
from sqlalchemy.orm import Session

from app.modules.llm_client import llm_client
from app.models.reasoning import LogicGraph, LogicNode, LogicEdge, ReasoningTrace


EXTRACT_PROPOSITIONS_PROMPT = """Analise o seguinte raciocínio e extraia todas as proposições (premissas, inferências e conclusões).

Raciocínio:
{reasoning}

Para cada proposição, identifique:
1. O tipo da proposição (premissa, inferência ou conclusão)
2. O conteúdo exato
3. Quaisquer dependências (de quais outras proposições ela depende)
4. Se parece ser uma suposição oculta/não declarada

Formate sua resposta como:

<propositions>
<prop id="1">
<type>[premise|inference|conclusion|hidden_premise]</type>
<content>[A proposição]</content>
<depends_on>[lista de IDs de proposições separados por vírgula, ou "none"]</depends_on>
<confidence>[0-100]</confidence>
</prop>
... (repita para cada proposição)
</propositions>

<relationships>
<rel>
<from>[ID da proposição]</from>
<to>[ID da proposição]</to>
<type>[supports|contradicts|implies|depends_on]</type>
<strength>[0-100]</strength>
</rel>
... (repita para cada relacionamento)
</relationships>"""


VALIDATE_LOGIC_PROMPT = """Analise a seguinte estrutura lógica em busca de problemas:

Proposições:
{propositions}

Relacionamentos:
{relationships}

Por favor, identifique:
1. CONTRADIÇÕES: Quaisquer proposições que se contradizem
2. LACUNAS LÓGICAS: Passos faltantes na cadeia de raciocínio
3. PREMISSAS OCULTAS: Suposições não declaradas das quais o raciocínio depende
4. CIRCULARIDADE: Quaisquer padrões de raciocínio circular

Formate sua resposta como:

<analysis>
<contradictions>
<item>
<props>[IDs das proposições envolvidas]</props>
<explanation>[Por que elas se contradizem]</explanation>
<severity>[high|medium|low]</severity>
</item>
... (se houver)
</contradictions>

<logic_gaps>
<item>
<between>[IDs das proposições onde existe a lacuna]</between>
<missing>[Qual passo está faltando]</missing>
<severity>[high|medium|low]</severity>
</item>
... (se houver)
</logic_gaps>

<hidden_premises>
<item>
<relied_by>[IDs das proposições que dependem desta]</relied_by>
<premise>[A suposição oculta]</premise>
<importance>[high|medium|low]</importance>
</item>
... (se houver)
</hidden_premises>

<circularity>
<item>
<cycle>[IDs das proposições no ciclo]</cycle>
<explanation>[Como a circularidade se manifesta]</explanation>
</item>
... (se houver)
</circularity>

<overall_validity>[0-100]</overall_validity>
</analysis>"""


class LogicValidator:
    """Graph of Thought logic validator."""

    def __init__(self, db: Session):
        self.db = db

    async def _extract_propositions(
        self,
        reasoning: str,
        provider: str,
        model: Optional[str],
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Extract propositions and relationships from reasoning text."""
        prompt = EXTRACT_PROPOSITIONS_PROMPT.format(reasoning=reasoning)

        response = await llm_client.generate(
            prompt=prompt,
            provider=provider,
            model=model,
            temperature=0.3,
        )

        content = response["content"]
        propositions = []
        relationships = []

        # Parse propositions
        prop_pattern = r'<prop id="(\d+)">(.*?)</prop>'
        for match in re.finditer(prop_pattern, content, re.DOTALL):
            prop_id = match.group(1)
            prop_content = match.group(2)

            prop_type_match = re.search(r"<type>(.*?)</type>", prop_content)
            content_match = re.search(r"<content>(.*?)</content>", prop_content, re.DOTALL)
            depends_match = re.search(r"<depends_on>(.*?)</depends_on>", prop_content)
            confidence_match = re.search(r"<confidence>(\d+)</confidence>", prop_content)

            propositions.append({
                "id": prop_id,
                "type": prop_type_match.group(1).strip() if prop_type_match else "inference",
                "content": content_match.group(1).strip() if content_match else "",
                "depends_on": [
                    d.strip() for d in depends_match.group(1).split(",")
                    if d.strip() and d.strip().lower() != "none"
                ] if depends_match else [],
                "confidence": int(confidence_match.group(1)) / 100 if confidence_match else None,
            })

        # Parse relationships
        rel_pattern = r"<rel>(.*?)</rel>"
        for match in re.finditer(rel_pattern, content, re.DOTALL):
            rel_content = match.group(1)

            from_match = re.search(r"<from>(.*?)</from>", rel_content)
            to_match = re.search(r"<to>(.*?)</to>", rel_content)
            type_match = re.search(r"<type>(.*?)</type>", rel_content)
            strength_match = re.search(r"<strength>(\d+)</strength>", rel_content)

            if from_match and to_match:
                relationships.append({
                    "from": from_match.group(1).strip(),
                    "to": to_match.group(1).strip(),
                    "type": type_match.group(1).strip() if type_match else "implies",
                    "strength": int(strength_match.group(1)) / 100 if strength_match else None,
                })

        return propositions, relationships

    async def _validate_logic(
        self,
        propositions: List[Dict[str, Any]],
        relationships: List[Dict[str, Any]],
        provider: str,
        model: Optional[str],
    ) -> Dict[str, Any]:
        """Validate the logical structure for issues."""
        props_str = "\n".join([
            f"[{p['id']}] ({p['type']}): {p['content']}"
            for p in propositions
        ])
        rels_str = "\n".join([
            f"{r['from']} --{r['type']}--> {r['to']}"
            for r in relationships
        ])

        prompt = VALIDATE_LOGIC_PROMPT.format(
            propositions=props_str,
            relationships=rels_str,
        )

        response = await llm_client.generate(
            prompt=prompt,
            provider=provider,
            model=model,
            temperature=0.2,
        )

        content = response["content"]

        # Parse validation results
        validation = {
            "contradictions": [],
            "logic_gaps": [],
            "hidden_premises": [],
            "circularity": [],
            "overall_validity": 50,
        }

        # Parse contradictions
        contradictions_match = re.search(r"<contradictions>(.*?)</contradictions>", content, re.DOTALL)
        if contradictions_match:
            for item_match in re.finditer(r"<item>(.*?)</item>", contradictions_match.group(1), re.DOTALL):
                item = item_match.group(1)
                props_match = re.search(r"<props>(.*?)</props>", item)
                expl_match = re.search(r"<explanation>(.*?)</explanation>", item, re.DOTALL)
                sev_match = re.search(r"<severity>(.*?)</severity>", item)

                if props_match:
                    validation["contradictions"].append({
                        "propositions": props_match.group(1).strip(),
                        "explanation": expl_match.group(1).strip() if expl_match else "",
                        "severity": sev_match.group(1).strip() if sev_match else "medium",
                    })

        # Parse logic gaps
        gaps_match = re.search(r"<logic_gaps>(.*?)</logic_gaps>", content, re.DOTALL)
        if gaps_match:
            for item_match in re.finditer(r"<item>(.*?)</item>", gaps_match.group(1), re.DOTALL):
                item = item_match.group(1)
                between_match = re.search(r"<between>(.*?)</between>", item)
                missing_match = re.search(r"<missing>(.*?)</missing>", item, re.DOTALL)
                sev_match = re.search(r"<severity>(.*?)</severity>", item)

                if between_match:
                    validation["logic_gaps"].append({
                        "between": between_match.group(1).strip(),
                        "missing": missing_match.group(1).strip() if missing_match else "",
                        "severity": sev_match.group(1).strip() if sev_match else "medium",
                    })

        # Parse hidden premises
        hidden_match = re.search(r"<hidden_premises>(.*?)</hidden_premises>", content, re.DOTALL)
        if hidden_match:
            for item_match in re.finditer(r"<item>(.*?)</item>", hidden_match.group(1), re.DOTALL):
                item = item_match.group(1)
                relied_match = re.search(r"<relied_by>(.*?)</relied_by>", item)
                premise_match = re.search(r"<premise>(.*?)</premise>", item, re.DOTALL)
                imp_match = re.search(r"<importance>(.*?)</importance>", item)

                if premise_match:
                    validation["hidden_premises"].append({
                        "relied_by": relied_match.group(1).strip() if relied_match else "",
                        "premise": premise_match.group(1).strip(),
                        "importance": imp_match.group(1).strip() if imp_match else "medium",
                    })

        # Parse circularity
        circ_match = re.search(r"<circularity>(.*?)</circularity>", content, re.DOTALL)
        if circ_match:
            for item_match in re.finditer(r"<item>(.*?)</item>", circ_match.group(1), re.DOTALL):
                item = item_match.group(1)
                cycle_match = re.search(r"<cycle>(.*?)</cycle>", item)
                expl_match = re.search(r"<explanation>(.*?)</explanation>", item, re.DOTALL)

                if cycle_match:
                    validation["circularity"].append({
                        "cycle": cycle_match.group(1).strip(),
                        "explanation": expl_match.group(1).strip() if expl_match else "",
                    })

        # Parse overall validity
        validity_match = re.search(r"<overall_validity>(\d+)</overall_validity>", content)
        if validity_match:
            validation["overall_validity"] = int(validity_match.group(1))

        return validation

    def _detect_cycles(self, relationships: List[Dict[str, Any]]) -> List[List[str]]:
        """Use NetworkX to detect cycles in the graph."""
        G = nx.DiGraph()

        for rel in relationships:
            G.add_edge(rel["from"], rel["to"])

        try:
            cycles = list(nx.simple_cycles(G))
            return cycles
        except:
            return []

    async def validate(
        self,
        user_id: UUID,
        reasoning_trace_id: Optional[UUID] = None,
        raw_text: Optional[str] = None,
        provider: str = "openai",
        model: Optional[str] = None,
    ) -> LogicGraph:
        """
        Validate the logic of a reasoning trace or raw text.
        """
        # Get reasoning text
        if reasoning_trace_id:
            trace = self.db.query(ReasoningTrace).filter(
                ReasoningTrace.id == reasoning_trace_id
            ).first()
            if not trace:
                raise ValueError(f"Reasoning trace not found: {reasoning_trace_id}")
            reasoning_text = trace.raw_response
        elif raw_text:
            reasoning_text = raw_text
        else:
            raise ValueError("Either reasoning_trace_id or raw_text must be provided")

        # Extract propositions and relationships
        propositions, relationships = await self._extract_propositions(
            reasoning_text, provider, model
        )

        # Validate logic
        validation = await self._validate_logic(
            propositions, relationships, provider, model
        )

        # Detect cycles using graph analysis
        detected_cycles = self._detect_cycles(relationships)

        # Merge detected cycles with LLM-identified circularity
        if detected_cycles and not validation["circularity"]:
            for cycle in detected_cycles:
                validation["circularity"].append({
                    "cycle": " -> ".join(cycle),
                    "explanation": "Cycle detected via graph analysis",
                })

        # Build graph structure for storage
        graph_structure = {
            "propositions": propositions,
            "relationships": relationships,
        }

        # Create LogicGraph record
        logic_graph = LogicGraph(
            user_id=user_id,
            reasoning_trace_id=reasoning_trace_id,
            graph_structure=graph_structure,
            has_contradictions=len(validation["contradictions"]) > 0,
            has_logic_gaps=len(validation["logic_gaps"]) > 0,
            has_hidden_premises=len(validation["hidden_premises"]) > 0,
            has_circularity=len(validation["circularity"]) > 0,
            contradictions=validation["contradictions"] if validation["contradictions"] else None,
            logic_gaps=validation["logic_gaps"] if validation["logic_gaps"] else None,
            hidden_premises=validation["hidden_premises"] if validation["hidden_premises"] else None,
            circular_references=validation["circularity"] if validation["circularity"] else None,
            overall_validity_score=validation["overall_validity"] / 100,
        )
        self.db.add(logic_graph)
        self.db.flush()

        # Create LogicNode records
        node_id_map = {}
        for prop in propositions:
            node = LogicNode(
                graph_id=logic_graph.id,
                node_type=prop["type"],
                content=prop["content"],
                truth_value=None,
                confidence=prop["confidence"],
            )
            self.db.add(node)
            self.db.flush()
            node_id_map[prop["id"]] = node.id

        # Create LogicEdge records
        for rel in relationships:
            if rel["from"] in node_id_map and rel["to"] in node_id_map:
                edge = LogicEdge(
                    graph_id=logic_graph.id,
                    source_node_id=node_id_map[rel["from"]],
                    target_node_id=node_id_map[rel["to"]],
                    edge_type=rel["type"],
                    strength=rel["strength"],
                )
                self.db.add(edge)

        self.db.commit()
        self.db.refresh(logic_graph)

        return logic_graph

    def get_graph(self, graph_id: UUID) -> Optional[LogicGraph]:
        """Retrieve a logic graph by ID."""
        return self.db.query(LogicGraph).filter(LogicGraph.id == graph_id).first()

    def get_user_graphs(self, user_id: UUID, limit: int = 50) -> List[LogicGraph]:
        """Get all logic graphs for a user."""
        return (
            self.db.query(LogicGraph)
            .filter(LogicGraph.user_id == user_id)
            .order_by(LogicGraph.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_graph_for_visualization(self, graph_id: UUID) -> Optional[Dict[str, Any]]:
        """Get graph data formatted for visualization."""
        graph = self.get_graph(graph_id)
        if not graph:
            return None

        # Format for D3.js/React Flow
        nodes = []
        edges = []

        for node in graph.nodes:
            nodes.append({
                "id": str(node.id),
                "type": node.node_type,
                "label": node.content[:50] + "..." if len(node.content) > 50 else node.content,
                "fullContent": node.content,
                "confidence": node.confidence,
            })

        for edge in graph.edges:
            edges.append({
                "id": str(edge.id),
                "source": str(edge.source_node_id),
                "target": str(edge.target_node_id),
                "type": edge.edge_type,
                "strength": edge.strength,
            })

        return {
            "nodes": nodes,
            "edges": edges,
            "issues": {
                "contradictions": graph.contradictions,
                "logic_gaps": graph.logic_gaps,
                "hidden_premises": graph.hidden_premises,
                "circularity": graph.circular_references,
            },
            "validity_score": graph.overall_validity_score,
        }
