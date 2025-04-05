#!/bin/bash

# Maximum number of retries
MAX_RETRIES=2
RETRY_COUNT=0

# Run the tests first time
echo "Running tests - Attempt 1"
mvn clean verify

# Check if there are any failed scenarios
while [ -f "target/failed_scenarios.txt" ] && [ $RETRY_COUNT -lt $MAX_RETRIES ]
do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "Retrying failed scenarios - Attempt $((RETRY_COUNT + 1))"
    
    # Run only failed scenarios
    mvn verify -Dtest=RerunFailedTestsRunner
done

# Final status message
if [ -f "target/failed_scenarios.txt" ]; then
    echo "There are still failing scenarios after $MAX_RETRIES retries"
    exit 1
else
    echo "All tests passed successfully!"
    exit 0
fi 