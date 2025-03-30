import dotenv from 'dotenv'
import OpenAI from "openai";

dotenv.config()

const client = new OpenAI({
  apiKey: process.env.XAI_API_KEY,
  baseURL: "https://api.x.ai/v1",
});

export default client
