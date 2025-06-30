import random
import matplotlib.pyplot as plt
import numpy as np

# Define the questions and their corresponding dimensions
questions = {
    "Spiritual": [
        "A spiritual view of reality enriches life by recognizing a profound, non-physical essence, such as a soul or divine purpose, that gives meaning and connection beyond the material world. (Spiritual = existence of a non-physical soul, spirit, or divine essence)",
        "There exists a spiritual dimension to reality that transcends the purely physical world."
    ],
    "Material": [
        "A material view of reality empowers us by focusing on the tangible, scientific world of matter and energy, providing clear, evidence-based understanding and practical solutions. (Material = reality consists only of physical matter and energy)",
        "Reality consists primarily of physical matter and energy that can be measured and studied scientifically."
    ],
    "Freedom": [
        "Prioritizing freedom in society fosters creativity, self-expression, and personal growth, allowing individuals to thrive without external constraints. (Freedom = ability to act and think without external constraints)",
        "Society functions best when individuals have maximum personal freedom to make their own choices."
    ],
    "Coercion": [
        "Embracing coercion in society ensures order, safety, and collective progress by guiding behavior toward shared goals and stability. (Coercion = use of force or authority to compel behavior)",
        "Some degree of social control and restriction is necessary for people to live together harmoniously."
    ],
    "Free Will": [
        "Believing in free will empowers individuals to shape their own destinies, fostering responsibility, creativity, and moral agency. (Free Will = ability to choose freely)",
        "Given identical circumstances, a person could have chosen to act differently than they did."
    ],
    "Determinism": [
        "Embracing determinism offers comfort and insight, recognizing that our actions align with natural causes, promoting understanding and empathy for human behavior. (Determinism = all actions are predetermined by prior causes)",
        "All human decisions are the inevitable result of prior causes, including genetics, upbringing, and brain chemistry."
    ],
    "Teleological": [
        "A teleological approach to ethics maximizes positive outcomes, ensuring actions benefit the greatest number and adapt to real-world results. (Teleological = focused on outcomes, e.g., utilitarianism)",
        "An action is morally right if it produces the best overall consequences for everyone involved."
    ],
    "Deontological": [
        "A deontological approach to ethics upholds integrity and consistency, grounding moral actions in universal principles and duties that respect human dignity. (Deontological = focused on principles, e.g., duty-based ethics)",
        "Some actions are inherently right or wrong regardless of their outcomes or consequences."
    ],
    "Individualism": [
        "Individualism strengthens society by championing personal autonomy, innovation, and self-reliance, allowing each person to reach their full potential. (Individualism = emphasis on personal autonomy and self-reliance)",
        "People should prioritize their personal goals and achievements over group needs."
    ],
    "Collectivism": [
        "Collectivism builds a stronger society by fostering cooperation, unity, and shared purpose, ensuring the well-being of all through mutual support. (Collectivism = emphasis on group goals and interdependence)",
        "Individual interests should be subordinated to the welfare of the community or society."
    ],
    "Optimism": [
        "Optimism inspires hope and action, driving progress by envisioning a brighter future and motivating solutions to challenges. (Optimism = expectation of favorable outcomes and progress)",
        "Human nature is fundamentally good, and people generally try to do the right thing."
    ],
    "Pessimism": [
        "Pessimism provides a realistic, cautious perspective, encouraging preparation and resilience by anticipating challenges and potential setbacks. (Pessimism = expectation of decline or negative outcomes)",
        "Left to their own devices, most people will act selfishly and cause harm to others."
    ],
    "Universalism": [
        "Universalism promotes fairness and unity, offering consistent ethical principles that guide all people toward justice and shared values. (Universalism = consistent principles across all societies)",
        "There are objective moral truths that apply to all people across all cultures and times."
    ],
    "Relativism": [
        "Relativism celebrates diversity and adaptability, respecting unique cultural and individual perspectives to create a more inclusive moral framework. (Relativism = principles depend on cultural or individual perspectives)",
        "What is considered right or wrong depends entirely on cultural context and historical circumstances."
    ],
    "Change": [
        "Embracing change fuels progress and innovation, adapting society to new opportunities and advancements for a better future. (Change = adopting new ideas, practices, or technologies)",
        "Society should embrace new ideas and rapid change to solve problems and improve life."
    ],
    "Tradition": [
        "Upholding tradition preserves wisdom and stability, honoring time-tested values and practices that anchor society's identity and strength. (Tradition = maintaining established customs and values)",
        "Traditional ways of life and established institutions provide essential stability and wisdom."
    ],
    "Belief in God": [
        "Belief in God provides purpose, comfort, and moral guidance, connecting individuals to a higher power and a sense of divine order. (Belief in God = acceptance of a higher power or deity)",
        "A supreme being or divine force plays an active role in the universe and human affairs."
    ],
    "Atheism": [
        "Atheism liberates individuals to find meaning through reason, science, and human potential, fostering independence and critical thinking. (Atheism = rejection of the existence of any deity)",
        "The universe operates according to natural laws without supernatural intervention or guidance."
    ],
    "Equality": [
        "Prioritizing equality empowers all people, ensuring fair treatment, equal opportunities, and a just society for everyone. (Equality = equal rights, opportunities, and treatment)",
        "All people deserve equal treatment and opportunities regardless of their abilities or circumstances."
    ],
    "Hierarchy": [
        "Embracing hierarchy organizes society effectively, rewarding merit and expertise while providing structure and clear leadership. (Hierarchy = organized rankings of power or status)",
        "Natural differences in talent and effort justify unequal outcomes and social rankings."
    ],
    "Reason": [
        "Relying on reason enhances decision-making, offering logical, evidence-based solutions that lead to clarity and progress. (Reason = logical, evidence-based thinking)",
        "The best decisions come from careful logical analysis rather than following feelings or intuition."
    ],
    "Emotion": [
        "Valuing emotion enriches decisions, tapping into intuition, empathy, and human connection for a deeper understanding of life. (Emotion = feelings, intuition)",
        "Emotions and gut instincts often provide better guidance than purely rational thinking."
    ],
    "Nature": [
        "Emphasizing nature highlights the power of genetics, revealing our unique potential and innate strengths that shape who we are. (Nature = innate, biological influences)",
        "People's personalities and abilities are primarily determined by their genetic inheritance."
    ],
    "Nurture": [
        "Focusing on nurture celebrates the transformative role of environment, showing how upbringing and experiences can unlock endless possibilities. (Nurture = upbringing, education, and social influences)",
        "Environmental factors like upbringing and education shape who people become more than genetics."
    ],
    "Absolutism": [
        "Absolutism upholds unwavering principles, providing a strong, consistent moral foundation that guides ethical decisions with clarity. (Absolutism = fixed, universal rules)",
        "Moral principles should be followed consistently even when doing so leads to difficult outcomes."
    ],
    "Pragmatism": [
        "Pragmatism excels in flexibility, crafting practical, context-sensitive solutions that effectively address real-world challenges. (Pragmatism = flexible, outcome-oriented approaches)",
        "Rules and principles should be flexible tools that can be modified when practical circumstances require it."
    ],
    "Security": [
        "Prioritizing security ensures stability and peace, protecting individuals and society with safety and predictability for a thriving life. (Security = safety, predictability, and protection)",
        "It's better to accept known limitations than to pursue uncertain possibilities that might fail."
    ],
    "Risk": [
        "Embracing risk sparks growth and opportunity, encouraging bold action and innovation for remarkable rewards and progress. (Risk = uncertainty with potential for reward or loss)",
        "Taking calculated risks and embracing uncertainty leads to greater rewards and personal growth."
    ],
    "Rational Self-Interest": [
        "Rational self-interest drives progress, empowering individuals to pursue reasoned goals that benefit both themselves and society. (Rational Self-Interest = pursuing personal benefit through reasoned choices)",
        "People should focus on advancing their own well-being rather than sacrificing for others."
    ],
    "Altruism": [
        "Altruism inspires nobility and connection, fostering a better world through selfless acts that uplift others and build community. (Altruism = selfless concern for others' well-being)",
        "We have a moral obligation to help others even when it requires personal sacrifice."
    ]
}
count = 0
# Initialize scores for each dimension
scores = {
    "Spiritual": 0,
    "Material": 0,
    "Freedom": 0,
    "Coercion": 0,
    "Free Will": 0,
    "Determinism": 0,
    "Teleological": 0,
    "Deontological": 0,
    "Individualism": 0,
    "Collectivism": 0,
    "Optimism": 0,
    "Pessimism": 0,
    "Universalism": 0,
    "Relativism": 0,
    "Change": 0,
    "Tradition": 0,
    "Belief in God": 0,
    "Atheism": 0,
    "Equality": 0,
    "Hierarchy": 0,
    "Reason": 0,
    "Emotion": 0,
    "Nature": 0,
    "Nurture": 0,
    "Absolutism": 0,
    "Pragmatism": 0,
    "Security": 0,
    "Risk": 0,
    "Rational Self-Interest": 0,
    "Altruism": 0
}

