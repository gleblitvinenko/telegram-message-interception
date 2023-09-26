from os import path
from pyrogram import Client, filters
from pyrogram import types
import csv
import configparser

# в файл config.ini потрібно вписати api_id, api_hash, та дані для проксі.

config = configparser.ConfigParser()
config.read("config.ini")
app = Client("account", api_id=int(config["pyrogram"]["api_id"]), api_hash=config["pyrogram"]["api_hash"])

chat_id: int | None = None
key_words: set[str] = {"test", "test2", "test3"}


def save_message(message: types.Message) -> None:
    headers = ["Chat name", "Time", "Message", "Username"]
    file_exists = path.exists("intercept_message.csv")
    with open("intercept_message.csv", 'a',  encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if not file_exists or f.tell() == 0:
            writer.writerow(headers)
        writer.writerow([message.chat.title, message.date, message.caption if message.text is None else message.text, message.from_user.username])


async def get_entity_id(url: str) -> int:
    """
    Get the entity ID from a given URL.

    Args:
        url (str): The URL to extract the entity ID from.

    Returns:
        int: The extracted entity ID.
    """
    try:
        chat_info = await app.get_chat(url)
        return chat_info.id
    except Exception as ex:
        print(ex)


@app.on_message(filters.command("set_url", prefixes=["/", "."]))
async def set_url(client: Client, message: types.Message):
    chat_name = message.text.split("/")[-1]
    global chat_id
    chat_id = await get_entity_id(url=chat_name)


@app.on_message(filters.text | filters.photo)
def parse(client: Client, message: types.Message):
    if message.chat.id == chat_id:
        if any(word in (message.text or '') or word in (message.caption or '') for word in key_words):
            save_message(message)


if __name__ == "__main__":
    app.run()
