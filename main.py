from memory.metadata_store import MetadataStore

STORE_PATH = "data/metadata.json"


def main():
    store = MetadataStore(STORE_PATH)

    print("\n--- EXISTING MEMORIES ---")
    for m in store.all_memories():
        print(f"- [{m['timestamp']}] {m['text']}")

    user_input = input("\nAdd memory (press Enter to skip): ").strip()

    if user_input:
        store.add_memory(
            text=user_input,
            source="manual_cli",
            mem_type="reflection"
        )
        print("Memory stored safely.")


if __name__ == "__main__":
    main()



