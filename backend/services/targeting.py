import hashlib

def evaluate_flag(flag: dict, user_context: dict) -> bool:
    """
    Pure function to evaluate if a flag is enabled for a specific user context.
    It expects the flag data as a dictionary (parsed from DB/Pydantic) and the user context.
    """
    # If the master switch is off, the flag is off for everyone
    if not flag.get("enabled", False):
        return False
    
    rule = flag.get("targeting_rule", {})
    rule_type = rule.get("type", "everyone")
    
    if rule_type == "everyone":
        return True
    
    elif rule_type == "group":
        # 1. Grab the nested 'context' dictionary that Flutter sends
        inner_context = user_context.get("context", {})
        
        # 2. Extract the groups from that inner dictionary
        user_groups = inner_context.get("groups", [])
        rule_groups = rule.get("groups", [])
        
        # Returns True if there's any intersection
        return bool(set(rule_groups) & set(user_groups))
    
    elif rule_type == "user_ids":
        return user_context.get("userId") in rule.get("ids", [])
    
    elif rule_type == "percentage":
        user_id = user_context.get("userId", "anonymous")
        # Combine user_id and flag_id so a user isn't always in the 10% bucket for *all* flags
        hash_input = f"{user_id}:{flag.get('id')}".encode('utf-8')
        
        # Convert sha256 hex string to an integer
        hash_int = int(hashlib.sha256(hash_input).hexdigest(), 16)
        
        # Map the integer to a 0-99 bucket
        bucket = hash_int % 100
        
        # If bucket is less than the percentage target, user is in the rollout
        return bucket < rule.get("percentage", 0)
    
    # Fail safe: if the rule is unknown, return False
    return False