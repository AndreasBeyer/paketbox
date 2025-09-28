# Paketbox Test Environment

This directory contains a comprehensive test suite for the Paketbox control system that simulates the Raspberry Pi GPIO environment without requiring actual hardware.

## Overview

The test environment provides:
- **GPIO Simulation**: Mocks RPi.GPIO module to simulate hardware interactions
- **Unit Tests**: Tests for individual functions and components  
- **Integration Tests**: Tests for complete system scenarios
- **Error Simulation**: Tests for error conditions and recovery
- **Thread Safety Tests**: Ensures concurrent operations work correctly
- **Motor Blockage Tests**: Simulates package obstruction scenarios
- **Timer Management Tests**: Validates timer-based operations

## Test Architecture

### Modular Testing Approach
The tests are designed to work with the modular architecture:
- **`paketbox.py`**: Main control logic and GPIO event handling
- **`handler.py`**: Motor control and GPIO handler functions
- **`state.py`**: Centralized state management
- **`config.py`**: Configuration and GPIO pin mappings
- **`PaketBoxState.py`**: State enumerations and management classes
- **`TimerManager.py`**: Timer management for motor operations
- **`mqtt.py`**: MQTT integration with fallback handling

## Running Tests

### Quick Start
```bash
# Run all tests with detailed output (Windows)
python tests/run_tests.py

# Run all tests with PYTHONPATH (Linux/Mac)
PYTHONPATH=. python tests/run_tests.py

# Run specific test module
python -m unittest tests.test_paketbox -v

# Run specific test class
python -m unittest tests.test_paketbox.TestPaketBox -v

# Run specific test method
python -m unittest tests.test_paketbox.TestPaketBox.test_Klappen_oeffnen_success -v
```

### Test Categories

#### 1. Unit Tests (`TestPaketBox`)
- **GPIO Handler Tests**: Test individual GPIO event handlers from `handler.py`
- **State Management Tests**: Test door/motor state tracking in `PaketBoxState.py`
- **Motor Control Tests**: Test flap opening/closing operations from `handler.py`
- **Error Handling Tests**: Test error states and prevention logic
- **Timer Management Tests**: Test `TimerManager.py` functionality
- **Motor Blockage Tests**: Test package obstruction detection

#### 2. Integration Tests (`TestPaketBoxIntegration`)
- **Complete Delivery Cycle**: Tests full package delivery workflow
- **Error Recovery**: Tests system behavior during error conditions
- **GPIO Event Simulation**: Tests various GPIO input scenarios
- **Thread Safety**: Tests concurrent operation safety
- **Cross-Module Integration**: Tests interaction between all modules

## Test Features

### GPIO Simulation
The test environment includes a sophisticated GPIO mock that:
- Simulates all GPIO constants (HIGH, LOW, BCM, etc.)
- Tracks GPIO setup and output operations
- Provides controllable input values for testing
- Logs all GPIO operations for debugging
- Works with the modular `handler.py` architecture

### Timer Simulation
Complex timer-based operations are properly mocked:
- Motor runtime timers are controlled for testing (`TimerManager.py`)
- End position checking callbacks can be triggered manually
- Multiple simultaneous timers are handled correctly
- Timer cancellation and cleanup is verified

### State Validation
Comprehensive state validation ensures:
- All door states are correctly tracked (`PaketBoxState.py`)
- Motor states are properly managed
- State transitions follow business logic
- Error conditions are properly detected
- Thread-safe state access is maintained (`state.py`)

## System States Tested

### Door States (from `PaketBoxState.py`)
- `CLOSED`: Normal closed position
- `OPEN`: Normal open position  
- `ERROR`: Error condition requiring intervention

### Motor States (from `PaketBoxState.py`)
- `STOPPED`: Motor not running
- `OPENING`: Motor opening flaps
- `CLOSING`: Motor closing flaps
- `ERROR`: Motor error condition

### Test Scenarios
1. **Normal Operations**
   - Successful flap opening/closing with proper timer management
   - Proper door locking/unlocking via `handler.py`
   - Correct state transitions through `state.py`

2. **Error Conditions**
   - Flap opening failures (motor blockage)
   - Flap closing failures (package obstruction)
   - Motor blockage detection and error state setting
   - Hardware failures in `handler.py` functions

