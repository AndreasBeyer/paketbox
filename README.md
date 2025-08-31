# Paketbox control in python

Quick and Dirty

## Test Environment

This project includes a comprehensive test environment that simulates the Raspberry Pi hardware without requiring actual GPIO hardware.

### Running Tests

```bash
# Run all tests with detailed output
python run_tests.py

# Run specific tests
python -m unittest test_paketbox.py -v
```

### Test Features

- **GPIO Simulation**: Complete mock of RPi.GPIO module
- **Unit Tests**: Tests for all system functions and state management
- **Integration Tests**: Complete delivery workflow testing
- **Error Simulation**: Tests error conditions and recovery
- **Thread Safety**: Ensures concurrent operations work correctly

**Test Coverage**: 28 tests covering all system states, GPIO operations, motor control, and error handling.

See [TEST_README.md](TEST_README.md) for detailed testing documentation.

## Deployment

Use the deployment script to copy the main script to a Raspberry Pi:

```bash
./deploy_paketbox.sh <USER> <RASPBERRY_PI_IP> <TARGET_PATH>
```
