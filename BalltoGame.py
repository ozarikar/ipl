import pandas as pd
import numpy as np

# Load the dataset
try:
    df = pd.read_csv('ipl_data_combined.csv', low_memory=False)
except FileNotFoundError:
    print("Error: 'sample_ipl_data.csv' not found. Make sure the file is in the same directory.")
    exit()

# --- 1. Data Cleaning and Basic Preparation ---
df.columns = df.columns.str.replace('"', '').str.strip()
# Reduced to only necessary columns for calculation + TeamName for winner determination
numeric_cols = [
    'IsExtra', 'Extras', 'RunRuns', 'IsDotball', 'MatchID',
    'IsWicket', 'InningsNo', 'ActualRuns', 'IsFour', 'IsSix', 'OverNo'
]
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    else:
        print(f"Warning: Essential column '{col}' not found in CSV. Results may be incorrect.")
        if col not in df.columns: # Create dummy if missing, but indicates problem
             df[col] = 0


cols_to_fill_na = ['ActualRuns', 'IsWicket', 'IsFour', 'IsSix', 'IsDotball', 'Extras', 'RunRuns']
for col in cols_to_fill_na:
    if col in df.columns:
        df[col] = df[col].fillna(0)

df['OverInteger'] = df['OverNo'].fillna(0).astype(float).astype(int)

# --- 2. Define Game Phases ---
df['Phase'] = 'Other' # Default for any balls not in defined phases (e.g. >20 overs if data has errors)
df.loc[df['OverInteger'] < 6, 'Phase'] = 'Powerplay'
df.loc[(df['OverInteger'] >= 6) & (df['OverInteger'] < 15), 'Phase'] = 'MiddleOvers'
df.loc[(df['OverInteger'] >= 15) & (df['OverInteger'] < 20), 'Phase'] = 'DeathOvers' # Assuming T20 max 20 overs

# --- 3. Function to Calculate Per-Innings Stats (Focused) ---
def get_innings_summary(innings_df):
    if innings_df.empty:
        empty_stats = {'TeamName': 'N/A'}
        metrics = ['Runs', 'Fours', 'Sixes', 'WicketsLost']
        phases = ['Powerplay', 'MiddleOvers', 'DeathOvers'] # No 'Overall' for these from phases
        for metric in metrics:
            for phase in phases:
                empty_stats[f'Batting_{metric}_{phase}'] = 0
        empty_stats['Batting_DotBalls_Overall'] = 0 # Dotballs only overall
        empty_stats['Bowling_ExtrasConceded_Overall'] = 0
        empty_stats['Bowling_BowlersUsed_Overall'] = 0
        return empty_stats

    summary = {}
    summary['TeamName'] = innings_df['TeamName'].iloc[0] if 'TeamName' in innings_df.columns and not innings_df['TeamName'].dropna().empty else 'N/A'

    # Batting Stats by Phase (Powerplay, Middle, Death)
    for phase_name, phase_df in innings_df.groupby('Phase'):
        if phase_name not in ['Powerplay', 'MiddleOvers', 'DeathOvers']: # Skip 'Other' phase if any
            continue
        summary[f'Batting_Runs_{phase_name}'] = phase_df['ActualRuns'].sum()
        summary[f'Batting_Fours_{phase_name}'] = phase_df['IsFour'].sum()
        summary[f'Batting_Sixes_{phase_name}'] = phase_df['IsSix'].sum()
        summary[f'Batting_WicketsLost_{phase_name}'] = phase_df['IsWicket'].sum()

    # Overall DotBalls (sum across all balls in the innings)
    summary['Batting_DotBalls_Overall'] = innings_df['IsDotball'].sum()
    
    # Bowling Stats for the team bowling in this innings (Overall)
    summary['Bowling_ExtrasConceded_Overall'] = innings_df['Extras'].sum()
    summary['Bowling_BowlersUsed_Overall'] = innings_df['BowlerName'].nunique() if 'BowlerName' in innings_df.columns else 0
    
    # Ensure all expected keys exist with 0 if not calculated
    metrics_bat_phase = ['Runs', 'Fours', 'Sixes', 'WicketsLost']
    phases_only = ['Powerplay', 'MiddleOvers', 'DeathOvers']
    for m in metrics_bat_phase:
        for p in phases_only:
            key = f'Batting_{m}_{p}'
            if key not in summary:
                summary[key] = 0
    if 'Batting_DotBalls_Overall' not in summary: summary['Batting_DotBalls_Overall'] = 0
    if 'Bowling_ExtrasConceded_Overall' not in summary: summary['Bowling_ExtrasConceded_Overall'] = 0
    if 'Bowling_BowlersUsed_Overall' not in summary: summary['Bowling_BowlersUsed_Overall'] = 0
    
    return summary

# --- 4. Process Each Match and Create Comparative Features ---
all_comparative_features = []

if 'MatchID' not in df.columns or 'InningsNo' not in df.columns:
    print("Error: 'MatchID' or 'InningsNo' column is missing from the input CSV.")
    exit()

