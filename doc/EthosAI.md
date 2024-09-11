# EthosAI: Ethical and Adaptive Current Life Imagination Model

## Project Overview

EthosAI is designed to simulate and enhance ethical decision-making processes in artificial intelligence systems, specifically focusing on real-time adaptive models. The system integrates various ethical, individual, and situational factors to determine the optimal action plan based on a **Current Life Imagination Model (CLIM)**.

### New Architecture

The system now incorporates a **CLIM Stack**, composed of multiple layers, each responsible for distinct aspects of decision-making:

1. **ETHIC Layer**: Handles the ethical implications of actions.
2. **INDIVIDUAL Layer**: Adjusts decisions based on individual preferences and personal considerations.
3. **SAMT Layer**: Focuses on short and medium-term optimizations, ensuring immediate needs are met.
4. **LCLIM Layer**: Provides a long-term, deep analysis of the situation.

### Decision Pipeline

The pipeline is designed to process information through these layers, allowing for a **multi-phase decision-making** process. Each layer evaluates the situation and produces a decision:

- **STOP**
- **EMERGENCY [SURVIVAL | ESSENTIAL | RECOMMENDED]**
- **GO**
- **NOGO**
- **WAIT**
- **ADJUST**
- **ESCALATE**

### Training and Test Cases

Training for each layer is based on test cases that simulate realistic scenarios. These test cases are structured in **JSON** format and processed layer by layer to improve the CLIM's response accuracy. The following processes are involved:

1. **Test Case Generation**: The system supports dynamic generation of test cases, which are used for training.
2. **Pipeline Execution**: Test cases are fed into the pipeline to evaluate the decision-making process.

The training phase is followed by evaluation, where the output from each layer is compared to expected decisions and fine-tuned accordingly.

---

## CLIM Stack

### ETHIC Layer

This layer is responsible for evaluating the ethical impact of a situation. It considers:
- Moral principles
- Ethical priorities (e.g., survival, justice, fairness)

### INDIVIDUAL Layer

The individual layer adjusts decisions based on personal considerations:
- Individual preferences
- Situational relevance
- Adaptability based on personal history and characteristics

### SAMT Layer

The short and medium-term optimization layer evaluates immediate needs and resources, focusing on:
- Current priorities
- Short-term goals
- Available tools

### LCLIM Layer

The long-term analysis layer takes a broader perspective, factoring in:
- Deep knowledge (e.g., GPT-4o level analysis)
- Historical data and trends
- Potential long-term consequences

---

## Emergency Pipelines

For critical situations, the system employs **Emergency Pipelines**, which prioritize certain layers based on the severity of the situation. The system defines three emergency pipelines:

1. **Survival Pipeline**: Focuses on ensuring survival, processing through ETHIC and SAMT layers.
2. **Essential Pipeline**: Addresses essential needs through ETHIC, SAMT, and INDIVIDUAL layers.
3. **Recommended Pipeline**: Handles non-critical but recommended actions, primarily through the SAMT and INDIVIDUAL layers.

These pipelines ensure that urgent decisions are made quickly while maintaining a structured process for less critical situations.

---

## Training Strategy

The CLIM is continuously trained using structured test cases. Each layer receives inputs from these test cases, refines its decision-making process, and integrates the new knowledge back into the model.

---

### Key Components of Training:

1. **Test Case JSON**: Test cases are stored in JSON format, capturing realistic situations and the expected responses.
2. **Layer-Specific Training**: Each layer of the CLIM is trained separately based on the relevant portion of the test case.
3. **Feedback Loop**: After training, the layers are re-evaluated with updated test cases to ensure accuracy and reliability.
4. **Emergency Training**: Special training pipelines exist for emergency scenarios, where rapid decision-making is necessary.
