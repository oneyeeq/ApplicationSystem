from enum import Enum


class StatusEnum(str, Enum):
    NEW = "новая"
    IN_PROGRESS = "в_процессе"
    COMPLETED = "завершена"
    REJECTED = "отклонена"
