# NBA Salary Prediction Model

In this project, I use historical NBA player performance data from 2013-2024 to predict the average annual value of contracts for upcoming free agents.

## Introduction
**Idea**: Can historical data be used to predict the salary that an upcoming NBA free agents will command?  

**Stakeholders**:
- NBA Teams:  
    - Use predictions to guide salary negotiations  
    - Identify underpaid players to target in trades  
- Players and Agents:  
    - Gain insight into the free agency market  
    - Use favorable predictions as leverage in contract negotiations  
    - Make informed decisions regarding contract offers and career moves  
- Sponsors:   
    - Assess player value for endorsements and sponsorship deals  
    - Identify future high-value players, primed to bring influence to a brand  

## Data
**1. Spotrac Active NBA Contracts Database:**  
https://www.spotrac.com/nba/contracts  
Features:  Player, POS: Primary position, AGE (at signing), START: Year contract begins, END: Year contract ends, Yrs: Contract length, Value: Total contract value, AAV: Average annual value of contract

**2. NBA Stats Kaggle Dataset, via NBA.com**
https://www.kaggle.com/datasets/shivamkumar121215/nba-stats-dataset-for-last-10-years
Features: Player, Year, Team, regular season and playoff stats: GP, MIN, PTS, FGM, FGA, FG_PCT, FG3M, FG3A, FG3_PCT, FTM, FTA, FT_PCT, OREB, DREB, REB, AST, STL, BLK, TOV, PF

**3. nba_api (Python package)**
https://github.com/swar/nba_api
Used to fetch 2024-25 player stats (regular season and playoffs) and player age/position data directly from NBA.com endpoints.

## Preprocessing 
### Cleaning:  
- Replaced null playoff statistics with 0 (player’s team did not make playoffs).    
- Changed data types to fit context (Ex: Age from Object to Int64).    
- Filled missing age values with league median.    
- Filter out non-standard contracts (10-day and two-way deals).    
- Pivot table so that playoff and regular season stats are counted as separate features and rows are uniquely indexed by player, season.  
- Inner join deals and stats tables on player and year/season.  
- Match reformat seasons from YYYY-YY to just the year that the season ended. This is to match the year the contract is signed in.

### Feature Engineering:

**Target Variable:**
- `salary_ratio`: AAV divided by the league salary cap for that year — normalizes salary across seasons so the model learns value relative to the cap, not raw dollars.

**Per-Game and Per-36 Statistics:**
- `[stat]_per_game`: Each counting stat divided by games played (regular season and playoffs).
- `[stat]_per36`: Each counting stat scaled to a 36-minute pace (regular season and playoffs) — standard NBA efficiency metric.

**Season-Normalized Ratio Features:**
- `[stat]_ratio`: Each stat expressed as deviation from the league average for that season (i.e., `player_stat / league_mean - 1`). Applied to counting stats, per-game, and per-36 variants. Accounts for league-wide trends over time (e.g., 20 PPG is far more common in 2025 than 2015).

**Advanced Efficiency Metrics:**
- `TS_pct_RegularSeason` / `TS_pct_Playoffs`: True Shooting Percentage — accounts for 2-pointers, 3-pointers, and free throws. Formula: `PTS / (2 * (FGA + 0.44 * FTA))`.
- `USG_proxy_RegularSeason` / `USG_proxy_Playoffs`: Usage rate proxy — share of team offensive possessions used per 36 minutes. Formula: `(FGA + 0.44*FTA + TOV) / MIN * 36`.

**Composite and Uplift Features:**
- `BoxComposite_RegularSeason` / `BoxComposite_Playoffs`: Points + Rebounds + Assists per game — a simple star-quality signal.
- `PTS_uplift`, `REB_uplift`, `AST_uplift`: Per-game playoff stat minus regular season stat — captures whether a player elevates in the postseason. Players whose teams missed the playoffs receive 0 (no penalty).

**Playoff Participation:**
- `made_playoffs`: Binary flag (1/0) indicating whether the player appeared in any playoff games that season.

**Non-Linear Age:**
- `Age_squared`: Age² — captures the non-linear relationship between age and salary (peak value around 27–29, declining on either side).

## Model Selection
### Models
- Simple Regression: Linear, Lasso (L1), Ridge (L2)  
- Tree Methods: Decision Tree Regression  
- Ensemble Methods: Random Forests Regressor, XGBoost Regressor  

### Evaluation Metrics
- R-squared  
- RMSE: root mean squared error  
- MAE: mean absolute error  
- CV-Score: Mean of r-squared scores for 7 folds  

### Hyperparameter Tuning
- Random Search CV
    - Tested 50 random hyperparameter combos over 7 folds = 350 fits

## Model Performance

### Initial Scores:
| | CV-score | R-squared | RMSE | MAE |
|---|---|---|---|---|
| **Random Forest** | **0.737575** | **0.783471** | **0.036683** | **0.023094** |
| XGBoost | 0.732902 | 0.767611 | 0.038003 | 0.023791 |
| Lasso | 0.717650 | 0.762571 | 0.038413 | 0.025681 |
| Ridge | 0.711132 | 0.754802 | 0.039036 | 0.026725|
| LinearRegression | 0.701215 | 0.752167 | 0.039246 | 0.026680 |

### RandomForest with Hyperparamter Tuning + Feature Engineering:
* CV-Score: **0.783157**  
* RMSE: **0.028013**  
* MAE: **0.016291**

## Results  
Player | Predicted AAV | Actual AAV | % Difference |
|---|---|---| --- |
| Myles Turner |-- | -- | -- |
| Kyrie Irving |-- | -- | -- |
| Duncan Robinson |-- | -- | -- |
| Luke Kornet |-- | -- | -- |
| Russell Westbrook |-- | -- | -- |
| Ty Jerome |-- | -- | -- |
| Al Horford |-- | -- | -- |


## Author
Caedin Manners  
Data Science B.A.  
UC Berkely c/o 2025