from datetime import datetime

def get_escalation_status(category, priority_score, created_at, status):
    
    # if already resolved no escalation needed
    if status == 'Resolved':
        return {
            "escalation_level": "Resolved",
            "days_pending": 0,
            "new_score": priority_score,
            "message": "✅ Issue has been resolved"
        }

    # calculate days pending
    created = datetime.strptime(created_at, '%d-%m-%Y %I:%M %p')
    days_pending = (datetime.now() - created).days

    # risk factor by category
    risk_factors = {
        'Water': 4,
        'Sanitation': 5,
        'Road': 3,
        'Electricity': 3,
        'Other': 2
    }

    risk = risk_factors.get(category, 2)

    # calculate new escalated score
    new_score = min(100, priority_score + (days_pending * risk))

    # determine escalation level
    if days_pending >= 7:
        level = "Critical"
        message = f"🔴 CRITICAL! Pending for {days_pending} days. Immediate action required!"
    elif days_pending >= 3:
        level = "Warning"
        message = f"🟡 WARNING! Pending for {days_pending} days. Solve soon!"
    else:
        level = "On Track"
        message = f"🟢 On Track. Pending for {days_pending} days."

    return {
        "escalation_level": level,
        "days_pending": days_pending,
        "new_score": new_score,
        "message": message
    }