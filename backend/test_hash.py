import hashlib

def simulate_rollout(flag_id="new_checkout_flow", target_percentage=50, total_users=10000):
    enabled_count = 0
    
    for i in range(total_users):
        # Generate 10,000 unique user IDs
        user_id = f"test_user_{i}"
        
        # Your exact targeting logic
        hash_input = f"{user_id}:{flag_id}".encode('utf-8')
        hash_int = int(hashlib.sha256(hash_input).hexdigest(), 16)
        bucket = hash_int % 100
        
        # If the bucket is 0-49, they get the feature
        if bucket < target_percentage:
            enabled_count += 1
            
    actual_percentage = (enabled_count / total_users) * 100
    print("--- HASH DISTRIBUTION RESULTS ---")
    print(f"Total Simulated Users: {total_users}")
    print(f"Target Rollout: {target_percentage}%")
    print(f"Actual Distribution: {actual_percentage}%")
    print("---------------------------------")

simulate_rollout()