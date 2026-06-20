from pydantic import BaseModel, Field


class CreateTaskRequest(BaseModel):
    ideaText: str = Field(min_length=1, max_length=4000)
    assetIds: list[str] = Field(default_factory=list)


class TaskResult(BaseModel):
    gameId: str | None = None
    manifestUrl: str | None = None


class GenerationTaskResponse(BaseModel):
    id: str
    status: str
    currentStep: str
    ideaText: str
    assetIds: list[str]
    result: TaskResult
    errorMessage: str | None = None
    createdAt: str | None = None
    startedAt: str | None = None
    finishedAt: str | None = None
    retriedFromTaskId: str | None = None


class AgentLogResponse(BaseModel):
    id: str
    level: str
    nodeName: str
    message: str
    createdAt: str
