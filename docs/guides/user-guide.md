# User Guide

## Running Playbooks

### Verbosity and Debugging

Use verbosity flags to see what's happening during playbook execution:

```bash
# Standard execution - minimal output
ansible-playbook site.yml

# Verbose (-v) - show task results
ansible-playbook site.yml -v

# More verbose (-vv) - show task input and output
ansible-playbook site.yml -vv

# Very verbose (-vvv) - show variable values and function calls
ansible-playbook site.yml -vvv

# Maximum verbosity (-vvvv) - show everything including library internals
ansible-playbook site.yml -vvvv
```

**When to use each level:**

| Level | Use Case |
|-------|----------|
| None | Production runs when you know it works |
| `-v` | Check task status, which tasks changed |
| `-vv` | See input/output, understand task behavior |
| `-vvv` | Debug variable issues, conditional logic |
| `-vvvv` | Deep debugging, plugin behavior issues |

### Check Mode and Diff Mode

Test playbooks without making changes:

```bash
# Check mode - simulate changes without applying
ansible-playbook site.yml --check

# Check mode + diff - show what would change
ansible-playbook site.yml --check --diff

# Diff mode only - run playbook and show changes
ansible-playbook site.yml --diff
```

!!! warning "Limited support in this collection"
    Check mode, diff, and change reporting are only supported in **very selective scenarios** (e.g. the workflow module supports check mode). RPC operations, actions, and many REST calls do not report whether they would or did make changes. Do not blindly trust `--check`, `--diff`, or `changed` for all tasks. See the [Developer Guide](developer-guide.md) for best practices and always validate in dev/staging before production.

### Step-by-Step Execution

Run playbook step-by-step for debugging:

```bash
# Step through each task (press ENTER to continue)
ansible-playbook site.yml --step

# Combine with verbosity
ansible-playbook site.yml --step -vv
```
