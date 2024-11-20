#!/usr/bin/env python3
import argparse
import subprocess
import time
import random
import sys

def evaluate_condition(stdout, stderr, condition):
    """
    Evaluates the success condition using Python's `eval`.
    """
    try:
        return eval(condition, {"stdout": stdout, "stderr": stderr})
    except Exception as e:
        print(f"Error evaluating condition: {e}")
        return False

def execute_command(command, condition, attempts, delay, backoff, max_delay, jitter, timeout):
    """
    Executes the given command repeatedly until it succeeds or the maximum
    number of attempts is reached.
    """
    for attempt in range(1, attempts + 1):
        try:
            start_time = time.time()
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout,
            )
            stdout, stderr = result.stdout, result.stderr
            success = evaluate_condition(stdout, stderr, condition)

            print(f"Attempt {attempt}/{attempts}:")
            print(f"Command: {' '.join(command)}")
            print(f"Exit Code: {result.returncode}")
            print(f"Stdout: {stdout.strip()}")
            print(f"Stderr: {stderr.strip()}")

            if success:
                print("Condition met. Exiting.")
                return True
            else:
                print("Condition not met. Retrying...")
        except subprocess.TimeoutExpired:
            print(f"Command timed out after {timeout} seconds.")
        except Exception as e:
            print(f"Error executing command: {e}")

        # Exponential backoff with jitter
        sleep_time = min(delay * (2 ** (attempt - 1)), max_delay)
        if jitter > 0:
            sleep_time += random.uniform(0, jitter)
        print(f"Sleeping for {sleep_time:.2f} seconds before next attempt...")
        time.sleep(sleep_time)

    print("Maximum attempts reached. Exiting.")
    return False

def main():
    parser = argparse.ArgumentParser(
        description="Execute a command repeatedly until it succeeds or exhausts the allowed number of attempts."
    )
    parser.add_argument("command", nargs=argparse.REMAINDER, help="The command to execute.")
    parser.add_argument("-a", "--attempts", type=int, default=5, help="Maximum number of attempts (default: 5).")
    parser.add_argument("-d", "--delay", type=float, default=1.0, help="Initial delay before retries (default: 1 second).")
    parser.add_argument("-b", "--backoff", type=float, default=2.0, help="Exponential backoff multiplier (default: 2).")
    parser.add_argument("-m", "--max-delay", type=float, default=30.0, help="Maximum delay between attempts (default: 30 seconds).")
    parser.add_argument("-j", "--jitter", type=float, default=0.0, help="Maximum jitter added to delay (default: 0).")
    parser.add_argument("-t", "--timeout", type=float, default=10.0, help="Timeout for each command execution (default: 10 seconds).")
    parser.add_argument("-c", "--condition", type=str, default="result.returncode == 0", help="Python condition to determine success (default: 'result.returncode == 0').")
    
    args = parser.parse_args()

    if not args.command:
        print("Error: No command specified.")
        sys.exit(1)

    success = execute_command(
        command=args.command,
        condition=args.condition,
        attempts=args.attempts,
        delay=args.delay,
        backoff=args.backoff,
        max_delay=args.max_delay,
        jitter=args.jitter,
        timeout=args.timeout,
    )

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()