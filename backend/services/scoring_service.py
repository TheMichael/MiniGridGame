#!/usr/bin/env python3
"""
Scoring service for AI Agent Galaxy.
Extracted from original app.py - handles game scoring with risk-reward system.
"""


def calculate_score(prediction, actual_steps, succeeded):
    """
    Calculate score based on prediction accuracy.

    SIMPLIFIED SCORING SYSTEM:
    - Perfect prediction (0 steps off): 100 points
    - Close (1-10 steps off): 50 points
    - Far (11-20 steps off): 25 points
    - Way off (21+ steps off): 0 points

    Note: If agent fails (120 steps) and user predicted 120,
    they only get points for close prediction, not perfect.

    Args:
        prediction: User's prediction (string or int)
        actual_steps: Actual steps taken by AI agent
        succeeded: Whether AI agent succeeded in reaching goal

    Returns:
        int: Calculated score
    """
    try:
        predicted_steps = int(prediction)

        # Validate prediction range
        if predicted_steps < 1 or predicted_steps > 120:
            return 0

        # Calculate difference
        difference = abs(predicted_steps - actual_steps)

        # If agent failed (120 steps) and prediction was 120,
        # treat as close but not perfect
        if not succeeded and predicted_steps == 120 and actual_steps == 120:
            return 50  # Close prediction, not perfect

        # Simple scoring based on accuracy
        if difference == 0:
            return 100  # Perfect prediction
        elif difference <= 10:
            return 50   # Close
        elif difference <= 20:
            return 25   # Far
        else:
            return 0    # Way off

    except ValueError:
        return 0


def get_score_explanation(prediction, actual_steps, succeeded, score):
    """Generate simple explanation for the score calculation."""
    try:
        prediction_num = int(prediction)
    except (ValueError, TypeError):
        return "Invalid prediction."

    # Validate prediction
    if prediction_num < 1 or prediction_num > 120:
        return "Invalid prediction range."

    # Calculate difference
    difference = abs(prediction_num - actual_steps)

    # Special case: predicted 120 and agent failed at 120
    if not succeeded and prediction_num == 120 and actual_steps == 120:
        return "Agent failed at 120 steps. Close prediction!"

    # Simple explanations
    if difference == 0:
        return "Perfect prediction! Exactly right!"
    elif difference <= 10:
        return f"Close! Only {difference} steps off."
    elif difference <= 20:
        return f"Not bad! {difference} steps off."
    else:
        return f"Try again! You were {difference} steps off."