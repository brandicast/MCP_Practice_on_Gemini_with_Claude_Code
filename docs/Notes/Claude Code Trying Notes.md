# Claude Code Trying Notes

## Installation

### Envrionment 

- WSL on Windows


Check wsl version.  Ideal is WSL2 with Ubuntu 20/22/24
```
   wsl --status 
```

 - 3 things require for Claude Code
    - NodeJS
    - Anthropic API Key
    - A Git Repo

- Node.JS

    Use NVM, not APT.  (Why?)

    Install NVM

    ```
    curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
    ```

    Open a new shell and confirm nvm with the followings:
    ```
    command -v nvm
    ```
    Install Node
    ```
    nvm install --lts
    nvm use --lts
    ```
    Confirm nvm and node
    ```
    node -v
    npm -v
    ```
- Install Claude Code
    ```
    npm install -g @anthropic-ai/claude-code
    ```
    Test with the following:
    ```
    claude --help
    ```
- Configure Anthopic API Key

    Go https://console.anthropic.com/ and get an API Key.  And then configure as env variable in WSL with:
    ```
    export ANTHROPIC_API_KEY="sk-ant-xxxxx"
    ```
    or write into ~/.bashrc or ~/.zshrc permernantly.
    ```
    echo 'export ANTHROPIC_API_KEY="sk-ant-xxxxx"' >> ~/.bashrc
    ```
    reload the .bashrc
    ```
    source ~/.bashrc
    ```
- Fine a repo on git and clone
    ```
    git clone ......
    cd project_folder
    ```
    under the project root folder, start claude with :
    ```
    claude
    ```

### Notes

#### Claude Code is stateless

- Every time before off work, if things hasn't done, give the instructions below and ask claude to remember what happened:
    ```
    Summarize the repository analysis and the proposed design
    into a markdown file at docs/smart-home-mcp-design.md.

    Include:
    - Current architecture overview
    - Proposed MCP tool design
    - Files to be modified
    - Open questions / TODOs

    Do not modify any code.
    ```
- And give the order next day
    ```
    Read docs/smart-home-mcp-design.md
    and implement the proposed MCP tool accordingly.
    ```

or 
- Before leaving
    ```
    Summarize today's design decisions
    into docs/design-notes.md.
    ```
- And next time
    ```
    Read docs/design-notes.md
    and continue implementation.
    ```





    
#### Regarding API Key

Need to keep it and save it.  Can't find it back even on Anthropic website.  Better to write it under project folder .env file with
```
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxx
```