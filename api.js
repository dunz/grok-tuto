// In your terminal, first run:
// npm install openai

import dotenv from 'dotenv'
import OpenAI from "openai";

dotenv.config()

const client = new OpenAI({
  apiKey: process.env.XAI_API_KEY,
  baseURL: "https://api.x.ai/v1",
});

const completion = await client.chat.completions.create({
  model: "grok-2-latest",
  messages: [
    {
      role: "system",
      content:
        "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy.",
    },
    {
      role: "user",
      content:
        "What is the meaning of life, the universe, and everything?",
    },
  ],
  // messages: [
  //   {
  //     role: "user",
  //     content: "Please write a write a report comparing firebase supabase",
  //   },
  // ],
});

console.log(completion);
console.log(completion.choices[0].message.content);
