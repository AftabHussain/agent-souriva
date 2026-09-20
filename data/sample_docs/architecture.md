# AgentSouriva architecture

AgentSouriva loads local documents, divides them into overlapping chunks, and stores normalized vectors in a FAISS index. Questions retrieve relevant chunks before the model generates an answer. The grounding policy requires citations to retrieved chunks and abstains when evidence is missing.

