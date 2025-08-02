# MCP Example Project

This project contains one Model Context Protocol (MCP) servers:
1. **mcp_demo** - A demo server using FastMCP with tools to retrieve the lastest email from Gmail and to make a summary of the latest email using a text summarization model locally

## Prerequisites

- Python 3.13+
- uv package manager
- Node.js (for VS Code MCP integration)

## Installation

Install dependencies using uv:

```bash
uv sync
```

## Running the MCP Servers

### 1. Demo MCP Server (mcp_demo)

The demo server provides basic functionality including an addition tool and sample resources.

```bash
source .venv/bin/activate  # Activate virtual environment
cd mcp_demo
mcp run server_Excercise.py --transport sse 
```

This will start the demo server with tools:
- `get_last_email_text` - Get the text of the latest email
- `summarize_text` - Summarize the latest email text



#### Setting up Gmail App Password

1. Enable 2-factor authentication on your Google account
2. Go to Google Account settings > Security > App passwords
3. Generate a new app password for "Mail"
4. Use this 16-character password (not your regular Gmail password)

## VS Code Integration

The project includes MCP configuration in `.vscode/mcp.json` that connects to both servers:

- **my-mcp-Email-ret-sum**: `http://127.0.0.1:8000/sse`

Make the server is running before using MCP tools in VS Code.

## Available Tools

### Demo Server Tools
- `get_last_email_text` - Retrieve the text of the latest email
- `summarize_text(text, num_sentences=3)` - Summarize any text or just the last email text

## Development

This project uses:
- **FastMCP** for the demo server
- **mcp** library for the IMAP server
- **IMAPClient** for Gmail integration
- **click** for CLI interface

## Troubleshooting

### SSL Issues
The IMAP server includes SSL fallback handling for development environments. If you encounter SSL certificate issues, the server will attempt to use a less secure SSL context.

### Authentication Errors
- Ensure you're using an app password, not your regular Gmail password
- Verify 2-factor authentication is enabled on your Google account
- Check that IMAP is enabled in Gmail settings

### Port Conflicts
If the default ports are in use, you can specify different ports when starting the servers.

## Prompt Example

### Retrive a given number of emails and create summary
"Retrieve the latest [number of emails] email from "[your email address]" with password "[gmail app password]" using the tool get_last_email_text, then summarize the latest email text using the tool summarize_text."
