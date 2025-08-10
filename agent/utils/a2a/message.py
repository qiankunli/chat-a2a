from typing import Tuple

from a2a.types import Message, Task, TaskArtifactUpdateEvent, TaskState, TaskStatusUpdateEvent, TextPart, Part


def get_text_from_message_parts(result: Task | Message | TaskStatusUpdateEvent | TaskArtifactUpdateEvent,
                                part_index: int = 0) -> Tuple[TaskState | None, str | None]:
    #todo 很不完整
    if isinstance(result, Task):
        artifacts = result.artifacts
        if not artifacts:
            return result.status.state, None
        part_root = artifacts[0].parts[part_index].root
        if isinstance(part_root, TextPart):
            return result.status.state, part_root.text
    elif isinstance(result, Message):
        return None, result.parts[part_index].text
    elif isinstance(result, TaskStatusUpdateEvent):
        part_root = result.status.message.parts[part_index].root
        if isinstance(part_root, TextPart):
            return result.status.state, part_root.text
    elif isinstance(result, TaskArtifactUpdateEvent):
        return None, result.artifact.content
    return None, None
