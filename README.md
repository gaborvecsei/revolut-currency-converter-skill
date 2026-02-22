# Revolut Currency Converter

Currency conversion CLI using Revolut's real-time exchange rates.

## Install

```bash
npx skills add <your-repo>
```

## Usage

```bash
python revolut-currency-converter/scripts/converter.py <command> [args]
```

### Commands

| Command | Description |
|---------|-------------|
| `convert <amount> <from> <to>` | Direct conversion |
| `find-route <amount> <from> <to>` | Find best route via bridges |
| `rate <from> <to>` | Get current rate |

### Examples

```bash
# Convert 1000 EUR to HUF
python converter.py convert 1000 EUR HUF

# Find best route for 50000 JPY to GBP
python converter.py find-route 50000 JPY GBP

# Get EUR to USD rate
python converter.py rate EUR USD
```

### Options

- `-n` - Max hops for find-route (default: 1)
- `-b` - Bridge currencies (default: EUR USD)
- `--pretty` - Pretty-print JSON
