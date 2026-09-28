import json
from datetime import datetime
from typing import TypedDict


class Event(TypedDict):
    type: str
    id: str
    timestamp: datetime


class LLMProviderMock:
    def invoke(self, prompt: str) -> dict:
        return {'summary': '', 'recommendations': []}


EVENT_TYPES = frozenset({'pr_opened', 'pr_merged', 'deployment', 'incident'})


def generate_team_insight(team_id: str, events: list[Event], llm_client: LLMProviderMock) -> dict:
    parsed_events = []
    for event in events:
        if event['type'] not in EVENT_TYPES:
            raise ValueError(f"unsupported event type: {event['type']!r}")
        parsed_events.append({'id': event['id'], 'type': event['type'], 'timestamp': event['timestamp']})

    by_id = {}
    for e in parsed_events:
        if e['id'] not in by_id:
            by_id[e['id']] = []
        by_id[e['id']].append(e)

    cycle_times = []
    for _, pr_events in by_id.items():
        types = {e['type'] for e in pr_events}
        if 'pr_opened' in types and 'pr_merged' in types:
            opened = next(e['timestamp'] for e in pr_events if e['type'] == 'pr_opened')
            merged = next(e['timestamp'] for e in pr_events if e['type'] == 'pr_merged')
            cycle_times.append((merged - opened).total_seconds() / 3600)

    metrics = {
        'merged_prs': len(cycle_times),
        'average_pr_cycle_time_hours': sum(cycle_times) / len(cycle_times) if cycle_times else 0,
        'deployments': sum(1 for e in parsed_events if e['type'] == 'deployment'),
        'incidents': sum(1 for e in parsed_events if e['type'] == 'incident'),
    }

    prompt = f"""Analyze this team's metrics and provide brief insights.
Metrics: {metrics}

Respond with JSON:
{{"summary": "one sentence summary", "recommendations": ["recommendation 1", "recommendation 2"]}}"""

    insight = None
    for attempt in range(3):
        try:
            response = llm_client.invoke(prompt)
            if isinstance(response, str):
                response = json.loads(response)
            if not isinstance(response, dict) or 'summary' not in response or 'recommendations' not in response:
                raise ValueError("missing required fields: summary, recommendations")
            insight = response
            break
        except (json.JSONDecodeError, ValueError) as e:
            if attempt == 2:
                insight = {'summary': '', 'recommendations': []}

    if insight is None:
        insight = {'summary': '', 'recommendations': []}

    return {
        'team_id': team_id,
        'metrics': metrics,
        'insight': insight,
    }