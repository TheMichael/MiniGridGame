#!/usr/bin/env python3
"""
Scoring service for AI Agent Galaxy.
Extracted from original app.py - handles game scoring with risk-reward system.
"""


def calculate_score(prediction, actual_steps, succeeded):
    """
    Calculate score based on prediction accuracy and risk level.
    
    Args:
        prediction: User's prediction (string or int, 'fail' for failure prediction)
        actual_steps: Actual steps taken by AI agent
        succeeded: Whether AI agent succeeded in reaching goal
        
    Returns:
        int: Calculated score
    """
    if prediction == 'fail':
        return 3 if not succeeded else 0
    
    try:
        predicted_steps = int(prediction)
        difference = abs(predicted_steps - actual_steps)
        
        # Base score from accuracy
        if difference == 0:
            base_score = 10
        elif difference <= 5:
            base_score = 8
        elif difference <= 10:
            base_score = 5
        else:
            base_score = 0
        
        # Risk-reward multiplier system
        if 35 <= predicted_steps <= 55:
            multiplier = 0.4
        elif 30 <= predicted_steps <= 65:
            multiplier = 0.7
        elif predicted_steps <= 29:
            multiplier = 0.1
        elif 66 <= predicted_steps <= 85:
            multiplier = 1.5
        elif predicted_steps >= 86:
            multiplier = 2.0
        else:
            multiplier = 1.0
        
        final_score = int(base_score * multiplier)
        return max(final_score, 1) if base_score > 0 else 0
        
    except ValueError:
        return 0


def get_score_explanation(prediction, actual_steps, succeeded, score):
    """Generate explanation for the score calculation."""
    prediction_num = int(prediction) if prediction != 'fail' else 0
    
    if prediction_num == 0:
        return "PERFECT! You predicted the failure correctly!" if not succeeded else "The agent actually succeeded, no points this time."
    
    difference = abs(prediction_num - actual_steps)
    
    # Base accuracy explanation
    if difference == 0:
        accuracy = "BULL'S EYE! Perfect prediction!"
    elif difference <= 5:
        accuracy = f"CLOSE! Only {difference} steps off."
    elif difference <= 10:
        accuracy = f"DECENT! {difference} steps off."
    else:
        accuracy = f"OFF TARGET - {difference} steps difference."
    
    # Risk zone explanation
    if 35 <= prediction_num <= 55:
        risk_explanation = " (Safe zone penalty applied)"
    elif prediction_num <= 29:
        risk_explanation = " (Impossible zone - heavy penalty)"
    elif 66 <= prediction_num <= 85:
        risk_explanation = " (Struggle zone bonus!)"
    elif prediction_num >= 86:
        risk_explanation = " (Failure zone bonus!)"
    else:
        risk_explanation = ""

    return f"{accuracy}{risk_explanation}"