for match_id, group in df.groupby('MatchID'): # Still need match_id for grouping
    match_features = {} # No MatchID in the final features dictionary

    in1_df = group[group['InningsNo'] == 1]
    in2_df = group[group['InningsNo'] == 2]

    stats_in1 = get_innings_summary(in1_df) # Team1 batting, Team2 bowling
    stats_in2 = get_innings_summary(in2_df) # Team2 batting, Team1 bowling

    # --- Determine Winner (for Team1_Won target variable) ---
    team1_name_for_winner = stats_in1['TeamName'] # Needed for winner logic
    # Calculate overall runs for winner determination
    team1_runs_overall = stats_in1.get('Batting_Runs_Powerplay',0) + \
                         stats_in1.get('Batting_Runs_MiddleOvers',0) + \
                         stats_in1.get('Batting_Runs_DeathOvers',0)
    team2_runs_overall = stats_in2.get('Batting_Runs_Powerplay',0) + \
                         stats_in2.get('Batting_Runs_MiddleOvers',0) + \
                         stats_in2.get('Batting_Runs_DeathOvers',0)
    
    winner_name = 'N/A'
    if team1_runs_overall > team2_runs_overall:
        winner_name = team1_name_for_winner
    elif team2_runs_overall > team1_runs_overall:
        winner_name = stats_in2['TeamName']
    else:
        winner_name = 'Tie'

    match_features['Team1_Won'] = 0
    if pd.notna(team1_name_for_winner) and team1_name_for_winner != 'N/A' and winner_name == team1_name_for_winner:
        match_features['Team1_Won'] = 1
    
    # --- Calculate Comparative (Margin) Features: (Team1 - Team2) ---
    # PHASES for Runs, Fours, Sixes, WicketsTaken
    phases_for_metrics = ['Powerplay', 'MiddleOvers', 'DeathOvers']
    
    # Batting Performance Margin (Runs, Fours, Sixes faced by Team1 vs Team2) per PHASE
    for metric in ['Runs', 'Fours', 'Sixes']:
        for phase in phases_for_metrics:
            t1_stat = stats_in1.get(f'Batting_{metric}_{phase}', 0)
            t2_stat = stats_in2.get(f'Batting_{metric}_{phase}', 0)
            match_features[f'{metric}_Margin_{phase}'] = t1_stat - t2_stat

    # Wickets Taken Margin per PHASE (Wickets taken by Team1's bowlers - Wickets taken by Team2's bowlers)
    for phase in phases_for_metrics:
        wkts_taken_by_T1 = stats_in2.get(f'Batting_WicketsLost_{phase}', 0) 
        wkts_taken_by_T2 = stats_in1.get(f'Batting_WicketsLost_{phase}', 0)
        match_features[f'WicketsTaken_Margin_{phase}'] = wkts_taken_by_T1 - wkts_taken_by_T2

    # OVERALL Margins for DotBalls, ExtrasConceded, BowlersUsed
    # DotBalls Margin (Overall)
    t1_dotballs = stats_in1.get('Batting_DotBalls_Overall', 0)
    t2_dotballs = stats_in2.get('Batting_DotBalls_Overall', 0)
    match_features['DotBalls_Margin_Overall'] = t1_dotballs - t2_dotballs
    
    # Extras Conceded Margin (Overall)
    extras_conceded_T1_bowlers = stats_in2.get('Bowling_ExtrasConceded_Overall', 0)
    extras_conceded_T2_bowlers = stats_in1.get('Bowling_ExtrasConceded_Overall', 0)
    match_features['ExtrasConceded_Margin_Overall'] = extras_conceded_T1_bowlers - extras_conceded_T2_bowlers

    # Bowlers Used Margin (Overall)
    bowlers_used_T1 = stats_in2.get('Bowling_BowlersUsed_Overall', 0)
    bowlers_used_T2 = stats_in1.get('Bowling_BowlersUsed_Overall', 0)
    match_features['BowlersUsed_Margin_Overall'] = bowlers_used_T1 - bowlers_used_T2
            
    all_comparative_features.append(match_features)

# --- 5. Create Final DataFrame ---
model_ready_df = pd.DataFrame(all_comparative_features)

# Define expected column order for readability and consistency
ordered_cols = ['Team1_Won'] 
# Overall margins that are kept
overall_margins_kept = ['DotBalls_Margin_Overall', 'ExtrasConceded_Margin_Overall', 'BowlersUsed_Margin_Overall']
ordered_cols.extend(sorted([col for col in model_ready_df.columns if col in overall_margins_kept]))

# Phase-specific margins
metrics_for_phase_margins = ['Runs', 'Fours', 'Sixes', 'WicketsTaken']
phases_order = ['Powerplay', 'MiddleOvers', 'DeathOvers']

for metric in metrics_for_phase_margins:
    for phase in phases_order:
        col_name = f'{metric}_Margin_{phase}'
        if col_name in model_ready_df.columns:
            ordered_cols.append(col_name)

# Ensure all columns are present and in order
final_ordered_cols = [col for col in ordered_cols if col in model_ready_df.columns]
# Add any columns that might have been generated but not in explicit order (should prevent issues)
for col in model_ready_df.columns:
    if col not in final_ordered_cols:
        final_ordered_cols.append(col)

model_ready_df = model_ready_df[final_ordered_cols]


# --- Display or Save ---
print(f"Successfully processed {model_ready_df.shape[0]} matches into comparative features.")
print("Model-ready comparative features DataFrame head (No MatchID, No Overall for Runs/Fours/Sixes/Wickets):")
print(model_ready_df.head().to_string())

model_ready_df.to_csv('games_summary.csv', index=False)
print("\nModel-ready comparative features saved to 'game_summary_model_ready_final.csv'")
print(f"\nTotal columns generated: {len(model_ready_df.columns)}")
print("Columns:", model_ready_df.columns.tolist())
print("\nInfo for the generated DataFrame:")
model_ready_df.info()