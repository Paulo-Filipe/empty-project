from datetime import datetime

class LLM_PROVIDE_MOCK:
    def invoke():
        return {}


class EVENT_SHAPE:
    type: str
    id: str
    timestamp: datetime

#  in this case is the same, because there is no sensible data, but in real scenarios, it will be diff.
class LLM_DTO:
    type: str
    id: str
    timestamp: datetime
    

TYPE_OF_EVENTS = ['pr_opened','pr_merged','deployment', 'incident'] 

def generate_team_insight(team_id, events: list[EVENT_SHAPE], llmProvider: LLM_PROVIDE_MOCK):

    # filter for bad formed or invalid events -> THROW EXCEPTION ON MALFORMED (?)

    parsed_events = []

    for event in events:
        if not event[EVENT_SHAPE.type] in TYPE_OF_EVENTS:
            raise TypeError(f'{event[EVENT_SHAPE.type]} is not a supported type event')
        # filter event into a type safe payload for LLM. not very memory eficient, I know.
        parsed_events.push({ 'id': event['id'], 'type': event['type'], 'timestamp': event['timestamp']})
    
    

   

    



    # calculate deterministic data (like delta time between events - cycle time)
    # LLM Inference
    # LLM retry -> if not reponded.
    # LLM  response format validation.
    # return format insurance
    

    return {
        "team_id": team_id,
        "metrics": {},
        "insight": {
            "summary": '',
            "recommentations": ''
        }
    }
