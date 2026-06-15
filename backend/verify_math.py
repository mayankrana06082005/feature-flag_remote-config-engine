import hashlib
import uuid

def check_rollout(user_id: str, flag_id: str, percentage: int) -> bool:
    """Replicates your FastAPI backend's deterministic hashing logic."""
    hash_str = f"{user_id}:{flag_id}".encode('utf-8')
    # Convert the SHA-256 hex string into an integer
    hash_int = int(hashlib.sha256(hash_str).hexdigest(), 16)
    # Check if the modulo 100 falls under the target percentage
    return (hash_int % 100) < percentage

def run_simulation():
    flag_id = "new_checkout_flow"
    target_percentage = 10
    total_users = 10000
    enabled_count = 0

    print("Simulating 10,000 unique user sessions...")

    for _ in range(total_users):
        # Generate a completely random, unique user ID for every loop
        user_id = str(uuid.uuid4())
        if check_rollout(user_id, flag_id, target_percentage):
            enabled_count += 1

    actual_percentage = (enabled_count / total_users) * 100

    print("\n==========================================")
    print(" 🧪 DETERMINISTIC MATH VERIFICATION")
    print("==========================================")
    print(f" Target Rollout : {target_percentage}%")
    print(f" Total Users    : {total_users:,}")
    print(f" Users Enabled  : {enabled_count:,}")
    print(f" Actual Rollout : {actual_percentage:.2f}%")
    print("==========================================")
    
    # A standard deviation of +/- 1% is excellent for 10k users
    if 9.0 <= actual_percentage <= 11.0:
        print(" ✅ PASS: Distribution is mathematically sound.")
    else:
        print(" ❌ FAIL: Distribution is skewed.")

if __name__ == "__main__":
    run_simulation()