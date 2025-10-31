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
- Add per game columns and per 36 minute columns for cumulative stats, giving the model more context.    
- Normalize stats by season by using the ratio-to-mean to compare performance to league average in that season. This accounts for leaguewide trends across time. (Ex: 20 PPG in 2025 is much more common than it was in 2015 due the widespread adoption of increasing three point attempts and a faster pace of play).    
- Normalize our target variable across years by using salary ratio instead of pure salary.    
    - salary ratio: A player’s salary as a percentage of the allowed maximum salary cap for that season.    

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