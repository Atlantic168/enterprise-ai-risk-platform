from app.llm import generate_answer


answer = generate_answer(
    system_prompt="You are an enterprise technology risk analyst.",
    user_prompt="What is AI governance and why is it important?",
)

print(answer)