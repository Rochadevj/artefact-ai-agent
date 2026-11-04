from src.agent import run_agent


def main():
    print("=" * 60)
    print("Empório da Música - Assistente Virtual")
    print("Digite 'sair' para encerrar.")
    print("=" * 60)

    history = []

    while True:
        user_message = input("\nVocê: ").strip()

        if not user_message:
            continue

        if user_message.lower() in {
            "sair",
            "exit",
            "quit",
        }:
            print("\nEmpório: Até mais! 🎵")
            break

        try:
            response, history = run_agent(
                user_message,
                history,
            )

            print(f"\nEmpório: {response}")

        except Exception as exc:
            print(
                "\nErro ao processar a mensagem:",
                str(exc),
            )


if __name__ == "__main__":
    main()