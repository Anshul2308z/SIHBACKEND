from chromadb.utils import embedding_functions

# Initialize default embedding function (ONNX based all-MiniLM-L6-v2)
ef = embedding_functions.DefaultEmbeddingFunction()
print(ef(["Hello world"])[0][:5])
