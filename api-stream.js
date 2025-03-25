import dotenv from 'dotenv'
import OpenAI from "openai";

dotenv.config()

const openai = new OpenAI({
  apiKey: process.env.XAI_API_KEY,
  baseURL: "https://api.x.ai/v1",
});

const stream = await openai.chat.completions.create({
  model: "grok-2-latest",
  messages: [
    { role: "system", content: "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy." },
    {
      role: "user",
      content: "What is the meaning of life, the universe, and everything?",
    }
  ],
  stream: true
});

// console.log(stream)

for await (const chunk of stream) {
  // console.log(chunk);
  console.log(chunk.choices[0].delta.content);
}