# Ask questions and record responses
questions_list = []
for dimension in questions:
    slist = questions[dimension]
    random.shuffle(slist)
    for i in range(len(slist)):  # Changed to use all questions in each dimension
        questions_list.append((dimension, slist[i]))

random.shuffle(questions_list)

for dimension, question in questions_list:
    count += 1
    print("\nQuestion", count, "of", len(questions_list))
    print("\n" + question)
    response = input("Please enter a number from 1 to 10, where 1 is 'strongly disagree' and 10 is 'strongly agree': ")
    while not response.isdigit() or not 1 <= int(response) <= 10:
        response = input("Invalid input. Please enter a number from 1 to 10: ")
    scores[dimension] += int(response)
    
# Calculate average score for each dimension
for dimension in scores:
    scores[dimension] /= len(questions[dimension])

# Plot radar graph
angles = np.linspace(0, 2*np.pi, len(scores), endpoint=False)
stats = [scores[dim] for dim in scores.keys()]

fig = plt.figure(figsize=(12,12))  # Increased figure size for better readability
ax = fig.add_subplot(111, polar=True)

ax.plot(angles, stats, 'o-', linewidth=2)
ax.fill(angles, stats, alpha=0.25)

ax.set_thetagrids(angles * 180/np.pi, list(scores.keys()))
ax.set_ylim(0,10)
ax.set_title("Philosophical Leanings", va='bottom', pad=20)

# Rotate labels for better readability
plt.xticks(angles * 180/np.pi, list(scores.keys()), rotation=45)

plt.tight_layout()
plt.show()