3. **Edge Cases**
   - GPIO debouncing behavior
   - Simultaneous door operations
   - Concurrent state access through `state.py`
   - Recovery from error states using `handler.ResetErrorState()`
   - Timer conflicts and cancellation

## Test Coverage

The test suite covers:
- ✅ All GPIO event handlers (left/right flaps, delivery door, mailbox, etc.)
- ✅ All motor control functions from `handler.py` (opening/closing flaps)
- ✅ All door lock/unlock operations from `handler.py`
- ✅ Complete delivery workflow end-to-end
- ✅ Error detection and handling across all modules
- ✅ State management and validation (`PaketBoxState.py`, `state.py`)
- ✅ Thread safety across modular architecture
- ✅ GPIO debouncing (configured in `config.py`)
- ✅ Timer-based operations (`TimerManager.py`)
- ✅ Motor blockage detection and recovery
- ✅ MQTT integration fallback handling
- ✅ Configuration validation (`config.py`)

## Motor Blockage Testing

### Comprehensive Blockage Scenarios
The test suite includes extensive motor blockage testing:

```python
# Test scenarios covered:
- Only left flap blocked by package
- Only right flap blocked by package  
- Both flaps blocked by large package
- Partial opening (flaps stuck halfway)
- Closing blockage (package prevents closing)
- Motor hardware failures
```

These tests ensure the system properly detects when packages interfere with flap operation and transitions to appropriate error states.

## Adding New Tests

### Test Structure for Modular Architecture
```python
@patch('handler.get_gpio')  # Mock GPIO access in handler.py
@patch('handler.setOutputWithRuntime')  # Mock timer functions
@patch('handler.threading.Timer')  # Mock threading operations
def test_new_feature(self, mock_timer, mock_setOutput, mock_get_gpio):
    """Test description"""
    # Setup GPIO mock
    mock_gpio = MagicMock()
    mock_gpio.HIGH = 1
    mock_gpio.LOW = 0
    mock_get_gpio.return_value = mock_gpio
    
    # Test logic here
    # Assert expected behavior
```

### Mock Guidelines
- Always mock GPIO operations to avoid hardware dependencies
- Use `@patch` decorators to isolate components under test
- Mock timers for timer-based functionality (`TimerManager.py`)
- Reset state in `setUp()` method for each test
- Test cross-module interactions properly

### Best Practices
- Write descriptive test names and docstrings
- Test both success and failure scenarios
- Use subtests for testing multiple similar cases
- Verify state changes across all relevant modules
- Keep tests focused and independent
- Test timer management and cleanup
- Verify error state propagation

## Configuration Testing

### GPIO Pin Configuration
Tests validate the GPIO pin mappings from `config.py`:
```python
# Input pins (Config.INPUTS)
- Pin 27 (0): Left flap closed sensor
- Pin 17 (1): Left flap open sensor
- Pin 9 (2): Right flap closed sensor
- Pin 22 (3): Right flap open sensor
- Pin 23 (4): Package door sensor
# ... etc

# Output pins (Config.OUTPUTS)  
- Pin 5 (0): Left flap motor close
- Pin 6 (1): Left flap motor open
- Pin 13 (2): Right flap motor close
- Pin 16 (3): Right flap motor open
- Pin 26 (7): Door lock relay
# ... etc
```

## Requirements

The test environment requires only standard Python libraries:
- `unittest` (built-in) - Core testing framework
- `unittest.mock` (built-in) - Mocking and patching
- `threading` (built-in) - Thread safety testing
- `time` (built-in) - Timer-based testing

**No external dependencies or hardware required!**

## Troubleshooting Tests

### Common Issues
1. **Import Errors**: Make sure to run from project root or set `PYTHONPATH=.`
2. **Timer Test Failures**: Check that timer callbacks are properly captured and executed
3. **State Test Failures**: Verify that state is reset in `setUp()` method
4. **Mock Failures**: Ensure GPIO mocks are properly configured for the modular architecture

### Debug Output
Enable debug output to trace test execution:
```python
# In test files, add:
import logging
logging.basicConfig(level=logging.DEBUG)

# Or run with verbose output:
python -m unittest tests.test_paketbox -v
```

The comprehensive test suite ensures that all components work correctly both individually and together, providing confidence for deployment to production hardware.