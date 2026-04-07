import OpenAI from 'openai';

const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
const MODEL = process.env.OPENAI_MODEL ?? 'gpt-4o';

type ContactWithRelations = {
  firstName: string;
  lastName: string;
  company?: string | null;
  jobTitle?: string | null;
  notes?: string | null;
  tags: string[];
  deals: { title: string; stage: string; value: number }[];
  activities: { type: string; subject: string; notes?: string | null }[];
};

type DealWithRelations = {
  title: string;
  stage: string;
  value: number;
  probability: number;
  contact: { firstName: string; lastName: string };
  activities: { type: string; subject: string; notes?: string | null }[];
};

async function chat(systemPrompt: string, userPrompt: string): Promise<string> {
  const response = await client.chat.completions.create({
    model: MODEL,
    messages: [
      { role: 'system', content: systemPrompt },
      { role: 'user', content: userPrompt },
    ],
    temperature: 0.4,
    max_tokens: 512,
  });
  return response.choices[0]?.message.content ?? '';
}

async function summarizeContact(contact: ContactWithRelations): Promise<string> {
  const context = JSON.stringify(contact, null, 2);
  return chat(
    'You are a CRM analyst. Summarize the customer relationship concisely (3–5 sentences).',
    `Customer data:\n${context}`,
  );
}

async function suggestNextActions(deal: DealWithRelations): Promise<string[]> {
  const context = JSON.stringify(deal, null, 2);
  const raw = await chat(
    'You are a sales coach. Suggest 3 specific next actions to advance this deal. Respond with a JSON array of strings.',
    `Deal data:\n${context}`,
  );
  try {
    const jsonMatch = raw.match(/\[[\s\S]*\]/);
    return jsonMatch ? (JSON.parse(jsonMatch[0]) as string[]) : [raw];
  } catch {
    return [raw];
  }
}

async function scoreRelationship(contact: ContactWithRelations): Promise<number> {
  const context = JSON.stringify(contact, null, 2);
  const raw = await chat(
    'You are a CRM scoring engine. Score the relationship health from 0 to 100. Respond with a single integer.',
    `Customer data:\n${context}`,
  );
  const match = raw.match(/\d+/);
  const score = match ? parseInt(match[0], 10) : 50;
  return Math.min(100, Math.max(0, score));
}

interface MindMapNode {
  id: string;
  label: string;
  type: string;
  children?: MindMapNode[];
}

async function generateMindMapData(contact: ContactWithRelations): Promise<MindMapNode> {
  const context = JSON.stringify(contact, null, 2);
  const raw = await chat(
    `You are a mind map generator. Given a CRM contact, output a JSON mind map tree.
Schema: { id: string, label: string, type: "root"|"deals"|"activities"|"tags"|"leaf", children?: [...] }
The root node should be the contact name.`,
    `Contact:\n${context}`,
  );
  try {
    const jsonMatch = raw.match(/\{[\s\S]*\}/);
    return jsonMatch ? (JSON.parse(jsonMatch[0]) as MindMapNode) : { id: 'root', label: `${contact.firstName} ${contact.lastName}`, type: 'root' };
  } catch {
    return { id: 'root', label: `${contact.firstName} ${contact.lastName}`, type: 'root' };
  }
}

export const aiService = {
  summarizeContact,
  suggestNextActions,
  scoreRelationship,
  generateMindMapData,
};
