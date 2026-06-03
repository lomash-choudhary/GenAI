import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

async function addTwoNumbersUsingLomashServer(a, b) {
  console.log(`\n🚀 Connecting to lomash-server MCP...`);
  console.log(`   (spawning: node mcp.js)\n`);

  const transport = new StdioClientTransport({
    command: 'node',
    args: ['mcp.js'],
    cwd: process.cwd()
  });

  const client = new Client(
    { name: 'lomash-client', version: '1.0.0' },
    { capabilities: {} }
  );

  await client.connect(transport);
  console.log('✅ Connected to lomash-server\n');

  console.log(`📞 Calling tool "addTwoNumbers" with input1=${a}, input2=${b}...\n`);

  const result = await client.callTool({
    name: 'addTwoNumbers',
    arguments: { input1: a, input2: b }
  });

  console.log('📦 Raw tool response:');
  console.dir(result, { depth: null });

  // Extract the text content
  const textContent = result.content?.find(c => c.type === 'text')?.text;
  const sum = textContent ? Number(textContent) : null;

  console.log(`\n🎉 Result from lomash-server: ${a} + ${b} = ${sum}\n`);

  await transport.close();
  console.log('👋 Disconnected from lomash-server\n');

  return sum;
}

// Demo: add 19 + 23 using the MCP tool
const num1 = 19;
const num2 = 23;

addTwoNumbersUsingLomashServer(num1, num2)
  .then(sum => {
    console.log(`Final verified sum: ${num1} + ${num2} = ${sum}`);
    process.exit(0);
  })
  .catch(err => {
    console.error('❌ Error using lomash-server MCP tool:', err);
    process.exit(1);
  });
