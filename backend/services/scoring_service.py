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
    - Failure prediction bonus: +50 points if correct

    Args:
        prediction: User's prediction (string or int, 'fail' for failure prediction)
        actual_steps: Actual steps taken by AI agent
        succeeded: Whether AI agent succeeded in reaching goal

    Returns:
        int: Calculated score
    """
    # Handle failure prediction
    if prediction == 'fail' or prediction == '0':
        return 50 if not succeeded else 0

    try:
        predicted_steps = int(prediction)

        # Failure prediction if they entered 0
        if predicted_steps == 0:
            return 50 if not succeeded else 0

        # Calculate difference
        difference = abs(predicted_steps - actual_steps)

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
        prediction_num = int(prediction) if prediction != 'fail' else 0
    except (ValueError, TypeError):
        prediction_num = 0

    # Handle failure prediction
    if prediction_num == 0:
        if not succeeded:
            return "Perfect! You correctly predicted the agent would fail."
        else:
            return "The agent succeeded. Better luck next time!"

    # Calculate difference
    difference = abs(prediction_num - actual_steps)

    # Simple explanations
    if difference == 0:
        return "Perfect prediction! Exactly right!"
    elif difference <= 10:
        return f"Close! Only {difference} steps off."
    elif difference <= 20:
        return f"Not bad! {difference} steps off."
    else:
        return f"Try again! You were {difference} steps off."