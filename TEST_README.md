# Paketbox Test Environment

This directory contains a comprehensive test suite for the Paketbox control system that simulates the Raspberry Pi GPIO environment without requiring actual hardware.

## Overview

The test environment provides:
- **GPIO Simulation**: Mocks RPi.GPIO module to simulate hardware interactions
- **Unit Tests**: Tests for individual functions and components
- **Integration Tests**: Tests for complete system scenarios
- **Error Simulation**: Tests for error conditions and recovery
- **Thread Safety Tests**: Ensures concurrent operations work correctly

## Running Tests

### Quick Start
```bash
# Run all tests with detailed output
python run_tests.py

# Run specific test module
python -m unittest test_paketbox.py -v

# Run specific test class
python -m unittest test_paketbox.TestPaketBox -v

# Run specific test method
python -m unittest test_paketbox.TestPaketBox.test_Klappen_oeffnen_success -v
```

### Test Categories

#### 1. Unit Tests (`TestPaketBox`)
- **GPIO Handler Tests**: Test individual GPIO event handlers
- **State Management Tests**: Test door state tracking and validation
- **Motor Control Tests**: Test flap opening/closing operations
- **Error Handling Tests**: Test error states and prevention logic

#### 2. Integration Tests (`TestPaketBoxIntegration`)
- **Complete Delivery Cycle**: Tests full package delivery workflow
- **Error Recovery**: Tests system behavior during error conditions
- **GPIO Event Simulation**: Tests various GPIO input scenarios
- **Thread Safety**: Tests concurrent operation safety

## Test Features

### GPIO Simulation
The test environment includes a sophisticated GPIO mock that:
- Simulates all GPIO constants (HIGH, LOW, BCM, etc.)
- Tracks GPIO setup and output operations
- Provides controllable input values for testing
- Logs all GPIO operations for debugging

### Timer Simulation
Complex timer-based operations are properly mocked:
- Motor runtime timers are controlled for testing
- End position checking callbacks can be triggered manually
- Multiple simultaneous timers are handled correctly

### State Validation
Comprehensive state validation ensures:
- All door states are correctly tracked
- State transitions follow business logic
- Error conditions are properly detected
- Thread-safe state access is maintained

## System States Tested

### Door States
- `CLOSED`: Normal closed position
- `OPEN`: Normal open position  
- `ERROR`: Error condition requiring intervention

### Test Scenarios
1. **Normal Operations**
   - Successful flap opening/closing
   - Proper door locking/unlocking
   - Correct state transitions

2. **Error Conditions**
   - Flap opening failures
   - Flap closing failures
   - Motor blockage detection
   - Invalid state transitions

3. **Edge Cases**
   - GPIO debouncing behavior
   - Simultaneous door operations
   - Concurrent state access
   - Recovery from error states

## Test Coverage

The test suite covers:
- ✅ All GPIO event handlers (left/right flaps, delivery door, mailbox, etc.)
- ✅ All motor control functions (opening/closing flaps)
- ✅ All door lock/unlock operations  
- ✅ Complete delivery workflow
- ✅ Error detection and handling
- ✅ State management and validation
- ✅ Thread safety
- ✅ GPIO debouncing
- ✅ Timer-based operations

## Adding New Tests

### Test Structure
```python
@patch('paketbox.GPIO')
def test_new_feature(self, mock_gpio):
    """Test description"""
    # Setup GPIO mock
    mock_gpio.HIGH = 1
    mock_gpio.LOW = 0
    
    # Test logic here
    # Assert expected behavior
```

### Mock Guidelines
- Always mock GPIO operations to avoid hardware dependencies
- Use `@patch` decorators to isolate components under test
- Mock timers for timer-based functionality
- Reset state in `setUp()` method for each test

### Best Practices
- Write descriptive test names and docstrings
- Test both success and failure scenarios
- Use subtests for testing multiple similar cases
- Verify state changes and GPIO operations
- Keep tests focused and independent

## Requirements

The test environment requires only standard Python libraries:
- `unittest` (built-in)
- `unittest.mock` (built-in)
- `threading` (built-in)
- `time` (built-in)

No external dependencies or hardware required!