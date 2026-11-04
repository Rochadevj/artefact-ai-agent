import json
import os

from dotenv import load_dotenv
from groq import Groq

from src.policies import search_policies
from src.prompts import SYSTEM_PROMPT
from src.tools import (
    get_active_promotions,
    get_order_status,
    search_products,
)


load_dotenv()


API_KEY = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")


if not API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY was not found. Add it to your .env file."
    )


client = Groq(api_key=API_KEY)


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": (
                "Search the store catalog for products, prices, categories "
                "and availability. Use this whenever the customer asks about "
                "a product, price, stock or product recommendations."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "Product name or keywords to search for."
                        ),
                    },
                    "category": {
                        "type": "string",
                        "description": (
                            "Product category, for example Violões or Guitarras."
                        ),
                    },
                    "max_price": {
                        "type": "number",
                        "description": (
                            "Maximum price in Brazilian reais."
                        ),
                    },
                    "only_available": {
                        "type": "boolean",
                        "description": (
                            "Whether to return only active products with stock."
                        ),
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_active_promotions",
            "description": (
                "Return the currently active promotions for products "
                "that are available in stock."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": (
                "Check order information. Requires both the order ID "
                "and customer email for privacy verification."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "integer",
                        "description": "The customer's order ID.",
                    },
                    "customer_email": {
                        "type": "string",
                        "description": (
                            "Email address associated with the order."
                        ),
                    },
                },
                "required": [
                    "order_id",
                    "customer_email",
                ],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_policies",
            "description": (
                "Search the store policy document. Use for opening hours, "
                "payments, returns, exchanges, warranties and store procedures."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "Customer question or keywords about store policies."
                        ),
                    },
                    "top_k": {
                        "type": "integer",
                        "description": (
                            "Maximum number of policy excerpts to retrieve."
                        ),
                    },
                },
                "required": ["query"],
            },
        },
    },
]


TOOL_FUNCTIONS = {
    "search_products": search_products,
    "get_active_promotions": get_active_promotions,
    "get_order_status": get_order_status,
    "search_policies": search_policies,
}


def execute_tool(tool_name: str, arguments: dict):
    function = TOOL_FUNCTIONS.get(tool_name)

    if function is None:
        return {
            "error": f"Unknown tool: {tool_name}"
        }

    try:
        return function(**arguments)

    except Exception as exc:
        return {
            "error": f"Tool execution failed: {str(exc)}"
        }


def run_agent(
    user_message: str,
    conversation_history: list[dict] | None = None,
) -> tuple[str, list[dict]]:

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]

    if conversation_history:
        messages.extend(conversation_history)

    messages.append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    for _ in range(5):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            parallel_tool_calls=False,
            temperature=0.2,
        )

        assistant_message = response.choices[0].message

        if not assistant_message.tool_calls:
            final_answer = assistant_message.content or (
                "Não consegui gerar uma resposta."
            )

            messages.append(
                {
                    "role": "assistant",
                    "content": final_answer,
                }
            )

            return final_answer, messages[1:]

        messages.append(
            {
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments,
                        },
                    }
                    for tool_call in assistant_message.tool_calls
                ],
            }
        )

        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name

            arguments = json.loads(
                tool_call.function.arguments or "{}"
            )

            result = execute_tool(
                tool_name,
                arguments,
            )

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": json.dumps(
                        result,
                        ensure_ascii=False,
                        default=str,
                    ),
                }
            )

    return (
        "Não consegui concluir a solicitação após várias tentativas.",
        messages[1:],
    )