# Problem-solving-with-scripting

Project Overview
This project implements two Python applications demonstrating advanced scripting techniques:

Part I: CourierOptimizer
A smart courier routing system for NordicExpress delivery service in Oslo. The system optimizes delivery routes based on multiple criteria (time, cost, CO2 emissions) and supports different transport modes.

Part II: Conway's Game of Life
An interactive cellular automaton simulator with pattern loading, multiple rule sets, and dynamic metaprogramming features.

Features Implemented
Core Requirements
Modular design with functions and classes
File I/O operations (CSV, pattern files, logs)
Metaprogramming (decorators, dynamic class modification, rule registry)
Custom error handling with exception hierarchy
Regular expressions for validation and pattern parsing
pytest testing (comprehensive test suites)
Logging with structured output
CLI interfaces for both application


## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Instructions

1. **Clone or download the repository**
   ```bash
   # If using git
   git clone <repository-url>
   cd Python-project-scripting
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation**
   ```bash
   python -m pytest tests/ -v
   ```
## Usage Guide

### Part I: CourierOptimizer

#### Running the Application

**Command:**
```powershell
python3 courier_main.py
```

**If `python3` doesn't work, try:**
```powershell
python courier_main.py
```
or
```powershell
py courier_main.py
```

#### Quick Start Example

When prompted for the file path, enter: `sample_data/deliveries.csv`

**Example session:**
```
Enter deliveries CSV file path (default: deliveries.csv): sample_data/deliveries.csv
Enter depot latitude (e.g., 59.9139 for Oslo): 59.9139
Enter depot longitude (e.g., 10.7522 for Oslo): 10.7522
Select transport mode (1-3): 2    # Bicycle
Select optimization objective (1-3): 1    # Fastest time
```

#### Interactive Menu Flow

1. **Input**: Provide path to CSV file (use `sample_data/deliveries.csv` for sample data)
2. **Depot Location**: Enter latitude/longitude coordinates (e.g., 59.9139, 10.7522 for Oslo)
3. **Transport Mode**: Choose Car, Bicycle, or Walking
4. **Optimization**: Select objective (time, cost, or CO2)
5. **Output**: View results and generated files

#### Input Format (CSV)

```csv
customer,latitude,longitude,priority,weight_kg
Aker Brygge Shop,59.9105,10.7305,High,3.5
Grünerløkka Cafe,59.9227,10.7579,Medium,2.1
```

**Validation Rules:**
- `priority`: Must be exactly "High", "Medium", or "Low" (case-sensitive)
- `latitude`: Float between -90 and 90
- `longitude`: Float between -180 and 180
- `weight_kg`: Non-negative number
- `customer`: Non-empty string with valid characters

#### Output Files

1. **route.csv**: Optimized route with details
2. **metrics.csv**: Summary statistics
3. **rejected.csv**: Invalid rows (if any)
4. **run.log**: Execution log

---

### Part II: Conway's Game of Life

#### Running the Application

**Command:**
```powershell
python3 game_main.py
```

**If `python3` doesn't work, try:**
```powershell
python game_main.py
```
or
```powershell
py game_main.py
```

#### Quick Start Examples

**Option 1: Load a sample pattern from file**
```
Select option (1-4): 2    # Load pattern from file
Enter pattern file path: sample_data/blinker.txt
Enter board width (10-100): 40
Enter board height (10-100): 70
```

**Available sample patterns:**
- `sample_data/blinker.txt` - Simple oscillator
- `sample_data/glider.txt` - Moving pattern
- `sample_data/glider_coords.txt` - Glider with coordinates
- `sample_data/pulsar.txt` - Period 3 oscillator

**Option 2: Use predefined pattern**
```
Select option (1-4): 3    # Use predefined pattern
Enter board width: 40
Enter board height: 40
Select pattern (1-5): 1    # Glider
```


