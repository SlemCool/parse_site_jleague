from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole

payload = Chat(
    messages=[Messages(role=MessagesRole.SYSTEM, content="Ты бот помощник")],
    temperature=1.4,
    max_tokens=100,
)


def generate_horoscope(token, name="Дева"):
    """Generates horoscope on LLM, for a given name"""
    try:
        with GigaChat(credentials=token, verify_ssl_certs=False) as giga:
            user_input = f"Напиши гороскоп для {name}"
            payload.messages.append(
                Messages(role=MessagesRole.USER, content=user_input)
            )
            response = giga.chat(payload)
            payload.messages.append(response.choices[0].message)
            return response.choices[0].message.content
    except Exception as error:
        print(f"Ошибка генерации гороскопа: {error}")
