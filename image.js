import dotenv from 'dotenv'
import OpenAI from 'openai';

dotenv.config()

const openai = new OpenAI({
  apiKey: process.env.XAI_API_KEY,
  baseURL: "https://api.x.ai/v1",
});

const response = await openai.images.generate({
  model: "grok-2-image",
  prompt: "A girl in a tree",
});

console.log(response.data);
