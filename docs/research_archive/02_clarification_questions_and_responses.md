# Clarification Questions and Responses

## Date: April 6, 2025

## ChatGPT's Questions

```
Thanks for the detailed background! To best answer your questions, could you share a few more details:

Render.com Backend:

What specific backend features do you need from Render (e.g., API hosting, background workers, scheduled jobs)?

What languages and frameworks are you using in your backend (e.g., Python + FastAPI)?

GoDaddy Hosting:

Will the frontend of KernResources.com be static (like HTML/CSS/JS) or dynamic (e.g., served by a web framework)?

Would you be open to migrating the domain to another provider if it significantly benefits the project?

LLaMA 4 Fine-Tuning:

Do you already have access to the LLaMA 4 model weights? If not, are you targeting Meta's LLaMA 3/4 open models or using OpenAI's GPT via API?

What kind of fine-tuning are you considering (e.g., LoRA, full fine-tuning, RAG-style augmentations)?

What is your rough compute budget (e.g., can afford a few hours of GPU time per month, or looking for free-tier options only)?

These will help tailor the research to your constraints and goals.
```

## User's Response

```
1. Regarding Render, I was planning to have that service all backend functions, such as maintaining the database, API calls, AI inference, & etc. This is because I think that it would be best if all of the maintenance were in one place. I am always open to suggestions for improving my plan. 

2. Regarding GoDaddy, the only objection that I would have to moving the domain to another service is that I understand that the process of moving a domain can be problematic. I am looking for a long-term hosting solution, so whichever host is chosen will need to have inexpensive plans that will work well with the chosen backend cloud service.

3. At this time, I am interested in fine tuning Llama 4 17B E mainly because I am very interested in how AI models "think." So, my choice is almost exclusively casual interest. I realize that it might be more economical to use an Instruct model for inference in my codebase. That said, I would like to better understand which platform would be most suitable for this task.
```

## Context

This exchange provides important clarifications about the project requirements:

1. **Backend Requirements**:
   - All backend functions should be handled by Render.com
   - This includes database management, API calls, and AI inference
   - Consolidating maintenance in one place is a priority

2. **Domain and Hosting Considerations**:
   - Open to moving from GoDaddy if beneficial, but concerned about migration complexity
   - Looking for an inexpensive, long-term hosting solution
   - The hosting solution should integrate well with the backend cloud service

3. **Llama 4 Fine-Tuning Goals**:
   - Interest in Llama 4 17B E model specifically
   - Motivation is primarily to understand how AI models "think" (research interest)
   - Acknowledges that using an Instruct model might be more economical
   - Seeking platform recommendations suitable for this task
