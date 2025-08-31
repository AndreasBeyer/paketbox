# Paketbox Control System

This repository contains a Python-based Raspberry Pi GPIO control system for an automated package delivery box (Paketbox). The system manages motors, sensors, and relays to automate package acceptance, door locking, and emptying operations.

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### Bootstrap and Test the Repository
- **No build step required** - This is pure Python with no compilation
- Set up and validate the environment:
  ```bash
  cd /home/runner/work/paketbox/paketbox
  python3 --version  # Requires Python 3.x
  python3 -c "import paketbox; print('Import successful')"  # Test import
  ```
- **Run comprehensive test suite**:
  ```bash
  PYTHONPATH=. python3 tests/run_tests.py
  ```
  - **NEVER CANCEL**: Tests take 65 seconds to complete. Set timeout to 5+ minutes.
  - All 28 tests must pass for a healthy codebase
  - Tests cover GPIO simulation, motor control, state management, and integration scenarios

### Run the Application
- **ALWAYS run tests first** to validate the environment
- Run the main application in mock mode (no hardware required):
  ```bash
  python3 paketbox.py
  ```
  - Application starts GPIO simulation and initializes hardware mock
  - Press Ctrl+C to stop the application
  - Mock mode allows full testing without Raspberry Pi hardware

### Test Individual Components
- Run specific test categories:
  ```bash
  # Run specific test class
  PYTHONPATH=. python3 -m unittest tests.test_paketbox.TestPaketBox -v
  
  # Run integration tests only
  PYTHONPATH=. python3 -m unittest tests.test_paketbox.TestPaketBoxIntegration -v
  
  # Run specific test method
  PYTHONPATH=. python3 -m unittest tests.test_paketbox.TestPaketBox.test_Klappen_oeffnen_success -v
  ```

## Validation

### Critical Requirements
- **ALWAYS run the full test suite** after making any changes: `PYTHONPATH=. python3 tests/run_tests.py`
- **NEVER CANCEL**: Test execution takes 65 seconds. Use timeouts of 5+ minutes minimum.
- All 28 tests must pass before committing changes
- Verify application starts without errors: `python3 paketbox.py` (exit with Ctrl+C)

### Manual Validation Scenarios
After making changes, validate these key scenarios through the test framework:
- **Complete delivery cycle**: Package door opens → closes → flaps open → flaps close → door unlocks
- **Error handling**: Motor failures are detected and system enters safe error state
- **GPIO simulation**: All sensor inputs and motor outputs function correctly
- **Thread safety**: Concurrent operations don't cause race conditions
- **State management**: Door states transition correctly (CLOSED ↔ OPEN ↔ ERROR)

### Test Coverage Validation
The test suite covers:
- ✅ All GPIO event handlers (flaps, delivery door, mailbox sensors)
- ✅ All motor control functions (opening/closing flaps with timers)
- ✅ Door lock/unlock operations
- ✅ Complete delivery workflow end-to-end
- ✅ Error detection and recovery mechanisms
- ✅ Thread-safe state management
- ✅ GPIO debouncing and timer operations

## Project Structure and Navigation

### Key Files (Ranked by Frequency of Access)
1. **`paketbox.py`** - Main control script (426 lines)
   - Contains all GPIO handlers, motor control functions, and state management
   - Includes MockGPIO class for hardware-independent testing
   - Entry point: `async def main()` with event loop
   
2. **`tests/test_paketbox.py`** - Comprehensive test suite
   - Unit tests (`TestPaketBox` class): Individual component testing
   - Integration tests (`TestPaketBoxIntegration` class): End-to-end scenarios
   - Always check this when modifying paketbox.py functionality

3. **`tests/run_tests.py`** - Test runner with detailed output and summary
   - Use this for full test execution with proper reporting

4. **`TEST_README.md`** - Detailed test environment documentation
   - Reference for understanding test scenarios and adding new tests

5. **`README.md`** - Project overview and basic setup instructions

6. **Deployment scripts**: `deploy_paketbox.sh` / `deploy_paketbox.bat`
   - Used for deploying to actual Raspberry Pi hardware

### Important Code Locations
- **State Management**: `class PaketBoxState` in paketbox.py (line 47)
- **GPIO Handlers**: `# region Callsbacks` in paketbox.py (line 188)
- **Motor Control**: `# region Actions` in paketbox.py (line 304)
- **Mock GPIO**: `class MockGPIO` in paketbox.py (lines 19-41)
- **Test Setup**: `setUp()` methods in test_paketbox.py for proper test isolation

## Dependencies and Environment

### Required Dependencies
- **Python 3.x** (tested with Python 3.12.3)
- **Standard library only**: unittest, threading, time, asyncio, enum
- **Hardware dependency**: RPi.GPIO (only on actual Raspberry Pi)
  - **Mock fallback included**: Automatic MockGPIO when RPi.GPIO unavailable
  - **No installation needed** for development/testing

### Environment Setup
- **No package installation required** for development
- **PYTHONPATH requirement**: Use `PYTHONPATH=.` for running tests from repository root
- **No build tools needed**: Pure Python, no compilation step
- **No linting configuration**: No automated code formatting rules defined

## Common Development Tasks

### Adding New Functionality
1. **Always start with tests**: Add test cases in `tests/test_paketbox.py`
2. **Follow existing patterns**: Use `@patch('paketbox.GPIO')` to mock hardware
3. **Implement in paketbox.py**: Add to appropriate region (Callbacks/Actions)
4. **Validate with full test suite**: `PYTHONPATH=. python3 tests/run_tests.py`
5. **Test manually**: Run `python3 paketbox.py` to verify application starts

### Debugging Issues
1. **Check test output**: Failed tests provide detailed error information
2. **Use mock GPIO logs**: MockGPIO prints all operations for debugging
3. **Verify imports**: Test with `python3 -c "import paketbox"`
4. **Check PYTHONPATH**: Tests require `PYTHONPATH=.` to find paketbox module

### Deployment Workflow
- **Development**: Always test in mock mode first
- **Integration**: Run full test suite for validation  
- **Production**: Use deployment scripts to copy to Raspberry Pi
- **Hardware testing**: Only after successful mock validation

## Timing Expectations

### Command Execution Times
- **Full test suite**: 65 seconds - **NEVER CANCEL, SET 5+ MINUTE TIMEOUTS**
- **Application startup**: <5 seconds to initialize and show "init abgeschlossen"
- **Individual tests**: 1-5 seconds each
- **Import validation**: <1 second

### Critical Timeout Settings
- **Test execution**: Minimum 300 seconds (5 minutes) timeout
- **Application startup**: 30 seconds timeout sufficient
- **GPIO operations**: Instantaneous in mock mode

## Hardware Context

### Physical System (Reference Only)
- **Target platform**: Raspberry Pi with GPIO control
- **Motors**: 2 flap motors with position sensors
- **Sensors**: Door position sensors, mailbox sensors, motion detection
- **Relais**: Motor control and door locking mechanisms
- **Operation**: Automated package acceptance and secure storage

### Development Environment
- **Mock simulation**: Full GPIO simulation without hardware
- **Hardware independence**: All functionality testable without Raspberry Pi
- **GPIO timing**: Motor operations use 65-second timers (configurable)
- **State persistence**: Thread-safe state management across operations

Remember: This system controls physical hardware in production. Always validate changes thoroughly in mock mode before considering deployment to actual hardware.