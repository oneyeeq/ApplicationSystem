from bot.dtos import RequestData


def format_user_requests(requests: list[RequestData]) -> str:
    request_lines = [
        (
            f"Заявка №{request.id}\n"
            f"Услуга: {request.service_name}\n"
            f"Статус: {request.status}"
        )
        for request in requests
    ]
    return "\n\n".join(request_lines)