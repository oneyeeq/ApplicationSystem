from bot.dtos import RequestData


def format_user_requests(requests: list[RequestData]) -> str:
    request_lines = [
        (f"Заявка №{request.id}\nУслуга: {request.service_name}\nСтатус: {request.status}")
        for request in requests
    ]
    return "\n\n".join(request_lines)
