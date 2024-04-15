from transformers import pipeline

# Load the question answering pipeline
qa_pipeline = pipeline("question-answering")

# Dictionary to hold contexts for different NPCs
npc_contexts = {
    "NPC1": "Context for NPC1. This NPC is interested in space exploration.",
    "NPC2": "Context for NPC2. This NPC is interested in ancient history.",
    "NPC3": "Context for NPC3. This NPC is interested in technology advancements.",
    # Add more NPCs and their contexts as needed
}

def get_answer_for_npc(npc_name, question):
    """
    Get the answer to a question for a specific NPC.
    """
    context = npc_contexts.get(npc_name, "")
    if not context:
        return "NPC not found.", None
    
    answer = qa_pipeline(question=question, context=context)
    return answer["answer"], context

# Example usage:
npc_name = "NPC1"
question = "What was the goal of the Apollo program?"
answer, context = get_answer_for_npc(npc_name, question)
print(f"For {npc_name}:")
print(f"Question: {question}")
print(f"Answer: {answer}")
