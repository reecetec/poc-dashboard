import socket
import sys

# Use the same service name as your app
pg_host = "postgres.ducklake.svc.cluster.local"
pg_port = 5432

print("--- Running Pre-flight Check ---")
print(f"Attempting to connect to {pg_host} on port {pg_port}...")

try:
    # Create a socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Set a short timeout so the script fails fast
    sock.settimeout(15)
    # Attempt to connect
    result = sock.connect_ex((pg_host, pg_port))

    if result == 0:
        print("Connection successful!")
        sock.close()
        sys.exit(0)  # Exit with success code
    else:
        print(f"Connection failed. Error code: {result}")
        print(
            "This is likely due to a NetworkPolicy blocking traffic between namespaces."
        )
        sock.close()
        sys.exit(1)  # Exit with failure code

except socket.gaierror:
    print(f"DNS resolution failed. Could not resolve host: {pg_host}")
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    sys.exit(1)
