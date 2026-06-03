import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from "zod";

const server = new McpServer({ name: "lomash-server", version: "1.0.0" });

server.registerTool(
    'addTwoNumbers',
    {
        title:'Add Numbers',
        description: 'Add two numbers numbers',
        inputSchema: z.object({input1: z.number(), input2: z.number()})
    },
    async function ({input1, input2}) {
        return {content: [{
            type: 'text',
            text: String(input1+input2)
        }]}
    }
)

const transport = new StdioServerTransport();
await server.connect(transport)