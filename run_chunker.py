from ingest.chunker import Chunker

chunker = Chunker(
    memory_path="data/metadata.json",
    chunk_path="data/chunks.json"
)

chunker.run()
print("Done.")


'''temporary file for running the chunker independently of the main process for testing purposes,
 run this file to generate chunks from existing memories and if new memories are added to the metadata store, they will be chunked as well.
 or if the chunk file is missing, it will be regenerated.
'''